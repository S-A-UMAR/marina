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

def order_confirm(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/order_confirm.html', {'order': order})

# ===========================================================================
# AUTHENTICATION VIEWS
# ===========================================================================

def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(orders, 10)
    orders_page = paginator.get_page(request.GET.get('page'))
    return render(request, 'my_marina/orders.html', {'orders': orders_page})

@login_required

def order_list(request):
    return redirect('store:dashboard_orders')

@login_required
def my_order_detail(request, order_number):
    """Customer order tracking detail page with visual timeline stepper and notification logs."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    timeline_data = order.get_timeline_data()
    notifications = Notification.objects.filter(order=order, user=request.user).order_by('-created_at')
    
    # Check if a package photo exists
    package_photo = getattr(order, 'package_photo', None)
    
    # Get any active interstate dispatch driver phone
    interstate_dispatch = None
    if order.delivery_type == Order.DELIVERY_INTERSTATE:
        from apps.orders.models import InterstateDispatch
        # Look up by state of this order on any dispatch batch it belongs to
        batch_item = order.dispatch_batches.first()
        if batch_item:
            interstate_dispatch = InterstateDispatch.objects.filter(batch=batch_item.batch, state=order.state).first()
            
    # Get local Kano dispatch details if in_transit
    local_dispatch = None
    if order.delivery_type == Order.DELIVERY_KANO:
        batch_item = order.dispatch_batches.first()
        if batch_item and batch_item.batch.rider_phone:
            local_dispatch = {
                'rider_name': batch_item.batch.rider_name,
                'rider_phone': batch_item.batch.rider_phone
            }

    context = {
        'order': order,
        'timeline_data': timeline_data,
        'notifications': notifications,
        'package_photo': package_photo,
        'interstate_dispatch': interstate_dispatch,
        'local_dispatch': local_dispatch,
    }
    return render(request, 'my_marina/order_detail.html', context)


