from django.contrib import admin
from .models import UserProfile

admin.site.registe(UserProfile)