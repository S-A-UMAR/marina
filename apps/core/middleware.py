from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.cache import cache
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


class LoginRateLimitMiddleware:
    """
    Cache-based rate limiting for staff and admin login endpoints.
    Blocks IP addresses with more than 5 failed login attempts within a 15-minute window.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only rate limit POST requests to login endpoints
        is_login_post = request.method == 'POST' and (
            request.path.startswith('/admin/login/') or request.path.startswith('/staff/login/')
        )
        
        if is_login_post:
            ip = self.get_client_ip(request)
            lockout_key = f"lockout_ip:{ip}"
            
            # Check if IP is currently locked out
            if cache.get(lockout_key):
                return HttpResponse(
                    "<html><body style='font-family:sans-serif; text-align:center; padding-top:100px; color:#333;'>"
                    "<div style='max-width:500px; margin:0 auto; padding:30px; border:1px solid #ccc; border-radius:8px;'>"
                    "<h2 style='color:#d9534f;'>Lockout Warning</h2>"
                    "<p>Too many failed login attempts have been detected from your IP address.</p>"
                    "<p>You have been locked out for <strong>15 minutes</strong> for security reasons.</p>"
                    "<p style='color:#777; font-size:14px;'>Marina Security Operations</p>"
                    "</div></body></html>",
                    status=429,
                    content_type="text/html"
                )
        
        response = self.get_response(request)
        
        if is_login_post:
            # If response is 200 (re-rendered login template on failure)
            if response.status_code == 200:
                ip = self.get_client_ip(request)
                attempts_key = f"login_attempts_ip:{ip}"
                attempts = cache.get(attempts_key, 0) + 1
                
                # Increment and set 15-minute (900 seconds) cache expiry
                cache.set(attempts_key, attempts, 900)
                
                if attempts >= 5:
                    cache.set(f"lockout_ip:{ip}", True, 900)
            elif response.status_code == 302:
                # Success — clear logs
                ip = self.get_client_ip(request)
                cache.delete(f"login_attempts_ip:{ip}")
                cache.delete(f"lockout_ip:{ip}")
                
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

