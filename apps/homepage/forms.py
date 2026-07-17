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


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'subtitle', 'banner_type', 'image', 'link_url', 'link_text', 'is_active', 'order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        boolean_fields = ['is_active']
        for name, field in self.fields.items():
            if name not in boolean_fields:
                field.widget.attrs['class'] = 'form-input'


# ---------------------------------------------------------------------------
# Site Settings Form
# ---------------------------------------------------------------------------


