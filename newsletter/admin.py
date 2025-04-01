from django.contrib import admin
from .models import NewsletterSubscriber

admin.site.registe(NewsletterSubscriber)