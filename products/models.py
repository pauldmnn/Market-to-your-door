from django.db import models


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

    def is_in_stock(self):
        return self.inventory > 0

    def __str__(self):
        return f"{self.name} - {self.get_price_unit_display()}"
