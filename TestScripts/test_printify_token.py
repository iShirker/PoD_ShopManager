"""
Test script for Printify API token validation.
Tests the connection and shows detailed response information.
"""
import requests
import json
import base64
from datetime import datetime

# The token to test
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzN2Q0YmQzMDM1ZmUxMWU5YTgwM2FiN2VlYjNjY2M5NyIsImp0aSI6IjRjNGIyYTlkNWZkMTY2NzIyMmZlM2Y4MGI5ODY1MWU2NTU1NDZmOGVhMjA1YjcxMTViM2M0YmE0OTYyNTk1N2EzOThjZjIwNjlhMmRkNGVhIiwiaWF0IjoxNzY5MDQyOTY1LjI3MDAxMiwibmJmIjoxNzY5MDQyOTY1LjI3MDAxNSwiZXhwIjoxODAwNTc4OTY1LjI2MTU4OCwic3ViIjoiMjU4NjM2NDAiLCJzY29wZXMiOlsic2hvcHMubWFuYWdlIiwic2hvcHMucmVhZCIsImNhdGFsb2cucmVhZCIsIm9yZGVycy5yZWFkIiwib3JkZXJzLndyaXRlIiwicHJvZHVjdHMucmVhZCIsInByb2R1Y3RzLndyaXRlIiwid2ViaG9va3MucmVhZCIsIndlYmhvb2tzLndyaXRlIiwidXBsb2Fkcy5yZWFkIiwidXBsb2Fkcy53cml0ZSIsInByaW50X3Byb3ZpZGVycy5yZWFkIiwidXNlci5pbmZvIl19.AhmAgxknAeditjUx26ulPmHsPZoiceNbgKDlekmXfFoegzayMX57bIUoVG9OuAzoVu-vxojuGHKfGi21NnCiGD5_uRNFPgx2V2kcfd0Mu7QIPMGmMDje6e8CZvVE3VehutXsmEEjH3-wQM8rPtgQSpDpm2MHnScX0eToxNNSdsmcILNDvHPxPc-wyP5YOogWq5ST1f_gSLcuJMFGMWQ5Dxg5nAhyhndcn3hEMugJ6pAqz47KJIxzYV6FHFfjZC8bi_hQ5GiTs5_l0QCQoC2QsMOS6b1aWDMXWKhqjT7faQvUooEcaac6tAIeYeqkdUC85cY_uEcJZN400cqv2uOKREoIEQgQw-IifMcNa9GcLOldCVHa4-19oRZF-wECg3ynW62M1mN1djzMDUUwqVBjm6LPGzKX4muONpMHd9pBSZaW7fUF6uEoassKVqWBrzM7fk0GkdjBpMM1UG21JnMgiefgFqBeRhdyhj6srn5V00qQ1MbQaTCtHyMdtHRpaG9GRX3Ib_iYzmwhZzzNpXexUAEvsvEr_epDSPWReSjDrmGI2LATseiPMarvtBM6Q3fsZaMNTZvPmRLTXOPnz3NGInFOi7l4kqDV6QOyocXfdUf_CI5_4QLzHvwwhKJ_NRdXcW6Q-TR42F1kPzeKQatSiuTUputsCYA34tlvBvyUDs0"

BASE_URL = "https://api.printify.com/v1"

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

def test_endpoint(url, headers, description):
    """Test an API endpoint and return detailed information."""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Status Text: {response.reason}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("[SUCCESS] Request successful!")
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")
                if isinstance(data, list):
                    print(f"Response: List with {len(data)} items")
                    if len(data) > 0:
                        print(f"First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'N/A'}")
                        print(f"First item sample: {json.dumps(data[0], indent=2)[:500]}")
                elif isinstance(data, dict):
                    print(f"Response: Dictionary with keys: {list(data.keys())}")
                    print(f"Response sample: {json.dumps(data, indent=2)[:500]}")
                else:
                    print(f"Response: {str(data)[:500]}")
            except json.JSONDecodeError:
                print(f"Response (not JSON): {response.text[:500]}")
        else:
            print(f"[FAILED] Request failed!")
            print(f"Response Text: {response.text[:500]}")
            try:
                error_data = response.json()
                print(f"Error JSON: {json.dumps(error_data, indent=2)}")
            except:
                pass
        
        return response
        
    except requests.exceptions.Timeout:
        print("[ERROR] TIMEOUT - Request took too long")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] CONNECTION ERROR: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("="*60)
    print("Printify API Token Test Script")
    print("="*60)
    
    # Decode JWT token
    print("\n[INFO] Decoding JWT Token...")
    token_data = decode_jwt(TOKEN)
    if token_data:
        print("Token Information:")
        print(f"  User ID (sub): {token_data.get('sub')}")
        print(f"  Issued At: {datetime.fromtimestamp(token_data.get('iat', 0))}")
        print(f"  Expires At: {datetime.fromtimestamp(token_data.get('exp', 0))}")
        print(f"  Scopes: {', '.join(token_data.get('scopes', []))}")
        is_expired = token_data.get('exp', 0) < datetime.now().timestamp()
        print(f"  Expired: {'YES [EXPIRED]' if is_expired else 'NO [VALID]'}")
    
    # Prepare headers
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Test different endpoints
    endpoints = [
        ('shops.json', 'Shops endpoint (shops.json)'),
        ('shops', 'Shops endpoint (shops)'),
        ('catalog/blueprints.json', 'Blueprints catalog'),
    ]
    
    for endpoint, description in endpoints:
        url = f"{BASE_URL}/{endpoint}"
        response = test_endpoint(url, headers, description)
        
        if response and response.status_code == 200:
            # If shops endpoint works, show shop details
            if 'shops' in endpoint:
                try:
                    data = response.json()
                    shops = data if isinstance(data, list) else data.get('data', data.get('shops', []))
                    if isinstance(shops, list) and len(shops) > 0:
                        print(f"\n[INFO] Found {len(shops)} shop(s):")
                        for i, shop in enumerate(shops[:3], 1):  # Show first 3
                            print(f"\n  Shop {i}:")
                            print(f"    ID: {shop.get('id')}")
                            print(f"    Title: {shop.get('title')}")
                            print(f"    Name: {shop.get('name')}")
                            print(f"    Email: {shop.get('email') or shop.get('owner_email', 'N/A')}")
                            print(f"    All keys: {list(shop.keys())}")
                except Exception as e:
                    print(f"Error parsing shops: {e}")
            break  # If one works, we're good
    
    print("\n" + "="*60)
    print("Test Complete")
    print("="*60)

if __name__ == '__main__':
    main()
