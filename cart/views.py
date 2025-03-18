from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from .models import Cart
from django.contrib import messages
from django.http import JsonResponse
import json
from decimal import Decimal


def view_cart(request):
    """
    A view to return the cart page with items from the Cart model.
    """
    cart_items = []
    overall_total = Decimal("0.00")
    if request.user.is_authenticated:
        # Load cart from the database
        cart_items = Cart.objects.filter(user=request.user)
        overall_total = sum(item.product.price * Decimal(item.quantity) for item in cart_items)

    else:
        # Load cart from session
        session_cart = request.session.get("cart", {})
        products = Product.objects.filter(id__in=session_cart.keys())
        cart_items = [{"product": p, "quantity": session_cart[str(p.id)], "total": p.price * Decimal(session_cart[str(p.id)])} for p in products]
        overall_total = sum(item["total"] for item in cart_items)

    return render(request, "cart/cart.html", {"cart_items": cart_items, "overall_total": round(overall_total, 2)})


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

    if request.user.is_authenticated:
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
    
    else:
        cart = request.session.get("cart", {})
        current_quantity = Decimal(cart.get(str(product.id), 0))
        new_total_quantity = current_quantity + quantity

        if new_total_quantity > product.inventory:
            messages.error(request, f"Only {product.inventory} {product.name}(s) are available.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        cart[str(product.id)] = float(new_total_quantity)
        request.session["cart"] = cart

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
        'grand_total': round(float(overall_total), 2),
    }
    return render(request, 'cart/cart.html', context)


def update_cart(request):
    """
    A view to update and remove products from the cart.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            slug = data.get("slug")
            new_quantity = Decimal(data.get("quantity", 0))

            if not slug:
                return JsonResponse({"success": False, "error": "Invalid product slug."})

            product = get_object_or_404(Product, slug=slug)

            if request.user.is_authenticated:
                #  LOGGED-IN USER: Update database cart
                cart_item = Cart.objects.filter(user=request.user, product=product).first()

                if not cart_item:
                    return JsonResponse({"success": False, "error": "Product not found in cart."})

                if new_quantity < 0:
                    new_quantity = 0

                if new_quantity > product.inventory:
                    return JsonResponse({"success": False, "error": f"Only {product.inventory} available in stock."})

                if new_quantity == 0:
                    cart_item.delete()
                else:
                    cart_item.quantity = float(new_quantity)
                    cart_item.save()

                cart_items = Cart.objects.filter(user=request.user)

            else:
                # ANONYMOUS USER: Update session cart
                cart = request.session.get("cart", {})
                if str(product.id) not in cart:
                    return JsonResponse({"success": False, "error": "Product not found in session cart."})

                if new_quantity < 0:
                    new_quantity = 0

                if new_quantity > product.inventory:
                    return JsonResponse({"success": False, "error": f"Only {product.inventory} available in stock."})

                if new_quantity == 0:
                    del cart[str(product.id)]
                else:
                    cart[str(product.id)] = float(new_quantity)

                request.session["cart"] = cart 
                cart_items = [{"product": p, "quantity": cart[str(p.id)], "total": p.price * Decimal(cart[str(p.id)])} for p in Product.objects.filter(id__in=cart.keys())]

            grand_total = sum(item["total"] for item in cart_items) if not request.user.is_authenticated else sum(item.product.price * Decimal(item.quantity) for item in cart_items)
            total_price = product.price * Decimal(new_quantity)
            cart_count = sum(Decimal(item["quantity"]) for item in cart_items) if not request.user.is_authenticated else sum(Decimal(item.quantity) for item in cart_items)

            return JsonResponse({
                "success": True,
                "new_quantity": float(new_quantity),
                "total_price": round(float(total_price), 2),
                "grand_total": round(float(grand_total), 2),
                "cart_count": int(cart_count),
                "cart_empty": len(cart_items) == 0,
            })

        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"success": False, "error": "Invalid JSON data."})