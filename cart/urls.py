from django.contrib import admin
from django.urls import path
from . import views
from .views import add_to_cart, cart_detail, update_cart, update_cart_item

urlpatterns = [
    path('', cart_detail, name='cart_detail'),
    path('add/<slug:slug>/', add_to_cart, name='add_to_cart'),
    path('update/', update_cart, name='update_cart'),
    path('update-item/<slug:slug>/<str:action>/', update_cart_item, name='update_cart_item')


]
