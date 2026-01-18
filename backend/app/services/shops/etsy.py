"""
Etsy API service.
Handles communication with Etsy Open API v3.
"""
import re
import requests
from flask import current_app
from datetime import datetime
from app import db
from app.models import Product, ProductVariant


class EtsyService:
    """Service for interacting with Etsy API."""

    BASE_URL = 'https://openapi.etsy.com/v3'

    def __init__(self, access_token):
        """
        Initialize Etsy service.

        Args:
            access_token: Etsy OAuth access token
        """
        self.access_token = access_token
        self.api_key = current_app.config.get('ETSY_API_KEY', '')
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

    def _request(self, method, endpoint, **kwargs):
        """
        Make API request to Etsy.

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

    def get_me(self):
        """Get current user info."""
        return self._request('GET', 'application/users/me')

    def get_shops(self, user_id):
        """
        Get shops owned by user.

        Args:
            user_id: Etsy user ID

        Returns:
            List of shops
        """
        return self._request('GET', f'application/users/{user_id}/shops')

    def get_shop(self, shop_id):
        """
        Get shop details.

        Args:
            shop_id: Etsy shop ID

        Returns:
            Shop details
        """
        return self._request('GET', f'application/shops/{shop_id}')

    def get_listings(self, shop_id, state='active', limit=100, offset=0):
        """
        Get shop listings.

        Args:
            shop_id: Etsy shop ID
            state: Listing state (active, inactive, draft, etc.)
            limit: Number of listings
            offset: Pagination offset

        Returns:
            Listings data
        """
        return self._request(
            'GET',
            f'application/shops/{shop_id}/listings',
            params={
                'state': state,
                'limit': limit,
                'offset': offset
            }
        )

    def get_listing(self, listing_id, includes=None):
        """
        Get listing details.

        Args:
            listing_id: Etsy listing ID
            includes: Additional data to include (Images, Inventory, etc.)

        Returns:
            Listing details
        """
        params = {}
        if includes:
            params['includes'] = ','.join(includes) if isinstance(includes, list) else includes
        return self._request('GET', f'application/listings/{listing_id}', params=params)

    def get_listing_inventory(self, listing_id):
        """
        Get listing inventory (variants/offerings).

        Args:
            listing_id: Etsy listing ID

        Returns:
            Inventory data with SKUs
        """
        return self._request('GET', f'application/listings/{listing_id}/inventory')

    def get_listing_images(self, listing_id):
        """
        Get listing images.

        Args:
            listing_id: Etsy listing ID

        Returns:
            List of images
        """
        return self._request('GET', f'application/listings/{listing_id}/images')

    def update_listing(self, shop_id, listing_id, data):
        """
        Update a listing.

        Args:
            shop_id: Etsy shop ID
            listing_id: Listing ID
            data: Update data

        Returns:
            Updated listing
        """
        return self._request(
            'PATCH',
            f'application/shops/{shop_id}/listings/{listing_id}',
            json=data
        )

    def update_listing_inventory(self, listing_id, inventory_data):
        """
        Update listing inventory (SKUs).

        Args:
            listing_id: Listing ID
            inventory_data: Inventory update data

        Returns:
            Updated inventory
        """
        return self._request(
            'PUT',
            f'application/listings/{listing_id}/inventory',
            json=inventory_data
        )


def get_etsy_shops(access_token):
    """
    Get Etsy shops for the authenticated user.

    Args:
        access_token: Etsy OAuth access token

    Returns:
        List of shop dictionaries
    """
    service = EtsyService(access_token)

    # Get user info first
    user = service.get_me()
    user_id = user.get('user_id')

    if not user_id:
        return []

    # Get shops
    shops_data = service.get_shops(user_id)
    shops = []

    for shop in shops_data.get('results', []):
        shops.append({
            'shop_id': shop.get('shop_id'),
            'shop_name': shop.get('shop_name'),
            'url': shop.get('url'),
            'icon_url': shop.get('icon_url_fullxfull'),
            'listing_count': shop.get('listing_active_count', 0)
        })

    return shops


def sync_etsy_listings(shop):
    """
    Sync listings from Etsy shop.

    Args:
        shop: Shop model instance

    Returns:
        Dict with sync results
    """
    service = EtsyService(shop.access_token)

    total = 0
    pod_count = 0
    offset = 0
    limit = 100

    while True:
        listings_data = service.get_listings(
            shop.shop_id,
            state='active',
            limit=limit,
            offset=offset
        )

        listings = listings_data.get('results', [])
        if not listings:
            break

        for listing in listings:
            listing_id = listing.get('listing_id')

            # Get inventory for SKUs
            try:
                inventory = service.get_listing_inventory(listing_id)
                products = inventory.get('products', [])

                # Check for POD supplier SKU patterns
                supplier_type = None
                sku_pattern = None
                skus = []

                for product in products:
                    offerings = product.get('offerings', [])
                    for offering in offerings:
                        sku = offering.get('sku', '') or product.get('sku', '')
                        if sku:
                            skus.append(sku)
                            detected = _detect_supplier_from_sku(sku)
                            if detected:
                                supplier_type = detected['supplier']
                                sku_pattern = detected['pattern']

                # Get images
                images = []
                try:
                    images_data = service.get_listing_images(listing_id)
                    images = [
                        img.get('url_fullxfull') or img.get('url_570xN')
                        for img in images_data.get('results', [])
                    ]
                except Exception:
                    pass

                # Create or update product
                product = Product.query.filter_by(
                    shop_id=shop.id,
                    listing_id=str(listing_id)
                ).first()

                if not product:
                    product = Product(
                        shop_id=shop.id,
                        listing_id=str(listing_id)
                    )
                    db.session.add(product)

                product.title = listing.get('title', '')
                product.description = listing.get('description')
                product.price = listing.get('price', {}).get('amount', 0) / 100 if listing.get('price') else None
                product.currency = listing.get('price', {}).get('currency_code', 'USD') if listing.get('price') else 'USD'
                product.sku = skus[0] if skus else None
                product.supplier_type = supplier_type
                product.sku_pattern = sku_pattern
                product.product_type = _extract_product_type(skus[0]) if skus else None
                product.thumbnail_url = images[0] if images else None
                product.images = images
                product.is_active = True
                product.sync_status = 'synced'
                product.last_synced_at = datetime.utcnow()

                # Sync variants
                _sync_etsy_variants(product, products)

                total += 1
                if supplier_type:
                    pod_count += 1

            except Exception as e:
                current_app.logger.error(f"Error syncing listing {listing_id}: {str(e)}")
                continue

        db.session.commit()
        offset += limit

        if len(listings) < limit:
            break

    return {
        'total': total,
        'pod_count': pod_count
    }


def _sync_etsy_variants(product, etsy_products):
    """
    Sync variants from Etsy product data.

    Args:
        product: Product model instance
        etsy_products: Etsy inventory products list
    """
    # Clear existing variants
    ProductVariant.query.filter_by(product_id=product.id).delete()

    for ep in etsy_products:
        property_values = ep.get('property_values', [])

        # Extract size and color from property values
        size = None
        color = None

        for prop in property_values:
            prop_name = prop.get('property_name', '').lower()
            values = prop.get('values', [])
            if 'size' in prop_name and values:
                size = values[0]
            elif 'color' in prop_name and values:
                color = values[0]

        # Get offerings (price/quantity for this variant)
        offerings = ep.get('offerings', [])
        for offering in offerings:
            variant = ProductVariant(
                product_id=product.id,
                variant_id=str(ep.get('product_id', offering.get('offering_id', ''))),
                sku=offering.get('sku', '') or ep.get('sku', ''),
                size=size,
                color=color,
                price=offering.get('price', {}).get('amount', 0) / 100 if offering.get('price') else None,
                quantity=offering.get('quantity', 0),
                is_available=offering.get('is_enabled', True)
            )
            db.session.add(variant)


def _detect_supplier_from_sku(sku):
    """
    Detect POD supplier from SKU pattern.

    Args:
        sku: Product SKU string

    Returns:
        Dict with supplier and pattern or None
    """
    sku_lower = sku.lower()

    # Common SKU patterns for different suppliers
    patterns = [
        # Gelato patterns
        (r'^gel[_-]', 'gelato', 'gel_'),
        (r'^gelato[_-]', 'gelato', 'gelato_'),
        (r'^glt[_-]', 'gelato', 'glt_'),

        # Printify patterns
        (r'^pfy[_-]', 'printify', 'pfy_'),
        (r'^printify[_-]', 'printify', 'printify_'),
        (r'^prf[_-]', 'printify', 'prf_'),

        # Printful patterns
        (r'^pfl[_-]', 'printful', 'pfl_'),
        (r'^printful[_-]', 'printful', 'printful_'),
        (r'^pf[_-]', 'printful', 'pf_'),

        # Generic patterns with supplier in SKU
        (r'gelato', 'gelato', 'gelato'),
        (r'printify', 'printify', 'printify'),
        (r'printful', 'printful', 'printful'),
    ]

    for pattern, supplier, prefix in patterns:
        if re.search(pattern, sku_lower):
            return {'supplier': supplier, 'pattern': prefix}

    return None


def _extract_product_type(sku):
    """
    Extract product type from SKU.

    Args:
        sku: Product SKU string

    Returns:
        Product type string or None
    """
    if not sku:
        return None

    # Common product codes in SKUs
    product_patterns = {
        r'gildan[_-]?18000': 'Gildan 18000 (Heavy Blend Sweatshirt)',
        r'gildan[_-]?18500': 'Gildan 18500 (Heavy Blend Hoodie)',
        r'gildan[_-]?5000': 'Gildan 5000 (Heavy Cotton Tee)',
        r'gildan[_-]?64000': 'Gildan 64000 (Softstyle Tee)',
        r'bella[_-]?3001': 'Bella Canvas 3001 (Unisex Jersey Tee)',
        r'bella[_-]?3413': 'Bella Canvas 3413 (Triblend Tee)',
        r'comfort[_-]?colors[_-]?1717': 'Comfort Colors 1717 (Garment Dyed Tee)',
        r'next[_-]?level[_-]?3600': 'Next Level 3600 (Unisex Tee)',
        r'champion[_-]?s700': 'Champion S700 (Double Dry Tee)',
    }

    sku_lower = sku.lower()
    for pattern, product_type in product_patterns.items():
        if re.search(pattern, sku_lower):
            return product_type

    return None
