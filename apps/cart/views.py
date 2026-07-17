import requests
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Avg, F
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# Import models
from apps.core.models import SiteSettings
from apps.core.utils import get_cart, is_staff_member, is_admin_member
from apps.accounts.models import UserProfile
from apps.brands.models import Brand
from apps.catalog.models import Category, Product, ProductImage, ProductSpecification, ProductReview
from apps.cart.models import Cart, CartItem
from apps.wishlist.models import Wishlist, WishlistItem
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment
from apps.inventory.models import StockMovement, Supplier
from apps.homepage.models import Banner
from apps.feedback.models import Feedback
from apps.rewards.models import Reward
from apps.notifications.models import Notification

# Import helpers across apps

# Import forms
from apps.accounts.forms import RegisterForm, LoginForm, ProfileForm
from apps.catalog.forms import ProductForm, BrandForm, CategoryForm, ReviewForm
from apps.inventory.forms import SupplierForm, StockInForm, StockOutForm
from apps.checkout.forms import CheckoutForm
from apps.feedback.forms import FeedbackForm, FeedbackStatusForm
from apps.rewards.forms import RewardForm
from apps.homepage.forms import BannerForm
from apps.core.forms import SiteSettingsForm
from apps.dashboard.forms import DashboardUserForm

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
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    product = get_object_or_404(Product, id=product_id, status=Product.STATUS_PUBLISHED)

    if product.out_of_stock:
        messages.error(request, f'Sorry, {product.name} is out of stock.')
        return redirect(request.META.get('HTTP_REFERER', 'store:home'))

    if quantity > product.current_stock:
        messages.error(request, f'Only {product.current_stock} units available.')
        return redirect(request.META.get('HTTP_REFERER', 'store:home'))

    cart = get_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        new_qty = cart_item.quantity + quantity
        if new_qty > product.current_stock:
            messages.error(request, f'Cannot add more — max available is {product.current_stock}.')
        else:
            cart_item.quantity = new_qty
            cart_item.save()
            messages.success(request, f'Updated {product.name} in your cart.')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, f'{product.name} added to cart.')

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

# ===========================================================================
# WISHLIST VIEWS
# ===========================================================================

@login_required

def get_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart

# ===========================================================================
# PUBLIC STOREFRONT VIEWS
# ===========================================================================

