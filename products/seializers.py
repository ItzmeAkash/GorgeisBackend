from rest_framework import serializers
from .models import Product

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
        read_only_fields = ['slug', 'discountPrice', 'discountAmount']  # These are auto-generated