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
    return {'site_settings': SiteSettings.get()}


def wishlist_count(request):
    count = 0
    if request.user.is_authenticated:
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            count = wishlist.item_count
        except Wishlist.DoesNotExist:
            pass
    return {'wishlist_count': count}


def categories_context(request):
    categories = Category.objects.filter(is_active=True).order_by('name')[:16]
    return {'nav_categories': categories}
