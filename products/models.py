from django.db import models
from django.conf import settings


class Category(models.Model):

    class Meta:
        verbose_name_plural = 'Categories'
        
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = [
        ('piece', 'Per Piece'),
        ('gram', 'Per Gram'),
        ('kilogram', 'Per Kilogram'),
    ]

    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    inventory = models.PositiveIntegerField(default=0)
    price_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='piece')

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return round(sum([r.rating for r in reviews]) / reviews.count(), 1)
        return 0


    def is_in_stock(self):
        return self.inventory > 0

    def __str__(self):
        return f"{self.name} - {self.get_price_unit_display()}"


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product') 

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name} ({self.rating}★)"
