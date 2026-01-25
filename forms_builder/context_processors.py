def user_permissions(request):
    is_admin = False
    if request.user.is_authenticated:
        is_admin = request.user.is_staff or request.user.groups.filter(name='admin').exists()
    return {'is_form_admin': is_admin}
