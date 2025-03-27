def is_admin_user(request):
    """
    Adds a boolean to the context indicating whether the user is a superuser or in the 'custom_admin' group.
    """
    user = request.user
    is_admin = False
    if user.is_authenticated:
        is_admin = user.is_superuser or user.groups.filter(name="custom_admin").exists()
    
    return {
        'is_admin_user': is_admin
    }
