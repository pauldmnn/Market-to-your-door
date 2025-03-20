import stripe
from django.http import HttpResponse
from checkout.models import Order, OrderItem
from cart.models import Cart

class StripeWebhookHandler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """
        Handle generic/unknown webhook events
        """
        print(f"Unhandled event type: {event['type']}")
        return HttpResponse(content=f"Unhandled event: {event['type']}", status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle successful payment
        """
        intent = event.data.object
        order_id = intent.metadata.get("order_id")

        if not order_id:
            print("Order ID missing from metadata!")
            return HttpResponse(status=400)

        try:
            order = Order.objects.get(id=order_id)
            order.status = "paid"
            order.payment_id = intent.id
            order.save()

            # Delete items from the cart after payment
            Cart.objects.filter(user=order.user).delete()

            print(f"Payment successful for Order {order.id}")
            return HttpResponse(status=200)

        except Order.DoesNotExist:
            print(f"Order {order_id} not found!")
            return HttpResponse(status=400)

    def handle_payment_intent_failed(self, event):
        """
        Handle failed payment
        """
        intent = event.data.object
        print(f"Payment failed: {intent['id']}")
        return HttpResponse(status=200)


    def handle_default_event(self):
        return f"Unhandled event type: {self.event.get('type')}"
