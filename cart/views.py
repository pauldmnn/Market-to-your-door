from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from django.contrib import messages
from django.http import JsonResponse
import json
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

    if product.inventory == 0:
        messages.error(request, f"{product.name} is out of stock.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    cart = request.session.get('cart', {})

    try:
        quantity = Decimal(request.POST.get('quantity', 1))
        if quantity <= 0:
            quantity = Decimal('0.1')
    except ValueError:
        quantity = Decimal('1')
    
    current_quantity_in_cart = Decimal(cart[slug]['quantity']) if slug in cart else Decimal('0')
    new_total_quantity = current_quantity_in_cart + quantity

    if new_total_quantity > product.inventory:
        messages.error(request, f"Only {product.inventory} {product.name}(s) are available in stock. You cannot add more.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if slug in cart:
        cart[slug]['quantity'] = float(Decimal(cart[slug]['quantity']) + quantity) 
    else:
        cart[slug] = {
            'quantity': float(quantity),
            'price': str(product.price)  
        }

    request.session['cart'] = cart
    messages.success(request, f"{product.name} (x{quantity}) has been added to your cart.")
    total_price = Decimal(cart[slug]['quantity']) * Decimal(product.price)

    grand_total = sum(Decimal(Product.objects.get(slug=item).price) * Decimal(cart[item]['quantity']) for item in cart)

    messages.success(request, f"{product.name} (x{quantity}) has been added to your cart.")

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'new_quantity': cart[slug]['quantity'],
            'total_price': round(float(total_price), 2),
            'grand_total': round(float(grand_total), 2),
        })

    return redirect(request.META.get('HTTP_REFERER', 'cart_detail'))



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
        grand_total = Decimal(product.price) * quantity
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

        try:
            data = json.loads(request.body)
            slug = data.get('slug')
            new_quantity = Decimal(data.get('quantity', 0))  

            if not slug:
                return JsonResponse({'success': False, 'error': "Invalid request data."})

            product = get_object_or_404(Product, slug=slug)

            # Ensure correct decimal or integer quantity input
            if product.price_unit == 'piece':
                new_quantity = int(new_quantity)
            else:
                new_quantity = Decimal(new_quantity)

            if new_quantity < 0:
                new_quantity = 0

            # Prevent exceeding inventory
            if new_quantity > product.inventory:
                return JsonResponse({'success': False, 'error': f"Only {product.inventory} available."})

            if new_quantity == 0:
                del cart[slug]
            else:
                cart[slug] = {'quantity': float(new_quantity), 'price': str(product.price)}

            request.session['cart'] = cart

            cart_empty = len(cart) == 0

            grand_total = sum(Decimal(Product.objects.get(slug=item).price) * Decimal(cart[item]['quantity']) for item in cart) if cart else Decimal('0')
            total_price = Decimal(new_quantity) * Decimal(product.price)

            return JsonResponse({
                'success': True,
                'new_quantity': float(new_quantity),
                'total_price': round(float(total_price), 2),
                'grand_total': round(float(grand_total), 2),
                'cart_empty': cart_empty
            })

        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'success': False, 'error': "Invalid JSON data."})