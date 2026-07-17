from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.core.models import SiteSettings
from apps.core.utils import get_cart
from apps.catalog.models import Product
from apps.cart.models import Cart, CartItem


def cart_view(request):
    cart = get_cart(request)
    settings_obj = SiteSettings.get()
    subtotal = cart.total
    shipping = settings_obj.shipping_fee if subtotal < settings_obj.free_shipping_threshold else 0
    total = subtotal + shipping
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
        'free_threshold': settings_obj.free_shipping_threshold,
    }
    return render(request, 'orders/cart.html', context)


@require_POST
def add_to_cart(request):
    """
    Add a product to cart.
    Supports both regular form POST (returns redirect) and
    AJAX fetch requests (returns JSON).
    """
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    product = get_object_or_404(Product, id=product_id, status=Product.STATUS_PUBLISHED)

    if product.out_of_stock:
        msg = f'Sorry, {product.name} is out of stock.'
        if is_ajax:
            return JsonResponse({'ok': False, 'message': msg}, status=400)
        messages.error(request, msg)
        return redirect(request.META.get('HTTP_REFERER', 'store:home'))

    if quantity > product.current_stock:
        msg = f'Only {product.current_stock} units available.'
        if is_ajax:
            return JsonResponse({'ok': False, 'message': msg}, status=400)
        messages.error(request, msg)
        return redirect(request.META.get('HTTP_REFERER', 'store:home'))

    cart = get_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        new_qty = cart_item.quantity + quantity
        if new_qty > product.current_stock:
            msg = f'Cannot add more — max available is {product.current_stock}.'
            if is_ajax:
                return JsonResponse({'ok': False, 'message': msg}, status=400)
            messages.error(request, msg)
        else:
            cart_item.quantity = new_qty
            cart_item.save()
            msg = f'Updated {product.name} in your cart.'
            if is_ajax:
                return JsonResponse({'ok': True, 'message': msg, 'cart_count': cart.items.count()})
            messages.success(request, msg)
    else:
        cart_item.quantity = quantity
        cart_item.save()
        msg = f'{product.name} added to cart.'
        if is_ajax:
            return JsonResponse({'ok': True, 'message': msg, 'cart_count': cart.items.count()})
        messages.success(request, msg)

    return redirect(request.META.get('HTTP_REFERER', 'store:home'))


@require_POST
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity <= 0:
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
    elif quantity > cart_item.product.current_stock:
        messages.error(request, f'Only {cart_item.product.current_stock} units available.')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated.')
    return redirect('store:cart')


def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.success(request, 'Item removed from your cart.')
    return redirect('store:cart')
