import requests
import os
import base64
import re
from datetime import datetime
from flask import request, Blueprint

# 1. Define the Blueprint
payments_bp = Blueprint('payments', __name__, url_prefix='/payments')

# 2. Helper to get Access Token
def get_access_token():
    """Generates the Safaricom API Access Token using .env credentials"""
    consumer_key = os.getenv('MPESA_CONSUMER_KEY')
    consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    try:
        response = requests.get(url, auth=(consumer_key, consumer_secret))
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception as e:
        print(f"Token Error: {str(e)}")
        return None

# 3. STK Push Route
@payments_bp.route('/stk-push', methods=['POST'])
def stk_push():
    raw_phone = request.form.get('phone', '').strip()
    amount = request.form.get('amount', '0').strip()
    
    # --- Kenyan Phone Number Normalization (Handles 07... and 01...) ---
    # Removes any spaces or non-digit characters first
    phone = re.sub(r'\D', '', raw_phone)
    
    if phone.startswith('0'):
        # Converts 07... to 2547... and 01... to 2541...
        phone = '254' + phone[1:]
    elif phone.startswith('7') or phone.startswith('1'):
        # Converts 7... to 2547...
        phone = '254' + phone
    # If it already starts with 254, we leave it as is.

    # Get Credentials from .env
    shortcode = os.getenv('MPESA_SHORTCODE')
    passkey = os.getenv('MPESA_PASSKEY')
    # Ensures APP_URL is correctly joined with the callback path
    base_url = os.getenv('APP_URL', 'http://127.0.0.1:5000').rstrip('/')
    callback_url = f"{base_url}/payments/callback"

    access_token = get_access_token()
    if not access_token:
        return '<div class="p-4 bg-red-100 text-red-700 rounded-lg">❌ Auth Error: Check your MPESA_CONSUMER_KEY & SECRET in .env</div>'

    # Security: Generate Password
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password_str = f"{shortcode}{passkey}{timestamp}"
    password = base64.b64encode(password_str.encode()).decode()

    headers = {"Authorization": f"Bearer {access_token}"}
    
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(float(amount)), # Handles cases where amount might be '10.0'
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": "AlberSchool",
        "TransactionDesc": "Fee Payment"
    }

    try:
        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers=headers
        )
        res_data = response.json()
        
        # Debugging: Prints the full Safaricom response to your terminal
        print(f"M-Pesa Response: {res_data}")

        if res_data.get('ResponseCode') == '0':
            return f'''
            <div class="p-4 bg-green-100 text-green-700 rounded-lg border border-green-200">
                ✅ <strong>Prompt Sent!</strong><br>
                Check phone <strong>{phone}</strong> for the PIN prompt.
            </div>
            '''
        else:
            # Captures the actual error message from Safaricom
            error_msg = res_data.get('CustomerMessage') or res_data.get('errorMessage') or "Declined"
            return f'<div class="p-4 bg-red-100 text-red-700 rounded-lg">❌ M-Pesa Refused: {error_msg}</div>'
            
    except Exception as e:
        return f'<div class="p-4 bg-red-100 text-red-700 rounded-lg">❌ System Error: {str(e)}</div>'