from django.core.cache import cache
from apps.cart.models import Cart
from apps.core.models import SiteSettings
from apps.wishlist.models import Wishlist
from apps.catalog.models import Category

def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.item_count
        except Cart.DoesNotExist:
            pass
    else:
        session_key = request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.get(session_key=session_key)
                count = cart.item_count
            except Cart.DoesNotExist:
                pass
    return {'cart_count': count}


def site_settings(request):
    """Cache SiteSettings for 5 minutes to avoid a DB hit on every page load."""
    settings_obj = cache.get('marina_site_settings')
    if settings_obj is None:
        settings_obj = SiteSettings.get()
        cache.set('marina_site_settings', settings_obj, 300)  # 5 minutes
    return {'site_settings': settings_obj}


def wishlist_count(request):
    count = 0
    if request.user.is_authenticated:
        cache_key = f'wishlist_count_{request.user.pk}'
        count = cache.get(cache_key)
        if count is None:
            try:
                wishlist = Wishlist.objects.get(user=request.user)
                count = wishlist.item_count
            except Wishlist.DoesNotExist:
                count = 0
            cache.set(cache_key, count, 120)  # 2 minutes
    return {'wishlist_count': count}


def categories_context(request):
    """Cache nav categories for 10 minutes."""
    nav_categories = cache.get('marina_nav_categories')
    if nav_categories is None:
        nav_categories = list(Category.objects.filter(is_active=True).order_by('name')[:16])
        cache.set('marina_nav_categories', nav_categories, 600)  # 10 minutes
    return {'nav_categories': nav_categories}

