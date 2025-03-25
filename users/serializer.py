import datetime
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
        