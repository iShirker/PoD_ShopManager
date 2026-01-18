"""
Test script to verify POD supplier API keys.
Run: python test_api_keys.py
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def test_etsy():
    """Test Etsy API key."""
    print("\n=== Testing Etsy API ===")
    api_key = os.getenv('ETSY_API_KEY')
    if not api_key or api_key == 'your-etsy-api-key':
        print("❌ Etsy: No API key configured")
        return False

    try:
        # Etsy's ping endpoint to verify API key
        response = requests.get(
            'https://openapi.etsy.com/v3/application/openapi-ping',
            headers={'x-api-key': api_key},
            timeout=10
        )
        if response.status_code == 200:
            print("✅ Etsy: API key is valid!")
            return True
        elif response.status_code == 401:
            print(f"❌ Etsy: Invalid API key (401 Unauthorized)")
        else:
            print(f"⚠️ Etsy: Unexpected response - Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ Etsy: Connection error - {str(e)}")
        return False


def test_shopify():
    """Test Shopify API credentials."""
    print("\n=== Testing Shopify API ===")
    api_key = os.getenv('SHOPIFY_API_KEY')
    api_secret = os.getenv('SHOPIFY_API_SECRET')

    if not api_key or api_key == 'your-shopify-api-key':
        print("❌ Shopify: No API key configured")
        return False

    if not api_secret or api_secret == 'your-shopify-api-secret':
        print("❌ Shopify: No API secret configured")
        return False

    # Shopify OAuth apps can't be directly tested without a store
    # We can only verify the credentials format
    print("✅ Shopify: API credentials configured")
    print(f"   API Key: {api_key[:10]}...")
    print(f"   API Secret: {api_secret[:10]}...")
    print("   ℹ️  Note: Shopify requires OAuth flow with a specific store to fully verify")
    return True


def test_gelato():
    """Test Gelato API key."""
    print("\n=== Testing Gelato API ===")
    api_key = os.getenv('GELATO_API_KEY')
    if not api_key or api_key == 'your-gelato-api-key':
        print("❌ Gelato: No API key configured")
        return False

    try:
        response = requests.get(
            'https://api.gelato.com/v3/products',
            headers={'X-API-KEY': api_key},
            timeout=10
        )
        if response.status_code == 200:
            print("✅ Gelato: API key is valid!")
            return True
        elif response.status_code == 401:
            print(f"❌ Gelato: Invalid API key (401 Unauthorized)")
        else:
            print(f"⚠️ Gelato: Unexpected response - Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ Gelato: Connection error - {str(e)}")
        return False


def test_printify():
    """Test Printify API key."""
    print("\n=== Testing Printify API ===")
    api_key = os.getenv('PRINTIFY_API_KEY')
    if not api_key or api_key == 'your-printify-api-key':
        print("❌ Printify: No API key configured")
        return False

    try:
        response = requests.get(
            'https://api.printify.com/v1/shops.json',
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=10
        )
        if response.status_code == 200:
            shops = response.json()
            print(f"✅ Printify: API key is valid! Found {len(shops)} shop(s)")
            for shop in shops:
                print(f"   - {shop.get('title', 'Unknown')} (ID: {shop.get('id')})")
            return True
        elif response.status_code == 401:
            print(f"❌ Printify: Invalid API key (401 Unauthorized)")
        else:
            print(f"⚠️ Printify: Unexpected response - Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ Printify: Connection error - {str(e)}")
        return False


def test_printful():
    """Test Printful API key."""
    print("\n=== Testing Printful API ===")
    api_key = os.getenv('PRINTFUL_API_KEY')
    if not api_key or api_key == 'your-printful-api-key':
        print("❌ Printful: No API key configured")
        return False

    try:
        response = requests.get(
            'https://api.printful.com/stores',
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            result = data.get('result', [])
            print(f"✅ Printful: API key is valid! Found {len(result)} store(s)")
            for store in result:
                print(f"   - {store.get('name', 'Unknown')} (ID: {store.get('id')})")
            return True
        elif response.status_code == 401:
            print(f"❌ Printful: Invalid API key (401 Unauthorized)")
            print(f"   Response: {response.text[:200]}")
        else:
            print(f"⚠️ Printful: Unexpected response - Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ Printful: Connection error - {str(e)}")
        return False


if __name__ == '__main__':
    print("=" * 50)
    print("API Key Verification")
    print("=" * 50)

    results = {
        'Etsy': test_etsy(),
        'Shopify': test_shopify(),
        'Gelato': test_gelato(),
        'Printify': test_printify(),
        'Printful': test_printful(),
    }

    print("\n" + "=" * 50)
    print("Summary:")
    print("=" * 50)
    for service, success in results.items():
        status = "✅ Valid" if success else "❌ Invalid/Not configured"
        print(f"  {service}: {status}")
