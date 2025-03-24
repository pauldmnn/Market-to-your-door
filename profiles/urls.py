from django.urls import path
from .views import create_profile, edit_profile, my_account

urlpatterns = [
    path('create/', create_profile, name='create_profile'),
    path('edit/', edit_profile, name='edit_profile'),
    path('my-account/', my_account, name='my_account'),
]
