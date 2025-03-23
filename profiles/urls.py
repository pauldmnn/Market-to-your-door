from django.urls import path
from .views import create_profile, edit_profile

urlpatterns = [
    path('create/', create_profile, name='create_profile'),
    path('edit/', edit_profile, name='edit_profile'),
]
