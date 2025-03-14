import uuid
from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from decimal import Decimal
from django.conf import settings
from django.db.models import Sum


class Order(models.Model):
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
    payment_id = models.CharField(max_length=255, blank=True, null=True)  

    def save(self, *args, **kwargs):
        """
        Generate a unique order number before saving.
        """
        if self.order_number ==  self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()
    
    def __str__(self):
        return self.order_number
    
    def calculate_total(self):
        """
        Calculate total price of all items in the order.
        """
        total = sum(item.get_total_price() for item in self.items.all())
        self.total_price = total.quantize(Decimal('0.01'))
        self.save()
        return self.total_price

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    def get_total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shipping_addresses")
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="shipping_address")
    full_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.full_name} - {self.address}"