import requests
import os
import random
import string

# Function to generate a random transaction reference
def generate_transaction_reference():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

# Initialize Flutterwave API details
FLW_PUBLIC_KEY = 'FLWPUBK_TEST-27d21cd18e97e16a388aef87fbb3c411-X'
FLW_SECRET_KEY = 'FLWSECK_TEST-fa9f76dea9dd1ae5f29784bc4bbfee46-X'

# Define the API endpoint
url = "https://api.flutterwave.com/v3/transfers"

# Define the transfer details
details = {
    "account_bank": "044",
    "account_number": "0690000040",
    "amount": 200,
    "currency": "NGN",
    "narration": "Payment for things",
    "reference": generate_transaction_reference(),
}

# Define headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {FLW_SECRET_KEY}"
}

# Send the POST request to initiate the transfer
response = requests.post(url, json=details, headers=headers)

# Print the response
print(response.json())
