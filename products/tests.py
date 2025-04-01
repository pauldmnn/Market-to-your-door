import pytest
from django.urls import reverse
from django.test import Client
from products.models import Category, Product


@pytest.mark.django_db
class TestProductModelsViews:
    def setup_method(self):
        self.client = Client()
        self.category = Category.objects.create(name="Fruits", slug="fruits")
        self.product = Product.objects.create(
            category=self.category,
            name="Apple",
            slug="apple",
            description="Fresh apple",
            price=1.50,
            inventory=10,
        )

    # ---------- MODEL TESTS ----------
    def test_product_str(self):
        assert str(self.product) == "Apple - Per Piece"

    def test_category_str(self):
        assert str(self.category) == "Fruits"

    def test_product_inventory_check(self):
        self.product.inventory = 0
        assert not self.product.is_in_stock()

    def test_product_average_rating_no_reviews(self):
        assert self.product.average_rating == 0

    def test_product_negative_inventory_raises_error(self):
        with pytest.raises(ValueError):
            self.product.inventory = -1
            self.product.save()

    # ---------- VIEW TESTS ----------
    def test_product_list_view(self):
        url = reverse("product_list")
        response = self.client.get(url)
        assert response.status_code == 200
        assert b"Apple" in response.content

    def test_product_detail_view(self):
        url = reverse("product_detail", args=[self.product.slug])
        response = self.client.get(url)
        assert response.status_code == 200
        assert b"Fresh apple" in response.content

    def test_category_products_view(self):
        url = reverse("category_products", args=[self.category.slug])
        response = self.client.get(url)
        assert response.status_code == 200
        assert b"Apple" in response.content
