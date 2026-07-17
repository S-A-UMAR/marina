from apps.cart.models import Cart

def is_staff_member(user):
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    try:
        return user.profile.is_staff_member()
    except Exception:
        return False


def is_admin_member(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    try:
        return user.profile.is_admin()
    except Exception:
        return False


def get_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart
