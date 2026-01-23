"""
Test to verify the deployed backend version has the current_app fix.
This script checks if the backend can handle the suppliers endpoint without NameError.
"""
import urllib.request
import urllib.error
import json

BACKEND_URL = "https://podshopmanagerbackend-production.up.railway.app/api"

def test_health():
    """Test health endpoint."""
    try:
        req = urllib.request.Request(f"{BACKEND_URL}/health")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            print(f"[OK] Health check: {data.get('status')}")
            return True
    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")
        return False

def test_suppliers_endpoint():
    """Test suppliers endpoint (will get 401, but should not get 500 with NameError)."""
    try:
        req = urllib.request.Request(f"{BACKEND_URL}/suppliers")
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"[OK] Suppliers endpoint returned: {response.getcode()}")
            return True
    except urllib.error.HTTPError as e:
        status = e.code
        if status == 401:
            # This is expected - we don't have auth token
            print(f"[OK] Suppliers endpoint returned 401 (expected - no auth)")
            # Check if response has CORS headers
            headers = dict(e.headers)
            if 'Access-Control-Allow-Origin' in headers:
                print(f"[OK] CORS headers present: {headers.get('Access-Control-Allow-Origin')}")
            else:
                print(f"[WARNING] CORS headers missing")
            return True
        elif status == 500:
            # This is bad - means there's a server error
            print(f"[ERROR] Suppliers endpoint returned 500 (server error)")
            try:
                error_body = json.loads(e.read().decode())
                print(f"Error details: {json.dumps(error_body, indent=2)}")
            except:
                error_body = e.read().decode()[:500]
                print(f"Error details: {error_body}")
            return False
        else:
            print(f"[INFO] Suppliers endpoint returned: {status}")
            return True
    except Exception as e:
        print(f"[ERROR] Suppliers endpoint test failed: {e}")
        return False

def test_printify_connect():
    """Test printify connect endpoint (will get 400/401, but should not get 500 with NameError)."""
    try:
        # Send a request without proper auth - should get 401, not 500
        req = urllib.request.Request(f"{BACKEND_URL}/suppliers/printify/connect", method='POST')
        req.add_header('Content-Type', 'application/json')
        req.data = json.dumps({'api_key': 'test'}).encode('utf-8')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"[OK] Printify connect returned: {response.getcode()}")
            return True
    except urllib.error.HTTPError as e:
        status = e.code
        if status == 401:
            print(f"[OK] Printify connect returned 401 (expected - no auth token)")
            return True
        elif status == 400:
            print(f"[OK] Printify connect returned 400 (expected - invalid input)")
            return True
        elif status == 500:
            # This is bad - means NameError or other server error
            print(f"[ERROR] Printify connect returned 500 (server error - might be NameError)")
            try:
                error_body = json.loads(e.read().decode())
                print(f"Error details: {json.dumps(error_body, indent=2)}")
                if 'NameError' in str(error_body) or 'current_app' in str(error_body):
                    print(f"[CRITICAL] NameError detected - fix not deployed!")
                else:
                    print(f"[INFO] Different 500 error (not NameError)")
            except:
                error_body = e.read().decode()[:500]
                print(f"Error details: {error_body}")
                if 'NameError' in error_body or 'current_app' in error_body:
                    print(f"[CRITICAL] NameError detected - fix not deployed!")
            return False
        else:
            print(f"[INFO] Printify connect returned: {status}")
            return True
    except Exception as e:
        print(f"[ERROR] Printify connect test failed: {e}")
        return False

def main():
    print("="*60)
    print("Deployment Version Test")
    print(f"Backend: {BACKEND_URL}")
    print("="*60)
    print("\nTesting if deployed version has current_app fix...")
    print("(If NameError occurs, the fix is not deployed)\n")
    
    results = []
    
    print("[TEST 1] Health endpoint")
    results.append(("Health", test_health()))
    
    print("\n[TEST 2] Suppliers endpoint (should get 401, not 500)")
    results.append(("Suppliers", test_suppliers_endpoint()))
    
    print("\n[TEST 3] Printify connect endpoint (should get 400/401, not 500)")
    results.append(("Printify Connect", test_printify_connect()))
    
    print("\n" + "="*60)
    print("Results Summary")
    print("="*60)
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n[SUCCESS] All tests passed - deployment appears to have the fix")
    else:
        print("\n[WARNING] Some tests failed - check if fix is deployed")
    
    print("="*60)

if __name__ == '__main__':
    main()
