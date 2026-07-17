from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from django.db import models
from django.contrib.auth.models import User
from apps.core.models import SiteSettings
from apps.accounts.models import UserProfile
from apps.brands.models import Brand
from apps.catalog.models import Category, Product, ProductImage, ProductSpecification, ProductReview
from apps.cart.models import Cart, CartItem
from apps.wishlist.models import Wishlist, WishlistItem
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment
from apps.inventory.models import StockMovement, Supplier
from apps.homepage.models import Banner
from apps.feedback.models import Feedback
from apps.rewards.models import Reward
from apps.notifications.models import Notification


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'phone', 'category', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': "Tell us what's on your mind..."
            }),
            'subject': forms.TextInput(attrs={'placeholder': 'Brief summary of your feedback'}),
            'name': forms.TextInput(attrs={'placeholder': 'Your name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'your@email.com (optional)'}),
            'phone': forms.TextInput(attrs={'placeholder': '0801 234 5678 (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')


# ---------------------------------------------------------------------------
# Reward Form (staff)
# ---------------------------------------------------------------------------


class FeedbackStatusForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['status', 'staff_notes']
        widgets = {
            'staff_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs['class'] = 'form-input'


