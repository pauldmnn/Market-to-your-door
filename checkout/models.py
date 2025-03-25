import uuid
from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from decimal import Decimal
from django.conf import settings
from django.db.models import Sum
from django_countries.fields import CountryField


class Order(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, blank=True  
    )
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        
    ]

    order_number = models.CharField(max_length=12, unique=True, editable=False,)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    shipping_address = models.OneToOneField("ShippingAddress", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Order {self.id}"

    def calculate_total(self):
        """
        Calculate total price of all items in the order, including delivery.
        """
        item_total = sum(item.get_total_price() for item in self.items.all())

        if item_total >= settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = Decimal('0.00')  
        else:
            self.delivery_cost = (Decimal(settings.STANDARD_DELIVERY_PERCENTAGE) / 100) * item_total

        self.total_price = (item_total + self.delivery_cost).quantize(Decimal('0.01'))
        self.save(update_fields=["total_price", "delivery_cost"])
        return self.total_price

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
            while Order.objects.filter(order_number=self.order_number).exists():
                self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex[:12].upper()
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    def get_total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"


class ShippingAddress(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True, blank=True)
    address_line1 = models.CharField(max_length=255, null=True, blank=True)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    country = CountryField(blank_label="(Select country)", default='GB')
    county = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.address_line1}, {self.city}"