from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import FileResponse
import os

# Import urlpatterns from all apps
from apps.homepage import urls as homepage_urls
from apps.catalog import urls as catalog_urls
from apps.cart import urls as cart_urls
from apps.wishlist import urls as wishlist_urls
from apps.checkout import urls as checkout_urls
from apps.orders import urls as orders_urls
from apps.payments import urls as payments_urls
from apps.accounts import urls as accounts_urls
from apps.customers import urls as customers_urls
from apps.core import urls as core_urls
from apps.dashboard import urls as dashboard_urls
from apps.feedback import urls as feedback_urls

combined_urlpatterns = (
    homepage_urls.urlpatterns +
    catalog_urls.urlpatterns +
    cart_urls.urlpatterns +
    wishlist_urls.urlpatterns +
    checkout_urls.urlpatterns +
    orders_urls.urlpatterns +
    payments_urls.urlpatterns +
    accounts_urls.urlpatterns +
    customers_urls.urlpatterns +
    core_urls.urlpatterns +
    dashboard_urls.urlpatterns +
    feedback_urls.urlpatterns
)

def serve_manifest(request):
    """Serve the PWA Web App Manifest."""
    manifest_path = os.path.join(settings.BASE_DIR, 'static', 'manifest.json')
    return FileResponse(open(manifest_path, 'rb'), content_type='application/manifest+json')

def serve_sw(request):
    """Serve the PWA Service Worker from root scope so it can control all pages."""
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'sw.js')
    response = FileResponse(open(sw_path, 'rb'), content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache'
    return response

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include((combined_urlpatterns, 'store'))),
    # PWA
    path('manifest.json', serve_manifest, name='pwa_manifest'),
    path('sw.js', serve_sw, name='pwa_sw'),
    path('offline/', TemplateView.as_view(template_name='offline.html'), name='offline'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else '')


