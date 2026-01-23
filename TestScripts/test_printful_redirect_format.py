"""
Test to see what redirect URI format Printful expects.
Check if it's redirect_uri or redirect_url.
"""
import urllib.parse

BACKEND_URL = "https://podshopmanagerbackend-production.up.railway.app"
CLIENT_ID = "app-2976562"

# Full redirect URI
full_redirect_uri = f"{BACKEND_URL}/api/auth/printful/callback"

print("="*70)
print("Printful OAuth Redirect URI Configuration")
print("="*70)
print()
print("Your Client ID: app-2976562")
print()
print("Full Redirect URI:")
print(full_redirect_uri)
print()
print("="*70)
print("PRINTFUL DASHBOARD CONFIGURATION:")
print("="*70)
print()
print("When Printful strips the URL, it might mean:")
print("1. They have separate fields (Domain + Path)")
print("2. They auto-add https://")
print("3. They expect just the domain in one field")
print()
print("TRY THESE OPTIONS:")
print()
print("Option 1: If there are TWO fields:")
print("  Domain/Base URL: podshopmanagerbackend-production.up.railway.app")
print("  Callback Path: /api/auth/printful/callback")
print()
print("Option 2: If there's ONE field, try:")
print("  podshopmanagerbackend-production.up.railway.app/api/auth/printful/callback")
print("  (without https:// - they might add it automatically)")
print()
print("Option 3: If it only accepts domain:")
print("  podshopmanagerbackend-production.up.railway.app")
print("  (Then check if there's a separate 'Callback Path' or 'Redirect Path' field)")
print()
print("="*70)
print("VERIFY IN PRINTFUL DASHBOARD:")
print("="*70)
print()
print("1. Go to: https://developers.printful.com/")
print("2. Sign in")
print("3. Find your app (Client ID: app-2976562)")
print("4. Look for:")
print("   - 'Redirect URI' field")
print("   - 'Callback URL' field")
print("   - 'Authorized Redirect URIs' field")
print("   - Separate 'Domain' and 'Path' fields")
print()
print("5. Check what fields are available and their labels")
print()
print("="*70)
