from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def email_validator(self,email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError(_('Invalid email address.'))
        
    
    def create_user(self,email,first_name,last_name,password,**extra_fields):
        if email:
            email  = self.normalize_email(email)
            self.email_validator(email)
            
        else:
            raise ValueError(_("An email address is required"))
        
        user = self.model(email=email, first_name=first_name,last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
            
    def create_superuser(self, first_name,last_name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault("is_active", True)
        
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')
        
        
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            **extra_fields
        )
        user.save(using=self._db)
        return user