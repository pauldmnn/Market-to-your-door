from django.urls import path
from .views import product_list, product_detail
from . import views

urlpatterns = [
    path('', product_list, name='product_list'),
    path('products/<slug:slug>', product_detail, name='product_detail'),
    path('market/<slug:category_slug>/', views.category_products, name='category_products'),
    path('products/', product_list, name='product_list'),
]
