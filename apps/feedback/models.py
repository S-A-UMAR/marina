from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class Feedback(models.Model):
    CATEGORY_SUGGESTION = 'suggestion'
    CATEGORY_BUG = 'bug'
    CATEGORY_PRODUCT_REQUEST = 'product_request'
    CATEGORY_WEBSITE = 'website'
    CATEGORY_DELIVERY = 'delivery'
    CATEGORY_GENERAL = 'general'
    CATEGORY_CHOICES = [
        (CATEGORY_SUGGESTION, 'Suggestion'),
        (CATEGORY_BUG, 'Bug Report'),
        (CATEGORY_PRODUCT_REQUEST, 'Product Request'),
        (CATEGORY_WEBSITE, 'Website Feedback'),
        (CATEGORY_DELIVERY, 'Delivery Feedback'),
        (CATEGORY_GENERAL, 'General Feedback'),
    ]

    STATUS_RECEIVED = 'received'
    STATUS_REVIEW = 'under_review'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_IMPLEMENTED = 'implemented'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_RECEIVED, 'Received'),
        (STATUS_REVIEW, 'Under Review'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_IMPLEMENTED, 'Implemented'),
        (STATUS_CLOSED, 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks')
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default=CATEGORY_GENERAL)
    subject = models.CharField(max_length=300)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_RECEIVED)
    staff_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Feedback'

    def __str__(self):
        return f'[{self.get_category_display()}] {self.subject}'


# ---------------------------------------------------------------------------
# Reward — Marina Appreciation Rewards
# ---------------------------------------------------------------------------


