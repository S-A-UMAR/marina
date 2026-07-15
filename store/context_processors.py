from .models import Cart, SiteSettings


def cart_count(request):
    """Inject cart item count into every template context."""
    count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            cart = Cart.objects.filter(session_key=session_key).first() if session_key else None

        if cart:
            count = cart.item_count
    except Exception:
        count = 0
    return {'cart_count': count}


def site_settings(request):
    """Inject site-wide settings into every template context."""
    settings_obj = SiteSettings.get()
    return {'site_settings': settings_obj}
