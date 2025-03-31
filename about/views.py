from django.shortcuts import render
from .models import AboutUs


def about_view(request):
    about = AboutUs.objects.first()
    return render(request, 'about/about.html', {'about': about})
