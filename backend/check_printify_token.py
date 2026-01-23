"""
Quick check for Printify token status.
Uses built-in libraries only.
"""
import base64
import json
import urllib.request
import urllib.error
from datetime import datetime

TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzN2Q0YmQzMDM1ZmUxMWU5YTgwM2FiN2VlYjNjY2M5NyIsImp0aSI6IjRjNGIyYTlkNWZkMTY2NzIyMmZlM2Y4MGI5ODY1MWU2NTU1NDZmOGVhMjA1YjcxMTViM2M0YmE0OTYyNTk1N2EzOThjZjIwNjlhMmRkNGVhIiwiaWF0IjoxNzY5MDQyOTY1LjI3MDAxMiwibmJmIjoxNzY5MDQyOTY1LjI3MDAxNSwiZXhwIjoxODAwNTc4OTY1LjI2MTU4OCwic3ViIjoiMjU4NjM2NDAiLCJzY29wZXMiOlsic2hvcHMubWFuYWdlIiwic2hvcHMucmVhZCIsImNhdGFsb2cucmVhZCIsIm9yZGVycy5yZWFkIiwib3JkZXJzLndyaXRlIiwicHJvZHVjdHMucmVhZCIsInByb2R1Y3RzLndyaXRlIiwid2ViaG9va3MucmVhZCIsIndlYmhvb2tzLndyaXRlIiwidXBsb2Fkcy5yZWFkIiwidXBsb2Fkcy53cml0ZSIsInByaW50X3Byb3ZpZGVycy5yZWFkIiwidXNlci5pbmZvIl19.AhmAgxknAeditjUx26ulPmHsPZoiceNbgKDlekmXfFoegzayMX57bIUoVG9OuAzoVu-vxojuGHKfGi21NnCiGD5_uRNFPgx2V2kcfd0Mu7QIPMGmMDje6e8CZvVE3VehutXsmEEjH3-wQM8rPtgQSpDpm2MHnScX0eToxNNSdsmcILNDvHPxPc-wyP5YOogWq5ST1f_gSLcuJMFGMWQ5Dxg5nAhyhndcn3hEMugJ6pAqz47KJIxzYV6FHFfjZC8bi_hQ5GiTs5_l0QCQoC2QsMOS6b1aWDMXWKhqjT7faQvUooEcaac6tAIeYeqkdUC85cY_uEcJZN400cqv2uOKREoIEQgQw-IifMcNa9GcLOldCVHa4-19oRZF-wECg3ynW62M1mN1djzMDUUwqVBjm6LPGzKX4muONpMHd9pBSZaW7fUF6uEoassKVqWBrzM7fk0GkdjBpMM1UG21JnMgiefgFqBeRhdyhj6srn5V00qQ1MbQaTCtHyMdtHRpaG9GRX3Ib_iYzmwhZzzNpXexUAEvsvEr_epDSPWReSjDrmGI2LATseiPMarvtBM6Q3fsZaMNTZvPmRLTXOPnz3NGInFOi7l4kqDV6QOyocXfdUf_CI5_4QLzHvwwhKJ_NRdXcW6Q-TR42F1kPzeKQatSiuTUputsCYA34tlvBvyUDs0"

def decode_jwt(token):
    """Decode JWT token to see its contents."""
    try:
        parts = token.split('.')
        if len(parts) >= 2:
            payload = parts[1]
            # Add padding if needed
            padding = len(payload) % 4
            if padding:
                payload += '=' * (4 - padding)
            decoded = base64.urlsafe_b64decode(payload)
            return json.loads(decoded)
    except Exception as e:
        print(f"Error decoding JWT: {e}")
    return None

def test_api_connection(token):
    """Test the API connection."""
    url = "https://api.printify.com/v1/shops.json"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            data = json.loads(response.read().decode())
            return True, status, data
    except urllib.error.HTTPError as e:
        return False, e.code, e.read().decode()[:200]
    except Exception as e:
        return False, None, str(e)

print("="*60)
print("Printify Token Status Check")
print("="*60)

# Decode token
print("\n[1] Decoding JWT Token...")
token_data = decode_jwt(TOKEN)
if token_data:
    print("Token Information:")
    print(f"  User ID: {token_data.get('sub')}")
    
    iat = token_data.get('iat', 0)
    exp = token_data.get('exp', 0)
    
    if iat:
        issued = datetime.fromtimestamp(iat)
        print(f"  Issued At: {issued}")
    
    if exp:
        expires = datetime.fromtimestamp(exp)
        now = datetime.now()
        is_expired = exp < now.timestamp()
        time_left = expires - now
        
        print(f"  Expires At: {expires}")
        print(f"  Status: {'[EXPIRED]' if is_expired else '[ACTIVE]'}")
        if not is_expired:
            days = time_left.days
            hours = time_left.seconds // 3600
            print(f"  Time Remaining: {days} days, {hours} hours")
    
    print(f"  Scopes: {len(token_data.get('scopes', []))} permissions")
else:
    print("  [ERROR] Could not decode token")

# Test API connection
print("\n[2] Testing API Connection...")
success, status, data = test_api_connection(TOKEN)

if success:
    print(f"  [SUCCESS] API Connection: Status {status}")
    if isinstance(data, list):
        print(f"  Found {len(data)} shop(s)")
        if len(data) > 0:
            shop = data[0]
            print(f"  Shop: {shop.get('title', 'N/A')} (ID: {shop.get('id')})")
elif status:
    print(f"  [FAILED] API Connection: Status {status}")
    print(f"  Error: {data}")
else:
    print(f"  [ERROR] Connection failed: {data}")

print("\n" + "="*60)
print("Check Complete")
print("="*60)
