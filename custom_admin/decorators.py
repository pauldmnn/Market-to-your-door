from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect


def superuser_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def custom_admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (
            request.user.is_superuser or request.user.groups.filter(name="custom_admin").exists()
        ):
            return view_func(request, *args, **kwargs)
        return redirect("account_login")
    return _wrapped_view