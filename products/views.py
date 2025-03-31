from django.shortcuts import render, get_object_or_404
from products.models import Product, Category
from reviews.forms import ReviewForm


def product_list(request):
    """
    A view to display all products including searching, sorting, and filtering
    """
    products = Product.objects.all()

    # Get filter values from GET request
    query = request.GET.get('q', '')
    name_filter = request.GET.get('name', '')
    category_filter = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_option = request.GET.get('sort', 'name')

    # Apply search query
    if query:
        products = products.filter(name__icontains=query)
        name_filter = query
    elif name_filter:
        products = products.filter(name__icontains=name_filter)

    # Filter by category slug
    if category_filter:
        products = products.filter(category__slug=category_filter)

    # Filter by price range
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass  # ignore invalid inputs
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Apply sorting
    if sort_option in ['name', '-name', 'price', '-price']:
        products = products.order_by(sort_option)
    elif sort_option == 'category':
        products = products.order_by('category__name')
    elif sort_option == '-category':
        products = products.order_by('-category__name')

    # Pass all necessary context to the template
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
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all()
    user_has_reviewed = False
    review_form = None

    if request.user.is_authenticated:
        user_has_reviewed = product.reviews.filter(user=request.user).exists()
        if not user_has_reviewed:
            review_form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'user_has_reviewed': user_has_reviewed,
        'review_form': review_form
    }
    return render(request, 'products/product_detail.html', context)


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
