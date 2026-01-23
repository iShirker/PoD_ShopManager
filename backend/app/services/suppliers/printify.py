"""
Printify API service.
Handles communication with Printify Print on Demand API.
"""
import requests
from flask import current_app


class PrintifyService:
    """Service for interacting with Printify API."""

    BASE_URL = 'https://api.printify.com/v1'

    def __init__(self, api_token):
        """
        Initialize Printify service.

        Args:
            api_token: Printify API token
        """
        # Clean and validate token
        self.api_token = api_token.strip() if api_token else ''
        if not self.api_token:
            raise ValueError('Printify API token is required')
        
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'POD-ShopManager/1.0'
        }

    def _request(self, method, endpoint, **kwargs):
        """
        Make API request to Printify.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request arguments

        Returns:
            Response JSON or raises exception
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Log request for debugging (without exposing full token)
        token_preview = f"{self.api_token[:20]}...{self.api_token[-10:]}" if len(self.api_token) > 30 else "***"
        
        try:
            response = requests.request(method, url, headers=self.headers, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Log more details for 401 errors
            if e.response.status_code == 401:
                error_detail = None
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text[:200]
                
                # Check if token might be invalid
                if not self.api_token or len(self.api_token) < 50:
                    raise ValueError(f'Invalid token format (too short). Token preview: {token_preview}')
                
                raise requests.exceptions.HTTPError(
                    f'401 Unauthorized - Token may be invalid or expired. '
                    f'Error: {error_detail}',
                    response=e.response
                )
            raise

    def get_shops(self):
        """Get all shops associated with the account."""
        # Try both endpoints - some versions use different formats
        try:
            return self._request('GET', 'shops.json')
        except requests.exceptions.HTTPError as e:
            # If shops.json fails, try shops endpoint
            if e.response.status_code == 404:
                return self._request('GET', 'shops')
            raise

    def get_shop(self, shop_id):
        """Get specific shop details."""
        return self._request('GET', f'shops/{shop_id}.json')

    def get_blueprints(self):
        """Get all available product blueprints (catalog)."""
        return self._request('GET', 'catalog/blueprints.json')

    def get_blueprint(self, blueprint_id):
        """
        Get specific blueprint details.

        Args:
            blueprint_id: Printify blueprint ID

        Returns:
            Blueprint details including print providers
        """
        return self._request('GET', f'catalog/blueprints/{blueprint_id}.json')

    def get_blueprint_print_providers(self, blueprint_id):
        """
        Get print providers for a blueprint.

        Args:
            blueprint_id: Printify blueprint ID

        Returns:
            List of available print providers
        """
        return self._request('GET', f'catalog/blueprints/{blueprint_id}/print_providers.json')

    def get_print_provider_variants(self, blueprint_id, print_provider_id):
        """
        Get variants available from a print provider.

        Args:
            blueprint_id: Printify blueprint ID
            print_provider_id: Print provider ID

        Returns:
            Available variants with pricing
        """
        return self._request(
            'GET',
            f'catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json'
        )

    def get_print_provider_shipping(self, blueprint_id, print_provider_id):
        """
        Get shipping info for a print provider.

        Args:
            blueprint_id: Printify blueprint ID
            print_provider_id: Print provider ID

        Returns:
            Shipping profiles and costs
        """
        return self._request(
            'GET',
            f'catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping.json'
        )

    def get_products(self, shop_id, page=1, limit=100):
        """
        Get products from a shop.

        Args:
            shop_id: Printify shop ID
            page: Page number
            limit: Items per page

        Returns:
            List of products
        """
        return self._request('GET', f'shops/{shop_id}/products.json', params={
            'page': page,
            'limit': limit
        })

    def get_product(self, shop_id, product_id):
        """
        Get specific product details.

        Args:
            shop_id: Printify shop ID
            product_id: Product ID

        Returns:
            Product details
        """
        return self._request('GET', f'shops/{shop_id}/products/{product_id}.json')

    def create_product(self, shop_id, product_data):
        """
        Create a new product.

        Args:
            shop_id: Printify shop ID
            product_data: Product details

        Returns:
            Created product
        """
        return self._request('POST', f'shops/{shop_id}/products.json', json=product_data)

    def publish_product(self, shop_id, product_id, publish_data):
        """
        Publish a product to connected sales channel.

        Args:
            shop_id: Printify shop ID
            product_id: Product ID
            publish_data: Publishing options

        Returns:
            Publishing result
        """
        return self._request(
            'POST',
            f'shops/{shop_id}/products/{product_id}/publish.json',
            json=publish_data
        )

    def create_order(self, shop_id, order_data):
        """
        Create a new order.

        Args:
            shop_id: Printify shop ID
            order_data: Order details

        Returns:
            Created order
        """
        return self._request('POST', f'shops/{shop_id}/orders.json', json=order_data)


def validate_printify_connection(api_token, shop_id=None):
    """
    Validate Printify API connection.

    Args:
        api_token: Printify API token
        shop_id: Optional shop ID to validate

    Returns:
        Tuple of (is_valid, result_or_error)
    """
    try:
        service = PrintifyService(api_token)
        
        # First, try to get shops to validate the token
        try:
            shops_response = service.get_shops()
        except requests.exceptions.HTTPError as e:
            # If shops endpoint fails, the token might still be valid
            # Try a simpler endpoint to validate
            if e.response.status_code in [401, 403]:
                raise  # Re-raise auth errors
            # For other errors, try to continue with empty shops
            shops_response = []

        # Handle different response formats
        # Printify API might return: list, {'data': [...]}, or {'shops': [...]}
        if isinstance(shops_response, dict):
            shops = shops_response.get('data', shops_response.get('shops', []))
        else:
            shops = shops_response if isinstance(shops_response, list) else []

        # Extract account info
        account_name = None
        email = None

        if shop_id:
            # Validate specific shop access
            shop = service.get_shop(shop_id)
            account_name = shop.get('title') or shop.get('name')
            # Try to extract email from shop data if available
            email = shop.get('email') or shop.get('owner_email')
            return True, {
                'shop': shop,
                'account_name': account_name,
                'email': email,
            }

        # Use first shop name as account name
        if shops and len(shops) > 0:
            first_shop = shops[0]
            # Printify shops have 'title' field, not 'name'
            account_name = first_shop.get('title') or first_shop.get('name')
            # Printify shops don't typically have email in shop data
            email = first_shop.get('email') or first_shop.get('owner_email')

        # If no shops found, still validate the token is working
        # Try to decode JWT token to get user info if available
        if not account_name:
            try:
                import base64
                import json
                # JWT tokens have 3 parts separated by dots
                parts = api_token.split('.')
                if len(parts) >= 2:
                    # Decode the payload (second part)
                    payload = parts[1]
                    # Add padding if needed
                    padding = len(payload) % 4
                    if padding:
                        payload += '=' * (4 - padding)
                    decoded = base64.urlsafe_b64decode(payload)
                    token_data = json.loads(decoded)
                    # Extract user ID from token
                    user_id = token_data.get('sub') or token_data.get('user_id')
                    if user_id:
                        account_name = f"Printify User {user_id}"
            except Exception:
                pass  # If JWT decoding fails, use fallback

        return True, {
            'shops': shops,
            'account_name': account_name or f"Printify ({api_token[-8:]})",
            'email': email,
        }
    except requests.exceptions.HTTPError as e:
        error_detail = None
        status_code = e.response.status_code if e.response else None
        
        try:
            if e.response and e.response.text:
                error_json = e.response.json()
                error_detail = (
                    error_json.get('message') or 
                    error_json.get('error') or 
                    error_json.get('description') or
                    str(error_json)
                )
        except:
            error_detail = e.response.text[:500] if (e.response and e.response.text) else str(e)
        
        if status_code == 401:
            return False, {
                'error': 'Invalid API token - token may be expired or incorrect',
                'details': error_detail or 'Authentication failed. Please check your Printify API token.'
            }
        elif status_code == 403:
            return False, {
                'error': 'Access forbidden - check API token permissions',
                'details': error_detail or 'Your token does not have the required permissions.'
            }
        elif status_code == 404:
            return False, {
                'error': 'API endpoint not found',
                'details': error_detail or 'The Printify API endpoint may have changed. Please check the API documentation.'
            }
        return False, {
            'error': f'API request failed (Status {status_code})',
            'details': error_detail or str(e)
        }
    except Exception as e:
        import traceback
        error_msg = str(e)
        # Provide more helpful error messages
        if 'Connection' in error_msg or 'timeout' in error_msg.lower():
            error_msg = 'Connection timeout - please check your internet connection and try again'
        elif 'SSL' in error_msg or 'certificate' in error_msg.lower():
            error_msg = 'SSL certificate error - please check your system time and date settings'
        
        return False, {
            'error': f'Connection failed: {error_msg}',
            'details': str(e)
        }


def get_printify_product_pricing(api_token, blueprint_id, print_provider_id):
    """
    Get product pricing from Printify.

    Args:
        api_token: Printify API token
        blueprint_id: Blueprint ID
        print_provider_id: Print provider ID

    Returns:
        Pricing information with variants
    """
    service = PrintifyService(api_token)
    try:
        variants = service.get_print_provider_variants(blueprint_id, print_provider_id)
        return {
            'variants': variants.get('variants', []),
            'currency': 'USD'  # Printify uses USD
        }
    except Exception:
        return None


def get_printify_shipping_cost(api_token, blueprint_id, print_provider_id, country='US'):
    """
    Get shipping cost for a Printify product.

    Args:
        api_token: Printify API token
        blueprint_id: Blueprint ID
        print_provider_id: Print provider ID
        country: Destination country

    Returns:
        Shipping cost information
    """
    service = PrintifyService(api_token)
    try:
        shipping = service.get_print_provider_shipping(blueprint_id, print_provider_id)

        # Find shipping profile for country
        profiles = shipping.get('profiles', [])
        for profile in profiles:
            countries = profile.get('countries', [])
            if country in countries or 'REST_OF_THE_WORLD' in countries:
                return {
                    'first_item': profile.get('first_item', {}).get('cost', 0) / 100,
                    'additional_item': profile.get('additional_items', {}).get('cost', 0) / 100,
                    'currency': profile.get('first_item', {}).get('currency', 'USD')
                }
        return None
    except Exception:
        return None
