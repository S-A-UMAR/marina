from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class UserProfile(models.Model):
    ROLE_CUSTOMER = 'customer'
    ROLE_SALES = 'sales'
    ROLE_INVENTORY = 'inventory'
    ROLE_DISPATCH = 'dispatch'
    ROLE_SUPPORT = 'support'
    ROLE_MARKETING = 'marketing'
    ROLE_ADMIN = 'admin'
    ROLE_SUPERADMIN = 'superadmin'
    ROLE_CHOICES = [
        (ROLE_CUSTOMER, 'Customer'),
        (ROLE_SALES, 'Sales Staff'),
        (ROLE_INVENTORY, 'Inventory Staff'),
        (ROLE_DISPATCH, 'Dispatch Staff'),
        (ROLE_SUPPORT, 'Customer Support'),
        (ROLE_MARKETING, 'Marketing Staff'),
        (ROLE_ADMIN, 'Administrator'),
        (ROLE_SUPERADMIN, 'Super Administrator'),
    ]

    CONTACT_WHATSAPP = 'whatsapp'
    CONTACT_SMS = 'sms'
    CONTACT_CALL = 'call'
    CONTACT_CHOICES = [
        (CONTACT_WHATSAPP, 'WhatsApp'),
        (CONTACT_SMS, 'SMS'),
        (CONTACT_CALL, 'Phone Call'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    preferred_contact = models.CharField(max_length=20, choices=CONTACT_CHOICES, default=CONTACT_WHATSAPP)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} – {self.get_role_display()}'

    def is_staff_member(self):
        return self.role in [
            self.ROLE_SALES, self.ROLE_INVENTORY, self.ROLE_DISPATCH,
            self.ROLE_SUPPORT, self.ROLE_MARKETING, self.ROLE_ADMIN, self.ROLE_SUPERADMIN
        ]

    def is_admin(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_SUPERADMIN]

    # Legacy compatibility
    def is_staff_or_admin(self):
        return self.is_staff_member()


class OTPCode(models.Model):
    phone = models.CharField(max_length=30, db_index=True)
    otp_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP for {self.phone} (Verified: {self.is_verified})"



# ---------------------------------------------------------------------------
# Brand
# ---------------------------------------------------------------------------


