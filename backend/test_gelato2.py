"""Test Gelato API key with different endpoints"""
import requests

API_KEY = "3698c94e-193f-4142-8192-448ef6640216-fba2f72c-7102-4e48-8e32-eed4b459c45a:57350485-18da-4ea0-8e10-64fd8fa074c1"

print("Testing Gelato API endpoints...\n")

endpoints = [
    ("v3/products", "https://api.gelato.com/v3/products"),
    ("v3/orders", "https://api.gelato.com/v3/orders"),
    ("v4/products", "https://api.gelato.com/v4/products"),
    ("v4/orders", "https://api.gelato.com/v4/orders"),
    ("ecommerce/stores", "https://ecommerce.gelatoapis.com/v1/stores"),
    ("order/v4", "https://order.api.gelato.com/v4/orders"),
]

for name, url in endpoints:
    print(f"Testing {name}: {url}")
    try:
        response = requests.get(
            url,
            headers={"X-API-KEY": API_KEY}
        )
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  SUCCESS! Response: {response.text[:300]}")
        else:
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
    print()
