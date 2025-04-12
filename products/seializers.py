from dataclasses import fields
from rest_framework import serializers
from .models import Cart, CartItems, Order, OrderItem, Product
from django.db import transaction

class ProductSerializer(serializers.ModelSerializer):
    discountAmount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = Product
        fields = [
            'id', 
            'productname', 
            'slug', 
            'productimage', 
            'packtitle', 
            'description', 
            'originalprice', 
            'discountPercentage', 
            'discountPrice', 
            'discountAmount',
            'stock'
        ]
        read_only_fields = ['slug', 'discountPrice', 'discountAmount'] 
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'productname','discountPrice']
        
class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(many=False)
    sub_total = serializers.SerializerMethodField(
        method_name="subTotal",
    )
    class Meta:
        model = CartItems
        fields  = ["id", "cart","product","quantity","sub_total"]
    
    def subTotal(self,cartItem:CartItems):
       return cartItem.quantity * cartItem.product.discountPrice 
        
    
class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("The Product does not exist")
        return value
        
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try:
            cartItems =  CartItems.objects.get(product_id=product_id,cart_id=cart_id)
            cartItems.quantity += quantity
            cartItems.save()
            
            self.instance = cartItems
        except:
            self.instance = CartItems.objects.create(cart_id=cart_id,**self.validated_data)
        return self.instance
    
    class Meta:
        model = CartItems
        fields = ['id', 'product_id', 'quantity']
         
         
class UpdateCartItemSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(read_only=True)
    class Meta:
        model = CartItems
        fields = ['quantity']
                        
class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True,read_only=True)
    cart_total = serializers.SerializerMethodField(
        method_name="get_cart_total",
    )
    class Meta:
        model =Cart
        fields = ['id','items',"cart_total"]
    
    def get_cart_total(self, cart: Cart):
        return sum(item.quantity * item.product.discountPrice for item in cart.items.select_related('product'))
            

        
class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = OrderItem
        fields = [
            "id","product","quantity"
        ]
        
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True,read_only=True)
    class Meta:
        model = Order
        fields = [
            "id","placed_at","pending_status","owner","items"
        ]
        
class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    
    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data["cart_id"]
            user_id = self.context['user_id']
            order = Order.objects.create(owner_id=user_id)
            cartItems = CartItems.objects.filter(cart_id=cart_id)
            orderitems = [OrderItem(order=order,
                    product=item.product,
                    quantity=item.quantity)
            for item in cartItems]
            OrderItem.objects.bulk_create(orderitems)
            Cart.objects.filter(id=cart_id).delete()
