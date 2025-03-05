from django.shortcuts import render
from .models import Product


def product_list(request):
    """
    A view to display all products including searching and sorting
    """

    products = Product.objects.all()

    return render(request, 'products/products.html', {
        'products': products,
    })
