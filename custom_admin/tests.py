import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Product, Category
from checkout.models import Order

@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass"
    )


@pytest.mark.django_db
def test_dashboard_home_authenticated_admin(client, admin_user):
    client.force_login(admin_user)
    url = reverse("dashboard_home")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_order_update_view(client, admin_user):
    client.force_login(admin_user)
    order = Order.objects.create(status="pending", total_price=100)
    url = reverse("order_update", args=[order.pk])
    data = {"status": "shipped", "payment_id": "test123"}
    response = client.post(url, data, follow=True)
    assert response.status_code == 200
    order.refresh_from_db()
    assert order.status == "shipped"


@pytest.mark.django_db
def test_category_crud(client, superuser):
    client.force_login(superuser)
    url_add = reverse("add_category")
    url_list = reverse("add_category")
    url_edit = reverse("edit_category", args=["fruits"])
    url_delete = reverse("delete_category", args=["fruits"])

    # Create category
    response = client.post(url_add, {"name": "Fruits", "slug": "fruits"}, follow=True)
    assert response.status_code == 200
    assert Category.objects.filter(slug="fruits").exists()

    # Edit category
    category = Category.objects.get(slug="fruits")
    response = client.post(url_edit, {"name": "Citrus", "slug": "fruits"}, follow=True)
    category.refresh_from_db()
    assert category.name == "Citrus"

    # Delete category
    response = client.post(url_delete, follow=True)
    assert not Category.objects.filter(slug="fruits").exists()


@pytest.mark.django_db
def test_manage_users(client, superuser):
    client.force_login(superuser)
    url = reverse("manage_users")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_promote_user(client, superuser):
    client.force_login(superuser)
    user = User.objects.create_user(username="basicuser", password="test")
    url = reverse("promote_user", args=[user.id])
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert user.groups.filter(name="custom_admin").exists()


@pytest.mark.django_db
def test_edit_user(client, superuser):
    client.force_login(superuser)
    url = reverse("edit_user", args=[superuser.id])
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_review_list_view(client, admin_user):
    client.force_login(admin_user)
    url = reverse("review_list")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_customer_questions_view(client, admin_user):
    client.force_login(admin_user)
    url = reverse("customer_questions")
    response = client.get(url)
    assert response.status_code == 200
