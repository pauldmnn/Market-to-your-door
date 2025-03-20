import stripe
from django.shortcuts import get_object_or_404
from .models import Order

class StripeWebhookHandler:
    """
    Class-based handler for processing Stripe webhook events.
    """

    def __init__(self, event):
        self.event = event

    def handle_event(self):
        event_type = self.event.get("type")
        if event_type == "payment_intent.succeeded":
            return self.handle_payment_intent_succeeded()
        elif event_type == "payment_intent.payment_failed":
            return self.handle_payment_intent_failed()
        else:
            return self.handle_default_event()

    def handle_payment_intent_succeeded(self):
        data_object = self.event["data"]["object"]
        order_id = data_object.get("metadata", {}).get("order_id")
        if not order_id:
            return "Order ID missing; cannot process success event."
        order = get_object_or_404(Order, id=order_id)
        order.status = "paid"
        order.payment_id = data_object.get("id")
        order.save()
        return f"Order {order.order_number} marked as paid."

    def handle_payment_intent_failed(self):
        data_object = self.event["data"]["object"]
        error_message = data_object.get("last_payment_error", {}).get("message", "Unknown error")
        return f"Payment failed: {error_message}"

    def handle_default_event(self):
        return f"Unhandled event type: {self.event.get('type')}"
