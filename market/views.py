from django.shortcuts import render
from allauth.account.forms import SignupForm


def index(request):
    """
    A view to return the index page
    """
    return render(request, 'market/index.html')


def home(request):
    return render(request, "market.html", {
        "form": SignupForm(),
    })
