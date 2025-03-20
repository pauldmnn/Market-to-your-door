import stripe
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from cart.models import Cart
from .models import Order, OrderItem, ShippingAddress
from .forms import ShippingAddressForm
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse
from checkout.webhook_handlers import StripeWebhookHandler

stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout(request):
    # Retrieve cart items for the current user
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect("cart_detail")

    # Calculate totals
    subtotal = sum(item.product.price * Decimal(item.quantity) for item in cart_items)
    delivery_cost = (Decimal('0.00') if subtotal >= settings.FREE_DELIVERY_THRESHOLD 
                     else (Decimal(settings.STANDARD_DELIVERY_PERCENTAGE) / 100) * subtotal)
    grand_total = subtotal + delivery_cost

    client_secret = None

    if request.method == "POST":
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            # Save shipping address
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()

            # Create an order
            order = Order.objects.create(
                user=request.user,
                total_price=grand_total,
                shipping_address=shipping_address
            )

            # Create OrderItems for each cart item
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity
                )

            # Create a Stripe PaymentIntent (amount in cents)
            payment_intent = stripe.PaymentIntent.create(
                amount=int(grand_total * 100),
                currency="gbp",
                metadata={"order_id": order.id},
            )
            client_secret = payment_intent.client_secret

            # Return JSON response with client_secret and order_id
            return JsonResponse({
                "client_secret": client_secret,
                "order_id": order.id,
            })
        else:
            errors = form.errors.as_json()
            return JsonResponse({"errors": errors}, status=400)
    else:
        form = ShippingAddressForm()

    # For GET requests, simply render the checkout page
    return render(request, "checkout/checkout.html", {
        "form": form,
        "cart_items": cart_items,
        "subtotal": round(float(subtotal), 2),
        "delivery_cost": round(float(delivery_cost), 2),
        "grand_total": round(float(grand_total), 2),
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
    })


def order_summary(request, order_id):
    """
    Displays the order summary after checkout.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, "checkout/order_summary.html", {
        "order": order,
        "order_items": order_items
    })


def payment(request, order_id):
    """
    Displays the Stripe payment page using the PaymentIntent's client secret.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
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
    Marks the order as 'paid' after successful payment and redirects
    to the Order Success page where the user can view their order details.
    """
    session_id = request.GET.get("session_id")
    if not session_id:
        messages.error(request, "No payment session found.")
        return redirect("checkout")
    
    try:
        # Retrieve the Stripe Checkout session
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Get the order_id from metadata (make sure you set this when creating the PaymentIntent or Checkout Session)
        order_id = session.metadata.get("order_id")
        if not order_id:
            messages.error(request, "Order metadata missing from payment session.")
            return redirect("checkout")
        
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order.status = "paid"
        order.payment_id = session.payment_intent
        order.save()

        if request.user.is_authenticated:
            Cart.objects.filter(user=request.user).delete()
        else:
            request.session["cart"] = {}
        
        messages.success(request, "Payment successful! Your order has been placed.")
        return redirect("order_success", order_id=order.id)
        
    except stripe.error.StripeError as e:
        messages.error(request, "Error retrieving payment session: " + str(e))
        return redirect("checkout")


def payment_cancel(request):
    """
    Handles failed or canceled payments.
    """
    messages.warning(request, "Payment was canceled. Please try again.")
    return redirect("checkout")


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    # Clear Cart after successful order
    Cart.objects.filter(user=request.user).delete()

    return render(request, "checkout/order_success.html", {
        "order": order,
        "order_items": order_items,
    })


@csrf_exempt
def stripe_webhook(request):
    """
    Handle Stripe webhooks
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