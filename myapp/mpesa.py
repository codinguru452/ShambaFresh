"""Safaricom Daraja STK Push helpers. Credentials are read from environment variables."""
import base64
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from django.conf import settings

class MpesaError(Exception):
    pass

def configured():
    return all([settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET,
                settings.MPESA_SHORTCODE, settings.MPESA_PASSKEY, settings.MPESA_CALLBACK_URL])

def access_token():
    if not configured():
        raise MpesaError('M-Pesa is not configured. Add your Daraja sandbox credentials to the .env file.')
    url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    try:
        response = requests.get(url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET), timeout=20)
        response.raise_for_status()
        return response.json()['access_token']
    except (requests.RequestException, ValueError, KeyError) as exc:
        raise MpesaError(f'Could not obtain M-Pesa access token: {exc}') from exc

def stk_push(phone, amount, account_reference):
    token = access_token()
    timestamp = datetime.now(ZoneInfo('Africa/Nairobi')).strftime('%Y%m%d%H%M%S')
    shortcode = settings.MPESA_SHORTCODE
    password = base64.b64encode(f'{shortcode}{settings.MPESA_PASSKEY}{timestamp}'.encode()).decode()
    payload = {
        'BusinessShortCode': shortcode,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': settings.MPESA_TRANSACTION_TYPE,
        'Amount': int(amount),
        'PartyA': phone,
        'PartyB': shortcode,
        'PhoneNumber': phone,
        'CallBackURL': settings.MPESA_CALLBACK_URL,
        'AccountReference': account_reference[:12],
        'TransactionDesc': 'Agrovet shop order',
    }
    try:
        response = requests.post(f'{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest',
                                 json=payload, headers={'Authorization': f'Bearer {token}'}, timeout=30)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise MpesaError(f'M-Pesa request failed: {exc}') from exc
    if data.get('ResponseCode') != '0':
        raise MpesaError(data.get('errorMessage') or data.get('ResponseDescription') or 'M-Pesa rejected the request.')
    return data
