from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm


def contact_us(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for contacting us. We'll get back to you shortly.")
            return redirect('contact_us')
    else:
        form = ContactForm()

    return render(request, 'contact/contact_us.html', {'form': form})
