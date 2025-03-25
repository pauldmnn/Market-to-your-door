from decimal import Decimal
from django.conf import settings
from products.models import Product
from .models import Cart

def cart_contents(request):
    """
    Ensures the cart data is available in the navbar on all pages.
    Handles both authenticated users (Cart model) and guest users (session).
    """
    total = Decimal("0.00")
    cart_count = Decimal("0")
    cart_data = []

    if request.user.is_authenticated:
        # Authenticated: load cart from the database
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            line_total = item.product.price * Decimal(item.quantity)
            total += line_total
            cart_count += Decimal(item.quantity)
            cart_data.append({
                "product": item.product,
                "quantity": item.quantity,
                "total_price": line_total,
            })
    else:
        # Guest: load cart from the session
        session_cart = request.session.get("cart", {})
        # Build cart_data from session_cart if it exists
        if session_cart:
            product_ids = session_cart.keys()
            products = Product.objects.filter(id__in=product_ids)
            for product in products:
                # Ensure product IDs are strings as stored in the session
                quantity = Decimal(str(session_cart.get(str(product.id), 0)))
                line_total = product.price * quantity
                total += line_total
                cart_count += quantity
                cart_data.append({
                    "product": product,
                    "quantity": quantity,
                    "total_price": line_total,
                })
        # If no session cart exists, cart_data remains an empty list.
    
    return {
        "cart_items": cart_data,
        "grand_total": round(float(total), 2),
        "cart_count": int(cart_count),
    }


def site_wide_messages(request):
    """
    Context processor to display free delivery message across all pages.
    """
    return {
        "free_delivery_message": f"Free delivery on orders over £{settings.FREE_DELIVERY_THRESHOLD}"
    }

