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

def verify_payment(request, reference):
    """Verify Paystack payment via server-to-server call."""
    payment = get_object_or_404(Payment, reference=reference)
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {getattr(settings, 'PAYSTACK_SECRET_KEY', '')}",
        "Content-Type": "application/json",
    }
    
    # In DEBUG mode, if the request is key-empty or fails, we allow automatic fallback verification for local testing.
    is_verified = False
    verification_data = {}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        if response.status_code == 200 and data.get('status') is True:
            status_data = data.get('data', {})
            if status_data.get('status') == 'success':
                is_verified = True
                verification_data = data
    except Exception as e:
        if settings.DEBUG:
            # Fallback for debug/local testing
            is_verified = True
            verification_data = {"status": True, "message": "Bypassed for local testing", "data": {"status": "success"}}
            messages.info(request, "Local testing: Payment simulated successfully.")
        else:
            messages.error(request, f'An error occurred while verifying payment: {str(e)}')
            
    if is_verified:
        payment.status = Payment.STATUS_SUCCESS
        payment.gateway_response = verification_data
        payment.save()
        order = payment.order
        order.status = Order.STATUS_PAYMENT_VERIFIED
        order.save()
        
        # Deduct stock
        for item in order.items.all():
            if item.product:
                item.product.current_stock = max(0, item.product.current_stock - item.quantity)
                item.product.save()
                StockMovement.objects.create(
                    product=item.product,
                    movement_type=StockMovement.TYPE_OUT,
                    quantity_change=-item.quantity,
                    notes=f"Sold in Order {order.order_number}",
                )
        return redirect('store:order_confirm', order_number=order.order_number)
    else:
        if settings.DEBUG:
            # If API call returned false/failure status, but we are in debug mode, let user simulate success
            payment.status = Payment.STATUS_SUCCESS
            payment.gateway_response = {"status": True, "message": "Bypassed for local testing after API fail", "data": {"status": "success"}}
            payment.save()
            order = payment.order
            order.status = Order.STATUS_PAYMENT_VERIFIED
            order.save()
            for item in order.items.all():
                if item.product:
                    item.product.current_stock = max(0, item.product.current_stock - item.quantity)
                    item.product.save()
                    StockMovement.objects.create(
                        product=item.product,
                        movement_type=StockMovement.TYPE_OUT,
                        quantity_change=-item.quantity,
                        notes=f"Sold in Order {order.order_number}",
                    )
            messages.info(request, "Local testing: Payment simulated successfully (Paystack verification failed/bypassed).")
            return redirect('store:order_confirm', order_number=order.order_number)
        else:
            payment.status = Payment.STATUS_FAILED
            payment.save()
            messages.error(request, 'Payment was not successful on Paystack.')
            return redirect('store:home')


def payment_cancel(request, reference):
    """Called when a user closes/cancels the Paystack payment modal.
    Marks the payment and order as cancelled so it shows correctly in order history.
    """
    try:
        payment = Payment.objects.get(reference=reference)
        if payment.status == Payment.STATUS_PENDING:
            payment.status = Payment.STATUS_CANCELLED
            payment.save()
            order = payment.order
            if order.status not in [Order.STATUS_PAYMENT_VERIFIED, Order.STATUS_DELIVERED, Order.STATUS_COMPLETED]:
                order.log_status_change(Order.STATUS_CANCELLED, note='Payment cancelled by customer on Paystack modal.')
    except Payment.DoesNotExist:
        pass
    messages.warning(request, 'Payment was cancelled. Your order has been marked as cancelled. You can place a new order anytime.')
    return redirect('store:my_orders')


import hashlib
import hmac
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def paystack_webhook(request):
    """Receive and process Paystack webhook events (charge.success, charge.failed, etc.)
    This is the server-side payment confirmation — more reliable than browser redirect alone.
    """
    if request.method != 'POST':
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(['POST'])

    # Verify webhook signature
    paystack_secret = getattr(settings, 'PAYSTACK_SECRET_KEY', '')
    signature = request.headers.get('X-Paystack-Signature', '')
    computed = hmac.new(
        paystack_secret.encode('utf-8'),
        request.body,
        hashlib.sha512
    ).hexdigest()

    if not hmac.compare_digest(computed, signature):
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    try:
        event = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    event_type = event.get('event', '')
    data = event.get('data', {})
    reference = data.get('reference', '')

    if event_type == 'charge.success':
        try:
            payment = Payment.objects.get(reference=reference)
            if payment.status != Payment.STATUS_SUCCESS:
                payment.status = Payment.STATUS_SUCCESS
                payment.gateway_response = event
                payment.save()
                order = payment.order
                if order.status != Order.STATUS_PAYMENT_VERIFIED:
                    order.status = Order.STATUS_PAYMENT_VERIFIED
                    order.save()
                    # Deduct stock if not already done
                    for item in order.items.all():
                        if item.product:
                            item.product.current_stock = max(0, item.product.current_stock - item.quantity)
                            item.product.save()
        except Payment.DoesNotExist:
            pass

    elif event_type in ('charge.failed', 'transfer.failed'):
        try:
            payment = Payment.objects.get(reference=reference)
            if payment.status == Payment.STATUS_PENDING:
                payment.status = Payment.STATUS_FAILED
                payment.gateway_response = event
                payment.save()
                order = payment.order
                if order.status not in [Order.STATUS_PAYMENT_VERIFIED, Order.STATUS_COMPLETED]:
                    order.status = Order.STATUS_CANCELLED
                    order.save()
        except Payment.DoesNotExist:
            pass

    return JsonResponse({'status': 'ok'})


