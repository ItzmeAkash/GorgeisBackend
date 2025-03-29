from django.db import models
from django.utils.text import slugify
from .utils import generate_unique_slug

class Product(models.Model):
    productname = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, null=True)
    productimage = models.ImageField()
    packtitle = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    originalprice = models.DecimalField(max_digits=10, decimal_places=2)
    discountPercentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Discount percentage (0-100)"
    )
    discountPrice = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Calculated discounted price"
    )
    stock = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
    
    def save(self, *args, **kwargs):
        # Generate a basic slug from the product name
        if not self.slug:
            base_slug = slugify(self.productname)
            # Now encrypt it
            self.slug = generate_unique_slug(Product, base_slug)
        # For existing products being updated
        elif not self.id:
            base_slug = slugify(self.productname)
            self.slug = generate_unique_slug(Product, base_slug, self.id)
            
        # Calculate and set discountPrice before saving
        if self.discountPercentage > 0:
            discount = self.originalprice * (self.discountPercentage / 100)
            self.discountPrice = round(self.originalprice - discount, 2)
        else:
            self.discountPrice = self.originalprice
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.productname
    
    # Optional: Calculate the discount amount
    @property
    def discountAmount(self):
        """Calculate the amount saved"""
        if self.discountPercentage > 0:
            return round(self.originalprice - self.discountPrice, 2)
        return 0.00