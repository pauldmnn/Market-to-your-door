import stripe
from django.core.mail import send_mail
from checkout.models import Order, ShippingAddress, OrderItem
from products.models import Product
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings


class StripeWebhookHandler:
    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """Send the user confirmation email"""
        cust_email = order.shipping_address.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order}
        )
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL}
        )

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )

    def handle_event(self, event):
        """Handle unknown webhook events"""
        return HttpResponse(status=200)

    def handle_payment_intent_succeeded(self, event):
        intent = event.data.object
        metadata = intent.get("metadata", {})
        order_id = metadata.get("order_id")

        try:
            order = Order.objects.get(id=order_id)
            order.status = "Paid"
            order.payment_id = intent.id

            billing_details = intent.get("charges", {}).get("data", [{}])[0].get("billing_details", {})
            order.billing_name = billing_details.get("name")
            order.billing_email = billing_details.get("email")

            shipping_details = intent.get("shipping", {})
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

            # Reduce product inventory
            for item in order.orderitem_set.all():
                product = item.product
                product.inventory -= item.quantity
                product.save()

            # Send confirmation email
            self._send_confirmation_email(order)

            print(f"Stripe payment succeeded for order {order_id}")
            return HttpResponse(status=200)

        except Order.DoesNotExist:
            print(f"Order {order_id} not found in DB")
            return HttpResponse(content=f"Order {order_id} not found", status=404)

    def handle_payment_intent_failed(self, event):
        intent = event.data.object
        print(f"Payment failed for: {intent.id}")
        return HttpResponse(status=200)
