from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class Payment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_REFUNDED = 'refunded'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_SUCCESS, 'Successful'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCELLED, 'Cancelled by User'),
        (STATUS_REFUNDED, 'Refunded'),
    ]

    GATEWAY_OPAY = 'opay'
    GATEWAY_PAYSTACK = 'paystack'
    GATEWAY_OFFLINE = 'offline'
    GATEWAY_CHOICES = [
        (GATEWAY_OPAY, 'OPay'),
        (GATEWAY_PAYSTACK, 'Paystack'),
        (GATEWAY_OFFLINE, 'Offline'),
    ]

    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='payment')
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES, default=GATEWAY_PAYSTACK)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    gateway_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Payment {self.reference} – {self.status}'


# ---------------------------------------------------------------------------
# Stock Movement
# ---------------------------------------------------------------------------


