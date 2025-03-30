from django.urls import path
from .views import submit_review


urlpatterns = [
    path('submit/<slug:product_slug>/', submit_review, name='submit_review'),
]
