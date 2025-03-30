
import stripe
import json
from decimal import Decimal
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from cart.models import Cart
from django.core.mail import send_mail
from django.template.loader import render_to_string
from products.models import Product
from .models import Order, OrderItem, ShippingAddress
from .forms import ShippingAddressForm
from checkout.webhook_handlers import StripeWebhookHandler
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout(request):
    """
    Handle checkout for both authenticated and guest users.
    """
    # Determine current user: use request.user if authenticated, else None
    user = request.user if request.user.is_authenticated else None

    # Retrieve cart items
    if user:
        cart_items_qs = Cart.objects.filter(user=user)
        if not cart_items_qs.exists():
            messages.error(request, "Your cart is empty!")
            return redirect("cart_detail")
        subtotal = sum(item.product.price * Decimal(item.quantity) for item in cart_items_qs)
        cart_items = cart_items_qs
    else:
        session_cart = request.session.get("cart", {})
        if not session_cart:
            messages.error(request, "Your cart is empty!")
            return redirect("cart_detail")
        subtotal = Decimal("0.00")
        cart_items = []
        product_ids = session_cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            quantity = Decimal(str(session_cart.get(str(product.id), 0)))
            line_total = product.price * quantity
            subtotal += line_total
            cart_items.append({
                "product": product,
                "quantity": quantity,
                "line_total": line_total,
            })

    # Calculate delivery cost and grand total
    delivery_cost = Decimal("0.00") if subtotal >= settings.FREE_DELIVERY_THRESHOLD else (Decimal(settings.STANDARD_DELIVERY_PERCENTAGE) / 100) * subtotal
    grand_total = subtotal + delivery_cost

    client_secret = None

    if request.method == "POST":
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            # Use the 'user' variable determined above
            shipping_address = form.save(commit=False)
            shipping_address.user = user 
            shipping_address.save()

            # Create an order
            order = Order.objects.create(
                user=user,  
                total_price=grand_total,
                shipping_address=shipping_address
            )

            # Create OrderItems from the cart data
            if user:
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity
                    )
                # Clear cart for logged-in user
                Cart.objects.filter(user=user).delete()
            else:
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item["product"],
                        quantity=item["quantity"]
                    )
                # Clear session cart
                request.session["cart"] = {}
                send_order_confirmation_email(order)

            # Create a Stripe PaymentIntent (amount in cents)
            payment_intent = stripe.PaymentIntent.create(
                amount=int(grand_total * 100),
                currency="gbp",
                metadata={"order_id": order.id},
            )
            client_secret = payment_intent.client_secret

            return JsonResponse({
                "client_secret": client_secret,
                "order_id": order.id,
            })
        else:
            errors = form.errors.as_json()
            return JsonResponse({"errors": errors}, status=400)
    else:
        form = ShippingAddressForm()

    return render(request, "checkout/checkout.html", {
        "form": form,
        "cart_items": cart_items,
        "subtotal": round(float(subtotal), 2),
        "delivery_cost": round(float(delivery_cost), 2),
        "grand_total": round(float(grand_total), 2),
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
    })


def send_order_confirmation_email(order):
    full_name = order.shipping_address.full_name
    order_items = OrderItem.objects.filter(order=order)

    subject = render_to_string(
        'checkout/confirmation_emails/confirmation_email_subject.txt',
    ).strip()

    body = render_to_string(
        'checkout/confirmation_emails/confirmation_email_body.txt',
        {
            'order': order,
            'full_name': full_name,
            'order_items': order_items,
        }
    )

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [order.shipping_address.email],
        fail_silently=False,
    )



def order_summary(request, order_id):
    """
    Display the order summary.
    For authenticated users, ensure the order belongs to them.
    For guest orders, user can view the order if they have the link.
    """
    order = get_object_or_404(Order, id=order_id)
    if request.user.is_authenticated and order.user and order.user != request.user:
        return HttpResponse("Unauthorized", status=401)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, "checkout/order_summary.html", {
        "order": order,
        "order_items": order_items,
    })


def order_success(request, order_id):
    # Retrieve the order regardless of user, then check if user is authenticated.
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    if request.user.is_authenticated and order.user and order.user != request.user:
        Cart.objects.filter(user=request.user).delete()
    else:
        request.session['cart'] = {}

    return render(request, "checkout/order_success.html", {
        "order": order,
        "order_items": order_items,
    })


def payment(request, order_id):
    """
    Render the payment page with the PaymentIntent's client secret.
    """
    order = get_object_or_404(Order, id=order_id)
    payment_intent = stripe.PaymentIntent.create(
        amount=int(order.total_price * 100),
        currency="gbp",
        metadata={"order_id": order.id}
    )
    return render(request, "checkout/payment.html", {
        "order": order,
        "client_secret": payment_intent.client_secret,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
    })


def payment_success(request):
    """
    Mark the order as 'paid' after successful payment and redirect to order success.
    """
    session_id = request.GET.get("session_id")
    if not session_id:
        messages.error(request, "No payment session found.")
        return redirect("checkout")
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        order_id = session.metadata.get("order_id")
        if not order_id:
            messages.error(request, "Order metadata missing from payment session.")
            return redirect("checkout")
        
        order = get_object_or_404(Order, id=order_id)
        order.status = "paid"
        order.payment_id = session.payment_intent
        order.save()
        
        messages.success(request, "Payment successful! Your order has been placed.")
        return redirect("order_success", order_id=order.id)
        
    except stripe.error.StripeError as e:
        messages.error(request, "Error retrieving payment session: " + str(e))
        return redirect("checkout")


def payment_cancel(request):
    """
    Handle failed or canceled payments.
    """
    messages.warning(request, "Payment was canceled. Please try again.")
    return redirect("checkout")


@csrf_exempt
def stripe_webhook(request):
    """
    Handle Stripe webhooks.
    """
    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    handler = StripeWebhookHandler(request)
    event_type = event['type']
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_failed,
    }
    event_handler = event_map.get(event_type, handler.handle_event)
    return event_handler(event)

