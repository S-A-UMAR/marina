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

def home(request):
    """Marina homepage — hero, featured, new arrivals, categories, brands."""
    hero_banners = Banner.objects.filter(banner_type=Banner.TYPE_HERO, is_active=True)[:3]
    promo_banners = Banner.objects.filter(banner_type=Banner.TYPE_PROMO, is_active=True)[:2]
    featured_products = Product.objects.filter(
        status=Product.STATUS_PUBLISHED, is_featured=True
    ).select_related('brand', 'category')[:8]
    new_arrivals = Product.objects.filter(
        status=Product.STATUS_PUBLISHED, is_new_arrival=True
    ).select_related('brand', 'category').order_by('-created_at')[:8]
    categories = Category.objects.filter(is_active=True)[:8]
    brands = Brand.objects.filter(is_active=True)[:10]

    context = {
        'hero_banners': hero_banners,
        'promo_banners': promo_banners,
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'categories': categories,
        'brands': brands,
    }
    return render(request, 'store/home.html', context)

def about_view(request):
    return render(request, 'info/about.html')

