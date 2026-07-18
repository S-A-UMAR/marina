"""
Marina Notification Service
Central place to create and dispatch notifications to customers.

Usage:
    from apps.notifications.services import notify

    notify(order, 'payment_confirmed')
    notify(order, 'kano_dispatch', extra={'rider_name': 'Musa', 'rider_phone': '08012345678'})
"""
from apps.notifications.models import Notification
from apps.notifications import messages as msg_templates
from apps.core.models import SiteSettings


EVENT_TEMPLATE_MAP = {
    Notification.EVENT_ORDER_RECEIVED:       msg_templates.order_received,
    Notification.EVENT_PAYMENT_CONFIRMED:    msg_templates.payment_confirmed,
    Notification.EVENT_PACKAGING_STARTED:    msg_templates.packaging_started,
    Notification.EVENT_PACKAGE_PHOTO:        msg_templates.package_sealed,
    Notification.EVENT_KANO_DISPATCH:        msg_templates.kano_dispatch,
    Notification.EVENT_INTERSTATE_HANDOVER:  msg_templates.interstate_handover,
    Notification.EVENT_DELIVERY_CONFIRM_REQ: msg_templates.delivery_confirm_request,
    Notification.EVENT_DELIVERY_CONFIRMED:   msg_templates.delivery_confirmed_satisfied,
    Notification.EVENT_DELIVERY_ISSUE:       msg_templates.delivery_issue,
}


def notify(order, event_type: str, extra: dict = None, channel=Notification.CHANNEL_WHATSAPP):
    """
    Create a Notification record for a customer and generate a WhatsApp link.

    Args:
        order: Order instance
        event_type: one of Notification.EVENT_* constants
        extra: dict of extra kwargs passed to the message template
        channel: default is 'whatsapp'

    Returns:
        Notification instance or None if customer has notifications disabled
    """
    if not order.notifications_enabled:
        return None

    if not order.user:
        return None

    site = SiteSettings.get()
    template_fn = EVENT_TEMPLATE_MAP.get(event_type)
    if not template_fn:
        return None

    extra = extra or {}
    try:
        data = template_fn(order, site=site, **extra)
    except Exception as e:
        # Never crash the order flow because of a notification error
        print(f'[Notification] Error rendering {event_type}: {e}')
        return None

    notification = Notification.objects.create(
        user=order.user,
        order=order,
        channel=channel,
        event_type=event_type,
        title=data.get('title', ''),
        message=data.get('message', ''),
        whatsapp_link=data.get('whatsapp_link', ''),
        status=Notification.STATUS_PENDING,
    )

    # If provider is just a link (manual), mark as "sent" since link is available
    if site.whatsapp_provider == SiteSettings.PROVIDER_LINK:
        notification.status = Notification.STATUS_SENT
        notification.save(update_fields=['status'])

    return notification


def get_unsent_notifications(order):
    """Return notifications with wa.me links ready to be manually sent."""
    return Notification.objects.filter(
        order=order,
        channel=Notification.CHANNEL_WHATSAPP,
        status=Notification.STATUS_SENT,
    ).order_by('-created_at')
