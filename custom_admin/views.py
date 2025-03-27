from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.models import User, Group
from custom_admin.decorators import custom_admin_required
from django.utils.decorators import method_decorator

from checkout.models import Order, OrderItem
from products.models import Product, Category
from .forms import OrderUpdateForm, ProductForm, CategoryForm

@custom_admin_required
def dashboard_home(request):
    """
    Dashboard homepage: List all orders.
    """
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/dashboard_home.html', {'orders': orders})

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

@method_decorator(custom_admin_required, name='dispatch')
class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'custom_admin/category_form.html'
    success_url = reverse_lazy('dashboard_home')

    def form_valid(self, form):
        messages.success(self.request, "Category added successfully.")
        return super().form_valid(form)

@custom_admin_required
def manage_admins(request):
    """
    View to allow the superuser to grant or revoke custom admin credentials.
    """
    admin_group, created = Group.objects.get_or_create(name="custom_admin")
    users = User.objects.all()
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")  
        user = get_object_or_404(User, id=user_id)
        if action == "add":
            admin_group.user_set.add(user)
            messages.success(request, f"{user.username} is now a custom admin.")
        elif action == "remove":
            admin_group.user_set.remove(user)
            messages.success(request, f"{user.username} has been removed from custom admin.")
        return redirect("manage_admins")
    return render(request, "custom_admin/manage_admins.html", {"users": users, "admin_group": admin_group})

