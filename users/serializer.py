from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6,write_only=True)

    
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'phone_number', 'date_of_birth')
        extra_kwargs = {
            'password': {
                'write_only': True,
            }
        }
    
        
    # Creating the User
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if password:
            # Create a new User instance
            user = User.objects.create(**validated_data)
            # Set the hashed password
            user.set_password(password)
            user.save()
            return user
        raise serializers.ValidationError("Password is missing")
        