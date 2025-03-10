from django.shortcuts import render, redirect


def view_cart(request):
    """
    A view to return the cart page
    """
    return render(request, 'cart/cart.html')


def add_to_cart(request, slug):
    """
    Add product and quantity to cart
    """
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    cart = request.session.get('cart', {})

    if slug in list(cart.keys()):
        cart[slug] += quantity
    else:
        cart[slug] = quantity

    request.session['cart'] = cart
    print(request.session['cart'])
    return redirect(redirect_url)
