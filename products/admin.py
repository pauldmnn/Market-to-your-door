from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'inventory', 'is_in_stock', 'created', 'updated']
    list_filter = ['category', 'created', 'updated']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def is_in_stock(self, obj):
        return obj.inventory > 0
    is_in_stock.boolean = True