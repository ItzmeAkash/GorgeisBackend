from django.test import TestCase

# Create your tests here.
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test email from Django.',
    'itzmeakashps@gmail.com',
    ['gorgiebackendtest@gmail.com'],  # Replace with a valid recipient
    fail_silently=False,
)