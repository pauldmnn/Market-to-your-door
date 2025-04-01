import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from checkout.models import Order, OrderItem, ShippingAddress
from products.models import Product, Category
from cart.models import Cart
from decimal import Decimal


@pytest.fixture
def test_user(db):
    return User.objects.create_user(username='testuser', password='testpass')


@pytest.fixture
def test_category():
    return Category.objects.create(name='Fruits')


@pytest.fixture
def test_product(test_category):
    return Product.objects.create(
        name='Apple',
        slug='apple',
        category=test_category,
        description='Fresh red apple',
        price=Decimal('1.50'),
        inventory=10
    )


@pytest.fixture
def shipping_address():
    return ShippingAddress.objects.create(
        full_name='John Doe',
        email='john@example.com',
        address_line1='123 Street',
        postal_code='12345',
        city='Cityville',
        country='GB',
        phone='1234567890'
    )


@pytest.mark.django_db
def test_order_number_is_generated(test_user, shipping_address):
    order = Order.objects.create(user=test_user, shipping_address=shipping_address)
    assert order.order_number is not None
    assert len(order.order_number) == 12


@pytest.mark.django_db
def test_order_str(test_user, shipping_address):
    order = Order.objects.create(user=test_user, shipping_address=shipping_address)
    assert str(order).startswith('Order')


@pytest.mark.django_db
def test_order_item_total_price(test_user, shipping_address, test_product):
    order = Order.objects.create(user=test_user, shipping_address=shipping_address)
    item = OrderItem.objects.create(order=order, product=test_product, quantity=3)
    assert item.get_total_price() == test_product.price * 3


@pytest.mark.django_db
def test_checkout_view_authenticated(client, test_user, test_product):
    client.force_login(test_user)
    session = client.session
    session["cart"] = {str(test_product.id): 2}
    session.save()

    response = client.get(reverse('checkout'))
    assert response.status_code == 200
    assert b"Stripe" in response.content


@pytest.mark.django_db
def test_checkout_view_authenticated(client, test_user, test_product):
    client.force_login(test_user)
    
    Cart.objects.create(user=test_user, product=test_product, quantity=2)

    response = client.get(reverse('checkout'))
    assert response.status_code == 200
    assert b"Stripe" in response.content


@pytest.mark.django_db
def test_order_summary_view(client, test_user, shipping_address):
    client.force_login(test_user)
    order = Order.objects.create(user=test_user, shipping_address=shipping_address)
    response = client.get(reverse('order_summary', args=[order.id]))
    assert response.status_code == 200
    assert b"Order" in response.content


@pytest.mark.django_db
def test_payment_cancel_view(client):
    response = client.get(reverse('payment_cancel'))
    assert response.status_code == 302
