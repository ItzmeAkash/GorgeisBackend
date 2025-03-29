import base64
import hashlib
import hmac

import secrets
import secrets
from django.conf import settings

# Get a secure key from settings or generate one
try:
    SECRET_KEY = settings.PRODUCT_SLUG_SECRET_KEY
except AttributeError:
    # Fallback to Django's SECRET_KEY
    SECRET_KEY = settings.SECRET_KEY

def encrypt_slug(text):
    """
    Encrypts a slug by generating a hash and encoding it.
    
    Args:
        text (str): The original slug text to encrypt
        
    Returns:
        str: Base64 URL-safe encoded hash that can be used in URLs
    """
    # Add some randomness
    salt = secrets.token_hex(8)
    
    # Create a keyed hash
    h = hmac.new(SECRET_KEY.encode(), msg=(text + salt).encode(), digestmod=hashlib.sha256)
    
    # Get first 16 bytes of digest and encode as base64
    digest = h.digest()[:16]
    encoded = base64.urlsafe_b64encode(digest).decode()
    
    # Remove padding and return
    return encoded.rstrip('=')

def generate_unique_slug(model_class, original_slug, instance_id=None):
    """
    Generates a unique encrypted slug for a model instance
    
    Args:
        model_class: The Django model class
        original_slug (str): The original slug to encrypt
        instance_id: Optional ID of existing instance (for updates)
        
    Returns:
        str: A unique encrypted slug
    """
    # Start with initial encryption
    slug = encrypt_slug(original_slug)
    
    # Check if it exists already
    qs = model_class.objects.filter(slug=slug)
    if instance_id:
        qs = qs.exclude(id=instance_id)
    
    # If slug exists, add random suffix and try again
    if qs.exists():
        random_suffix = secrets.token_hex(4)
        slug = encrypt_slug(f"{original_slug}-{random_suffix}")
    
    return slug



# Generate a cryptographically secure random key of 50 characters
secure_key = secrets.token_urlsafe(50)
