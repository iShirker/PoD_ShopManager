"""Test Gelato API key"""
import base64
import requests

API_KEY = "3698c94e-193f-4142-8192-448ef6640216-fba2f72c-7102-4e48-8e32-eed4b459c45a:57350485-18da-4ea0-8e10-64fd8fa074c1"
BASE_URL = "https://api.gelato.com/v3"

print("Testing Gelato API key...\n")

# Test 1: X-API-KEY header
print("Test 1: Using X-API-KEY header")
try:
    response = requests.get(
        f"{BASE_URL}/stores",
        headers={"X-API-KEY": API_KEY}
    )
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")

print()

# Test 2: Basic Auth
print("Test 2: Using Basic Auth")
try:
    encoded = base64.b64encode(API_KEY.encode()).decode()
    response = requests.get(
        f"{BASE_URL}/stores",
        headers={"Authorization": f"Basic {encoded}"}
    )
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")

print()

# Test 3: Bearer token (in case it's actually a token)
print("Test 3: Using Bearer token")
try:
    response = requests.get(
        f"{BASE_URL}/stores",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")

print()

# Test 4: Try v4 API endpoint
print("Test 4: Using v4 API with X-API-KEY")
try:
    response = requests.get(
        "https://api.gelato.com/v4/stores",
        headers={"X-API-KEY": API_KEY}
    )
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")
