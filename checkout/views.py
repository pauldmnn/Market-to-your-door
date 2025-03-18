import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from cart.models import Cart
from .models import Order, OrderItem, ShippingAddress
from .forms import ShippingAddressForm
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse

stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout(request):
    """
    Handles the checkout process and integrates Stripe for payment.
    """
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect("cart_detail")

    # Calculate totals
    subtotal = sum(item.product.price * Decimal(item.quantity) for item in cart_items)
    delivery_cost = (Decimal('0.00') if subtotal >= settings.FREE_DELIVERY_THRESHOLD 
                     else (Decimal(settings.STANDARD_DELIVERY_PERCENTAGE) / 100) * subtotal)
    grand_total = subtotal + delivery_cost

    order = None
    client_secret = None
    show_payment_form = False

    if request.method == "POST":
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            # Create the shipping address instance but don't save yet
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()

            # Create an order (without shipping address first)
            order = Order.objects.create(
                user=request.user,
                total_price=grand_total,
                shipping_address=shipping_address
            )

            # Create Stripe PaymentIntent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(grand_total * 100),
                currency="gbp",
                metadata={"order_id": order.id},
            )
            client_secret = payment_intent.client_secret

            show_payment_form = True
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = ShippingAddressForm()

    return render(request, "checkout/checkout.html", {
        "form": form,
        "cart_items": cart_items,
        "subtotal": round(float(subtotal), 2),
        "delivery_cost": round(float(delivery_cost), 2),
        "grand_total": round(float(grand_total), 2),
        "order": order,
        "client_secret": client_secret,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        "show_payment_form": show_payment_form,
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
    """
    Displays the order success page where the user can see their order summary and grand total.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, "checkout/order_success.html", {
        "order": order,
        "order_items": order_items,
    })
