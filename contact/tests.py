import pytest
from django.urls import reverse
from contact.models import CustomerQuestion
from contact.forms import ContactForm


#Models Test
@pytest.mark.django_db
def test_customer_question_str_representation():
    question = CustomerQuestion.objects.create(
        full_name="Jane Doe",
        email="jane@example.com",
        details="Can I change my delivery address?"
    )
    assert str(question) == "Jane Doe - jane@example.com"


# Form Test
def test_contact_form_valid():
    form_data = {
        'full_name': 'John Doe',
        'email': 'john@example.com',
        'details': 'Is my order shipped?'
    }
    form = ContactForm(data=form_data)
    assert form.is_valid()  


def test_contact_form_missing_fields():
    form_data = {
        'full_name': '',
        'email': '',
        'details': '',
    }
    form = ContactForm(data=form_data)
    assert not form.is_valid()
    assert 'full_name' in form.errors
    assert 'email' in form.errors
    assert 'details' in form.errors


# Views Test
@pytest.mark.django_db
def test_contact_us_get_view(client):
    url = reverse("contact_us")
    response = client.get(url)
    assert response.status_code == 200
    assert b"Contact" in response.content  


@pytest.mark.django_db
def test_contact_us_post_valid(client):
    url = reverse("contact_us")
    data = {
        'full_name': 'Alice Smith',
        'email': 'alice@example.com',
        'details': 'Do you deliver on weekends?',
    }
    response = client.post(url, data, follow=True)

    assert response.status_code == 200
    assert CustomerQuestion.objects.filter(email="alice@example.com").exists()
    assert b"Thank you for contacting us" in response.content


@pytest.mark.django_db
def test_contact_us_post_invalid(client):
    url = reverse("contact_us")
    data = {
        'full_name': '',
        'email': '',
        'details': '',
    }
    response = client.post(url, data)
    assert response.status_code == 200
    assert CustomerQuestion.objects.count() == 0
