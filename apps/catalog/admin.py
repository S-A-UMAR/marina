from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVideo, ProductReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_cover', 'order')
    readonly_fields = ()

    def get_queryset(self, request):
        return super().get_queryset(request).filter(session_token='')


class ProductVideoInline(admin.TabularInline):
    model = ProductVideo
    extra = 1
    fields = ('video', 'title', 'order')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(session_token='')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'selling_price', 'previous_price', 'current_stock', 'is_featured', 'status')
    list_filter = ('is_featured', 'status', 'category')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVideoInline]


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
