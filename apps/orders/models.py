from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class Order(models.Model):
    # Full Marina order lifecycle
    STATUS_PENDING = 'pending'
    STATUS_AWAITING_PAYMENT = 'awaiting_payment'
    STATUS_PAYMENT_VERIFIED = 'payment_verified'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_PROCESSING = 'processing'
    STATUS_PACKED = 'packed'
    STATUS_READY_DISPATCH = 'ready_dispatch'
    STATUS_DISPATCHED = 'dispatched'
    STATUS_IN_TRANSIT = 'in_transit'
    STATUS_DELIVERED = 'delivered'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_AWAITING_PAYMENT, 'Awaiting Payment'),
        (STATUS_PAYMENT_VERIFIED, 'Payment Verified'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_PACKED, 'Packed'),
        (STATUS_READY_DISPATCH, 'Ready for Dispatch'),
        (STATUS_DISPATCHED, 'Dispatched'),
        (STATUS_IN_TRANSIT, 'In Transit'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_FAILED, 'Failed'),
    ]

    # Checkout method
    METHOD_ONLINE = 'online'
    METHOD_WHATSAPP = 'whatsapp'
    METHOD_CALL = 'call'
    METHOD_CHOICES = [
        (METHOD_ONLINE, 'Online Payment (OPay)'),
        (METHOD_WHATSAPP, 'WhatsApp Assisted'),
        (METHOD_CALL, 'Request a Call'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    session_key = models.CharField(max_length=40, blank=True, null=True)
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    checkout_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default=METHOD_ONLINE)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.order_number}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = 'MRN' + uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status not in [self.STATUS_CANCELLED, self.STATUS_FAILED, self.STATUS_COMPLETED]

    STATUS_TIMELINE = [
        STATUS_PENDING,
        STATUS_AWAITING_PAYMENT,
        STATUS_PAYMENT_VERIFIED,
        STATUS_CONFIRMED,
        STATUS_PROCESSING,
        STATUS_PACKED,
        STATUS_READY_DISPATCH,
        STATUS_DISPATCHED,
        STATUS_IN_TRANSIT,
        STATUS_DELIVERED,
        STATUS_COMPLETED,
    ]

    def timeline_step(self):
        try:
            return self.STATUS_TIMELINE.index(self.status)
        except ValueError:
            return -1




class OrderItem(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.product_name}'

    @property
    def subtotal(self):
        return self.price * self.quantity


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------


