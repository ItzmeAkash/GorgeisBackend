from django.shortcuts import render
from rest_framework.response import Response
from products.models import Cart, CartItems, Order, Product
from products.seializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CreateOrderSerializer, OrderSerializer, ProductSerializer, UpdateCartItemSerializer
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin
# Create your views here.
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        """
        - List and retrieve operations are open to all.
        - Create, update, patch and delete operations require admin privileges.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]


class CartViewSet(CreateModelMixin,GenericViewSet,RetrieveModelMixin,DestroyModelMixin):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    
    
    
class CartItemsViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    def get_queryset(self): 
        return CartItems.objects.filter(cart_id=self.kwargs["cart_pk"])
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {"cart_id":self.kwargs["cart_pk"]}
    
    
    

class OrderViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerializer
        return OrderSerializer
        
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        
        return Order.objects.filter(owner=user)
    
    def get_serializer_context(self):
        return {"user_id":self.request.user.id}
    
    
    
