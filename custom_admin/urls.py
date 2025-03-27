from django.urls import path
from . import views
from .views import ProductUpdateView, ProductDeleteView, ProductListView



urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('order/<int:pk>/update/', views.OrderUpdateView.as_view(), name='order_update'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_create'),
    path('manage-admins/', views.manage_admins, name='manage_admins'),
    path('product/edit/<int:pk>/', ProductUpdateView.as_view(), name='edit_product'),
    path('product/delete/<int:pk>/', ProductDeleteView.as_view(), name='delete_product'),
]




