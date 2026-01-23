"""
Printful API service.
Handles communication with Printful Print on Demand API.
"""
import requests
from flask import current_app


class PrintfulService:
    """Service for interacting with Printful API."""

    BASE_URL = 'https://api.printful.com'

    def __init__(self, api_key):
        """
        Initialize Printful service.

        Args:
            api_key: Printful API key
        """
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def _request(self, method, endpoint, **kwargs):
        """
        Make API request to Printful.

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
        data = response.json()
        return data.get('result', data)

    def get_store_info(self):
        """Get store information."""
        return self._request('GET', 'store')

    def get_products(self):
        """Get catalog of available products."""
        return self._request('GET', 'products')
    
    def get_categories(self):
        """Get list of all product categories."""
        return self._request('GET', 'categories')

    def get_product(self, product_id):
        """
        Get specific product details.

        Args:
            product_id: Printful product ID

        Returns:
            Product details including variants
        """
        return self._request('GET', f'products/{product_id}')

    def get_variant(self, variant_id):
        """
        Get specific variant details.

        Args:
            variant_id: Printful variant ID

        Returns:
            Variant details with pricing
        """
        return self._request('GET', f'products/variant/{variant_id}')

    def get_sync_products(self, limit=100, offset=0):
        """
        Get synced products from connected store.

        Args:
            limit: Number of items
            offset: Pagination offset

        Returns:
            List of synced products
        """
        return self._request('GET', 'sync/products', params={
            'limit': limit,
            'offset': offset
        })

    def get_sync_product(self, sync_product_id):
        """
        Get specific synced product.

        Args:
            sync_product_id: Sync product ID

        Returns:
            Synced product details
        """
        return self._request('GET', f'sync/products/{sync_product_id}')

    def create_sync_product(self, product_data):
        """
        Create a synced product.

        Args:
            product_data: Product details

        Returns:
            Created product
        """
        return self._request('POST', 'sync/products', json=product_data)

    def get_shipping_rates(self, recipient, items):
        """
        Calculate shipping rates.

        Args:
            recipient: Shipping address
            items: List of items

        Returns:
            Available shipping rates
        """
        return self._request('POST', 'shipping/rates', json={
            'recipient': recipient,
            'items': items
        })

    def get_countries(self):
        """Get list of supported countries."""
        return self._request('GET', 'countries')

    def create_order(self, order_data):
        """
        Create a new order.

        Args:
            order_data: Order details

        Returns:
            Created order
        """
        return self._request('POST', 'orders', json=order_data)

    def get_order(self, order_id):
        """
        Get order details.

        Args:
            order_id: Printful order ID

        Returns:
            Order details
        """
        return self._request('GET', f'orders/{order_id}')

    def estimate_costs(self, order_data):
        """
        Estimate order costs without creating order.

        Args:
            order_data: Order details

        Returns:
            Cost estimate
        """
        return self._request('POST', 'orders/estimate-costs', json=order_data)


def validate_printful_connection(api_key):
    """
    Validate Printful API connection.

    Args:
        api_key: Printful API key

    Returns:
        Tuple of (is_valid, result_or_error)
    """
    try:
        service = PrintfulService(api_key)
        store = service.get_store_info()

        # Extract email if available in store info
        email = store.get('email') or store.get('owner_email') or store.get('contact_email')

        return True, {
            'store': store,
            'store_id': store.get('id'),
            'store_name': store.get('name'),
            'account_name': store.get('name') or f"Printful ({api_key[-8:]})",
            'email': email,
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return False, {'error': 'Invalid API key'}
        return False, {'error': str(e)}
    except Exception as e:
        return False, {'error': str(e)}


def get_printful_product_pricing(api_key, product_id):
    """
    Get product pricing from Printful.

    Args:
        api_key: Printful API key
        product_id: Product ID

    Returns:
        Pricing information with variants
    """
    service = PrintfulService(api_key)
    try:
        product = service.get_product(product_id)
        variants = product.get('variants', [])

        return {
            'product': product.get('product', {}),
            'variants': [
                {
                    'id': v.get('id'),
                    'name': v.get('name'),
                    'size': v.get('size'),
                    'color': v.get('color'),
                    'color_code': v.get('color_code'),
                    'price': float(v.get('price', 0))
                }
                for v in variants
            ],
            'currency': 'USD'
        }
    except Exception:
        return None


def get_printful_shipping_cost(api_key, variant_id, country='US', quantity=1):
    """
    Get shipping cost for a Printful product.

    Args:
        api_key: Printful API key
        variant_id: Variant ID
        country: Destination country code
        quantity: Number of items

    Returns:
        Shipping cost information
    """
    service = PrintfulService(api_key)
    try:
        rates = service.get_shipping_rates(
            recipient={
                'country_code': country,
                'state_code': None,
                'city': 'Anytown',
                'zip': '12345'
            },
            items=[{
                'variant_id': variant_id,
                'quantity': quantity
            }]
        )

        # Get standard shipping
        standard = next(
            (r for r in rates if r.get('id') == 'STANDARD'),
            rates[0] if rates else None
        )

        if standard:
            total = float(standard.get('rate', 0))
            # Estimate per-item costs
            if quantity > 1:
                first_item = total * 0.7  # Approximate
                additional = (total - first_item) / (quantity - 1)
            else:
                first_item = total
                additional = total * 0.3  # Approximate for additional items

            return {
                'first_item': round(first_item, 2),
                'additional_item': round(additional, 2),
                'total': total,
                'currency': standard.get('currency', 'USD'),
                'shipping_method': standard.get('name', 'Standard')
            }
        return None
    except Exception:
        return None
