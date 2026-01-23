"""
Test script to verify Printful redirect URI is correct.
This shows the exact redirect URI that needs to be whitelisted in Printful.
"""
import urllib.parse

# Backend URL (production)
BACKEND_URL = "https://podshopmanagerbackend-production.up.railway.app"
CLIENT_ID = "app-7057380"

# Generate the redirect URI
redirect_uri = f"{BACKEND_URL}/api/auth/printful/callback"

# Generate a sample OAuth URL to show what's being sent
state = "test_state_123"
params = {
    'client_id': CLIENT_ID,
    'redirect_uri': redirect_uri,
    'response_type': 'code',
    'state': state
}

auth_url = f"https://www.printful.com/oauth/authorize?{urllib.parse.urlencode(params)}"

print("="*70)
print("Printful OAuth Redirect URI Configuration")
print("="*70)
print()
print("BACKEND_URL:", BACKEND_URL)
print()
print("REDIRECT URI (must be whitelisted in Printful):")
print(redirect_uri)
print()
print("Sample OAuth URL being generated:")
print(auth_url)
print()
print("="*70)
print("STEPS TO WHITELIST IN PRINTFUL:")
print("="*70)
print()
print("1. Go to Printful Developers Dashboard:")
print("   https://developers.printful.com/")
print("   OR")
print("   https://www.printful.com/dashboard/developer")
print()
print("2. Sign in to your Printful account")
print()
print("3. Find your OAuth App:")
print("   - Look for Client ID: app-7057380")
print("   - Click on it to edit")
print()
print("4. Find 'Redirect URIs' or 'Allowed Redirect URIs' section")
print()
print("5. Add this EXACT URL (copy and paste):")
print("   " + redirect_uri)
print()
print("6. Save the changes")
print()
print("7. Try connecting again")
print()
print("="*70)
print("IMPORTANT NOTES:")
print("="*70)
print()
print("[OK] The redirect URI must match EXACTLY (including https://)")
print("[OK] No trailing slash")
print("[OK] Case-sensitive")
print("[OK] Must include the full path: /api/auth/printful/callback")
print()
print("If you have multiple redirect URIs, add this one:")
print("  " + redirect_uri)
print()
print("="*70)
