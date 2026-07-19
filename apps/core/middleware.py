from django.shortcuts import redirect
from django.contrib import messages
from apps.core.utils import is_admin_member, is_staff_member

class RestrictAdminMiddleware:
    """
    Middleware to restrict access to Django /admin/ panel.
    Only allows users who are admin members (role=admin, role=superadmin, or is_superuser=True).
    Staff members are redirected to the Staff Dashboard (/staff/).
    Customers/Guests are redirected to My Marina (/my-marina/).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            # Exclude logout and standard assets from blocking
            allowed_prefixes = ['/admin/logout/', '/admin/jsi18n/']
            if not any(request.path.startswith(p) for p in allowed_prefixes):
                if request.user.is_authenticated:
                    if not is_admin_member(request.user):
                        messages.error(request, "Access denied. Only Administrators can access the Django Admin panel.")
                        if is_staff_member(request.user):
                            return redirect('store:dashboard_overview')
                        return redirect('store:my_marina')
        return self.get_response(request)
