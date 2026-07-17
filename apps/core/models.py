from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class SiteSettings(models.Model):
    business_name = models.CharField(max_length=200, default='Marina Gadgets Kano')
    tagline = models.CharField(max_length=300, blank=True, default='Premium Gadgets. Trusted Service.')
    about_text = models.TextField(blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    whatsapp_number = models.CharField(max_length=30, blank=True, help_text='Include country code, e.g. 2348012345678')
    email = models.EmailField(blank=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    currency_symbol = models.CharField(max_length=5, default='₦')
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=1500.00)
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=50000.00)
    hero_title = models.CharField(max_length=200, blank=True, default='Premium Gadgets for Every Need')
    hero_subtitle = models.CharField(max_length=300, blank=True, default='Trusted by thousands across Kano. Fast delivery, genuine products, real support.')
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    whatsapp_url = models.URLField(blank=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce singleton
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ---------------------------------------------------------------------------
# User Profile
# ---------------------------------------------------------------------------


