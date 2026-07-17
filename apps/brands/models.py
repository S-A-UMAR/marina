from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class Brand(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def product_count(self):
        return self.products.filter(status=Product.STATUS_PUBLISHED).count()


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------


