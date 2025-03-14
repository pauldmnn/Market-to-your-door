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
    delivery_cost = Decimal('0.00') if subtotal >= settings.FREE_DELIVERY_THRESHOLD else (Decimal(settings.STANDARD_DELIVERY_PERCENTAGE) / 100) * subtotal
    grand_total = subtotal + delivery_cost

    order = None
    client_secret = None

    if request.method == "POST":
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()

            #  Create an order before generating client_secret
            order = Order.objects.create(user=request.user, total_price=grand_total, shipping_address=shipping_address)

            # Create Stripe PaymentIntent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(grand_total * 100), 
                currency="gbp",
            )
            client_secret = payment_intent.client_secret
            
            print("\n✅ Stripe PaymentIntent Created:")
            print(f"   - ID: {payment_intent.id}")
            print(f"   - Amount: {payment_intent.amount / 100} GBP")
            print(f"   - Client Secret: {payment_intent.client_secret}")
            print(f"   - Status: {payment_intent.status}\n")

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


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(request):
    """
    A view to create a Stripe checkout 
    session for payment processing.
    """
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect("cart_detail")

    subtotal = sum(item.product.price * Decimal(item.quantity) for item in cart_items)

    if subtotal >= settings.FREE_DELIVERY_THRESHOLD:
        delivery_cost = Decimal('0.00')
    else:
        delivery_cost = (Decimal(settings.STANDARD_DELIVERY_PERCENTAGE) / 100) * subtotal

    grand_total = subtotal + delivery_cost

    order = Order.objects.create(
        user=request.user,
        total_price=grand_total
    )

    line_items = [
        {
            "price_data": {
                "currency": "gbp",
                "unit_amount": int(item.product.price * 100),
                "product_data": {
                    "name": item.product.name,
                },
            },
            "quantity": int(item.quantity),
        }
        for item in cart_items
    ]

    line_items.append({
        "price_data": {
            "currency": "gbp",
            "unit_amount": int(delivery_cost * 100),
            "product_data": {
                "name": "Delivery Fee",
            },
        },
        "quantity": 1,
    })

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url=settings.STRIPE_SUCCESS_URL + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=settings.STRIPE_CANCEL_URL,
        metadata={"order_id": str(order.id)},
    )

    return JsonResponse({"id": checkout_session.id})


def payment(request, order_id):
    """
    Displays the Stripe payment page with a valid client secret.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Create a PaymentIntent for the order
    payment_intent = stripe.PaymentIntent.create(
        amount=int(order.total_price * 100),  
        currency="gbp",
    )

    return render(request, "checkout/payment.html", {
        "order": order,
        "client_secret": payment_intent.client_secret, 
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY
    })


def payment_success(request):
    """
    Marks the order as 'Paid' after successful payment.
    """
    session_id = request.GET.get("session_id")
    if not session_id:
        messages.error(request, "No payment session found.")
        return redirect("checkout")

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if "order_id" not in session.metadata:
            messages.error(request, "Order metadata missing from payment session.")
            return redirect("checkout")
        
        order_id = session.metadata["order_id"]

        order = get_object_or_404(Order, id=order_id)
        order.status = "paid"
        order.payment_id = session.payment_intent
        order.save()

        messages.success(request, "Payment successful! Your order has been placed.")
        return redirect("order_summary", order_id=order.id)

    except stripe.error.StripeError:
        messages.error(request, "Error retrieving payment session.")
        return redirect("checkout")


def payment_cancel(request):
    """
    Handles failed or canceled payments.
    """
    messages.warning(request, "Payment was canceled. Please try again.")
    return redirect("checkout")
