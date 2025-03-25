from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product
from .models import Cart


def cart_contents(request):
    """
    Ensures the cart data is available in the navbar on all pages.
    """
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        # Sum up the quantity for all items
        cart_count = sum(item.quantity for item in cart_items)
        cart_total = sum(item.product.price * Decimal(item.quantity) for item in cart_items)
    else:
        # For guest users, cart is stored in session as a dict: { product_id: quantity }
        session_cart = request.session.get('cart', {})
        cart_count = sum(session_cart.values())  
        cart_total = Decimal("0.00")
        for product_id, quantity in session_cart.items():
            try:
                product = Product.objects.get(id=product_id)
                cart_total += product.price * Decimal(quantity)
            except Product.DoesNotExist:
                continue

    total = Decimal("0.00")
    cart_count = 0
    cart_data = []

    for item in cart_items:
        total += item.product.price * Decimal(item.quantity)
        cart_count += Decimal(item.quantity)

        cart_data.append({
            "product": item.product,
            "quantity": item.quantity,
            "total_price": item.product.price * Decimal(item.quantity)
        })

    return {
        "cart_items": cart_data,
        "grand_total": round(float(total), 2),
        "cart_count": int(cart_count)
    }

def site_wide_messages(request):
    """
    Context processor to display free delivery message across all pages.
    """
    return {
        "free_delivery_message": f"Free delivery on orders over £{settings.FREE_DELIVERY_THRESHOLD}"
    }

