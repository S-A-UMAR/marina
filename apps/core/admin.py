from django.contrib import admin
from .models import SiteSettings, DeliverableCity, PickupLocation


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'email', 'phone', 'currency_symbol')
    fieldsets = (
        ('Business Information', {
            'fields': ('business_name', 'tagline', 'about_text', 'address', 'phone', 'support_phone', 'email', 'support_email', 'logo')
        }),
        ('Currency & Shipping', {
            'fields': ('currency_symbol', 'shipping_fee', 'free_shipping_threshold')
        }),
        ('Delivery Estimates (Display Text)', {
            'fields': ('delivery_estimate_kano', 'delivery_estimate_interstate'),
            'description': 'These are shown on the checkout page to inform customers — they are not added to the order total.'
        }),
        ('Homepage Hero', {
            'fields': ('hero_title', 'hero_subtitle')
        }),
        ('Social Links', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'whatsapp_url', 'whatsapp_number')
        }),
        ('WhatsApp Notifications', {
            'fields': ('whatsapp_provider', 'whatsapp_api_key', 'whatsapp_api_secret')
        }),
        ('SMS Notifications', {
            'fields': ('sms_provider', 'sms_api_key')
        }),
        ('Dashboard Settings', {
            'fields': ('notification_sound', 'dashboard_poll_interval', 'default_printer_name')
        }),
    )


class PickupLocationInline(admin.TabularInline):
    model = PickupLocation
    extra = 1
    fields = ('name', 'address', 'phone')


@admin.register(DeliverableCity)
class DeliverableCityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'is_active')
    list_filter = ('state', 'is_active')
    search_fields = ('name', 'state')
    list_editable = ('is_active',)
    inlines = [PickupLocationInline]


@admin.register(PickupLocation)
class PickupLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'phone')
    search_fields = ('name', 'address')
    list_filter = ('city__state',)
