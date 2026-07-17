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

@login_required
def my_marina(request):
    """Customer personal dashboard."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    active_orders = orders.filter(status__in=[
        Order.STATUS_PENDING, Order.STATUS_CONFIRMED,
        Order.STATUS_PROCESSING, Order.STATUS_DISPATCHED, Order.STATUS_IN_TRANSIT
    ])
    recent_orders = orders[:5]
    
    try:
        wishlist = Wishlist.objects.get(user=request.user)
        wishlist_count = wishlist.item_count
    except Wishlist.DoesNotExist:
        wishlist_count = 0

    rewards = Reward.objects.filter(user=request.user, status=Reward.STATUS_ACTIVE)[:3]
    notifications_qs = Notification.objects.filter(user=request.user, is_read=False)
    unread_count = notifications_qs.count()
    unread_notifications = notifications_qs[:5]

    context = {
        'recent_orders': recent_orders,
        'active_order_count': active_orders.count(),
        'wishlist_count': wishlist_count,
        'active_rewards': rewards,
        'unread_notifications': unread_notifications,
        'unread_count': unread_count,
    }
    return render(request, 'my_marina/dashboard.html', context)

@login_required

def my_rewards(request):
    rewards = Reward.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_marina/rewards.html', {'rewards': rewards})

@login_required

def my_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    # Mark all as read
    notifications.filter(is_read=False).update(is_read=True)
    paginator = Paginator(notifications, 20)
    notifs_page = paginator.get_page(request.GET.get('page'))
    return render(request, 'my_marina/notifications.html', {'notifications': notifs_page})

