"""
Marina Notification Message Templates
All customer-facing message text lives here for easy editing.
"""
from django.conf import settings
from urllib.parse import quote


def _wa_link(phone: str, message: str) -> str:
    """Generate a pre-filled wa.me link."""
    clean = ''.join(c for c in phone if c.isdigit())
    return f'https://wa.me/{clean}?text={quote(message)}'


def payment_confirmed(order, site=None) -> dict:
    msg = (
        f"✅ *Payment Confirmed!*\n\n"
        f"Hi {order.full_name}, your payment for order *#{order.order_number}* "
        f"has been confirmed.\n\n"
        f"We have received your order and will begin packaging shortly.\n\n"
        f"Track your order from your Marina account.\n\n"
        f"Thank you for choosing Marina Gadgets Kano! 🙏"
    )
    return {
        'title': 'Payment Confirmed',
        'message': msg,
        'whatsapp_link': _wa_link(order.phone, msg) if order.phone else '',
    }


def order_received(order, site=None) -> dict:
    items_text = '\n'.join(
        f'• {item.product_name} ×{item.quantity}'
        for item in order.items.all()
    )
    msg = (
        f"🎉 *Order Received!*\n\n"
        f"Hi {order.full_name}, your order *#{order.order_number}* has been received.\n\n"
        f"*Items ordered:*\n{items_text}\n\n"
        f"*Total:* ₦{order.total_amount:,.0f}\n\n"
        f"We will notify you as your order progresses. "
        f"You can also track your order in your Marina account.\n\n"
        f"Thank you for shopping with Marina Gadgets Kano! 🙏"
    )
    return {
        'title': 'Order Received',
        'message': msg,
        'whatsapp_link': _wa_link(order.phone, msg) if order.phone else '',
    }


def packaging_started(order, site=None) -> dict:
    msg = (
        f"📦 *Packaging Started*\n\n"
        f"Hi {order.full_name}, great news! We have started packaging your order "
        f"*#{order.order_number}*.\n\n"
        f"Your package will be sealed and ready for dispatch shortly.\n\n"
        f"Thank you for your patience! 🙏"
    )
    return {
        'title': 'Packaging Started',
        'message': msg,
        'whatsapp_link': _wa_link(order.phone, msg) if order.phone else '',
    }


def package_sealed(order, photo_url='', site=None) -> dict:
    photo_line = f'\n📸 View package photo: {photo_url}\n' if photo_url else ''
    msg = (
        f"✅ *Package Sealed!*\n\n"
        f"Hi {order.full_name}, your order *#{order.order_number}* has been "
        f"packaged and sealed.{photo_line}\n"
        f"Your package is now awaiting dispatch. We will notify you as soon as "
        f"it is on its way!\n\n"
        f"Thank you for choosing Marina Gadgets Kano! 🙏"
    )
    return {
        'title': 'Package Sealed',
        'message': msg,
        'whatsapp_link': _wa_link(order.phone, msg) if order.phone else '',
    }


def kano_dispatch(order, rider_name='', rider_phone='', site=None) -> dict:
    support_phone = site.support_phone if site else '0806 886 0972'
    support_email = site.support_email if site else 'support@marinagadgets.com'

    items_text = '\n'.join(
        f'• {item.product_name} ×{item.quantity}'
        for item in order.items.all()
    )
    rider_line = f'Dispatch Rider: *{rider_name}* — {rider_phone}\n' if rider_name or rider_phone else f'Rider Phone: *{rider_phone}*\n'

    msg = (
        f"🛵 *Your order is out for delivery!*\n\n"
        f"Hi {order.full_name}, your order *#{order.order_number}* is on its way to you.\n\n"
        f"*{rider_line}*"
        f"The rider will contact you shortly.\n\n"
        f"*Your package contains:*\n{items_text}\n\n"
        f"For enquiries or complaints:\n"
        f"📞 Phone: {support_phone}\n"
        f"📧 Email: {support_email}\n\n"
        f"Thank you for choosing Marina Gadgets Kano! 🙏"
    )
    return {
        'title': 'Out for Delivery',
        'message': msg,
        'whatsapp_link': _wa_link(order.phone, msg) if order.phone else '',
    }


def interstate_handover(order, driver_phone='', transport_company='', site=None) -> dict:
    business_name = site.business_name if site else 'Marina Gadgets Kano'
    support_phone = site.support_phone if site else '0806 886 0972'

    company_line = f'Transport Company: *{transport_company}*\n' if transport_company else ''
    msg = (
        f"🚛 *Your order has been handed over to a transport driver.*\n\n"
        f"Hi {order.full_name}, your order *#{order.order_number}* is on its way!\n\n"
        f"*Driver Phone Number:*\n{driver_phone}\n\n"
        f"{company_line}"
        f"The driver will contact you regarding your package and any applicable waybill fee.\n\n"
        f"For enquiries:\n"
        f"📞 {support_phone}\n\n"
        f"Thank you for choosing {business_name}. 🙏"
    )
    return {
        'title': 'Handed to Interstate Driver',
        'message': msg,
        'whatsapp_link': _wa_link(order.phone, msg) if order.phone else '',
    }


def delivery_confirm_request(order, site=None) -> dict:
    # Use production domain (configured or default)
    base_url = 'https://marinagadgets.com'
    yes_url = f"{base_url}/orders/{order.order_number}/confirm-delivery/yes/"
    no_url = f"{base_url}/orders/{order.order_number}/confirm-delivery/no/"
    
    msg = (
        f"📬 *Delivery Confirmation*\n\n"
        f"Hi {order.full_name}, we hope your order *#{order.order_number}* arrived safely!\n\n"
        f"*Have you received your order?*\n\n"
        f"Please click a link below to confirm:\n\n"
        f"✅ *YES, I received it:*\n{yes_url}\n\n"
        f"❌ *NO, I have issues:*\n{no_url}\n\n"
        f"Your feedback helps us serve you better. Thank you! 🙏"
    )
    return {
        'title': 'Delivery Confirmation Request',
        'message': msg,
        'whatsapp_link': _wa_link(order.phone, msg) if order.phone else '',
    }


def delivery_confirmed_satisfied(order, site=None) -> dict:
    business_name = site.business_name if site else 'Marina Gadgets Kano'
    msg = (
        f"🎉 *Thank you for your trust!*\n\n"
        f"Hi {order.full_name}, we are so glad your order arrived safely and you are happy "
        f"with your purchase!\n\n"
        f"We appreciate your trust in {business_name}. "
        f"Come back anytime — we have more great gadgets waiting for you! 😊\n\n"
        f"Don't forget to share your experience with friends and family. "
        f"See you again soon! 🙏"
    )
    return {
        'title': 'Thank You!',
        'message': msg,
        'whatsapp_link': _wa_link(order.phone, msg) if order.phone else '',
    }


def delivery_issue(order, site=None) -> dict:
    support_phone = site.support_phone if site else '0806 886 0972'
    msg = (
        f"⚠️ *Delivery Issue Reported*\n\n"
        f"Hi {order.full_name}, we are sorry to hear that there was an issue with your order "
        f"*#{order.order_number}*.\n\n"
        f"Please contact our customer care team immediately so we can resolve this for you:\n\n"
        f"📞 *{support_phone}*\n\n"
        f"Our team is standing by to help you. We will not rest until this is fully resolved. 🙏"
    )
    return {
        'title': 'Delivery Issue - Support Required',
        'message': msg,
        'whatsapp_link': _wa_link(order.phone, msg) if order.phone else '',
    }
