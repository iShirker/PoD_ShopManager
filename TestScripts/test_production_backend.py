"""
Test script to verify production backend API is accessible.
Tests the backend at https://podshopmanagerbackend-production.up.railway.app/api
"""
import urllib.request
import urllib.error
import json

BACKEND_URL = "https://podshopmanagerbackend-production.up.railway.app/api"

def test_endpoint(endpoint, method='GET', data=None, token=None):
    """Test a backend API endpoint."""
    url = f"{BACKEND_URL}/{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json')
        
        if token:
            req.add_header('Authorization', f'Bearer {token}')
        
        if data and method in ['POST', 'PUT', 'PATCH']:
            req.data = json.dumps(data).encode('utf-8')
            req.method = method
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            response_data = None
            try:
                response_data = json.loads(response.read().decode())
            except:
                response_data = response.read().decode()
            
            print(f"[SUCCESS] Status {status}")
            if isinstance(response_data, dict):
                print(f"Response: {json.dumps(response_data, indent=2)[:500]}")
            else:
                print(f"Response: {str(response_data)[:500]}")
            return True, status, response_data
    except urllib.error.HTTPError as e:
        status = e.code
        error_body = None
        try:
            error_body = json.loads(e.read().decode())
        except:
            error_body = e.read().decode()[:500]
        
        print(f"[FAILED] Status {status}")
        print(f"Error: {error_body}")
        return False, status, error_body
    except urllib.error.URLError as e:
        print(f"[ERROR] Connection failed: {e}")
        return False, None, str(e)
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        return False, None, str(e)

def main():
    print("="*60)
    print("Production Backend API Test")
    print(f"Backend URL: {BACKEND_URL}")
    print("="*60)
    
    # Test 1: Health check (no auth required)
    print("\n[TEST 1] Health Check Endpoint")
    success1, status1, _ = test_endpoint('health')
    
    # Test 2: Suppliers endpoint (requires auth - will fail but shows if endpoint exists)
    print("\n[TEST 2] Suppliers List Endpoint (requires auth)")
    success2, status2, data2 = test_endpoint('suppliers')
    
    # Test 3: Auth endpoints (should be accessible)
    print("\n[TEST 3] Auth Endpoints")
    print("  Testing /auth/google/authorize...")
    success3, status3, _ = test_endpoint('auth/google/authorize')
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Health Check: {'[SUCCESS]' if success1 else '[FAILED]'} (Status: {status1})")
    print(f"Suppliers List: {'[SUCCESS]' if success2 else '[FAILED]'} (Status: {status2})")
    print(f"Auth Endpoint: {'[SUCCESS]' if success3 else '[FAILED]'} (Status: {status3})")
    
    if success1:
        print("\n[INFO] Backend is accessible and responding!")
        if status2 == 401:
            print("[INFO] Suppliers endpoint requires authentication (expected)")
        elif status2 == 404:
            print("[WARNING] Suppliers endpoint not found - check route configuration")
    else:
        print("\n[ERROR] Backend is not accessible!")
        print("Possible issues:")
        print("  - Backend service is not running")
        print("  - URL is incorrect")
        print("  - Network/firewall blocking connection")
        print("  - CORS configuration issue")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    main()
