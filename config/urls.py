from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include((combined_urlpatterns, 'store'))),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else '')

