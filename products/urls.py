from codecs import lookup
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products.views import CartItemsViewSet, CartViewSet, OrderViewSet, ProductViewSet
from rest_framework_nested import routers

# Create a router and register our viewset with it
router = DefaultRouter()
router.register('products', ProductViewSet,basename='product')
router.register('carts',CartViewSet,basename='cart')
router.register('orders', OrderViewSet,basename='orders')
#Nested Router
cart_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
cart_router.register("items",CartItemsViewSet,basename='cart-items')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('', include(cart_router.urls)),
]

# This will generate the following URLs:
# GET /products/ - List all products (everyone can access)
# GET /products/{slug}/ - Get a specific product (everyone can access)
# POST /products/ - Create a new product (admin only)
# PUT/PATCH /products/{slug}/ - Update a product (admin only)
# DELETE /products/{slug}/ - Delete a product (admin only)