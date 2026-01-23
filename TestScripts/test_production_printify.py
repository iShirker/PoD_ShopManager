"""
Test Printify connection through production backend API.
This requires a backend JWT token for authentication.
"""
import urllib.request
import urllib.error
import json

BACKEND_URL = "https://podshopmanagerbackend-production.up.railway.app/api"
PRINTIFY_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzN2Q0YmQzMDM1ZmUxMWU5YTgwM2FiN2VlYjNjY2M5NyIsImp0aSI6IjRjNGIyYTlkNWZkMTY2NzIyMmZlM2Y4MGI5ODY1MWU2NTU1NDZmOGVhMjA1YjcxMTViM2M0YmE0OTYyNTk1N2EzOThjZjIwNjlhMmRkNGVhIiwiaWF0IjoxNzY5MDQyOTY1LjI3MDAxMiwibmJmIjoxNzY5MDQyOTY1LjI3MDAxNSwiZXhwIjoxODAwNTc4OTY1LjI2MTU4OCwic3ViIjoiMjU4NjM2NDAiLCJzY29wZXMiOlsic2hvcHMubWFuYWdlIiwic2hvcHMucmVhZCIsImNhdGFsb2cucmVhZCIsIm9yZGVycy5yZWFkIiwib3JkZXJzLndyaXRlIiwicHJvZHVjdHMucmVhZCIsInByb2R1Y3RzLndyaXRlIiwid2ViaG9va3MucmVhZCIsIndlYmhvb2tzLndyaXRlIiwidXBsb2Fkcy5yZWFkIiwidXBsb2Fkcy53cml0ZSIsInByaW50X3Byb3ZpZGVycy5yZWFkIiwidXNlci5pbmZvIl19.AhmAgxknAeditjUx26ulPmHsPZoiceNbgKDlekmXfFoegzayMX57bIUoVG9OuAzoVu-vxojuGHKfGi21NnCiGD5_uRNFPgx2V2kcfd0Mu7QIPMGmMDje6e8CZvVE3VehutXsmEEjH3-wQM8rPtgQSpDpm2MHnScX0eToxNNSdsmcILNDvHPxPc-wyP5YOogWq5ST1f_gSLcuJMFGMWQ5Dxg5nAhyhndcn3hEMugJ6pAqz47KJIxzYV6FHFfjZC8bi_hQ5GiTs5_l0QCQoC2QsMOS6b1aWDMXWKhqjT7faQvUooEcaac6tAIeYeqkdUC85cY_uEcJZN400cqv2uOKREoIEQgQw-IifMcNa9GcLOldCVHa4-19oRZF-wECg3ynW62M1mN1djzMDUUwqVBjm6LPGzKX4muONpMHd9pBSZaW7fUF6uEoassKVqWBrzM7fk0GkdjBpMM1UG21JnMgiefgFqBeRhdyhj6srn5V00qQ1MbQaTCtHyMdtHRpaG9GRX3Ib_iYzmwhZzzNpXexUAEvsvEr_epDSPWReSjDrmGI2LATseiPMarvtBM6Q3fsZaMNTZvPmRLTXOPnz3NGInFOi7l4kqDV6QOyocXfdUf_CI5_4QLzHvwwhKJ_NRdXcW6Q-TR42F1kPzeKQatSiuTUputsCYA34tlvBvyUDs0"

# You need a backend JWT token - get it by logging in through the frontend
# Or temporarily disable JWT for testing
BACKEND_JWT_TOKEN = None  # Set this if you have a backend auth token

def test_printify_connection(backend_token=None):
    """Test Printify connection through backend API."""
    url = f"{BACKEND_URL}/suppliers/printify/connect"
    
    data = {
        "api_key": PRINTIFY_TOKEN.strip()
    }
    
    print(f"\n{'='*60}")
    print("Testing Printify Connection via Production Backend")
    print(f"URL: {url}")
    print(f"Printify Token: {PRINTIFY_TOKEN[:30]}...{PRINTIFY_TOKEN[-20:]}")
    print(f"{'='*60}")
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        req.add_header('User-Agent', 'POD-ShopManager-Test/1.0')
        
        if backend_token:
            req.add_header('Authorization', f'Bearer {backend_token}')
            print(f"Using backend JWT token: {backend_token[:20]}...")
        else:
            print("[WARNING] No backend JWT token provided")
            print("This request will fail with 401 Unauthorized")
            print("To get a token:")
            print("  1. Log in through the frontend")
            print("  2. Check browser DevTools > Application > Local Storage")
            print("  3. Copy the 'accessToken' value")
            print("  4. Set BACKEND_JWT_TOKEN in this script")
        
        with urllib.request.urlopen(req, timeout=30) as response:
            status = response.getcode()
            response_data = json.loads(response.read().decode())
            
            print(f"\n[SUCCESS] Status {status}")
            print(f"Response:")
            print(json.dumps(response_data, indent=2))
            return True, response_data
    except urllib.error.HTTPError as e:
        status = e.code
        error_body = None
        try:
            error_body = json.loads(e.read().decode())
        except:
            error_body = e.read().decode()[:500]
        
        print(f"\n[FAILED] Status {status}")
        print(f"Error Response:")
        if isinstance(error_body, dict):
            print(json.dumps(error_body, indent=2))
        else:
            print(error_body)
        
        if status == 401:
            if not backend_token:
                print("\n[INFO] 401 Unauthorized - Need backend JWT token")
            else:
                print("\n[INFO] 401 Unauthorized - Backend token may be invalid or expired")
        elif status == 500:
            print("\n[INFO] 500 Server Error - Check backend logs for details")
        
        return False, error_body
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)

def main():
    print("="*60)
    print("Production Backend - Printify Connection Test")
    print(f"Backend: {BACKEND_URL}")
    print("="*60)
    
    # Test connection
    success, result = test_printify_connection(BACKEND_JWT_TOKEN)
    
    print("\n" + "="*60)
    print("Test Result")
    print("="*60)
    if success:
        print("[SUCCESS] Printify connection test passed!")
        if isinstance(result, dict) and 'connection' in result:
            conn = result['connection']
            print(f"  Connection ID: {conn.get('id')}")
            print(f"  Account Name: {conn.get('account_name')}")
            print(f"  Account Email: {conn.get('account_email', 'N/A')}")
    else:
        print("[FAILED] Printify connection test failed")
        if isinstance(result, dict):
            error = result.get('error', 'Unknown error')
            details = result.get('details', '')
            print(f"  Error: {error}")
            if details:
                print(f"  Details: {details}")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    main()
