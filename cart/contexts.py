from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product


def cart_contents(request):
    """
    Context processor to provide cart contents globally across the site.
    """
    cart_items = []
    total = Decimal('0.00')
    product_count = 0
    cart = request.session.get('cart', {})

    for slug, item_data in cart.items():
        product = get_object_or_404(Product, slug=slug)

        # Handle decimal quantities
        quantity = Decimal(item_data['quantity'])
        total += quantity * Decimal(product.price)
        product_count += quantity

        cart_items.append({
            'product': product,
            'quantity': quantity,
        })

    # Handle delivery charges if applicable
    if total < Decimal(settings.FREE_DELIVERY_THRESHOLD):
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = Decimal(settings.FREE_DELIVERY_THRESHOLD) - total
    else:
        delivery = Decimal('0.00')
        free_delivery_delta = Decimal('0.00')

    overall_total = total + delivery

    context = {
        'cart_items': cart_items,
        'total': total.quantize(Decimal('0.01')),  # Ensure proper decimal formatting
        'product_count': product_count,
        'delivery': delivery.quantize(Decimal('0.01')),
        'free_delivery_delta': free_delivery_delta.quantize(Decimal('0.01')),
        'free_delivery_threshold': Decimal(settings.FREE_DELIVERY_THRESHOLD),
        'overall_total': overall_total.quantize(Decimal('0.01')),
    }

    return context

