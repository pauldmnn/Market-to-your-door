from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal


def view_cart(request):
    """
    A view to return the cart page
    """
    return render(request, 'cart/cart.html')


def add_to_cart(request, slug):
    """
    Adds the product to the cart with the user-specified quantity.
    """
    product = get_object_or_404(Product, slug=slug)
    cart = request.session.get('cart', {})

    try:
        quantity = Decimal(request.POST.get('quantity', 1))
        if quantity <= 0:
            quantity = Decimal('0.1')
    except ValueError:
        quantity = Decimal('1')

    if slug in cart:
        cart[slug]['quantity'] = float(Decimal(cart[slug]['quantity']) + quantity) 
    else:
        cart[slug] = {
            'quantity': float(quantity),
            'price': str(product.price)  
        }

    request.session['cart'] = cart
    messages.success(request, f"{product.name} (x{quantity}) has been added to your cart.")

    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)


def cart_detail(request):
    """
    Displays the cart with a form to update quantities.
    """
    cart = request.session.get('cart', {})
    cart_items = []
    products = Product.objects.filter(slug__in=cart.keys())

    overall_total = Decimal('0.00')

    for product in products:
        quantity = Decimal(cart[product.slug]['quantity'])
        grand_total = Decimal(product.price)* quantity
        cart_items.append({
            'product': product,
            'quantity': quantity.quantize(Decimal('0.1')),
            'grand_total': grand_total.quantize(Decimal('0.01'))
        })
    
        overall_total += grand_total

    context = {
        'cart_items': cart_items,
        'overall_total': overall_total,
    }
    return render(request, 'cart/cart.html', context)


def update_cart(request):
    """
    A view to update and remove products from the cart
    """

    if request.method == 'POST':
        cart = request.session.get('cart', {})

        if 'update' in request.POST:  
            slug = request.POST.get('update')
            new_qty = request.POST.get(f'quantity_{slug}')
            if new_qty is not None:
                try:
                    new_qty = Decimal(new_qty)
                    if new_qty > 0:
                        cart[slug]['quantity'] = float(new_qty)
                        messages.success(request, "Cart updated successfully.")
                    else:
                        del cart[slug]  
                        messages.success(request, "Product removed from cart.")
                except ValueError:
                    messages.error(request, "Invalid quantity entered.")

        elif 'remove' in request.POST:
            slug = request.POST.get('remove')
            if slug in cart:
                del cart[slug]
                messages.success(request, "Product removed from cart.")

        request.session['cart'] = cart 

    return redirect('cart_detail')


