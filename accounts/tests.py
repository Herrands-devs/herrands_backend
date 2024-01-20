from django.test import TestCase

# Create your tests here.
from django.core.mail import send_mail
from django.conf import settings
settings.configure()

print(send_mail('Test', 'hello', settings.EMAIL_HOST_USER, ['toluiwal@gmail.com']))


