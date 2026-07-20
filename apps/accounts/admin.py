from django.contrib import admin
from .models import UserProfile, OTPCode


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone')


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ('phone', 'created_at', 'expires_at', 'attempts', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('phone',)
    readonly_fields = ('otp_hash', 'created_at')
