import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from cart.models import Cart
from .models import Order, OrderItem, ShippingAddress
from .forms import ShippingAddressForm
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse



def checkout(request):
    """
    Handles the checkout process.
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

    if request.method == "POST":
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user, 
                total_price=grand_total,
            )

            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.order = order
            shipping_address.save()

            order.shipping_address = shipping_address
            order.save()

            # Create an order

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )

            cart_items.delete()  

            messages.success(request, "Order placed successfully!")
            return redirect("order_summary", order_id=order.id)
    else:
        form = ShippingAddressForm()

    return render(request, "checkout/checkout.html", {
        "form": form,
        "cart_items": cart_items,
        "subtotal": round(float(subtotal), 2),
        "delivery_cost": round(float(delivery_cost), 2),
        "grand_total": round(float(grand_total), 2),
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
        metadata={"order_id": order.id},
    )

    return JsonResponse({"id": checkout_session.id})

def payment(request):
    """
    Displays the Stripe payment page.
    """
    order = Order.objects.filter(user=request.user).last()

    if not order:
        messages.error(request, "No active order found.")
        return redirect("checkout")

    return render(request, "checkout/payment.html", {
        "order": order,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY
    })

def payment_success(request):
    """
    Marks the order as 'Paid' after successful payment.
    """
    session_id = request.GET.get("session_id")
    session = stripe.checkout.Session.retrieve(session_id)
    order_id = session.metadata["order_id"]

    order = get_object_or_404(Order, id=order_id)
    order.status = "paid"
    order.payment_id = session.payment_intent
    order.save()

    messages.success(request, "Payment successful! Your order has been placed.")
    return redirect("order_summary", order_id=order.id)

def payment_cancel(request):
    """
    Handles failed or canceled payments.
    """
    messages.warning(request, "Payment was canceled. Please try again.")
    return redirect("checkout")
