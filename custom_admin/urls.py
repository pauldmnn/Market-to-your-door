from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('order/<int:pk>/update/', views.OrderUpdateView.as_view(), name='order_update'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_create'),
    path('manage-admins/', views.manage_admins, name='manage_admins'),
]
