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


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            'business_name', 'tagline', 'about_text', 'address', 'phone', 'whatsapp_number',
            'email', 'logo', 'currency_symbol', 'shipping_fee', 'free_shipping_threshold',
            'hero_title', 'hero_subtitle',
            'facebook_url', 'instagram_url', 'twitter_url', 'whatsapp_url'
        ]
        widgets = {
            'about_text': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'


# ---------------------------------------------------------------------------
# Dashboard User Form
# ---------------------------------------------------------------------------


