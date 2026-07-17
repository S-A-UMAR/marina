from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class Banner(models.Model):
    TYPE_HERO = 'hero'
    TYPE_PROMO = 'promo'
    TYPE_ANNOUNCEMENT = 'announcement'
    TYPE_CHOICES = [
        (TYPE_HERO, 'Hero Banner'),
        (TYPE_PROMO, 'Promotional Banner'),
        (TYPE_ANNOUNCEMENT, 'Announcement'),
    ]

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    banner_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_HERO)
    image = models.ImageField(upload_to='banners/', blank=True, null=True)
    link_url = models.URLField(blank=True)
    link_text = models.CharField(max_length=100, blank=True, default='Shop Now')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f'{self.get_banner_type_display()}: {self.title}'


# ---------------------------------------------------------------------------
# Feedback — "Build Marina With Us"
# ---------------------------------------------------------------------------


