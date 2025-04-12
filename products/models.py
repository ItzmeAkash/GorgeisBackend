from statistics import mode
import uuid
from django.conf import settings
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
    
class Cart(models.Model):
    id = models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    
class CartItems(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", blank=True, null=True, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True, related_name="cartitems", db_index=True)
    quantity = models.PositiveSmallIntegerField(default=0)
    
    
    def __str__(self):
        return f"{self.quantity} x {self.product.productname} in cart {self.cart.id}"
    
    
class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILD = 'F'
    
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Completed'),
        (PAYMENT_STATUS_FAILD, 'Failed'),
    ]
    placed_at = models.DateTimeField(auto_now_add=True)
    pending_status = models.CharField(
        max_length=50,
        choices=PAYMENT_STATUS_CHOICES,
        default='PAYMENT_STATUS_PENDING',
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    def __str__(self):
        return self.pending_status
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, )
    quantity = models.PositiveSmallIntegerField()
    
    def __str__(self):
        return self.product.productname