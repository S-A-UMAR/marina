from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist ({self.user.username})"

    @property
    def item_count(self):
        return self.items.count()




class WishlistItem(models.Model):
    wishlist = models.ForeignKey('wishlist.Wishlist', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('wishlist', 'product')

    def __str__(self):
        return f'{self.product.name} in {self.wishlist}'


# ---------------------------------------------------------------------------
# Order — Full Marina lifecycle
# ---------------------------------------------------------------------------


