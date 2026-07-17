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

def category_page(request, slug):
    """Products filtered by category with sorting and filtering."""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products_qs = Product.objects.filter(
        category=category, status=Product.STATUS_PUBLISHED
    ).select_related('brand')

    # Filters
    brand_filter = request.GET.get('brand', '')
    condition_filter = request.GET.get('condition', '')
    availability = request.GET.get('availability', '')
    sort = request.GET.get('sort', 'newest')

    if brand_filter:
        products_qs = products_qs.filter(brand__slug=brand_filter)
    if condition_filter:
        products_qs = products_qs.filter(condition=condition_filter)
    if availability == 'in_stock':
        products_qs = products_qs.filter(current_stock__gt=0)

    if sort == 'price_low':
        products_qs = products_qs.order_by('selling_price')
    elif sort == 'price_high':
        products_qs = products_qs.order_by('-selling_price')
    elif sort == 'newest':
        products_qs = products_qs.order_by('-created_at')

    paginator = Paginator(products_qs, 16)
    products = paginator.get_page(request.GET.get('page'))
    brands_in_category = Brand.objects.filter(
        products__category=category, products__status=Product.STATUS_PUBLISHED
    ).distinct()

    context = {
        'category': category,
        'products': products,
        'brands_in_category': brands_in_category,
        'brand_filter': brand_filter,
        'condition_filter': condition_filter,
        'availability': availability,
        'sort': sort,
        'condition_choices': Product.CONDITION_CHOICES,
    }
    return render(request, 'store/category_page.html', context)

def brand_list(request):
    """All brands page."""
    brands = Brand.objects.filter(is_active=True).annotate(
        product_count=Count('products', filter=Q(products__status=Product.STATUS_PUBLISHED))
    )
    context = {'brands': brands}
    return render(request, 'store/brands.html', context)

def brand_detail(request, slug):
    """Products filtered by brand."""
    brand = get_object_or_404(Brand, slug=slug, is_active=True)
    products_qs = Product.objects.filter(
        brand=brand, status=Product.STATUS_PUBLISHED
    ).select_related('category')

    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        products_qs = products_qs.order_by('selling_price')
    elif sort == 'price_high':
        products_qs = products_qs.order_by('-selling_price')
    else:
        products_qs = products_qs.order_by('-created_at')

    paginator = Paginator(products_qs, 16)
    products = paginator.get_page(request.GET.get('page'))
    context = {'brand': brand, 'products': products, 'sort': sort}
    return render(request, 'store/brand_detail.html', context)

def search_results(request):
    """Product search with filters."""
    query = request.GET.get('q', '').strip()
    products_qs = Product.objects.filter(status=Product.STATUS_PUBLISHED).select_related('brand', 'category')

    if query:
        products_qs = products_qs.filter(
            Q(name__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query) |
            Q(sku__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Filters
    brand_filter = request.GET.get('brand', '')
    condition_filter = request.GET.get('condition', '')
    sort = request.GET.get('sort', '')

    if brand_filter:
        products_qs = products_qs.filter(brand__slug=brand_filter)
    if condition_filter:
        products_qs = products_qs.filter(condition=condition_filter)
    if sort == 'price_low':
        products_qs = products_qs.order_by('selling_price')
    elif sort == 'price_high':
        products_qs = products_qs.order_by('-selling_price')
    elif sort == 'newest':
        products_qs = products_qs.order_by('-created_at')

    paginator = Paginator(products_qs, 16)
    products = paginator.get_page(request.GET.get('page'))
    brands = Brand.objects.filter(is_active=True)

    context = {
        'query': query,
        'products': products,
        'brands': brands,
        'brand_filter': brand_filter,
        'condition_filter': condition_filter,
        'sort': sort,
        'result_count': products_qs.count(),
        'condition_choices': Product.CONDITION_CHOICES,
    }
    return render(request, 'store/search_results.html', context)

def product_detail(request, slug):
    """Full product detail page."""
    product = get_object_or_404(Product, slug=slug, status=Product.STATUS_PUBLISHED)
    gallery_images = product.gallery_images.all()
    specifications = product.specifications.all()
    reviews = product.reviews.select_related('user').order_by('-created_at')
    related_products = Product.objects.filter(
        category=product.category, status=Product.STATUS_PUBLISHED
    ).exclude(id=product.id).select_related('brand')[:4]

    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    user_reviewed = False
    if request.user.is_authenticated:
        user_reviewed = ProductReview.objects.filter(product=product, user=request.user).exists()

    review_form = ReviewForm()
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            if user_reviewed:
                messages.warning(request, "You've already reviewed this product.")
            else:
                rev = review_form.save(commit=False)
                rev.product = product
                rev.user = request.user
                rev.save()
                messages.success(request, 'Thank you for your review!')
                return redirect('store:product_detail', slug=product.slug)

    # Check if in wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            in_wishlist = WishlistItem.objects.filter(wishlist=wishlist, product=product).exists()
        except Wishlist.DoesNotExist:
            pass

    context = {
        'product': product,
        'gallery_images': gallery_images,
        'specifications': specifications,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'review_count': reviews.count(),
        'review_form': review_form,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
        'user_reviewed': user_reviewed,
        'whatsapp_number': getattr(settings, 'MARINA_WHATSAPP_NUMBER', ''),
    }
    return render(request, 'store/product_detail.html', context)

# ===========================================================================
# CART VIEWS
# ===========================================================================

