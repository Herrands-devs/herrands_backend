import random
import string
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from twilio.rest import Client  # Import the Twilio Client if using Twilio

def generate_otp(length=6):
    characters = string.digits
    otp = ''.join(random.choice(characters) for _ in range(length))
    return otp

def send_otp_email(email, otp):
    subject = 'Your OTP for Login'
    message = f'Your OTP is: {otp}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def send_otp_phone(phone_number, otp):
    account_sid = 'ACadc78116636051ed92f38403f37aa936'  # Replace with your Twilio account SID
    auth_token = '0703ee80a43d2df4a68988c0e0a47ed0'  # Replace with your Twilio auth token
    twilio_phone_number = '+12314032534'  # Replace with your Twilio phone number

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f'Your OTP is: {otp}',
        from_=twilio_phone_number,
        to=phone_number
    )