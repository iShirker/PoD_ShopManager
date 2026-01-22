"""
Gelato API service.
Handles communication with Gelato Print on Demand API.
"""
import base64
import requests
from flask import current_app


class GelatoService:
    """Service for interacting with Gelato API."""

    BASE_URL = 'https://api.gelato.com/v3'

    def __init__(self, api_key=None, access_token=None):
        """
        Initialize Gelato service.

        Args:
            api_key: Gelato API key (can be simple key or clientId:secret format)
            access_token: Gelato OAuth access token
        """
        self.api_key = api_key
        self.access_token = access_token
        self.headers = self._build_headers()

    def _build_headers(self):
        headers = {'Content-Type': 'application/json'}
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        elif self.api_key:
            # Gelato API uses X-API-KEY header for all API key formats
            headers['X-API-KEY'] = self.api_key
        return headers

    def _request(self, method, endpoint, **kwargs):
        """
        Make API request to Gelato.

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

    def get_stores(self):
        """Get all stores associated with the account."""
        # Use ecommerce API for stores
        url = "https://ecommerce.gelatoapis.com/v1/stores"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def validate_connection(self):
        """Validate the API key by fetching products."""
        return self._request('GET', 'products', params={'limit': 1})

    def get_products(self, store_id=None, limit=100, offset=0):
        """
        Get available products catalog.

        Args:
            store_id: Optional store ID filter
            limit: Number of products to fetch
            offset: Pagination offset

        Returns:
            List of products
        """
        params = {'limit': limit, 'offset': offset}
        if store_id:
            params['storeId'] = store_id
        return self._request('GET', 'products', params=params)

    def get_product(self, product_uid):
        """
        Get specific product details.

        Args:
            product_uid: Gelato product UID

        Returns:
            Product details
        """
        return self._request('GET', f'products/{product_uid}')

    def get_product_prices(self, product_uid, country='US'):
        """
        Get product pricing for a specific country.

        Args:
            product_uid: Gelato product UID
            country: ISO country code

        Returns:
            Pricing information
        """
        return self._request('GET', f'products/{product_uid}/prices', params={'country': country})

    def get_shipping_methods(self, country='US'):
        """
        Get available shipping methods and costs.

        Args:
            country: ISO country code

        Returns:
            Shipping methods and prices
        """
        return self._request('GET', 'shipping/methods', params={'country': country})

    def create_order(self, order_data):
        """
        Create a new order.

        Args:
            order_data: Order details including items and shipping

        Returns:
            Created order details
        """
        return self._request('POST', 'orders', json=order_data)

    def get_order(self, order_id):
        """
        Get order details.

        Args:
            order_id: Gelato order ID

        Returns:
            Order details
        """
        return self._request('GET', f'orders/{order_id}')

    def create_product(self, product_data):
        """
        Create a custom product in Gelato.

        Args:
            product_data: Product details including design files

        Returns:
            Created product details
        """
        return self._request('POST', 'products', json=product_data)


def validate_gelato_connection(api_key=None, access_token=None):
    """
    Validate Gelato API connection.

    Args:
        api_key: Gelato API key
        access_token: Gelato OAuth access token

    Returns:
        Tuple of (is_valid, result_or_error)
    """
    try:
        service = GelatoService(api_key=api_key, access_token=access_token)
        # Validate by fetching products (stores endpoint may be empty)
        products = service.validate_connection()

        # Also try to get stores
        store_list = []
        store_name = None
        email = None
        try:
            stores = service.get_stores()
            store_list = stores.get('stores', [])
            if store_list:
                first_store = store_list[0]
                store_name = first_store.get('name') or first_store.get('title')
                # Try to extract email if available
                email = first_store.get('email') or first_store.get('owner_email') or first_store.get('contact_email')
        except Exception:
            pass

        # Extract account name from API key format or store name
        account_name = store_name
        if not account_name and api_key:
            # API key format: clientId-...:secret
            # Try to extract a meaningful identifier
            if ':' in api_key:
                client_part = api_key.split(':')[0]
                # Use last 8 chars of client ID as identifier
                account_name = f"Gelato ({client_part[-8:]})"
            else:
                account_name = f"Gelato ({api_key[-8:]})"

        return True, {
            'stores': store_list,
            'store_id': store_list[0].get('id') if store_list else None,
            'products_available': len(products.get('products', [])) > 0,
            'account_name': account_name,
            'email': email,
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return False, {'error': 'Invalid API key'}
        if e.response.status_code == 403:
            return False, {'error': 'Access forbidden - check API key permissions'}
        return False, {'error': str(e)}
    except Exception as e:
        return False, {'error': str(e)}


def get_gelato_product_pricing(api_key, product_uid, country='US', access_token=None):
    """
    Get product pricing from Gelato.

    Args:
        api_key: Gelato API key
        product_uid: Product identifier
        country: Destination country
        access_token: Gelato OAuth access token

    Returns:
        Pricing information
    """
    service = GelatoService(api_key=api_key, access_token=access_token)
    try:
        prices = service.get_product_prices(product_uid, country)
        return {
            'base_price': prices.get('price'),
            'currency': prices.get('currency', 'USD'),
            'variants': prices.get('variants', [])
        }
    except Exception:
        return None


def get_gelato_shipping_cost(api_key, product_uid, country='US', quantity=1, access_token=None):
    """
    Calculate shipping cost for a Gelato product.

    Args:
        api_key: Gelato API key
        product_uid: Product identifier
        country: Destination country
        quantity: Number of items
        access_token: Gelato OAuth access token

    Returns:
        Shipping cost information
    """
    service = GelatoService(api_key=api_key, access_token=access_token)
    try:
        shipping = service.get_shipping_methods(country)
        # Get standard shipping cost
        standard = next(
            (m for m in shipping.get('methods', []) if m.get('type') == 'standard'),
            None
        )
        if standard:
            first_item = standard.get('price', 0)
            additional_item = standard.get('additionalItemPrice', first_item * 0.5)
            return {
                'first_item': first_item,
                'additional_item': additional_item,
                'total': first_item + (additional_item * (quantity - 1)) if quantity > 1 else first_item
            }
        return None
    except Exception:
        return None
