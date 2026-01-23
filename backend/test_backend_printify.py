"""
Test script to verify Printify connection through the backend API.
This tests the full flow: token -> backend -> Printify API
"""
import urllib.request
import urllib.error
import json
import base64
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:5000"  # Change to your backend URL if different
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzN2Q0YmQzMDM1ZmUxMWU5YTgwM2FiN2VlYjNjY2M5NyIsImp0aSI6IjRjNGIyYTlkNWZkMTY2NzIyMmZlM2Y4MGI5ODY1MWU2NTU1NDZmOGVhMjA1YjcxMTViM2M0YmE0OTYyNTk1N2EzOThjZjIwNjlhMmRkNGVhIiwiaWF0IjoxNzY5MDQyOTY1LjI3MDAxMiwibmJmIjoxNzY5MDQyOTY1LjI3MDAxNSwiZXhwIjoxODAwNTc4OTY1LjI2MTU4OCwic3ViIjoiMjU4NjM2NDAiLCJzY29wZXMiOlsic2hvcHMubWFuYWdlIiwic2hvcHMucmVhZCIsImNhdGFsb2cucmVhZCIsIm9yZGVycy5yZWFkIiwib3JkZXJzLndyaXRlIiwicHJvZHVjdHMucmVhZCIsInByb2R1Y3RzLndyaXRlIiwid2ViaG9va3MucmVhZCIsIndlYmhvb2tzLndyaXRlIiwidXBsb2Fkcy5yZWFkIiwidXBsb2Fkcy53cml0ZSIsInByaW50X3Byb3ZpZGVycy5yZWFkIiwidXNlci5pbmZvIl19.AhmAgxknAeditjUx26ulPmHsPZoiceNbgKDlekmXfFoegzayMX57bIUoVG9OuAzoVu-vxojuGHKfGi21NnCiGD5_uRNFPgx2V2kcfd0Mu7QIPMGmMDje6e8CZvVE3VehutXsmEEjH3-wQM8rPtgQSpDpm2MHnScX0eToxNNSdsmcILNDvHPxPc-wyP5YOogWq5ST1f_gSLcuJMFGMWQ5Dxg5nAhyhndcn3hEMugJ6pAqz47KJIxzYV6FHFfjZC8bi_hQ5GiTs5_l0QCQoC2QsMOS6b1aWDMXWKhqjT7faQvUooEcaac6tAIeYeqkdUC85cY_uEcJZN400cqv2uOKREoIEQgQw-IifMcNa9GcLOldCVHa4-19oRZF-wECg3ynW62M1mN1djzMDUUwqVBjm6LPGzKX4muONpMHd9pBSZaW7fUF6uEoassKVqWBrzM7fk0GkdjBpMM1UG21JnMgiefgFqBeRhdyhj6srn5V00qQ1MbQaTCtHyMdtHRpaG9GRX3Ib_iYzmwhZzzNpXexUAEvsvEr_epDSPWReSjDrmGI2LATseiPMarvtBM6Q3fsZaMNTZvPmRLTXOPnz3NGInFOi7l4kqDV6QOyocXfdUf_CI5_4QLzHvwwhKJ_NRdXcW6Q-TR42F1kPzeKQatSiuTUputsCYA34tlvBvyUDs0"

# You'll need a valid JWT token from your backend for authentication
# For testing, you can either:
# 1. Get a token by logging in first
# 2. Temporarily disable JWT requirement for testing
# 3. Use a test user token
BACKEND_AUTH_TOKEN = None  # Set this if you have a backend auth token

def decode_jwt(token):
    """Decode JWT token to see its contents."""
    try:
        parts = token.split('.')
        if len(parts) >= 2:
            payload = parts[1]
            padding = len(payload) % 4
            if padding:
                payload += '=' * (4 - padding)
            decoded = base64.urlsafe_b64decode(payload)
            return json.loads(decoded)
    except Exception as e:
        print(f"Error decoding JWT: {e}")
    return None

def test_backend_health():
    """Test if backend is running."""
    print("\n[1] Testing Backend Health...")
    url = f"{BACKEND_URL}/api/health"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"  [SUCCESS] Backend is running: {data.get('message')}")
            return True
    except urllib.error.URLError as e:
        print(f"  [ERROR] Cannot reach backend: {e}")
        print(f"  Make sure backend is running at {BACKEND_URL}")
        return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def test_printify_connection(printify_token, backend_token=None):
    """Test Printify connection through backend API."""
    print("\n[2] Testing Printify Connection via Backend API...")
    url = f"{BACKEND_URL}/api/suppliers/printify/connect"
    
    # Prepare request data
    data = {
        "api_key": printify_token.strip()
    }
    data_json = json.dumps(data).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(url, data=data_json)
    req.add_header('Content-Type', 'application/json')
    
    # Add backend auth token if provided
    if backend_token:
        req.add_header('Authorization', f'Bearer {backend_token}')
        print(f"  Using backend auth token: {backend_token[:20]}...")
    else:
        print("  [WARNING] No backend auth token provided - request may fail with 401")
        print("  You need to authenticate with the backend first")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            status = response.getcode()
            response_data = json.loads(response.read().decode())
            
            print(f"  [SUCCESS] Status {status}")
            print(f"  Response: {json.dumps(response_data, indent=2)}")
            return True, response_data
    except urllib.error.HTTPError as e:
        status = e.code
        error_body = None
        try:
            error_body = json.loads(e.read().decode())
        except:
            error_body = e.read().decode()[:500]
        
        print(f"  [FAILED] Status {status}")
        print(f"  Error: {error_body}")
        
        if status == 401:
            if not backend_token:
                print("\n  [INFO] You need to authenticate with the backend first.")
                print("  Options:")
                print("  1. Log in through the frontend and get a token")
                print("  2. Use the /api/auth/login endpoint to get a token")
                print("  3. Temporarily disable JWT for testing")
        
        return False, error_body
    except Exception as e:
        print(f"  [ERROR] {type(e).__name__}: {e}")
        return False, str(e)

def test_direct_printify(token):
    """Test Printify API directly (for comparison)."""
    print("\n[3] Testing Printify API Directly (for comparison)...")
    url = "https://api.printify.com/v1/shops.json"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token.strip()}')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'POD-ShopManager/1.0')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            data = json.loads(response.read().decode())
            print(f"  [SUCCESS] Direct API call: Status {status}")
            if isinstance(data, list) and len(data) > 0:
                print(f"  Found {len(data)} shop(s): {data[0].get('title', 'N/A')}")
            return True
    except urllib.error.HTTPError as e:
        print(f"  [FAILED] Direct API call: Status {e.code}")
        print(f"  Error: {e.read().decode()[:200]}")
        return False
    except Exception as e:
        print(f"  [ERROR] {type(e).__name__}: {e}")
        return False

def main():
    print("="*60)
    print("Backend Printify Connection Test")
    print("="*60)
    
    # Decode Printify token
    print("\n[0] Printify Token Info:")
    token_data = decode_jwt(TOKEN)
    if token_data:
        exp = token_data.get('exp', 0)
        is_expired = exp < datetime.now().timestamp() if exp else False
        print(f"  User ID: {token_data.get('sub')}")
        print(f"  Expires: {datetime.fromtimestamp(exp) if exp else 'N/A'}")
        print(f"  Status: {'[EXPIRED]' if is_expired else '[ACTIVE]'}")
        print(f"  Token length: {len(TOKEN)} characters")
        print(f"  Token preview: {TOKEN[:30]}...{TOKEN[-20:]}")
    
    # Test direct Printify API first (to verify token works)
    print("\n[INFO] Testing direct Printify API connection first...")
    direct_success = test_direct_printify(TOKEN)
    
    # Test backend health
    backend_running = test_backend_health()
    
    if backend_running:
        # Test through backend
        if BACKEND_AUTH_TOKEN:
            backend_success, result = test_printify_connection(TOKEN, BACKEND_AUTH_TOKEN)
        else:
            print("\n[INFO] Testing without backend auth token (will likely fail)...")
            print("[INFO] To get a backend auth token:")
            print("  1. Log in through the frontend")
            print("  2. Check browser DevTools > Application > Local Storage")
            print("  3. Copy the 'accessToken' value")
            print("  4. Set BACKEND_AUTH_TOKEN in this script")
            backend_success, result = test_printify_connection(TOKEN)
    else:
        print("\n[INFO] Backend is not running. Skipping backend API test.")
        print("[INFO] To test the backend:")
        print("  1. Start the backend server: python run.py")
        print("  2. Run this script again")
        backend_success = False
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Direct Printify API: {'[SUCCESS]' if direct_success else '[FAILED]'}")
    print(f"Backend API: {'[SUCCESS]' if backend_success else '[FAILED]'}")
    
    if direct_success and not backend_success:
        print("\n[ANALYSIS] Token works directly but fails through backend.")
        print("  This suggests an issue with:")
        print("  - Backend authentication (need valid JWT)")
        print("  - Token handling in backend code")
        print("  - Request format or headers")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    main()
