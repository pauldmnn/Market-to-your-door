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
    else:
        cart_items = []

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

