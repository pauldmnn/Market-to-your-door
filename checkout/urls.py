from django.urls import path
from . import views


urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("order-summary/<int:order_id>/", views.order_summary, name="order_summary"),
]