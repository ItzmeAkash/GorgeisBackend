from django.contrib import admin

from products.models import Cart, CartItems, Order, OrderItem, Product

# Register your models here.
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItems)
admin.site.register(Order)
admin.site.register(OrderItem)