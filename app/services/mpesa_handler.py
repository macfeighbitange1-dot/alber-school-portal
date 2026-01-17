import requests
import base64
from datetime import datetime
import os

class MpesaService:
    def __init__(self):
        self.consumer_key = os.getenv("MPESA_CONSUMER_KEY")
        self.consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")
        self.passkey = os.getenv("MPESA_PASSKEY")
        self.shortcode = os.getenv("MPESA_SHORTCODE")
        self.base_url = "https://sandbox.safaricom.co.ke" # Switch to Live for prod

    def _get_access_token(self):
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        auth = (self.consumer_key, self.consumer_secret)
        response = requests.get(url, auth=auth)
        return response.json().get('access_token')

    def initiate_stk_push(self, phone_number: str, amount: int, account_ref: str):
        token = self._get_access_token()
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode()

        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": f"{os.getenv('APP_URL')}/api/mpesa/callback",
            "AccountReference": account_ref, # Admission Number
            "TransactionDesc": "School Fees Payment"
        }
        
        response = requests.post(
            f"{self.base_url}/mpesa/stkpush/v1/processrequest", 
            json=payload, 
            headers=headers
        )
        return response.json()