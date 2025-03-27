from django.urls import path
from .views import subscribe_to_newsletter

urlpatterns = [
    path('subscribe/', subscribe_to_newsletter, name='subscribe_newsletter'),
]
