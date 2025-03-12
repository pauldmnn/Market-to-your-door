from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from django.contrib import messages


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
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    if slug in cart:
        cart[slug]['quantity'] += quantity
    else:
        cart[slug] = {
            'quantity': quantity,
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

    for product in products:
        quantity = cart[product.slug]['quantity']
        grand_total = product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'grand_total': grand_total
        })

    overall_total = sum(item['grand_total'] for item in cart_items)

    context = {
        'cart_items': cart_items,
        'overall_total': overall_total,
    }
    return render(request, 'cart/cart.html', context)


def update_cart(request):
    """
    Updates the cart quantities based on the submitted form.
    """
    if request.method == 'POST':
        cart = request.session.get('cart', {})

        for slug in list(cart.keys()):
            new_qty = request.POST.get(f'quantity_{slug}')
            if new_qty is not None:
                try:
                    new_qty = int(new_qty)
                    if new_qty > 0:
                        cart[slug]['quantity'] = new_qty
                    else:
                        del cart[slug]
                except ValueError:
                    pass

        request.session['cart'] = cart
        messages.success(request, "Cart updated successfully.")

    return redirect('cart_detail')


def update_cart_item(request, slug, action):
    """
    A view to update the item quantity by incrementing or decrementing amount
    """
    cart = request.session.get('cart', {})

    if slug in cart:
        if action == 'increment':
            cart[slug]['quantity'] += 1
        elif action == 'decrement':
            cart[slug]['quantity'] -= 1
            if cart[slug]['quantity'] < 1:
                del cart[slug]
        else:
            messages.error(request, "Invalid action.")
    else:
        messages.error(request, "Product not in cart.")

    request.session['cart'] = cart
    return redirect('cart_detail')


