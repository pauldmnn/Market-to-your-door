from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User, Group
from custom_admin.decorators import custom_admin_required, superuser_required
from django.utils.decorators import method_decorator
from checkout.models import Order, OrderItem
from products.models import Product, Category
from reviews.models import Review, ReviewReply
from custom_admin.decorators import custom_admin_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


from .forms import OrderUpdateForm, ProductForm, CategoryForm
from django.contrib.auth.decorators import login_required, user_passes_test


@custom_admin_required
def dashboard_home(request):
    """
    Dashboard homepage: List all orders.
    """
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/dashboard_home.html', {'orders': orders})


@superuser_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully")
            return redirect('product_list')
        else:
            messages.error(request, "Please correct errors bellow")
    else:
        form = ProductForm()
    return render(request, 'custom_admin/add_product.html', {'form': form})


@method_decorator(custom_admin_required, name='dispatch')
class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderUpdateForm
    template_name = 'custom_admin/order_update.html'
    success_url = reverse_lazy('dashboard_home')

    def form_valid(self, form):
        messages.success(self.request, "Order updated successfully.")
        return super().form_valid(form)

@method_decorator(custom_admin_required, name='dispatch')
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'custom_admin/product_form.html'
    success_url = reverse_lazy('dashboard_home')

    def form_valid(self, form):
        messages.success(self.request, "Product added successfully.")
        return super().form_valid(form)
    
@custom_admin_required
class ProductListView(ListView):
    model = Product
    context_object_name = 'products'

    def get_template_names(self):
        user = self.request.user
        if user.is_authenticated and (user.is_superuser or user.groups.filter(name="custom_admin").exists()):
            return ['custom_admin/product_list_admin.html']
        return ['products/products.html']


@custom_admin_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('product_list')
    return render(request, 'custom_admin/confirm_delete.html', {'product': product})


@method_decorator(custom_admin_required, name='dispatch')
class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'custom_admin/edit_product.html'
    success_url = reverse_lazy('dashboard_home')

    def form_valid(self, form):
        messages.success(self.request, "Product updated successfully.")
        return super().form_valid(form)
    

@method_decorator(custom_admin_required, name='dispatch')
class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'custom_admin/delete_product.html'
    success_url = reverse_lazy('dashboard_home')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Product deleted successfully.")
        return super().delete(request, *args, **kwargs)
    

@method_decorator(custom_admin_required, name='dispatch')
def add_category(request):
    from products.models import Category
    categories = Category.objects.all()
    form = CategoryForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Category added successfully.")
        return redirect('add_category')

    return render(request, 'custom_admin/add_category.html', {
        'form': form,
        'categories': categories
    })


@custom_admin_required
class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'custom_admin/category_form.html'
    success_url = reverse_lazy('dashboard_home')

    def form_valid(self, form):
        messages.success(self.request, "Category added successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


@custom_admin_required
def edit_category(request, slug):
    category = get_object_or_404(Category, slug=slug)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect('add_category')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'custom_admin/edit_category.html', {
        'form': form,
        'category': category
    })


@custom_admin_required
def delete_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()  

    if request.method == 'POST':
        if products.exists():
            messages.error(request, "Cannot delete category with existing products.")
        else:
            category.delete()
            messages.success(request, "Category deleted successfully.")
        return redirect('add_category')

    return render(request, 'custom_admin/confirm_delete_category.html', {
        'category': category,
        'products_exist': products.exists()
    })



@superuser_required
def manage_users(request):
    user_type = request.GET.get("type", "normal")
    admin_group, _ = Group.objects.get_or_create(name="custom_admin")

    if user_type == "admin":
        users = User.objects.filter(groups=admin_group)
    else:
        users = User.objects.exclude(groups=admin_group)

    context = {
        "users": users,
        "user_type": user_type,
    }
    return render(request, "custom_admin/manage_users.html", context)


@superuser_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        messages.error(request, "Cannot delete a superuser.")
    else:
        user.delete()
        messages.success(request, "User deleted successfully.")
    return redirect("manage_users")


@superuser_required
def promote_to_admin(request, user_id):
    user = get_object_or_404(User, id=user_id)
    admin_group, _ = Group.objects.get_or_create(name="custom_admin")
    admin_group.user_set.add(user)
    messages.success(request, f"{user.username} promoted to admin.")
    return redirect("manage_users")


@superuser_required
def promote_user(request, user_id, role):
    user = get_object_or_404(User, id=user_id)

    if role == "admin":
        admin_group, _ = Group.objects.get_or_create(name="custom_admin")
        admin_group.user_set.add(user)
        messages.success(request, f"{user.username} promoted to admin.")
    elif role == "superuser":
        user.is_superuser = True
        user.save()
        messages.success(request, f"{user.username} promoted to superuser.")

    return redirect("manage_users")


@custom_admin_required
def review_list(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/review_list.html', {'reviews': reviews})


@custom_admin_required
def reply_to_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            ReviewReply.objects.create(review=review, user=request.user, content=content)
            messages.success(request, 'Reply submitted successfully.')
        return redirect('review_list')

    return render(request, 'custom_admin/reply_form.html', {'review': review})


@custom_admin_required
def mark_order_shipped(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status == "Paid":
        messages.warning(request, "Order already marked as Paid. Cannot mark as Shipped again.")
        return redirect("dashboard_home")

    # Update order status
    order.status = "Paid/Shipped"
    order.save()

    # Send email to customer
    subject = f"Your Order #{order.order_number} has been shipped"
    message = render_to_string("emails/order_shipped_email.txt", {
        "order": order,
        "shipping_address": order.shipping_address,
    })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [order.user.email])

    messages.success(request, f"Order {order.order_number} marked as shipped and email sent.")
    return redirect("dashboard_home")



