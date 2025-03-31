from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.utils.decorators import method_decorator


def superuser_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def custom_admin_required(view_func=None):
    def check(user):
        return user.is_authenticated and (user.is_superuser or user.groups.filter(name='custom_admin').exists())

    decorator = user_passes_test(check)

    if view_func is None:
        return decorator

    # Detect if it's a class-based view
    if hasattr(view_func, 'as_view'):
        return method_decorator(decorator, name='dispatch')(view_func)
    else:
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not check(request.user):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
