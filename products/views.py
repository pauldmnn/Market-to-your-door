from django.shortcuts import render, get_object_or_404
from .models import Product


def product_list(request):
    """
    A view to display all products including searching and sorting
    """

    products = Product.objects.all()

    return render(request, 'products/products.html', {
        'products': products,
    })


def product_detail(request, slug):
    """
    A view to display individual product details
    """

    product = get_object_or_404(Product, slug=slug)

    return render(request, 'products/product_detail.html', {
        'product': product,
    })