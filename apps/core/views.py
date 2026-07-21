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

def contact_view(request):
    submitted = False
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()
        if name and message:
            submitted = True
            messages.success(request, 'Thank you! We received your message and will respond within 24 hours.')
        else:
            messages.error(request, 'Please fill in all required fields.')
    return render(request, 'info/contact.html', {'submitted': submitted})

def faq_view(request):
    return render(request, 'info/faq.html')

def shipping_view(request):
    return render(request, 'info/shipping.html')

def warranty_view(request):
    return render(request, 'info/warranty.html')

def privacy_policy_view(request):
    return render(request, 'info/privacy_policy.html')

def terms_view(request):
    return render(request, 'info/terms.html')


def robots_txt(request):
    """Dynamic robots.txt generation."""
    sitemap_url = request.build_absolute_uri('/sitemap.xml')
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Disallow: /staff/\n"
        "Disallow: /my-marina/\n\n"
        f"Sitemap: {sitemap_url}"
    )
    return HttpResponse(content, content_type="text/plain")


def sitemap_xml(request):
    """Dynamic sitemap.xml generation."""
    import xml.etree.ElementTree as ET
    from django.urls import reverse

    urlset = ET.Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    # Static Pages
    static_urls = [
        'store:home', 'store:info_about', 'store:info_contact', 'store:info_faq',
        'store:info_shipping', 'store:info_warranty', 'store:privacy_policy', 'store:terms', 'store:brands'
    ]

    for url_name in static_urls:
        try:
            url = reverse(url_name)
            loc = request.build_absolute_uri(url)
            url_el = ET.SubElement(urlset, 'url')
            ET.SubElement(url_el, 'loc').text = loc
            ET.SubElement(url_el, 'changefreq').text = 'weekly'
            ET.SubElement(url_el, 'priority').text = '0.8'
        except Exception:
            pass

    # Categories
    for cat in Category.objects.all():
        try:
            url = reverse('store:category_page', kwargs={'slug': cat.slug})
            loc = request.build_absolute_uri(url)
            url_el = ET.SubElement(urlset, 'url')
            ET.SubElement(url_el, 'loc').text = loc
            ET.SubElement(url_el, 'changefreq').text = 'weekly'
            ET.SubElement(url_el, 'priority').text = '0.7'
        except Exception:
            pass

    # Brands
    for brand in Brand.objects.all():
        try:
            url = reverse('store:brand_detail', kwargs={'slug': brand.slug})
            loc = request.build_absolute_uri(url)
            url_el = ET.SubElement(urlset, 'url')
            ET.SubElement(url_el, 'loc').text = loc
            ET.SubElement(url_el, 'changefreq').text = 'weekly'
            ET.SubElement(url_el, 'priority').text = '0.7'
        except Exception:
            pass

    # Products
    for prod in Product.objects.filter(is_active=True):
        try:
            url = reverse('store:product_detail', kwargs={'slug': prod.slug})
            loc = request.build_absolute_uri(url)
            url_el = ET.SubElement(urlset, 'url')
            ET.SubElement(url_el, 'loc').text = loc
            ET.SubElement(url_el, 'changefreq').text = 'daily'
            ET.SubElement(url_el, 'priority').text = '0.9'
        except Exception:
            pass

    xml_str = ET.tostring(urlset, encoding='utf-8', method='xml')
    return HttpResponse(xml_str, content_type="application/xml")


# ===========================================================================
# STAFF PORTAL VIEWS
# ===========================================================================

