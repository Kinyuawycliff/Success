import random
import string
import requests
import base64
import datetime
from fastapi import HTTPException
from requests.auth import HTTPBasicAuth

from app.config import (MPESA_CONFIG)

# Load M-Pesa configuration
CONSUMER_KEY = MPESA_CONFIG["CONSUMER_KEY"]
CONSUMER_SECRET = MPESA_CONFIG["CONSUMER_SECRET"]
BUSINESS_SHORT_CODE = MPESA_CONFIG["BUSINESS_SHORT_CODE"]
PASSKEY = MPESA_CONFIG["PASSKEY"]




#! ------------------ credentials helpers --------------------

# Generate random username and password
def generate_credentials():
    username = 'Z' + ''.join(random.choices(string.digits, k=3))
    password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return username, password


# Generate a random voucher code
def generate_voucher(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))




#! ------------------ stk push helpers --------------------

# Generate access token for M-Pesa API

def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise HTTPException(status_code=500, detail="Failed to authenticate with M-Pesa API")



# Generate password for M-Pesa STK Push
def generate_password():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    data_to_encode = BUSINESS_SHORT_CODE + PASSKEY + timestamp
    encoded_string = base64.b64encode(data_to_encode.encode()).decode()
    return encoded_string, timestamp





# TEMPORARY store (in-memory)
metadata_store = {}

def save_metadata_to_store(checkout_id: str, data: dict):
    metadata_store[checkout_id] = data

def get_metadata_from_store(checkout_id: str):
    return metadata_store.get(checkout_id)
