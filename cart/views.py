from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from .models import Cart
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json
from decimal import Decimal


def view_cart(request):
    """
    A view to return the cart page with items from the Cart model.
    """
    cart_items = Cart.objects.filter(user=request.user)
    overall_total = sum(item.product.price * Decimal(item.quantity) for item in cart_items)

    context = {
        'cart_items': cart_items,
        'overall_total': round(float(overall_total), 2),
    }
    return render(request, 'cart/cart.html', context)


def add_to_cart(request, slug):
    """
    Adds the product to the cart with the user-specified quantity.
    """
    product = get_object_or_404(Product, slug=slug)

    if product.inventory == 0:
        messages.error(request, f"{product.name} is out of stock.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        quantity = Decimal(request.POST.get('quantity', 1))
        if quantity <= 0:
            quantity = Decimal('0.1')
    except ValueError:
        quantity = Decimal('1')

    cart_item, created = Cart.objects.get_or_create(
        user=request.user, product=product,
        defaults={'quantity': float(quantity)}
    )

    if not created:
        new_total_quantity = cart_item.quantity + quantity
        if new_total_quantity > product.inventory:
            messages.error(request, f"Only {product.inventory} {product.name}(s) are available.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        cart_item.quantity = new_total_quantity
        cart_item.save()

    messages.success(request, f"{product.name} (x{quantity}) has been added to your cart.")

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_items = Cart.objects.filter(user=request.user)
        grand_total = sum(item.product.price * Decimal(item.quantity) for item in cart_items)
        total_price = cart_item.product.price * Decimal(cart_item.quantity)

        return JsonResponse({
            'success': True,
            'new_quantity': cart_item.quantity,
            'total_price': round(float(total_price), 2),
            'grand_total': round(float(grand_total), 2),
        })

    return redirect(request.META.get('HTTP_REFERER', 'cart_detail'))


def cart_detail(request):
    """
    Displays the cart with a form to update quantities.
    """
    cart_items = Cart.objects.filter(user=request.user)
    overall_total = sum(item.product.price * Decimal(item.quantity) for item in cart_items)

    context = {
        'cart_items': cart_items,
        'overall_total': round(float(overall_total), 2),
    }
    return render(request, 'cart/cart.html', context)


def update_cart(request):
    """
    A view to update and remove products from the cart
    """

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            slug = data.get('slug')
            new_quantity = Decimal(data.get('quantity', 0))  

            if not slug:
                return JsonResponse({'success': False, 'error': "Invalid request data."})

            product = get_object_or_404(Product, slug=slug)
            cart_item = get_object_or_404(Cart, user=request.user, product=product)

            # Ensure correct quantity input
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
                cart_item.delete()
            else:
                cart_item.quantity = new_quantity
                cart_item.save()

            cart_empty = not Cart.objects.filter(user=request.user).exists()
            grand_total = sum(item.product.price * Decimal(item.quantity) for item in Cart.objects.filter(user=request.user))
            total_price = product.price * new_quantity

            return JsonResponse({
                'success': True,
                'new_quantity': float(new_quantity),
                'total_price': round(float(total_price), 2),
                'grand_total': round(float(grand_total), 2),
                'cart_empty': cart_empty
            })

        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'success': False, 'error': "Invalid JSON data."})