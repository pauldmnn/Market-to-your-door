from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import NewsletterForm
from django.core.mail import send_mail
from django.conf import settings


def subscribe_to_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            subscriber = form.save()

            # Send confirmation email
            send_mail(
                subject="Thank you for subscribing!",
                message="Thank you for subscribing to Market to Your Door newsletter.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscriber.email],
                fail_silently=False,
            )

            messages.success(request, "Thank you for subscribing!")
            return redirect('market')
    else:
        form = NewsletterForm()
    return render(request, 'newsletter/subscribe.html', {'form': form})
