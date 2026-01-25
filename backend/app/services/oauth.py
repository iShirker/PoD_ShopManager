"""
OAuth service for handling third-party authentication.
"""
import hashlib
import base64
import requests
from urllib.parse import urlencode
from flask import current_app


def get_google_auth_url(state):
    """
    Generate Google OAuth authorization URL.

    Args:
        state: Random state string for CSRF protection

    Returns:
        Authorization URL string
    """
    params = {
        'client_id': current_app.config['GOOGLE_CLIENT_ID'],
        'redirect_uri': f"{current_app.config.get('BACKEND_URL', 'http://localhost:5000')}/api/auth/google/callback",
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'access_type': 'offline',
        'prompt': 'consent'
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


def exchange_google_code(code):
    """
    Exchange Google authorization code for tokens and user info.

    Args:
        code: Authorization code from callback

    Returns:
        User info dictionary
    """
    # Exchange code for tokens
    token_response = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'client_id': current_app.config['GOOGLE_CLIENT_ID'],
            'client_secret': current_app.config['GOOGLE_CLIENT_SECRET'],
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': f"{current_app.config.get('BACKEND_URL', 'http://localhost:5000')}/api/auth/google/callback"
        }
    )
    token_response.raise_for_status()
    tokens = token_response.json()

    # Get user info
    user_response = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f"Bearer {tokens['access_token']}"}
    )
    user_response.raise_for_status()
    return user_response.json()


def get_etsy_auth_url(state, code_verifier):
    """
    Generate Etsy OAuth authorization URL.
    Etsy uses PKCE (Proof Key for Code Exchange).

    Args:
        state: Random state string for CSRF protection
        code_verifier: Random string for PKCE

    Returns:
        Authorization URL string
    """
    # Generate code challenge from verifier
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip('=')

    params = {
        'response_type': 'code',
        'client_id': current_app.config['ETSY_API_KEY'],
        'redirect_uri': current_app.config['ETSY_REDIRECT_URI'],
        'scope': 'listings_r listings_w shops_r shops_w transactions_r',
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    return f"https://www.etsy.com/oauth/connect?{urlencode(params)}"


def exchange_etsy_code(code, code_verifier):
    """
    Exchange Etsy authorization code for tokens and user info.

    Args:
        code: Authorization code from callback
        code_verifier: PKCE code verifier

    Returns:
        Tuple of (token_data, user_info)
    """
    # Exchange code for tokens
    token_response = requests.post(
        'https://api.etsy.com/v3/public/oauth/token',
        data={
            'grant_type': 'authorization_code',
            'client_id': current_app.config['ETSY_API_KEY'],
            'redirect_uri': current_app.config['ETSY_REDIRECT_URI'],
            'code': code,
            'code_verifier': code_verifier
        }
    )
    token_response.raise_for_status()
    tokens = token_response.json()

    # Get user info
    user_response = requests.get(
        'https://openapi.etsy.com/v3/application/users/me',
        headers={
            'Authorization': f"Bearer {tokens['access_token']}",
            'x-api-key': current_app.config['ETSY_API_KEY']
        }
    )
    user_response.raise_for_status()

    return tokens, user_response.json()


def get_shopify_auth_url(shop_domain, state):
    """
    Generate Shopify OAuth authorization URL for app installation.

    Args:
        shop_domain: Shopify store domain (e.g., mystore.myshopify.com)
        state: Random state string for CSRF protection

    Returns:
        Authorization URL string
    """
    # Clean up domain
    if not shop_domain.endswith('.myshopify.com'):
        shop_domain = f"{shop_domain}.myshopify.com"

    # Comprehensive scopes for PoD Manager app
    scopes = ','.join([
        'read_products',
        'write_products',
        'read_orders',
        'write_orders',
        'read_fulfillments',
        'write_fulfillments',
        'read_inventory',
        'write_inventory',
        'read_locations',
        'read_merchant_managed_fulfillment_orders',
        'write_merchant_managed_fulfillment_orders'
    ])

    # Shopify can reject OAuth with 400 if redirect_uri isn't whitelisted or doesn't match
    # required host constraints in the app configuration. Prefer an explicit config override,
    # otherwise default to the backend callback (legacy flow).
    redirect_uri = current_app.config.get('SHOPIFY_REDIRECT_URI')
    if not redirect_uri:
        redirect_uri = f"{current_app.config.get('BACKEND_URL', 'http://localhost:5000')}/api/auth/shopify/callback"

    params = {
        'client_id': current_app.config['SHOPIFY_API_KEY'],
        'scope': scopes,
        'redirect_uri': redirect_uri,
        'state': state
    }
    return f"https://{shop_domain}/admin/oauth/authorize?{urlencode(params)}"


def exchange_shopify_code(shop_domain, code):
    """
    Exchange Shopify authorization code for access token.

    Args:
        shop_domain: Shopify store domain
        code: Authorization code from callback

    Returns:
        Token data dictionary
    """
    # Clean up domain
    if not shop_domain.endswith('.myshopify.com'):
        shop_domain = f"{shop_domain}.myshopify.com"

    token_response = requests.post(
        f"https://{shop_domain}/admin/oauth/access_token",
        json={
            'client_id': current_app.config['SHOPIFY_API_KEY'],
            'client_secret': current_app.config['SHOPIFY_API_SECRET'],
            'code': code
        }
    )
    token_response.raise_for_status()
    return token_response.json()


def refresh_etsy_token(refresh_token):
    """
    Refresh Etsy access token.

    Args:
        refresh_token: Current refresh token

    Returns:
        New token data dictionary
    """
    token_response = requests.post(
        'https://api.etsy.com/v3/public/oauth/token',
        data={
            'grant_type': 'refresh_token',
            'client_id': current_app.config['ETSY_API_KEY'],
            'refresh_token': refresh_token
        }
    )
    token_response.raise_for_status()
    return token_response.json()


# Gelato OAuth
def get_gelato_auth_url(state):
    """
    Generate Gelato OAuth authorization URL.

    Args:
        state: Random state string for CSRF protection

    Returns:
        Authorization URL string
    """
    params = {
        'client_id': current_app.config.get('GELATO_CLIENT_ID', ''),
        'redirect_uri': current_app.config.get(
            'GELATO_REDIRECT_URI',
            f"{current_app.config.get('BACKEND_URL', 'http://localhost:5000')}/api/auth/gelato/callback"
        ),
        'response_type': 'code',
        'state': state
    }
    scope = current_app.config.get('GELATO_OAUTH_SCOPE', '')
    if scope:
        params['scope'] = scope
    return f"{current_app.config.get('GELATO_OAUTH_AUTHORIZE_URL', '')}?{urlencode(params)}"


def exchange_gelato_code(code):
    """
    Exchange Gelato authorization code for tokens.

    Args:
        code: Authorization code from callback

    Returns:
        Token data dictionary with access_token and refresh_token
    """
    token_response = requests.post(
        current_app.config.get('GELATO_OAUTH_TOKEN_URL', ''),
        data={
            'grant_type': 'authorization_code',
            'client_id': current_app.config.get('GELATO_CLIENT_ID', ''),
            'client_secret': current_app.config.get('GELATO_CLIENT_SECRET', ''),
            'code': code,
            'redirect_uri': current_app.config.get(
                'GELATO_REDIRECT_URI',
                f"{current_app.config.get('BACKEND_URL', 'http://localhost:5000')}/api/auth/gelato/callback"
            )
        }
    )
    token_response.raise_for_status()
    return token_response.json()


def refresh_gelato_token(refresh_token):
    """
    Refresh Gelato access token.

    Args:
        refresh_token: Current refresh token

    Returns:
        New token data dictionary
    """
    token_response = requests.post(
        current_app.config.get('GELATO_OAUTH_TOKEN_URL', ''),
        data={
            'grant_type': 'refresh_token',
            'client_id': current_app.config.get('GELATO_CLIENT_ID', ''),
            'client_secret': current_app.config.get('GELATO_CLIENT_SECRET', ''),
            'refresh_token': refresh_token
        }
    )
    token_response.raise_for_status()
    return token_response.json()


# Printify OAuth
def get_printify_auth_url(state):
    """
    Generate Printify OAuth authorization URL.

    Args:
        state: Random state string for CSRF protection

    Returns:
        Authorization URL string
    """
    params = {
        'client_id': current_app.config.get('PRINTIFY_CLIENT_ID', ''),
        'redirect_uri': f"{current_app.config.get('BACKEND_URL', 'http://localhost:5000')}/api/auth/printify/callback",
        'response_type': 'code',
        'state': state
    }
    return f"https://printify.com/oauth/authorize?{urlencode(params)}"


def exchange_printify_code(code):
    """
    Exchange Printify authorization code for tokens.

    Args:
        code: Authorization code from callback

    Returns:
        Token data dictionary with access_token and refresh_token
    """
    token_response = requests.post(
        'https://printify.com/oauth/token',
        data={
            'grant_type': 'authorization_code',
            'client_id': current_app.config.get('PRINTIFY_CLIENT_ID', ''),
            'client_secret': current_app.config.get('PRINTIFY_CLIENT_SECRET', ''),
            'code': code,
            'redirect_uri': f"{current_app.config.get('BACKEND_URL', 'http://localhost:5000')}/api/auth/printify/callback"
        }
    )
    token_response.raise_for_status()
    return token_response.json()


def refresh_printify_token(refresh_token):
    """
    Refresh Printify access token.

    Args:
        refresh_token: Current refresh token

    Returns:
        New token data dictionary
    """
    token_response = requests.post(
        'https://printify.com/oauth/token',
        data={
            'grant_type': 'refresh_token',
            'client_id': current_app.config.get('PRINTIFY_CLIENT_ID', ''),
            'client_secret': current_app.config.get('PRINTIFY_CLIENT_SECRET', ''),
            'refresh_token': refresh_token
        }
    )
    token_response.raise_for_status()
    return token_response.json()


def get_printify_shops(access_token):
    """
    Get list of shops from Printify.

    Args:
        access_token: Printify access token

    Returns:
        List of shops
    """
    response = requests.get(
        'https://api.printify.com/v1/shops.json',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    response.raise_for_status()
    return response.json()


# Printful OAuth
def get_printful_auth_url(state):
    """
    Generate Printful OAuth authorization URL.

    Args:
        state: Random state string for CSRF protection

    Returns:
        Authorization URL string
    """
    params = {
        'client_id': current_app.config.get('PRINTFUL_CLIENT_ID', ''),
        'redirect_url': f"{current_app.config.get('BACKEND_URL', 'http://localhost:5000')}/api/auth/printful/callback",
        'response_type': 'code',
        'state': state
    }
    return f"https://www.printful.com/oauth/authorize?{urlencode(params)}"


def exchange_printful_code(code):
    """
    Exchange Printful authorization code for tokens.

    Args:
        code: Authorization code from callback

    Returns:
        Token data dictionary with access_token
    """
    redirect_url = f"{current_app.config.get('BACKEND_URL', 'http://localhost:5000')}/api/auth/printful/callback"
    
    token_response = requests.post(
        'https://www.printful.com/oauth/token',
        data={
            'grant_type': 'authorization_code',
            'client_id': current_app.config.get('PRINTFUL_CLIENT_ID', ''),
            'client_secret': current_app.config.get('PRINTFUL_CLIENT_SECRET', ''),
            'code': code,
            'redirect_url': redirect_url  # Include redirect_url for security validation
        }
    )
    token_response.raise_for_status()
    return token_response.json()


def refresh_printful_token(refresh_token):
    """
    Refresh Printful access token.

    Args:
        refresh_token: Current refresh token

    Returns:
        New token data dictionary
    """
    token_response = requests.post(
        'https://www.printful.com/oauth/token',
        data={
            'grant_type': 'refresh_token',
            'client_id': current_app.config.get('PRINTFUL_CLIENT_ID', ''),
            'client_secret': current_app.config.get('PRINTFUL_CLIENT_SECRET', ''),
            'refresh_token': refresh_token
        }
    )
    token_response.raise_for_status()
    return token_response.json()


def get_printful_stores(access_token):
    """
    Get list of stores from Printful.

    Args:
        access_token: Printful access token

    Returns:
        List of stores
    """
    response = requests.get(
        'https://api.printful.com/stores',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    response.raise_for_status()
    return response.json()
