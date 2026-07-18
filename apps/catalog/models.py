from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid


class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=100, blank=True, default='fa-solid fa-microchip',
        help_text='FontAwesome class e.g. fa-solid fa-laptop'
    )
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='subcategories',
        help_text='Leave blank for top-level category. Select parent to make this a subcategory.'
    )
    sort_order = models.PositiveIntegerField(default=0, help_text='Lower = appears first')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']

    def __str__(self):
        if self.parent:
            return f'{self.parent.name} → {self.name}'
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def product_count(self):
        return self.products.filter(status=Product.STATUS_PUBLISHED).count()

    @property
    def is_subcategory(self):
        return self.parent is not None

    @property
    def top_level(self):
        return self.parent if self.parent else self


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------


class Product(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_HIDDEN = 'hidden'
    STATUS_ARCHIVED = 'archived'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_HIDDEN, 'Hidden'),
        (STATUS_ARCHIVED, 'Archived'),
    ]

    CONDITION_NEW = 'new'
    CONDITION_UK_USED = 'uk_used'
    CONDITION_REFURBISHED = 'refurbished'
    CONDITION_CHOICES = [
        (CONDITION_NEW, 'New'),
        (CONDITION_UK_USED, 'UK Used'),
        (CONDITION_REFURBISHED, 'Refurbished'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    sku = models.CharField(max_length=100, blank=True)
    brand = models.ForeignKey(
        'brands.Brand', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products'
    )
    category = models.ForeignKey(
        'catalog.Category', on_delete=models.SET_NULL, null=True,
        related_name='products',
        help_text='Select a subcategory if available'
    )
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default=CONDITION_NEW)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    previous_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cover_image = models.ImageField(upload_to='products/', blank=True, null=True)
    current_stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            n = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def effective_price(self):
        return self.selling_price

    @property
    def discount_percent(self):
        if self.previous_price and self.previous_price > self.selling_price:
            return int(((self.previous_price - self.selling_price) / self.previous_price) * 100)
        return 0

    @property
    def is_discounted(self):
        return bool(self.previous_price and self.previous_price > self.selling_price)

    @property
    def in_stock(self):
        return self.current_stock > 0

    @property
    def is_low_stock(self):
        return 0 < self.current_stock <= self.low_stock_threshold

    @property
    def out_of_stock(self):
        return self.current_stock == 0

    @property
    def is_active(self):
        return self.status == self.STATUS_PUBLISHED


class ProductImage(models.Model):
    product = models.ForeignKey(
        'catalog.Product', on_delete=models.CASCADE, related_name='gallery_images',
        null=True, blank=True
    )
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_cover = models.BooleanField(default=False, help_text='Use as cover/primary image')
    session_token = models.CharField(max_length=100, blank=True, db_index=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        if self.product:
            return f'Image for {self.product.name}'
        return f'Temp Image ({self.session_token})'


class ProductVideo(models.Model):
    """Short product demo/unboxing videos."""
    product = models.ForeignKey(
        'catalog.Product', on_delete=models.CASCADE, related_name='videos',
        null=True, blank=True
    )
    video = models.FileField(upload_to='products/videos/')
    title = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    session_token = models.CharField(max_length=100, blank=True, db_index=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        if self.product:
            return f'Video for {self.product.name}'
        return f'Temp Video ({self.session_token})'


class ProductSpecification(models.Model):
    product = models.ForeignKey(
        'catalog.Product', on_delete=models.CASCADE, related_name='specifications'
    )
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.product.name}: {self.key} = {self.value}'


class ProductReview(models.Model):
    product = models.ForeignKey(
        'catalog.Product', on_delete=models.CASCADE, related_name='reviews'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f'{self.user.username} – {self.product.name} ({self.rating}/5)'
