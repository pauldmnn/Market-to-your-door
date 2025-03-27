from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from products.models import Product
from django.contrib.auth.decorators import login_required


@login_required
def submit_review(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)

    if Review.objects.filter(user=request.user, product=product).exists():
        messages.error(request, "You've already reviewed this product.")
        return redirect('product_detail', slug=product.slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Thank you for your review!")
            return redirect('product_detail', slug=product.slug)
    else:
        form = ReviewForm()

    return redirect('product_detail', slug=product.slug)
