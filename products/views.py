from django.shortcuts import render,redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category


def product_list(request):
    """
    A view to display all products including searching and sorting
    """

    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, 'products/products.html', {
        'products': products, 'query': query
    })


def product_detail(request, slug):
    """
    A view to display individual product details
    """

    product = get_object_or_404(Product, slug=slug)

    return render(request, 'products/product_detail.html', {
        'product': product,
    })


def category_products(request, category_slug):
    """
    A view to retrieve the categories
    """
    category = get_object_or_404(Category, slug=category_slug)

    products = Product.objects.filter(category=category)
    return render(request, 'products/category_products.html', {
        'category': category,
        'products': products
    } )