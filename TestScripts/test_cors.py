"""
Test CORS configuration on production backend.
Verifies that CORS headers are properly set.
"""
import urllib.request
import urllib.error
import json

BACKEND_URL = "https://podshopmanagerbackend-production.up.railway.app/api"
FRONTEND_ORIGIN = "https://podshopmanagerfrontend-production.up.railway.app"

def test_cors_headers(endpoint, method='GET', data=None):
    """Test if CORS headers are present in response."""
    url = f"{BACKEND_URL}/{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('Origin', FRONTEND_ORIGIN)
        
        if data and method in ['POST', 'PUT', 'PATCH']:
            req.data = json.dumps(data).encode('utf-8')
            req.method = method
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            headers = dict(response.headers)
            
            print(f"Status: {status}")
            print(f"\nCORS Headers:")
            cors_headers = {
                'Access-Control-Allow-Origin': headers.get('Access-Control-Allow-Origin', 'NOT SET'),
                'Access-Control-Allow-Credentials': headers.get('Access-Control-Allow-Credentials', 'NOT SET'),
                'Access-Control-Allow-Methods': headers.get('Access-Control-Allow-Methods', 'NOT SET'),
                'Access-Control-Allow-Headers': headers.get('Access-Control-Allow-Headers', 'NOT SET'),
            }
            
            for key, value in cors_headers.items():
                status_icon = "[OK]" if value != "NOT SET" else "[MISSING]"
                print(f"  {status_icon} {key}: {value}")
            
            # Check if CORS is working
            if cors_headers['Access-Control-Allow-Origin'] == FRONTEND_ORIGIN:
                print(f"\n[SUCCESS] CORS is properly configured!")
            elif cors_headers['Access-Control-Allow-Origin'] != "NOT SET":
                print(f"\n[WARNING] CORS origin mismatch:")
                print(f"  Expected: {FRONTEND_ORIGIN}")
                print(f"  Got: {cors_headers['Access-Control-Allow-Origin']}")
            else:
                print(f"\n[ERROR] CORS headers are missing!")
            
            return True, status, headers
    except urllib.error.HTTPError as e:
        status = e.code
        headers = dict(e.headers)
        
        print(f"Status: {status} (Error)")
        print(f"\nCORS Headers in Error Response:")
        cors_headers = {
            'Access-Control-Allow-Origin': headers.get('Access-Control-Allow-Origin', 'NOT SET'),
            'Access-Control-Allow-Credentials': headers.get('Access-Control-Allow-Credentials', 'NOT SET'),
        }
        
        for key, value in cors_headers.items():
            status_icon = "[OK]" if value != "NOT SET" else "[MISSING]"
            print(f"  {status_icon} {key}: {value}")
        
        if cors_headers['Access-Control-Allow-Origin'] == FRONTEND_ORIGIN:
            print(f"\n[SUCCESS] CORS headers present in error response!")
        else:
            print(f"\n[ERROR] CORS headers missing in error response!")
            print(f"  This will cause CORS errors in the browser")
        
        try:
            error_body = json.loads(e.read().decode())
            print(f"\nError Response: {json.dumps(error_body, indent=2)[:500]}")
        except:
            error_body = e.read().decode()[:500]
            print(f"\nError Response: {error_body}")
        
        return False, status, headers
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        return False, None, {}

def main():
    print("="*60)
    print("CORS Configuration Test")
    print(f"Backend: {BACKEND_URL}")
    print(f"Frontend Origin: {FRONTEND_ORIGIN}")
    print("="*60)
    
    # Test 1: Health endpoint (no auth required)
    print("\n[TEST 1] Health Endpoint (should have CORS)")
    test_cors_headers('health')
    
    # Test 2: Suppliers endpoint (requires auth - will get 401)
    print("\n[TEST 2] Suppliers Endpoint (401 error - should have CORS)")
    test_cors_headers('suppliers')
    
    # Test 3: OPTIONS preflight request
    print("\n[TEST 3] OPTIONS Preflight Request")
    try:
        req = urllib.request.Request(f"{BACKEND_URL}/suppliers", method='OPTIONS')
        req.add_header('Origin', FRONTEND_ORIGIN)
        req.add_header('Access-Control-Request-Method', 'POST')
        req.add_header('Access-Control-Request-Headers', 'Content-Type, Authorization')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            headers = dict(response.headers)
            print(f"Status: {response.getcode()}")
            print(f"CORS Headers:")
            print(f"  Access-Control-Allow-Origin: {headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
            print(f"  Access-Control-Allow-Methods: {headers.get('Access-Control-Allow-Methods', 'NOT SET')}")
            print(f"  Access-Control-Allow-Headers: {headers.get('Access-Control-Allow-Headers', 'NOT SET')}")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    print("\n" + "="*60)
    print("Test Complete")
    print("="*60)

if __name__ == '__main__':
    main()
