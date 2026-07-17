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


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'brand', 'category', 'condition',
            'short_description', 'description',
            'selling_price', 'previous_price',
            'current_stock', 'low_stock_threshold',
            'cover_image', 'status', 'is_featured', 'is_new_arrival',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'short_description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        boolean_fields = ['is_featured', 'is_new_arrival']
        for name, field in self.fields.items():
            if name not in boolean_fields:
                field.widget.attrs['class'] = 'form-input'
            else:
                field.widget.attrs['class'] = 'form-checkbox'




class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'logo', 'description', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'is_active':
                field.widget.attrs['class'] = 'form-input'




class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'is_active':
                field.widget.attrs['class'] = 'form-input'




class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-input'}),
            'comment': forms.Textarea(attrs={'class': 'form-input', 'rows': 4,
                                             'placeholder': 'Share your experience with this product...'}),
        }


# ---------------------------------------------------------------------------
# Stock Forms
# ---------------------------------------------------------------------------


