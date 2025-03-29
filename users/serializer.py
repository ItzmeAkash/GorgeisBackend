import datetime
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import serializers
from .models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'phone_number', 
                  'date_of_birth', 'is_active', 'is_staff', 'date_joined')
        read_only_fields = ('is_active', 'is_staff', 'date_joined')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_date_of_birth(self, value):
        if isinstance(value, str):
            date_formats = [
                '%Y-%m-%d',      # 1999-06-21
                '%d-%m-%Y',      # 21-06-1999
                '%m-%d-%Y',      # 06-21-1999
                '%d/%m/%Y',      # 21/06/1999
                '%m/%d/%Y',      # 06/21/1999
                '%d.%m.%Y',      # 21.06.1999
                '%Y/%m/%d',      # 1999/06/21
            ]
            for date_format in date_formats:
                try:
                    parsed_date = datetime.datetime.strptime(value, date_format).date()
                    return parsed_date
                except ValueError:
                    continue
            raise serializers.ValidationError("Invalid date format. Please use YYYY-MM-DD format.")
        return value

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


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile without requiring password.
    """
    password = serializers.CharField(max_length=68, min_length=6, write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'phone_number', 'date_of_birth')
        read_only_fields = ('id', 'email')  # Email cannot be changed

    def validate_date_of_birth(self, value):
        if isinstance(value, str):
            date_formats = [
                '%Y-%m-%d',      # 1999-06-21
                '%d-%m-%Y',      # 21-06-1999
                '%m-%d-%Y',      # 06-21-1999
                '%d/%m/%Y',      # 21/06/1999
                '%m/%d/%Y',      # 06/21/1999
                '%d.%m.%Y',      # 21.06.1999
                '%Y/%m/%d',      # 1999/06/21
            ]
            for date_format in date_formats:
                try:
                    parsed_date = datetime.datetime.strptime(value, date_format).date()
                    return parsed_date
                except ValueError:
                    continue
            raise serializers.ValidationError("Invalid date format. Please use YYYY-MM-DD format.")
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        # Update all other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # If password is provided, update it
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No User found with this email")
        return value


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, write_only=True)
    token = serializers.CharField()
    uidb64 = serializers.CharField()

    def validate(self, data):
        try:
            uid = urlsafe_base64_decode(data['uidb64']).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid reset link")
        
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, data['token']):
            raise serializers.ValidationError("Invalid token or expired token")
        
        return data

    def save(self):
        uid = urlsafe_base64_decode(self.validated_data["uidb64"]).decode()
        user = User.objects.get(pk=uid)
        user.set_password(self.validated_data['password'])
        user.save()
        return user