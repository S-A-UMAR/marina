from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class Reward(models.Model):
    TYPE_DISCOUNT = 'discount'
    TYPE_STORE_CREDIT = 'store_credit'
    TYPE_FREE_DELIVERY = 'free_delivery'
    TYPE_EXCLUSIVE_OFFER = 'exclusive_offer'
    TYPE_PRIORITY_SUPPORT = 'priority_support'
    TYPE_CHOICES = [
        (TYPE_DISCOUNT, 'Discount'),
        (TYPE_STORE_CREDIT, 'Store Credit'),
        (TYPE_FREE_DELIVERY, 'Free Delivery'),
        (TYPE_EXCLUSIVE_OFFER, 'Exclusive Offer'),
        (TYPE_PRIORITY_SUPPORT, 'Priority Support'),
    ]

    STATUS_ACTIVE = 'active'
    STATUS_REDEEMED = 'redeemed'
    STATUS_EXPIRED = 'expired'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_REDEEMED, 'Redeemed'),
        (STATUS_EXPIRED, 'Expired'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards')
    reward_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    reason = models.CharField(max_length=300)
    value = models.CharField(max_length=100, blank=True, help_text='e.g., 10% off, ₦500 credit')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='issued_rewards')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_reward_type_display()} for {self.user.username}'


# ---------------------------------------------------------------------------
# Notification
# ---------------------------------------------------------------------------


