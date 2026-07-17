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

def checkout(request):
    """3-method checkout: Online (OPay/Paystack), WhatsApp Assisted, Request a Call."""
    cart = get_cart(request)
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('store:home')

    settings_obj = SiteSettings.get()
    subtotal = cart.total
    shipping = settings_obj.shipping_fee if subtotal < settings_obj.free_shipping_threshold else 0
    total = subtotal + shipping

    initial = {}
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        initial = {
            'full_name': request.user.get_full_name(),
            'email': request.user.email,
            'phone': profile.phone if profile else '',
            'address': profile.address if profile else '',
            'city': profile.city if profile else '',
            'state': profile.state if profile else '',
        }

    form = CheckoutForm(initial=initial)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            else:
                if not request.session.session_key:
                    request.session.create()
                order.session_key = request.session.session_key

            order.subtotal = subtotal
            order.shipping_fee = shipping
            order.total_amount = total
            order.save()

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    price=item.product.effective_price
                )

            checkout_method = form.cleaned_data.get('checkout_method', Order.METHOD_ONLINE)

            if checkout_method == Order.METHOD_WHATSAPP:
                cart.items.all().delete()
                return redirect('store:whatsapp_checkout', order_number=order.order_number)

            elif checkout_method == Order.METHOD_CALL:
                cart.items.all().delete()
                return redirect('store:request_call', order_number=order.order_number)

            else:
                # Online payment — Paystack
                reference = 'PAY_' + uuid.uuid4().hex[:12].upper()
                Payment.objects.create(
                    order=order,
                    reference=reference,
                    amount=total,
                    gateway=Payment.GATEWAY_PAYSTACK
                )
                cart.items.all().delete()
                context = {
                    'order': order,
                    'reference': reference,
                    'amount_kobo': int(total * 100),
                    'paystack_public_key': getattr(settings, 'PAYSTACK_PUBLIC_KEY', ''),
                    'email': order.email,
                }
                return render(request, 'payments/initiate.html', context)

    context = {
        'cart': cart,
        'form': form,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
        'free_threshold': settings_obj.free_shipping_threshold,
    }
    return render(request, 'orders/checkout.html', context)

def whatsapp_checkout(request, order_number):
    """Generate WhatsApp pre-filled message and redirect."""
    order = get_object_or_404(Order, order_number=order_number)
    settings_obj = SiteSettings.get()
    whatsapp_number = settings_obj.whatsapp_number or getattr(settings, 'MARINA_WHATSAPP_NUMBER', '')

    items_text = '\n'.join(
        [f'• {item.quantity}x {item.product_name} — ₦{item.price:,.0f}' for item in order.items.all()]
    )
    message = (
        f"Hello Marina! I'd like to complete my order.\n\n"
        f"*Order Reference:* {order.order_number}\n"
        f"*Name:* {order.full_name}\n"
        f"*Phone:* {order.phone}\n"
        f"*Delivery:* {order.city}, {order.state}\n\n"
        f"*Items:*\n{items_text}\n\n"
        f"*Total:* ₦{order.total_amount:,.0f}\n\n"
        f"Please confirm and advise on payment."
    )

    import urllib.parse
    whatsapp_url = f"https://wa.me/{whatsapp_number}?text={urllib.parse.quote(message)}"

    context = {
        'order': order,
        'whatsapp_url': whatsapp_url,
        'whatsapp_number': whatsapp_number,
    }
    return render(request, 'orders/whatsapp_checkout.html', context)

def request_call(request, order_number):
    """Request-a-call confirmation page."""
    order = get_object_or_404(Order, order_number=order_number)
    order.status = Order.STATUS_PENDING
    order.save()
    context = {'order': order}
    return render(request, 'orders/request_call.html', context)

