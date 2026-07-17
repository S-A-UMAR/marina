from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class Notification(models.Model):
    CHANNEL_WHATSAPP = 'whatsapp'
    CHANNEL_SMS = 'sms'
    CHANNEL_IN_APP = 'in_app'
    CHANNEL_CHOICES = [
        (CHANNEL_WHATSAPP, 'WhatsApp'),
        (CHANNEL_SMS, 'SMS'),
        (CHANNEL_IN_APP, 'In-App'),
    ]

    EVENT_OTP = 'otp'
    EVENT_ORDER_RECEIVED = 'order_received'
    EVENT_PAYMENT_CONFIRMED = 'payment_confirmed'
    EVENT_PACKING = 'packing'
    EVENT_DISPATCH = 'dispatch'
    EVENT_DELIVERED = 'delivered'
    EVENT_FEEDBACK = 'feedback'
    EVENT_REWARD = 'reward'
    EVENT_GENERAL = 'general'
    EVENT_CHOICES = [
        (EVENT_OTP, 'OTP'),
        (EVENT_ORDER_RECEIVED, 'Order Received'),
        (EVENT_PAYMENT_CONFIRMED, 'Payment Confirmed'),
        (EVENT_PACKING, 'Packing Complete'),
        (EVENT_DISPATCH, 'Dispatch Update'),
        (EVENT_DELIVERED, 'Delivery Completed'),
        (EVENT_FEEDBACK, 'Feedback Update'),
        (EVENT_REWARD, 'Reward Issued'),
        (EVENT_GENERAL, 'General'),
    ]

    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_PENDING = 'pending'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_IN_APP)
    event_type = models.CharField(max_length=30, choices=EVENT_CHOICES, default=EVENT_GENERAL)
    title = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SENT)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_event_type_display()} → {self.user.username}'


# ---------------------------------------------------------------------------
# Supplier (kept for inventory management)
# ---------------------------------------------------------------------------


