from django.shortcuts import render, redirect
from django.contrib import messages
from cart.models import Cart
from .models import Order, OrderItem, ShippingAddress
from .forms import ShippingAddressForm

def checkout(request):
    """
    Handles the checkout process.
    """
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect("cart_detail")

    if request.method == "POST":
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()

            order = Order.objects.create(user=request.user, total_price=0)
            order.shipping_address = shipping_address
            order.save()

            total_price = 0
            for item in cart_items:
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
                total_price += item.product.price * item.quantity

            order.total_price = total_price
            order.save()

            cart_items.delete()  

            messages.success(request, "Order placed successfully!")
            return redirect("order_summary", order_id=order.id)
    else:
        form = ShippingAddressForm()

    return render(request, "checkout/checkout.html", {"form": form, "cart_items": cart_items})


def order_summary(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, "checkout/order_summary.html", {"order": order})