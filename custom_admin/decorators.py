from django.core.exceptions import PermissionDenied

def custom_admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_superuser or request.user.groups.filter(name="custom_admin").exists()):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("You do not have permission to access this section.")
    return _wrapped_view