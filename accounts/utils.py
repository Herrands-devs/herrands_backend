import random
import string
import requests
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from twilio.rest import Client  # Import the Twilio Client if using Twilio
from twilio.base.exceptions import TwilioException

def generate_otp(length=4):
    characters = string.digits
    otp = ''.join(random.choice(characters) for _ in range(length))
    return otp

def send_otp_email(email, otp):
    subject = 'Your OTP for Login'
    message = f'Your OTP is: {otp}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

'''def send_otp_phone(phone_number, otp):
    try:
        account_sid = 'ACadc78116636051ed92f38403f37aa936'  # Replace with your Twilio account SID
        auth_token = '0703ee80a43d2df4a68988c0e0a47ed0'  # Replace with your Twilio auth token
        twilio_phone_number = '+12314032534'  # Replace with your Twilio phone number

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=f'Your OTP is: {otp}',
            from_=twilio_phone_number,
            to=phone_number
        )
        # Log or return a success message if needed
        print(f'Message sent successfully to {phone_number}')
    except TwilioException as e:
        # Log the exception or fail silently
        print(f'TwilioException: {e}')'''
def send_otp_phone(phone_number, otp):
    url = "https://api.ng.termii.com/api/sms/otp/send"

    payload = {
        "api_key": "TLp9W4ZIkCUJDrSoIkSlvBjRA4JwbOPfbgs4OyCLJZhLVNJoLB9lAZF9zV4Ytv",
        "message_type": "NUMERIC",
        "to": phone_number,
        "from": "Herrands",
        "channel": "generic",
        "pin_attempts": 10,
        "pin_time_to_live": 5,
        "pin_length": 4,
        "pin_placeholder": f"< {otp} >",
        "message_text": f"Your one time password is < {otp} >",
        "pin_type": "NUMERIC"
    }

    headers = {
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx HTTP status codes
        print(response.text)
        # Log or return a success message if needed
        print(f'Message sent successfully to {phone_number}')
    except requests.exceptions.RequestException as e:
        # Log the exception or fail silently
        print(f'RequestException: {e}')

    