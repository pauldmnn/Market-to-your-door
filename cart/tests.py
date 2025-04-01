import pytest
from django.contrib.auth.models import User
from products.models import Product, Category
from cart.models import Cart
from decimal import Decimal
from django.urls import reverse


@pytest.mark.django_db
def test_cart_str_method():
    user = User.objects.create_user(username='tester', password='testpass')
    category = Category.objects.create(name='Fruits')
    product = Product.objects.create(
        name='Banana',
        slug='banana',
        category=category,
        price=1.5,
        description='Fresh bananas',
        inventory=100,
        image='products/test.jpg',
    )
    cart_item = Cart.objects.create(user=user, product=product, quantity=2)
    assert str(cart_item) == '2 x Banana for tester'


@pytest.mark.django_db
def test_get_total_price():
    category = Category.objects.create(name='Fruits')
    product = Product.objects.create(
        name='Apple',
        slug='apple',
        category=category,
        price=2.0,
        description='Fresh apple',
        inventory=100,
        image='products/test.jpg',
    )
    cart = Cart.objects.create(product=product, quantity=3)
    assert cart.get_total_price() == Decimal('6.0')


@pytest.mark.django_db
def test_add_to_cart_authenticated(client):
    user = User.objects.create_user(username='testuser', password='pass')
    client.login(username='testuser', password='pass')
    category = Category.objects.create(name='Veggies')
    product = Product.objects.create(
        name='Carrot',
        slug='carrot',
        category=category,
        price=0.8,
        description='Fresh carrot',
        inventory=50,
        image='products/test.jpg',
    )
    response = client.post(reverse('add_to_cart', args=[product.slug]), {'quantity': 2})
    assert response.status_code == 302
    assert Cart.objects.filter(user=user, product=product).exists()
    assert Cart.objects.get(user=user, product=product).quantity == 2


@pytest.mark.django_db
def test_add_to_cart_guest(client):
    category = Category.objects.create(name='Veggies')
    product = Product.objects.create(
        name='Tomato',
        slug='tomato',
        category=category,
        price=1.0,
        description='Fresh tomato',
        inventory=10,
        image='products/test.jpg',
    )
    response = client.post(reverse('add_to_cart', args=[product.slug]), {'quantity': 2}, follow=True)
    assert response.status_code == 200
    cart = client.session['cart']
    assert str(product.id) in cart
    assert cart[str(product.id)] == 2.0


@pytest.mark.django_db
def test_view_cart_authenticated(client):
    user = User.objects.create_user(username='viewer', password='pass')
    client.login(username='viewer', password='pass')
    category = Category.objects.create(name='Juice')
    product = Product.objects.create(
        name='Orange Juice',
        slug='orange-juice',
        category=category,
        price=3.5,
        description='Fresh orange juice',
        inventory=20,
        image='products/test.jpg',
    )
    Cart.objects.create(user=user, product=product, quantity=2)
    response = client.get(reverse('cart_detail'))
    assert response.status_code == 200
    assert b'Orange Juice' in response.content
    assert b'7.0' in response.content


@pytest.mark.django_db
def test_cart_detail_guest(client):
    category = Category.objects.create(name='Milk')
    product = Product.objects.create(
        name='Milk',
        slug='milk',
        category=category,
        price=1.5,
        description='Fresh milk',
        inventory=10,
        image='products/test.jpg',
    )
    session = client.session
    session['cart'] = {str(product.id): 3.0}
    session.save()
    response = client.get(reverse('cart_detail'))
    assert response.status_code == 200
    assert b'Milk' in response.content
    assert b'4.5' in response.content