from django.shortcuts import render,redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Product


def product_list(request):
    """
    A view to display all products including searching and sorting
    """

    products = Product.objects.all()
    query = None

    if request.GET:
        if 'q' in request.GET:
            query = request.GET('q')
            if not query:
                messages.error(request, "No items found. Please try again!")
                return redirect(reverse('products'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    return render(request, 'products/products.html', {
        'products': products, 'search_term': query
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