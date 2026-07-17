from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class StockMovement(models.Model):
    TYPE_IN = 'IN'
    TYPE_OUT = 'OUT'
    TYPE_ADJUST = 'ADJUST'
    TYPE_CHOICES = [
        (TYPE_IN, 'Stock In'),
        (TYPE_OUT, 'Stock Out'),
        (TYPE_ADJUST, 'Adjustment'),
    ]

    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantity_change = models.IntegerField()
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        direction = '+' if self.quantity_change >= 0 else ''
        return f'{self.product.name}: {direction}{self.quantity_change} ({self.movement_type})'


# ---------------------------------------------------------------------------
# Banner / Hero Banner (homepage management)
# ---------------------------------------------------------------------------


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


