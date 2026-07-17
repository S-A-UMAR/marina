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


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_email', 'phone', 'address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'


# ---------------------------------------------------------------------------
# Checkout Form — supports 3 checkout methods
# ---------------------------------------------------------------------------


class StockInForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(status=Product.STATUS_PUBLISHED),
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Quantity to add'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Optional notes'})
    )




class StockOutForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(status=Product.STATUS_PUBLISHED, current_stock__gt=0),
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Quantity to remove'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 2})
    )

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        if product and quantity and quantity > product.current_stock:
            raise forms.ValidationError(
                f'Only {product.current_stock} units available for {product.name}.'
            )
        return cleaned_data


# ---------------------------------------------------------------------------
# Feedback Form — "Build Marina With Us"
# ---------------------------------------------------------------------------


