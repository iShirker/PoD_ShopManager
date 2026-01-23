"""
Test Printful connection with Client ID and Secret.
Printful supports both OAuth 2.0 and API Key authentication.
This script tests different authentication methods.
"""
import urllib.request
import urllib.error
import urllib.parse
import base64
import json

# Printful credentials
CLIENT_ID = "app-7057380"
SECRET_KEY = "zihJZx3xaDVdHSwP4A92MXfuH16w2XjJQaYjbAqTIQ3bhf5X5v3P723VVGcrxzEZ"

PRINTFUL_API_URL = "https://api.printful.com"

def test_basic_auth():
    """Test Basic Auth with Client ID and Secret."""
    print("="*60)
    print("TEST 1: Basic Authentication (Client ID + Secret)")
    print("="*60)
    
    try:
        # Create Basic Auth header
        credentials = f"{CLIENT_ID}:{SECRET_KEY}"
        encoded = base64.b64encode(credentials.encode()).decode()
        
        url = f"{PRINTFUL_API_URL}/store"
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Basic {encoded}')
        req.add_header('Content-Type', 'application/json')
        
        print(f"URL: {url}")
        print(f"Auth: Basic {CLIENT_ID}:***")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            print(f"\n[SUCCESS] Status: {response.getcode()}")
            print(f"Response: {json.dumps(data, indent=2)[:500]}")
            return True, data
    except urllib.error.HTTPError as e:
        print(f"\n[FAILED] Status: {e.code}")
        try:
            error_body = json.loads(e.read().decode())
            print(f"Error: {json.dumps(error_body, indent=2)}")
        except:
            error_body = e.read().decode()[:500]
            print(f"Error: {error_body}")
        return False, None
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        return False, None

def test_oauth_token_exchange():
    """Test OAuth token exchange (requires OAuth flow)."""
    print("\n" + "="*60)
    print("TEST 2: OAuth Token Exchange")
    print("="*60)
    print("Note: This requires OAuth authorization code from Printful")
    print("This test shows the token exchange endpoint structure")
    
    # This would require an authorization code from OAuth flow
    # Just show the endpoint structure
    print(f"\nOAuth Token Endpoint: {PRINTFUL_API_URL}/oauth/token")
    print("This requires:")
    print("  1. User authorizes app via OAuth")
    print("  2. Get authorization code")
    print("  3. Exchange code for access token")
    print("\n[SKIPPED] Requires OAuth flow")
    return False, None

def test_api_key_auth():
    """Test API Key authentication (Personal Access Token)."""
    print("\n" + "="*60)
    print("TEST 3: API Key Authentication (Bearer Token)")
    print("="*60)
    print("Note: This requires a Personal Access Token from Printful")
    print("This is different from Client ID/Secret")
    print("\n[SKIPPED] Requires Personal Access Token")
    return False, None

def main():
    print("="*60)
    print("Printful Connection Test")
    print(f"Client ID: {CLIENT_ID}")
    print(f"Secret: ***{SECRET_KEY[-8:]}")
    print("="*60)
    
    # Test Basic Auth first (most likely to work)
    success, data = test_basic_auth()
    
    if success:
        print("\n" + "="*60)
        print("[SUCCESS] Basic Auth works!")
        print("="*60)
        print("\nStore Information:")
        if data and 'result' in data:
            store = data['result']
            print(f"  Store ID: {store.get('id')}")
            print(f"  Store Name: {store.get('name')}")
            print(f"  Store Type: {store.get('type')}")
            print(f"  Email: {store.get('email', 'N/A')}")
        print("\nRecommendation: Use Basic Auth for Printful connection")
    else:
        print("\n" + "="*60)
        print("[INFO] Basic Auth did not work")
        print("="*60)
        print("\nPrintful supports:")
        print("1. OAuth 2.0 Flow (Client ID + Secret)")
        print("   - Requires user authorization")
        print("   - Returns access token")
        print("2. Personal Access Token (API Key)")
        print("   - Direct Bearer token")
        print("   - Can be generated in Printful dashboard")
        print("\nNext steps:")
        print("- Implement OAuth flow for Printful")
        print("- OR ask user to generate Personal Access Token")

if __name__ == '__main__':
    main()
