from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.catalog.models import Product
from apps.wishlist.models import Wishlist, WishlistItem


def wishlist_view(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please log in to view your wishlist.')
        return redirect('store:login')
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.select_related('product__brand', 'product__category')
    context = {'wishlist': wishlist, 'items': items}
    return render(request, 'store/wishlist.html', context)


@login_required
@require_POST
def add_to_wishlist(request):
    """
    Toggle wishlist item (add/remove).
    Supports AJAX via X-Requested-With header.
    """
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id, status=Product.STATUS_PUBLISHED)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)

    if created:
        msg = f'{product.name} saved to your wishlist.'
        in_wishlist = True
    else:
        # Toggle: remove if already saved
        item.delete()
        msg = f'{product.name} removed from wishlist.'
        in_wishlist = False

    if is_ajax:
        return JsonResponse({
            'ok': True,
            'message': msg,
            'in_wishlist': in_wishlist,
            'wishlist_count': wishlist.items.count(),
        })

    messages.success(request, msg)
    return redirect(request.META.get('HTTP_REFERER', 'store:wishlist'))


@login_required
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    item.delete()
    messages.success(request, 'Item removed from wishlist.')
    return redirect('store:wishlist')
