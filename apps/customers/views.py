from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from apps.core.utils import get_cart
from apps.orders.models import Order
from apps.wishlist.models import Wishlist
from apps.rewards.models import Reward
from apps.notifications.models import Notification


@login_required
def my_marina(request):
    """Customer personal dashboard."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    active_orders = orders.filter(status__in=[
        Order.STATUS_RECEIVED, Order.STATUS_PAYMENT_CONFIRMED,
        Order.STATUS_PENDING, Order.STATUS_AWAITING_PAYMENT, Order.STATUS_PAYMENT_VERIFIED,
        Order.STATUS_CONFIRMED, Order.STATUS_PENDING_PACKAGING, Order.STATUS_PACKAGING,
        Order.STATUS_PACKING, Order.STATUS_PACKED, Order.STATUS_AWAITING_DISPATCH,
        Order.STATUS_DISPATCHED, Order.STATUS_IN_TRANSIT, Order.STATUS_DELIVERED
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

