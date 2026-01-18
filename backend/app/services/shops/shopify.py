"""
Shopify API service.
Handles communication with Shopify Admin API.
"""
import re
import requests
from flask import current_app
from datetime import datetime
from app import db
from app.models import Product, ProductVariant


class ShopifyService:
    """Service for interacting with Shopify Admin API."""

    API_VERSION = '2024-01'

    def __init__(self, shop_domain, access_token):
        """
        Initialize Shopify service.

        Args:
            shop_domain: Shopify store domain (mystore.myshopify.com)
            access_token: Shopify access token
        """
        self.shop_domain = shop_domain
        self.access_token = access_token
        self.base_url = f"https://{shop_domain}/admin/api/{self.API_VERSION}"
        self.headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json'
        }

    def _request(self, method, endpoint, **kwargs):
        """
        Make API request to Shopify.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request arguments

        Returns:
            Response JSON or raises exception
        """
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_shop(self):
        """Get shop information."""
        return self._request('GET', 'shop.json')

    def get_products(self, limit=250, page_info=None):
        """
        Get products from shop.

        Args:
            limit: Number of products (max 250)
            page_info: Pagination cursor

        Returns:
            Products data with pagination
        """
        params = {'limit': limit}
        if page_info:
            params['page_info'] = page_info

        return self._request('GET', 'products.json', params=params)

    def get_product(self, product_id):
        """
        Get product details.

        Args:
            product_id: Shopify product ID

        Returns:
            Product details
        """
        return self._request('GET', f'products/{product_id}.json')

    def update_product(self, product_id, data):
        """
        Update a product.

        Args:
            product_id: Shopify product ID
            data: Update data

        Returns:
            Updated product
        """
        return self._request('PUT', f'products/{product_id}.json', json={'product': data})

    def update_variant(self, variant_id, data):
        """
        Update a product variant.

        Args:
            variant_id: Shopify variant ID
            data: Update data

        Returns:
            Updated variant
        """
        return self._request('PUT', f'variants/{variant_id}.json', json={'variant': data})

    def get_inventory_levels(self, inventory_item_ids):
        """
        Get inventory levels for items.

        Args:
            inventory_item_ids: List of inventory item IDs

        Returns:
            Inventory levels
        """
        return self._request(
            'GET',
            'inventory_levels.json',
            params={'inventory_item_ids': ','.join(str(i) for i in inventory_item_ids)}
        )


def get_shopify_shop_info(shop_domain, access_token):
    """
    Get Shopify shop information.

    Args:
        shop_domain: Shopify store domain
        access_token: Shopify access token

    Returns:
        Shop info dictionary or None
    """
    try:
        service = ShopifyService(shop_domain, access_token)
        data = service.get_shop()
        return data.get('shop', {})
    except Exception:
        return None


def sync_shopify_products(shop):
    """
    Sync products from Shopify shop.

    Args:
        shop: Shop model instance

    Returns:
        Dict with sync results
    """
    service = ShopifyService(shop.shopify_domain, shop.access_token)

    total = 0
    pod_count = 0
    page_info = None

    while True:
        try:
            products_data = service.get_products(limit=250, page_info=page_info)
        except Exception as e:
            current_app.logger.error(f"Error fetching Shopify products: {str(e)}")
            break

        products = products_data.get('products', [])
        if not products:
            break

        for shopify_product in products:
            product_id = shopify_product.get('id')
            variants = shopify_product.get('variants', [])

            # Check for POD supplier SKU patterns
            supplier_type = None
            sku_pattern = None
            first_sku = None

            for variant in variants:
                sku = variant.get('sku', '')
                if sku and not first_sku:
                    first_sku = sku
                if sku:
                    detected = _detect_supplier_from_sku(sku)
                    if detected:
                        supplier_type = detected['supplier']
                        sku_pattern = detected['pattern']
                        break

            # Get images
            images = [
                img.get('src')
                for img in shopify_product.get('images', [])
            ]

            # Create or update product
            product = Product.query.filter_by(
                shop_id=shop.id,
                listing_id=str(product_id)
            ).first()

            if not product:
                product = Product(
                    shop_id=shop.id,
                    listing_id=str(product_id)
                )
                db.session.add(product)

            # Get price from first variant
            first_variant = variants[0] if variants else {}
            price = first_variant.get('price')

            product.title = shopify_product.get('title', '')
            product.description = shopify_product.get('body_html')
            product.price = float(price) if price else None
            product.currency = 'USD'  # Shopify default
            product.sku = first_sku
            product.supplier_type = supplier_type
            product.sku_pattern = sku_pattern
            product.product_type = _extract_product_type(first_sku) or shopify_product.get('product_type')
            product.category = shopify_product.get('product_type')
            product.thumbnail_url = images[0] if images else None
            product.images = images
            product.is_active = shopify_product.get('status') == 'active'
            product.sync_status = 'synced'
            product.last_synced_at = datetime.utcnow()

            # Sync variants
            _sync_shopify_variants(product, variants)

            total += 1
            if supplier_type:
                pod_count += 1

        db.session.commit()

        # Check for next page (simplified - Shopify uses Link header for pagination)
        if len(products) < 250:
            break

    return {
        'total': total,
        'pod_count': pod_count
    }


def _sync_shopify_variants(product, shopify_variants):
    """
    Sync variants from Shopify variant data.

    Args:
        product: Product model instance
        shopify_variants: Shopify variants list
    """
    # Clear existing variants
    ProductVariant.query.filter_by(product_id=product.id).delete()

    for sv in shopify_variants:
        # Extract size and color from options
        size = None
        color = None

        option1 = sv.get('option1', '')
        option2 = sv.get('option2', '')
        option3 = sv.get('option3', '')

        # Try to identify size and color from options
        for option in [option1, option2, option3]:
            if option:
                option_lower = option.lower()
                # Check if it's a size
                if option_lower in ['xs', 's', 'm', 'l', 'xl', '2xl', '3xl', '4xl', '5xl',
                                    'small', 'medium', 'large', 'extra large']:
                    size = option
                # Check if it could be a color (not a size)
                elif not size or option_lower not in ['xs', 's', 'm', 'l', 'xl']:
                    color = option

        variant = ProductVariant(
            product_id=product.id,
            variant_id=str(sv.get('id', '')),
            sku=sv.get('sku', ''),
            size=size,
            color=color,
            price=float(sv.get('price', 0)),
            compare_at_price=float(sv.get('compare_at_price')) if sv.get('compare_at_price') else None,
            quantity=sv.get('inventory_quantity', 0),
            is_available=sv.get('inventory_quantity', 0) > 0 or sv.get('inventory_policy') == 'continue'
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
    if not sku:
        return None

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
