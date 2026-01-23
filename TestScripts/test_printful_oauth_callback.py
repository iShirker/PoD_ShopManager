"""
Test Printful OAuth callback flow to diagnose oauth_failed error.
This script tests each step of the OAuth callback process.
"""
import requests
import json
from urllib.parse import urlencode, parse_qs, urlparse

# Production backend URL
BACKEND_URL = "https://podshopmanagerbackend-production.up.railway.app"

# Printful OAuth credentials (from .env)
CLIENT_ID = "app-2976562"
CLIENT_SECRET = "oxH4SmBcKU7td5p26owQwXiYeNYJetLsrq6pnc2PxO1Z7fjz9eiUOhvAIRNraUZ4"

# Printful API endpoints
PRINTFUL_AUTHORIZE_URL = "https://www.printful.com/oauth/authorize"
PRINTFUL_TOKEN_URL = "https://www.printful.com/oauth/token"
PRINTFUL_API_URL = "https://api.printful.com"

def test_authorization_url_generation():
    """Test if authorization URL is generated correctly."""
    print("="*70)
    print("TEST 1: Authorization URL Generation")
    print("="*70)
    
    redirect_url = f"{BACKEND_URL}/api/auth/printful/callback"
    state = "test_state_123:user_456"  # Format: state:user_id
    
    params = {
        'client_id': CLIENT_ID,
        'redirect_url': redirect_url,  # Note: Printful uses redirect_url, not redirect_uri
        'response_type': 'code',
        'state': state
    }
    
    auth_url = f"{PRINTFUL_AUTHORIZE_URL}?{urlencode(params)}"
    
    print(f"Client ID: {CLIENT_ID}")
    print(f"Redirect URL: {redirect_url}")
    print(f"State: {state}")
    print(f"\nGenerated Authorization URL:")
    print(auth_url)
    print("\n[OK] Authorization URL format looks correct")
    print("[INFO] redirect_url parameter is used (not redirect_uri)")
    return auth_url

def test_token_exchange(code=None):
    """
    Test token exchange with authorization code.
    Note: This requires a real authorization code from OAuth flow.
    """
    print("\n" + "="*70)
    print("TEST 2: Token Exchange")
    print("="*70)
    
    if not code:
        print("[SKIPPED] No authorization code provided")
        print("[INFO] To test this, you need to:")
        print("  1. Complete OAuth flow in browser")
        print("  2. Copy the 'code' parameter from callback URL")
        print("  3. Run this script with: test_token_exchange('your_code_here')")
        return None
    
    try:
        print(f"Exchanging code for tokens...")
        print(f"Token URL: {PRINTFUL_TOKEN_URL}")
        
        response = requests.post(
            PRINTFUL_TOKEN_URL,
            data={
                'grant_type': 'authorization_code',
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'code': code
                # Note: Printful docs don't show redirect_url in token exchange
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"\n[SUCCESS] Token exchange successful!")
            print(f"Access Token: {token_data.get('access_token', 'N/A')[:30]}...")
            print(f"Token Type: {token_data.get('token_type', 'N/A')}")
            print(f"Expires At: {token_data.get('expires_at', 'N/A')}")
            print(f"Refresh Token: {token_data.get('refresh_token', 'N/A')[:30]}...")
            return token_data
        else:
            print(f"\n[FAILED] Token exchange failed")
            print(f"Response: {response.text[:500]}")
            try:
                error_data = response.json()
                print(f"Error Details: {json.dumps(error_data, indent=2)}")
            except:
                pass
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Request failed: {type(e).__name__}: {e}")
        return None

def test_get_stores(access_token):
    """Test getting stores list from Printful API."""
    print("\n" + "="*70)
    print("TEST 3: Get Stores List")
    print("="*70)
    
    if not access_token:
        print("[SKIPPED] No access token provided")
        return None
    
    try:
        url = f"{PRINTFUL_API_URL}/stores"
        print(f"URL: {url}")
        print(f"Authorization: Bearer {access_token[:30]}...")
        
        response = requests.get(
            url,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            stores = data.get('result', [])
            print(f"\n[SUCCESS] Retrieved {len(stores)} store(s)")
            if stores:
                print(f"First Store ID: {stores[0].get('id', 'N/A')}")
                print(f"First Store Name: {stores[0].get('name', 'N/A')}")
            return data
        else:
            print(f"\n[FAILED] Get stores failed")
            print(f"Response: {response.text[:500]}")
            try:
                error_data = response.json()
                print(f"Error Details: {json.dumps(error_data, indent=2)}")
            except:
                pass
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Request failed: {type(e).__name__}: {e}")
        return None

def test_get_store_info(access_token, store_id=None):
    """
    Test getting store information.
    Note: The current implementation uses 'GET /store' which might be wrong.
    According to Printful API docs, it should be 'GET /stores/{id}' or 'GET /stores'.
    """
    print("\n" + "="*70)
    print("TEST 4: Get Store Info (Current Implementation)")
    print("="*70)
    
    if not access_token:
        print("[SKIPPED] No access token provided")
        return None
    
    # Test current implementation (GET /store - singular)
    print("Testing: GET /store (singular) - Current implementation")
    try:
        url = f"{PRINTFUL_API_URL}/store"
        print(f"URL: {url}")
        
        response = requests.get(
            url,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n[SUCCESS] GET /store works!")
            print(f"Response: {json.dumps(data, indent=2)[:500]}")
            return data
        else:
            print(f"\n[FAILED] GET /store returned {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except requests.exceptions.HTTPError as e:
        print(f"\n[FAILED] HTTP Error: {e.response.status_code}")
        print(f"Response: {e.response.text[:500]}")
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Request failed: {type(e).__name__}: {e}")
    
    # Test alternative: GET /stores (plural) - from API docs
    print("\n" + "-"*70)
    print("Testing: GET /stores (plural) - From Printful API docs")
    try:
        url = f"{PRINTFUL_API_URL}/stores"
        print(f"URL: {url}")
        
        response = requests.get(
            url,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            stores = data.get('result', [])
            print(f"\n[SUCCESS] GET /stores works! Found {len(stores)} store(s)")
            if stores and store_id is None:
                # Use first store
                store_id = stores[0].get('id')
                print(f"Using first store ID: {store_id}")
            
            # If we have a store_id, get specific store info
            if store_id:
                print("\n" + "-"*70)
                print(f"Testing: GET /stores/{store_id} - Specific store")
                url = f"{PRINTFUL_API_URL}/stores/{store_id}"
                print(f"URL: {url}")
                
                response = requests.get(
                    url,
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    store_data = response.json()
                    print(f"[SUCCESS] Got store details")
                    print(f"Store Name: {store_data.get('result', {}).get('name', 'N/A')}")
                    return store_data.get('result', {})
            
            return data.get('result', [])[0] if stores else None
            
    except requests.exceptions.HTTPError as e:
        print(f"\n[FAILED] HTTP Error: {e.response.status_code}")
        print(f"Response: {e.response.text[:500]}")
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Request failed: {type(e).__name__}: {e}")
    
    return None

def test_full_flow_simulation():
    """Simulate the full OAuth callback flow."""
    print("\n" + "="*70)
    print("TEST 5: Full OAuth Callback Flow Simulation")
    print("="*70)
    
    print("This simulates what happens in the callback handler:")
    print("\n1. Extract code and state from callback URL")
    print("2. Extract user_id from state (format: 'state:user_id')")
    print("3. Exchange code for tokens")
    print("4. Get stores list")
    print("5. Get store info (this might be failing)")
    print("6. Create/update supplier connection")
    
    print("\n[INFO] To test with real data:")
    print("  1. Complete OAuth flow in browser")
    print("  2. Copy the callback URL")
    print("  3. Extract 'code' parameter")
    print("  4. Run: test_token_exchange('your_code_here')")
    print("  5. Then test API calls with the returned access token")

def analyze_callback_url(callback_url):
    """
    Analyze a callback URL to extract parameters.
    Usage: analyze_callback_url('https://backend.com/callback?code=xxx&state=yyy&success=1')
    """
    print("\n" + "="*70)
    print("ANALYZE: Callback URL")
    print("="*70)
    
    try:
        parsed = urlparse(callback_url)
        params = parse_qs(parsed.query)
        
        print(f"Full URL: {callback_url}")
        print(f"\nExtracted Parameters:")
        for key, value in params.items():
            print(f"  {key}: {value[0] if value else 'N/A'}")
        
        code = params.get('code', [None])[0]
        state = params.get('state', [None])[0]
        success = params.get('success', [None])[0]
        error = params.get('error', [None])[0]
        
        print(f"\nAnalysis:")
        if error:
            print(f"  [ERROR] Error parameter: {error}")
        elif not code:
            print(f"  [ERROR] No 'code' parameter found")
        elif success == '0':
            print(f"  [ERROR] User rejected authorization (success=0)")
        else:
            print(f"  [OK] Code present: {code[:30]}...")
            if state:
                print(f"  [OK] State present: {state}")
                if ':' in state:
                    user_id = state.split(':')[1]
                    print(f"  [OK] User ID extracted: {user_id}")
                else:
                    print(f"  [WARNING] State doesn't contain user_id (format: 'state:user_id')")
            else:
                print(f"  [WARNING] No state parameter")
        
        return {
            'code': code,
            'state': state,
            'success': success,
            'error': error
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to parse URL: {e}")
        return None

def main():
    print("="*70)
    print("Printful OAuth Callback Diagnostic Test")
    print("="*70)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Client ID: {CLIENT_ID}")
    print(f"Client Secret: ***{CLIENT_SECRET[-8:]}")
    print("="*70)
    
    # Test 1: Authorization URL
    test_authorization_url_generation()
    
    # Test 2: Token exchange (requires code)
    test_token_exchange()
    
    # Test 5: Flow simulation
    test_full_flow_simulation()
    
    print("\n" + "="*70)
    print("DIAGNOSIS: Common Issues")
    print("="*70)
    print("\n1. Token Exchange Issues:")
    print("   - Missing redirect_url parameter (might be required)")
    print("   - Invalid client_id or client_secret")
    print("   - Authorization code expired or already used")
    print("   - Redirect URL mismatch")
    
    print("\n2. Store Info Issues:")
    print("   - GET /store (singular) might not exist")
    print("   - Should use GET /stores (plural) or GET /stores/{id}")
    print("   - Access token might not have required scopes")
    
    print("\n3. State/User ID Issues:")
    print("   - State format should be 'state:user_id'")
    print("   - User must be authenticated when starting OAuth")
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\nTo diagnose the actual error:")
    print("1. Check Railway backend logs for the exact exception")
    print("2. Complete OAuth flow and copy the callback URL")
    print("3. Run: analyze_callback_url('your_callback_url_here')")
    print("4. Extract the code and run: test_token_exchange('code_here')")
    print("5. Test API calls with the access token")
    print("\nThe error 'oauth_failed' is a generic catch-all.")
    print("Check backend logs to see the actual exception message.")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'analyze':
            if len(sys.argv) > 2:
                analyze_callback_url(sys.argv[2])
            else:
                print("Usage: python test_printful_oauth_callback.py analyze <callback_url>")
        elif sys.argv[1] == 'exchange':
            if len(sys.argv) > 2:
                token_data = test_token_exchange(sys.argv[2])
                if token_data:
                    access_token = token_data.get('access_token')
                    if access_token:
                        print("\n" + "="*70)
                        print("Testing API calls with access token...")
                        print("="*70)
                        test_get_stores(access_token)
                        test_get_store_info(access_token)
            else:
                print("Usage: python test_printful_oauth_callback.py exchange <authorization_code>")
        else:
            print("Usage:")
            print("  python test_printful_oauth_callback.py")
            print("  python test_printful_oauth_callback.py analyze <callback_url>")
            print("  python test_printful_oauth_callback.py exchange <authorization_code>")
    else:
        main()
