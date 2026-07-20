import uuid
import urllib.parse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings

from apps.core.models import SiteSettings, DeliverableCity, PickupLocation
from apps.core.utils import get_cart
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment


NIGERIAN_STATES = [
    'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue',
    'Borno', 'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu',
    'FCT - Abuja', 'Gombe', 'Imo', 'Jigawa', 'Kaduna', 'Kano', 'Katsina',
    'Kebbi', 'Kogi', 'Kwara', 'Lagos', 'Nasarawa', 'Niger', 'Ogun', 'Ondo',
    'Osun', 'Oyo', 'Plateau', 'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara',
]


@login_required(login_url='/auth/login/')
def checkout(request):
    """
    Overhauled 3-step checkout:
    Step 1: Customer details + State > City > (Address or Pickup Point).
    Step 2: Payment method selection.
    """
    cart = get_cart(request)
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('store:home')

    settings_obj = SiteSettings.get()
    subtotal = cart.total
    total = subtotal  # No shipping fee in total — customer pays rider separately

    # Pre-fill from user profile
    profile = getattr(request.user, 'profile', None)
    # Populate form_data. If POST fails validation, we merge the POST data.
    form_data = {
        'full_name': request.POST.get('full_name', '').strip() if request.method == 'POST' else (request.user.get_full_name() or ''),
        'phone': request.POST.get('phone', '').strip() if request.method == 'POST' else (profile.phone if profile else ''),
        'email': request.POST.get('email', '').strip() if request.method == 'POST' else request.user.email,
        'state': request.POST.get('state', '').strip() if request.method == 'POST' else (profile.state if profile else ''),
        'city': request.POST.get('city', '').strip() if request.method == 'POST' else (profile.city if profile else ''),
        'address': request.POST.get('address', '').strip() if request.method == 'POST' else (profile.address if profile else ''),
        'notes': request.POST.get('notes', '').strip() if request.method == 'POST' else '',
        'delivery_mode': request.POST.get('delivery_mode', Order.DELIVERY_MODE_HOME) if request.method == 'POST' else Order.DELIVERY_MODE_HOME,
        'pickup_location': request.POST.get('pickup_location', '') if request.method == 'POST' else '',
    }

    if request.method == 'POST':
        # Collect form data
        full_name = form_data['full_name']
        phone = form_data['phone']
        email = form_data['email']
        state = form_data['state']
        city_name = form_data['city']
        checkout_method = request.POST.get('checkout_method', Order.METHOD_ONLINE)
        notes = form_data['notes']
        delivery_mode = form_data['delivery_mode']
        pickup_location_id = form_data['pickup_location']
        address = form_data['address']

        # Validate
        errors = []
        if not full_name:
            errors.append('Full name is required.')
        if not phone:
            errors.append('Phone number is required.')
        if not state:
            errors.append('Please select your state.')
        if not city_name:
            errors.append('Please select your city.')

        is_kano = state.lower() == 'kano'
        if is_kano and delivery_mode == Order.DELIVERY_MODE_HOME and not address:
            errors.append('Please enter your delivery address for home delivery.')
        if not is_kano and delivery_mode == Order.DELIVERY_MODE_PICKUP and not pickup_location_id:
            errors.append('Please select a pickup location.')

        if errors:
            for e in errors:
                messages.error(request, e)
            context = _checkout_context(settings_obj, cart, subtotal, total, form_data)
            return render(request, 'orders/checkout.html', context)

        # Recompute total server-side (security: don't trust client-side values)
        subtotal = sum(item.product.effective_price * item.quantity for item in cart.items.select_related('product'))
        total = subtotal

        # Determine pickup location FK
        pickup_obj = None
        if pickup_location_id:
            try:
                pickup_obj = PickupLocation.objects.get(id=pickup_location_id)
            except PickupLocation.DoesNotExist:
                pass

        # Create order
        order = Order.objects.create(
            user=request.user,
            status=Order.STATUS_RECEIVED,
            checkout_method=checkout_method,
            delivery_mode=delivery_mode,
            pickup_location=pickup_obj,
            full_name=full_name,
            phone=phone,
            email=email,
            address=address,
            city=city_name,
            state=state,
            subtotal=subtotal,
            shipping_fee=0,
            total_amount=total,
            notes=notes,
        )

        # Create order items and deduct stock
        for item in cart.items.select_related('product'):
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                quantity=item.quantity,
                price=item.product.effective_price,
            )
            # Deduct stock
            product = item.product
            product.current_stock = max(0, product.current_stock - item.quantity)
            product.save(update_fields=['current_stock'])

        # Clear cart
        cart.items.all().delete()

        # Route by payment method
        if checkout_method == Order.METHOD_WHATSAPP:
            return redirect('store:whatsapp_checkout', order_number=order.order_number)
        elif checkout_method == Order.METHOD_CALL:
            return redirect('store:request_call', order_number=order.order_number)
        else:
            # Paystack
            reference = 'MRN_' + uuid.uuid4().hex[:10].upper()
            Payment.objects.create(
                order=order,
                reference=reference,
                amount=total,
                gateway=Payment.GATEWAY_PAYSTACK,
            )
            return render(request, 'payments/initiate.html', {
                'order': order,
                'reference': reference,
                'amount_kobo': int(total * 100),
                'paystack_public_key': getattr(settings, 'PAYSTACK_PUBLIC_KEY', ''),
                'email': order.email or request.user.email,
            })

    context = _checkout_context(settings_obj, cart, subtotal, total, form_data)
    return render(request, 'orders/checkout.html', context)


def _checkout_context(settings_obj, cart, subtotal, total, form_data):
    return {
        'cart': cart,
        'subtotal': subtotal,
        'total': total,
        'states': NIGERIAN_STATES,
        'form_data': form_data,
        'site_settings': settings_obj,
        'delivery_estimate_kano': settings_obj.delivery_estimate_kano,
        'delivery_estimate_interstate': settings_obj.delivery_estimate_interstate,
    }



def whatsapp_checkout(request, order_number):
    """Generate WhatsApp pre-filled message."""
    order = get_object_or_404(Order, order_number=order_number)
    settings_obj = SiteSettings.get()
    whatsapp_number = settings_obj.whatsapp_number or getattr(settings, 'MARINA_WHATSAPP_NUMBER', '')

    items_text = '\n'.join(
        [f'• {item.quantity}x {item.product_name} — ₦{item.price:,.0f}' for item in order.items.all()]
    )
    delivery_info = (
        f"Home Delivery ({order.city}, {order.state})\nAddress: {order.address}"
        if order.delivery_mode == Order.DELIVERY_MODE_HOME
        else f"Pickup Point: {order.pickup_location.name if order.pickup_location else 'TBD'} ({order.city}, {order.state})"
    )
    message = (
        f"Hello Marina! I'd like to complete my order.\n\n"
        f"*Order Ref:* {order.order_number}\n"
        f"*Name:* {order.full_name}\n"
        f"*Phone:* {order.phone}\n"
        f"*Delivery:* {delivery_info}\n\n"
        f"*Items:*\n{items_text}\n\n"
        f"*Items Total:* ₦{order.total_amount:,.0f}\n\n"
        f"Please confirm and advise on payment."
    )
    whatsapp_url = f"https://wa.me/{whatsapp_number}?text={urllib.parse.quote(message)}"
    return render(request, 'orders/whatsapp_checkout.html', {
        'order': order,
        'whatsapp_url': whatsapp_url,
        'whatsapp_number': whatsapp_number,
    })


def request_call(request, order_number):
    """Request-a-call confirmation page."""
    order = get_object_or_404(Order, order_number=order_number)
    order.status = Order.STATUS_RECEIVED
    order.save(update_fields=['status'])
    return render(request, 'orders/request_call.html', {'order': order})
