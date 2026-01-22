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
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
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
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_shops(self):
        """Get all shops associated with the account."""
        return self._request('GET', 'shops.json')

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
        shops = service.get_shops()

        # Extract account info
        account_name = None
        email = None

        if shop_id:
            # Validate specific shop access
            shop = service.get_shop(shop_id)
            account_name = shop.get('title') or shop.get('name')
            return True, {
                'shop': shop,
                'account_name': account_name,
            }

        # Use first shop name as account name
        if shops and len(shops) > 0:
            first_shop = shops[0]
            account_name = first_shop.get('title') or first_shop.get('name')

        return True, {
            'shops': shops,
            'account_name': account_name or f"Printify ({api_token[-8:]})",
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return False, {'error': 'Invalid API token'}
        return False, {'error': str(e)}
    except Exception as e:
        return False, {'error': str(e)}


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
