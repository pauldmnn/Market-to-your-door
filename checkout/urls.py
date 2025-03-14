from django.urls import path
from . import views
from .views import (
    payment, create_checkout_session, 
    payment_success, payment_cancel
)


urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("order-summary/<int:order_id>/", views.order_summary, name="order_summary"),
    path("payment/", payment, name="payment"),
    path("create-checkout-session/", create_checkout_session, name="create_checkout_session"),
    path("checkout/success/", payment_success, name="payment_success"),
    path("checkout/cancel/", payment_cancel, name="payment_cancel"),
]