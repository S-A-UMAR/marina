from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


# ---------------------------------------------------------------------------
# Order
# ---------------------------------------------------------------------------

class Order(models.Model):
    # Full Marina order lifecycle
    STATUS_PENDING              = 'pending'
    STATUS_AWAITING_PAYMENT     = 'awaiting_payment'
    STATUS_PAYMENT_VERIFIED     = 'payment_verified'
    STATUS_CONFIRMED            = 'confirmed'
    STATUS_PENDING_PACKAGING    = 'pending_packaging'
    STATUS_PACKAGING            = 'packaging'
    STATUS_PACKED               = 'packed'
    STATUS_AWAITING_DISPATCH    = 'awaiting_dispatch'
    STATUS_DISPATCHED           = 'dispatched'
    STATUS_IN_TRANSIT           = 'in_transit'
    STATUS_DELIVERED            = 'delivered'
    STATUS_COMPLETED            = 'completed'
    STATUS_CANCELLED            = 'cancelled'
    STATUS_FAILED               = 'failed'
    STATUS_REFUNDED             = 'refunded'
    STATUS_RETURNED             = 'returned'
    STATUS_DELIVERY_FAILED      = 'delivery_failed'
    STATUS_ON_HOLD              = 'on_hold'
    STATUS_AWAITING_RESPONSE    = 'awaiting_response'

    STATUS_CHOICES = [
        (STATUS_PENDING,            'Pending'),
        (STATUS_AWAITING_PAYMENT,   'Awaiting Payment'),
        (STATUS_PAYMENT_VERIFIED,   'Payment Verified'),
        (STATUS_CONFIRMED,          'Confirmed'),
        (STATUS_PENDING_PACKAGING,  'Pending Packaging'),
        (STATUS_PACKAGING,          'Packaging In Progress'),
        (STATUS_PACKED,             'Packed'),
        (STATUS_AWAITING_DISPATCH,  'Awaiting Dispatch'),
        (STATUS_DISPATCHED,         'Dispatched'),
        (STATUS_IN_TRANSIT,         'In Transit'),
        (STATUS_DELIVERED,          'Delivered'),
        (STATUS_COMPLETED,          'Completed'),
        (STATUS_CANCELLED,          'Cancelled'),
        (STATUS_FAILED,             'Failed'),
        (STATUS_REFUNDED,           'Refunded'),
        (STATUS_RETURNED,           'Returned'),
        (STATUS_DELIVERY_FAILED,    'Delivery Failed'),
        (STATUS_ON_HOLD,            'On Hold'),
        (STATUS_AWAITING_RESPONSE,  'Awaiting Customer Response'),
    ]

    # Delivery type
    DELIVERY_KANO       = 'kano'
    DELIVERY_INTERSTATE = 'interstate'
    DELIVERY_PICKUP     = 'pickup'
    DELIVERY_CHOICES = [
        (DELIVERY_KANO,       'Kano Delivery'),
        (DELIVERY_INTERSTATE, 'Interstate Delivery'),
        (DELIVERY_PICKUP,     'Shop Pickup'),
    ]

    # Checkout method
    METHOD_ONLINE   = 'online'
    METHOD_WHATSAPP = 'whatsapp'
    METHOD_CALL     = 'call'
    METHOD_CHOICES = [
        (METHOD_ONLINE,   'Online Payment (Paystack)'),
        (METHOD_WHATSAPP, 'WhatsApp Assisted'),
        (METHOD_CALL,     'Request a Call'),
    ]

    user             = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    session_key      = models.CharField(max_length=40, blank=True, null=True)
    order_number     = models.CharField(max_length=20, unique=True, blank=True, db_index=True)
    status           = models.CharField(max_length=25, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    checkout_method  = models.CharField(max_length=20, choices=METHOD_CHOICES, default=METHOD_ONLINE)
    delivery_type    = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default=DELIVERY_KANO, blank=True)
    full_name        = models.CharField(max_length=200)
    phone            = models.CharField(max_length=20)
    email            = models.EmailField(blank=True)
    address          = models.TextField(blank=True)
    city             = models.CharField(max_length=100, blank=True)
    state            = models.CharField(max_length=100, blank=True)
    subtotal         = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_fee     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes            = models.TextField(blank=True)
    is_new           = models.BooleanField(default=True, help_text='True until staff opens the order')
    notifications_enabled = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

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
        return self.status not in [
            self.STATUS_CANCELLED, self.STATUS_FAILED,
            self.STATUS_COMPLETED, self.STATUS_REFUNDED
        ]

    # Visual timeline for My Marina customer view
    STATUS_TIMELINE = [
        STATUS_PENDING,
        STATUS_AWAITING_PAYMENT,
        STATUS_PAYMENT_VERIFIED,
        STATUS_CONFIRMED,
        STATUS_PENDING_PACKAGING,
        STATUS_PACKAGING,
        STATUS_PACKED,
        STATUS_AWAITING_DISPATCH,
        STATUS_DISPATCHED,
        STATUS_IN_TRANSIT,
        STATUS_DELIVERED,
        STATUS_COMPLETED,
    ]

    STATUS_TIMELINE_LABELS = {
        STATUS_PENDING:             ('fa-clock', 'Order Placed'),
        STATUS_AWAITING_PAYMENT:    ('fa-credit-card', 'Awaiting Payment'),
        STATUS_PAYMENT_VERIFIED:    ('fa-circle-check', 'Payment Confirmed'),
        STATUS_CONFIRMED:           ('fa-thumbs-up', 'Order Confirmed'),
        STATUS_PENDING_PACKAGING:   ('fa-box', 'Preparing to Package'),
        STATUS_PACKAGING:           ('fa-box-open', 'Packaging In Progress'),
        STATUS_PACKED:              ('fa-box-archive', 'Package Sealed'),
        STATUS_AWAITING_DISPATCH:   ('fa-warehouse', 'Awaiting Dispatch'),
        STATUS_DISPATCHED:          ('fa-truck', 'Dispatched'),
        STATUS_IN_TRANSIT:          ('fa-truck-fast', 'In Transit'),
        STATUS_DELIVERED:           ('fa-house-circle-check', 'Delivered'),
        STATUS_COMPLETED:           ('fa-star', 'Completed'),
    }

    def timeline_step(self):
        try:
            return self.STATUS_TIMELINE.index(self.status)
        except ValueError:
            return -1

    def get_timeline_data(self):
        """Returns list of (status, label, icon, is_done) for template rendering."""
        current_step = self.timeline_step()
        result = []
        for i, s in enumerate(self.STATUS_TIMELINE):
            icon, label = self.STATUS_TIMELINE_LABELS.get(s, ('fa-circle', s))
            result.append({
                'status': s,
                'label': label,
                'icon': icon,
                'is_done': i <= current_step,
                'is_current': i == current_step,
            })
        return result

    def log_status_change(self, new_status, changed_by=None, note=''):
        """Record a status change in the audit trail."""
        OrderStatusHistory.objects.create(
            order=self,
            old_status=self.status,
            new_status=new_status,
            changed_by=changed_by,
            note=note,
        )
        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])


# ---------------------------------------------------------------------------
# Order Item
# ---------------------------------------------------------------------------

class OrderItem(models.Model):
    order        = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='items')
    product      = models.ForeignKey('catalog.Product', on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255)
    quantity     = models.PositiveIntegerField()
    price        = models.DecimalField(max_digits=12, decimal_places=2)
    is_packed    = models.BooleanField(default=False, help_text='Staff checks off during packaging')

    def __str__(self):
        return f'{self.quantity} x {self.product_name}'

    @property
    def subtotal(self):
        return self.price * self.quantity


# ---------------------------------------------------------------------------
# Order Status History (Audit Trail)
# ---------------------------------------------------------------------------

class OrderStatusHistory(models.Model):
    order       = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='history')
    old_status  = models.CharField(max_length=25, blank=True)
    new_status  = models.CharField(max_length=25)
    changed_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    note        = models.TextField(blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'#{self.order.order_number}: {self.old_status} → {self.new_status}'


# ---------------------------------------------------------------------------
# Package Photo
# ---------------------------------------------------------------------------

class PackagePhoto(models.Model):
    order       = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='package_photo')
    photo       = models.ImageField(upload_to='packages/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    note        = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f'Package photo for #{self.order.order_number}'


# ---------------------------------------------------------------------------
# Dispatch Rider (saved riders for Kano deliveries)
# ---------------------------------------------------------------------------

class DispatchRider(models.Model):
    name      = models.CharField(max_length=150)
    phone     = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    added_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.phone})'


# ---------------------------------------------------------------------------
# Dispatch Batch
# ---------------------------------------------------------------------------

class DispatchBatch(models.Model):
    STATUS_PREPARED  = 'prepared'
    STATUS_SENT      = 'sent'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_PREPARED,  'Prepared'),
        (STATUS_SENT,      'Sent to Park'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    batch_number = models.CharField(max_length=30, unique=True, blank=True)
    rider        = models.ForeignKey(DispatchRider, on_delete=models.SET_NULL, null=True, blank=True)
    rider_name   = models.CharField(max_length=150, blank=True)   # manual entry fallback
    rider_phone  = models.CharField(max_length=20, blank=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PREPARED)
    created_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    notes        = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.batch_number

    def save(self, *args, **kwargs):
        if not self.batch_number:
            today = timezone.now().strftime('%Y%m%d')
            count = DispatchBatch.objects.filter(batch_number__startswith=f'MB-{today}').count() + 1
            self.batch_number = f'MB-{today}-{count:03d}'
        super().save(*args, **kwargs)

    @property
    def order_count(self):
        return self.batch_items.count()

    @property
    def states_included(self):
        return list(
            self.batch_items.values_list('order__state', flat=True).distinct()
        )


class DispatchBatchItem(models.Model):
    batch = models.ForeignKey(DispatchBatch, on_delete=models.CASCADE, related_name='batch_items')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='dispatch_batches')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('batch', 'order')

    def __str__(self):
        return f'{self.batch.batch_number} → #{self.order.order_number}'


# ---------------------------------------------------------------------------
# Interstate Dispatch (driver info per state within a batch)
# ---------------------------------------------------------------------------

class InterstateDispatch(models.Model):
    batch              = models.ForeignKey(DispatchBatch, on_delete=models.CASCADE, related_name='interstate_dispatches')
    state              = models.CharField(max_length=100)
    driver_name        = models.CharField(max_length=150, blank=True)
    driver_phone       = models.CharField(max_length=20)
    transport_company  = models.CharField(max_length=200, blank=True)
    plate_number       = models.CharField(max_length=20, blank=True)
    customer_notified  = models.BooleanField(default=False)
    notified_at        = models.DateTimeField(null=True, blank=True)
    created_at         = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('batch', 'state')
        ordering = ['state']

    def __str__(self):
        return f'{self.batch.batch_number} → {self.state} (Driver: {self.driver_phone})'
