"""
Test script to check Printful categories API.
Tests the categories endpoint to see what structure it returns.
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# Get Printful access token from environment
ACCESS_TOKEN = os.getenv('PRINTFUL_ACCESS_TOKEN') or input("Enter Printful access token: ")

BASE_URL = 'https://api.printful.com'

def test_categories():
    """Test Printful categories endpoint."""
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    print("=" * 80)
    print("Testing Printful Categories API")
    print("=" * 80)
    
    # Test categories endpoint
    try:
        url = f"{BASE_URL}/categories"
        print(f"\n1. Testing GET {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Response type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"Response keys: {list(data.keys())}")
            result = data.get('result', data)
            if isinstance(result, list):
                print(f"Categories count: {len(result)}")
                if result:
                    print(f"\nFirst category structure:")
                    print(json.dumps(result[0], indent=2))
                    print(f"\nFirst 5 category names:")
                    for i, cat in enumerate(result[:5]):
                        cat_name = cat.get('title') or cat.get('name') or cat.get('category') or str(cat)
                        print(f"  {i+1}. {cat_name}")
            else:
                print(f"Result type: {type(result)}")
                print(f"Result: {json.dumps(result, indent=2)[:500]}")
        elif isinstance(data, list):
            print(f"Categories count: {len(data)}")
            if data:
                print(f"\nFirst category structure:")
                print(json.dumps(data[0], indent=2))
        else:
            print(f"Unexpected response: {json.dumps(data, indent=2)[:500]}")
            
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {e.response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Also test a sample product to see category structure
    print("\n" + "=" * 80)
    print("Testing Printful Products API (to see category in products)")
    print("=" * 80)
    
    try:
        url = f"{BASE_URL}/products"
        print(f"\n2. Testing GET {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        result = data.get('result', data) if isinstance(data, dict) else data
        if isinstance(result, list) and result:
            print(f"Products count: {len(result)}")
            sample_product = result[0]
            print(f"\nSample product keys: {list(sample_product.keys())}")
            print(f"\nSample product category fields:")
            print(f"  category_id: {sample_product.get('category_id')}")
            print(f"  category: {sample_product.get('category')}")
            print(f"  category_name: {sample_product.get('category_name')}")
            print(f"  type: {sample_product.get('type')}")
            print(f"  type_name: {sample_product.get('type_name')}")
            print(f"\nFull sample product (first 1000 chars):")
            print(json.dumps(sample_product, indent=2)[:1000])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_categories()
