from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products.views import ProductViewSet

# Create a router and register our viewset with it
router = DefaultRouter()
router.register('', ProductViewSet,basename='product')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]

# This will generate the following URLs:
# GET /products/ - List all products (everyone can access)
# GET /products/{slug}/ - Get a specific product (everyone can access)
# POST /products/ - Create a new product (admin only)
# PUT/PATCH /products/{slug}/ - Update a product (admin only)
# DELETE /products/{slug}/ - Delete a product (admin only)