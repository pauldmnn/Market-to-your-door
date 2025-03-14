from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from products.models import Product, Category


def product_list(request):
    """
    A view to display all products including searching, sorting and filtering
    """
    products = Product.objects.all()

    query = request.GET.get('q', '')
    name_filter = request.GET.get('name', '')
    category_filter = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_option = request.GET.get('sort', 'name')
    if query:
        products = Product.objects.filter(name__icontains=query)
        name_filter = query
    else:
        if name_filter:
            products = products.filter(name__icontains=name_filter)
        if category_filter:
            products = products.filter(category__slug=category_filter)
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

    if sort_option in ['name', '-name', 'price', '-price']:
        products = products.order_by(sort_option)
    elif sort_option == 'category':
        products = products.order_by('category__name')
    elif sort_option == '-category':
        products = products.order_by('-category__name')
       
    context = {
        'products': products,
        'name_filter': name_filter,
        'category_filter': category_filter,
        'min_price': min_price,
        'max_price': max_price,
        'sort_option': sort_option,
        'categories': Category.objects.all(),
        'query': query,
    }

    return render(request, 'products/products.html', context)


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
    })
    