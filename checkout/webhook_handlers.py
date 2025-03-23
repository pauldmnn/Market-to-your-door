import stripe
from django.core.mail import send_mail
from checkout.models import Order, ShippingAddress, OrderItem
from products.models import Product
from django.contrib.auth.models import User
from django.http import HttpResponse


class StripeWebhookHandler:
    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """Handle unknown webhook events"""
        return HttpResponse(status=200)

    def handle_payment_intent_succeeded(self, event):
        intent = event.data.object
        metadata = intent.get("metadata", {})
        order_id = metadata.get("order_id")

        # 🔹 Get billing details from the payment method
        billing_details = intent.get("charges", {}).get("data", [{}])[0].get("billing_details", {})
        shipping_details = intent.get("shipping", {})

        try:
            order = Order.objects.get(id=order_id)
            order.status = "paid"
            order.payment_id = intent.id

            # 🔹 Optionally update billing info on order
            order.billing_name = billing_details.get("name")
            order.billing_email = billing_details.get("email")
            order.save()

            # 🔹 Optionally update shipping address if not stored earlier
            address = order.shipping_address
            if not address:
                address = ShippingAddress.objects.create(
                    user=order.user,
                    full_name=shipping_details.get("name"),
                    address_line1=shipping_details.get("address", {}).get("line1"),
                    address_line2=shipping_details.get("address", {}).get("line2", ""),
                    city=shipping_details.get("address", {}).get("city"),
                    postcode=shipping_details.get("address", {}).get("postal_code"),
                    country=shipping_details.get("address", {}).get("country"),
                    phone=shipping_details.get("phone", "")
                )
                order.shipping_address = address
                order.save()

            return HttpResponse(status=200)

        except Order.DoesNotExist:
            return HttpResponse(content=f"Order {order_id} not found", status=404)

    def handle_payment_intent_failed(self, event):
        intent = event.data.object
        print(f"Payment failed for: {intent.id}")
        return HttpResponse(status=200)
