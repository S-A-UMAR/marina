from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    CHANNEL_WHATSAPP = 'whatsapp'
    CHANNEL_SMS      = 'sms'
    CHANNEL_IN_APP   = 'in_app'
    CHANNEL_CHOICES = [
        (CHANNEL_WHATSAPP, 'WhatsApp'),
        (CHANNEL_SMS,      'SMS'),
        (CHANNEL_IN_APP,   'In-App'),
    ]

    EVENT_OTP                   = 'otp'
    EVENT_ORDER_RECEIVED        = 'order_received'
    EVENT_PAYMENT_CONFIRMED     = 'payment_confirmed'
    EVENT_PACKAGING_STARTED     = 'packaging_started'
    EVENT_PACKING               = 'packing'
    EVENT_PACKAGE_PHOTO         = 'package_photo'
    EVENT_AWAITING_DISPATCH     = 'awaiting_dispatch'
    EVENT_KANO_DISPATCH         = 'kano_dispatch'
    EVENT_INTERSTATE_HANDOVER   = 'interstate_handover'
    EVENT_DISPATCH              = 'dispatch'
    EVENT_DELIVERED             = 'delivered'
    EVENT_DELIVERY_CONFIRM_REQ  = 'delivery_confirm_request'
    EVENT_DELIVERY_CONFIRMED    = 'delivery_confirmed'
    EVENT_DELIVERY_ISSUE        = 'delivery_issue'
    EVENT_FEEDBACK              = 'feedback'
    EVENT_REWARD                = 'reward'
    EVENT_GENERAL               = 'general'

    EVENT_CHOICES = [
        (EVENT_OTP,                 'OTP'),
        (EVENT_ORDER_RECEIVED,      'Order Received'),
        (EVENT_PAYMENT_CONFIRMED,   'Payment Confirmed'),
        (EVENT_PACKAGING_STARTED,   'Packaging Started'),
        (EVENT_PACKING,             'Packing Complete'),
        (EVENT_PACKAGE_PHOTO,       'Package Photo Sent'),
        (EVENT_AWAITING_DISPATCH,   'Awaiting Dispatch'),
        (EVENT_KANO_DISPATCH,       'Kano Dispatch'),
        (EVENT_INTERSTATE_HANDOVER, 'Interstate Handover'),
        (EVENT_DISPATCH,            'Dispatch Update'),
        (EVENT_DELIVERED,           'Delivery Completed'),
        (EVENT_DELIVERY_CONFIRM_REQ,'Delivery Confirmation Request'),
        (EVENT_DELIVERY_CONFIRMED,  'Delivery Confirmed'),
        (EVENT_DELIVERY_ISSUE,      'Delivery Issue Reported'),
        (EVENT_FEEDBACK,            'Feedback Update'),
        (EVENT_REWARD,              'Reward Issued'),
        (EVENT_GENERAL,             'General'),
    ]

    STATUS_SENT    = 'sent'
    STATUS_FAILED  = 'failed'
    STATUS_PENDING = 'pending'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SENT,    'Sent'),
        (STATUS_FAILED,  'Failed'),
    ]

    user               = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    order              = models.ForeignKey(
        'orders.Order', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='notifications'
    )
    channel            = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_IN_APP)
    event_type         = models.CharField(max_length=30, choices=EVENT_CHOICES, default=EVENT_GENERAL)
    title              = models.CharField(max_length=200)
    message            = models.TextField()
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SENT)
    is_read            = models.BooleanField(default=False)
    whatsapp_link      = models.URLField(blank=True, help_text='Pre-filled wa.me link for manual sending')
    created_at         = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_event_type_display()} → {self.user.username}'
