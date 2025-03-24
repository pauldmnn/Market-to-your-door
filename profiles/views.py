from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserProfileForm
from django.contrib.auth.decorators import login_required
from allauth.account.views import ConfirmEmailView
from checkout.models import Order
from .models import UserProfile




@login_required
def create_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('profile_detail')
        form = UserProfileForm()
    return render(request, 'profiles/create_profile.html', {'form': form})


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_detail')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'profiles/edit_profile.html', {'form': form})




@login_required
def my_account(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    # Get the user's orders; adjust field names as per your Order model.
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('my_account')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'profiles/my_account.html', {
        'form': form,
        'orders': orders,
    })


class CustomConfirmEmailView(ConfirmEmailView):
    def get(self, *args, **kwargs):
        response = super().get(*args, **kwargs)
        return redirect('/?login=1')
