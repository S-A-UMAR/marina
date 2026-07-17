from django.contrib import admin
from .models import Supplier, StockMovement

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'phone')
    search_fields = ('name', 'contact_email')

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'movement_type', 'quantity_change', 'performed_by', 'date')
    list_filter = ('movement_type', 'date')
    search_fields = ('product__name', 'notes')
