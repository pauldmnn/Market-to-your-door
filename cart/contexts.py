from django.conf import settings
from products.models import Product


def cart(request):
    return {
        'cart': request.session.get('cart', {})
    }


def cart_total(request):
    """
    Context processor to make the grand total available in all templates.
    """
    cart = request.session.get('cart', {})
    overall_total = 0.00  

    for slug, item in cart.items():
        try:
            product = Product.objects.get(slug=slug)
            overall_total += product.price * item['quantity']
        except Product.DoesNotExist:
            pass  

    return {'overall_total': overall_total}