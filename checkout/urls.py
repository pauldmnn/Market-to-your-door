from django.urls import path
from .views import checkout, payment, payment_success, payment_cancel, order_summary, order_success, stripe_webhook

urlpatterns = [
    path("checkout/", checkout, name="checkout"),
    path("payment/<int:order_id>/", payment, name="payment"),
    path("success/", payment_success, name="payment_success"),    
    path("cancel/", payment_cancel, name="payment_cancel"),
    path("order-summary/<int:order_id>/", order_summary, name="order_summary"),
    path("order-success/<int:order_id>/", order_success, name="order_success"),
    path("wh/", stripe_webhook, name="stripe_webhook"),

]
