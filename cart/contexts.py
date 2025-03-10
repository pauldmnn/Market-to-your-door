from django.conf import settings


def cart(request):
    return {
        'cart': request.session.get('cart', {})
    }