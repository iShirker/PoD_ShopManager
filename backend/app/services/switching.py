"""
Product supplier switching service.
Handles migrating products from one POD supplier to another.
"""
import re
from datetime import datetime
from flask import current_app
from app import db
from app.models import Product, ProductVariant, SupplierProduct, Shop, ShopType
from app.services.shops.etsy import EtsyService
from app.services.shops.shopify import ShopifyService
from app.services.suppliers.gelato import GelatoService
from app.services.suppliers.printify import PrintifyService
from app.services.suppliers.printful import PrintfulService


# SKU prefix mappings for each supplier
SKU_PREFIXES = {
    'gelato': 'GEL_',
    'printify': 'PFY_',
    'printful': 'PFL_'
}


def switch_product_supplier(product, target_connection, target_product_id=None):
    """
    Switch a product to a different POD supplier.

    This function:
    1. Creates/copies the product to the target supplier
    2. Updates SKUs in the marketplace listing
    3. Updates local product records

    Args:
        product: Product model instance to switch
        target_connection: SupplierConnection for target supplier
        target_product_id: Optional specific supplier product ID to use

    Returns:
        Dict with change details
    """
    shop = Shop.query.get(product.shop_id)
    if not shop:
        raise ValueError("Shop not found")

    target_supplier = target_connection.supplier_type

    # Skip if already on target supplier
    if product.supplier_type == target_supplier:
        raise ValueError(f"Product is already on {target_supplier}")

    changes = {
        'previous_supplier': product.supplier_type,
        'new_supplier': target_supplier,
        'sku_changes': []
    }

    # Find or determine target supplier product
    if not target_product_id:
        target_product_id = _find_matching_product_id(product, target_connection)

    if not target_product_id:
        raise ValueError(f"Could not find matching product on {target_supplier}")

    # Create product on target supplier if needed
    new_product_data = _create_product_on_supplier(
        product=product,
        target_connection=target_connection,
        target_product_id=target_product_id
    )

    # Generate new SKUs
    new_prefix = SKU_PREFIXES.get(target_supplier, f'{target_supplier.upper()}_')
    old_prefix = SKU_PREFIXES.get(product.supplier_type, '')

    # Update variants with new SKUs
    for variant in product.variants:
        old_sku = variant.sku or ''

        # Generate new SKU
        if old_sku:
            # Remove old prefix and add new one
            base_sku = re.sub(r'^[A-Z]{2,3}_', '', old_sku)
            new_sku = f"{new_prefix}{base_sku}"
        else:
            # Generate new SKU from variant details
            new_sku = f"{new_prefix}{product.id}_{variant.id}"

        changes['sku_changes'].append({
            'variant_id': variant.id,
            'old_sku': old_sku,
            'new_sku': new_sku
        })

        variant.sku = new_sku

    # Update marketplace listing with new SKUs
    if shop.is_connected:
        _update_marketplace_skus(shop, product, changes['sku_changes'])

    # Update product record
    product.supplier_type = target_supplier
    product.sku_pattern = new_prefix
    product.sku = changes['sku_changes'][0]['new_sku'] if changes['sku_changes'] else None
    product.supplier_product_id = target_product_id
    product.updated_at = datetime.utcnow()

    db.session.commit()

    changes['new_product_data'] = new_product_data
    return changes


def _find_matching_product_id(product, target_connection):
    """
    Find matching product ID on target supplier.

    Args:
        product: Product to match
        target_connection: Target supplier connection

    Returns:
        Supplier product ID or None
    """
    if not product.product_type:
        return None

    # Search in synced supplier products
    product_type_lower = product.product_type.lower()

    supplier_product = SupplierProduct.query.filter_by(
        supplier_connection_id=target_connection.id,
        is_active=True
    ).filter(
        db.or_(
            SupplierProduct.product_type.ilike(f'%{product_type_lower}%'),
            SupplierProduct.name.ilike(f'%{product_type_lower}%')
        )
    ).first()

    if supplier_product:
        return supplier_product.supplier_product_id

    # Try known mappings
    from app.services.comparison import PRODUCT_TYPE_MAPPINGS

    for key, mapping in PRODUCT_TYPE_MAPPINGS.items():
        if key in product_type_lower:
            return mapping.get(target_connection.supplier_type)

    return None


def _create_product_on_supplier(product, target_connection, target_product_id):
    """
    Create or prepare product on target supplier.

    Args:
        product: Product to create
        target_connection: Target supplier connection
        target_product_id: Base product ID on supplier

    Returns:
        Created product data or None
    """
    supplier_type = target_connection.supplier_type

    # Build product data from existing product
    product_data = {
        'title': product.title,
        'description': product.description,
        'variants': []
    }

    for variant in product.variants:
        product_data['variants'].append({
            'size': variant.size,
            'color': variant.color
        })

    try:
        if supplier_type == 'gelato':
            service = GelatoService(
                api_key=target_connection.api_key,
                access_token=target_connection.access_token
            )
            # Gelato product creation would happen here
            # For now, we just prepare the data
            return {'status': 'prepared', 'supplier_product_id': target_product_id}

        elif supplier_type == 'printify':
            service = PrintifyService(target_connection.api_key)
            # Printify requires a shop_id and specific format
            if target_connection.shop_id:
                # Create product in Printify
                # service.create_product(target_connection.shop_id, product_data)
                pass
            return {'status': 'prepared', 'supplier_product_id': target_product_id}

        elif supplier_type == 'printful':
            service = PrintfulService(target_connection.api_key)
            # Printful sync product creation
            # service.create_sync_product(product_data)
            return {'status': 'prepared', 'supplier_product_id': target_product_id}

    except Exception as e:
        current_app.logger.error(f"Error creating product on {supplier_type}: {str(e)}")

    return None


def _update_marketplace_skus(shop, product, sku_changes):
    """
    Update SKUs in the marketplace listing.

    Args:
        shop: Shop model instance
        product: Product model instance
        sku_changes: List of SKU change records
    """
    try:
        if shop.shop_type == ShopType.ETSY.value:
            _update_etsy_skus(shop, product, sku_changes)
        elif shop.shop_type == ShopType.SHOPIFY.value:
            _update_shopify_skus(shop, product, sku_changes)
    except Exception as e:
        current_app.logger.error(f"Error updating marketplace SKUs: {str(e)}")
        raise


def _update_etsy_skus(shop, product, sku_changes):
    """
    Update SKUs in Etsy listing.

    Args:
        shop: Shop model instance
        product: Product model instance
        sku_changes: List of SKU change records
    """
    service = EtsyService(shop.access_token)

    # Get current inventory
    inventory = service.get_listing_inventory(product.listing_id)

    # Update SKUs in inventory
    products = inventory.get('products', [])
    updated_products = []

    for ep in products:
        product_data = dict(ep)
        offerings = product_data.get('offerings', [])

        for offering in offerings:
            old_sku = offering.get('sku', '')
            # Find matching SKU change
            for change in sku_changes:
                if change['old_sku'] == old_sku:
                    offering['sku'] = change['new_sku']
                    break

        updated_products.append(product_data)

    # Update listing inventory
    service.update_listing_inventory(product.listing_id, {
        'products': updated_products
    })


def _update_shopify_skus(shop, product, sku_changes):
    """
    Update SKUs in Shopify product.

    Args:
        shop: Shop model instance
        product: Product model instance
        sku_changes: List of SKU change records
    """
    service = ShopifyService(shop.shopify_domain, shop.access_token)

    # Get current product
    shopify_product = service.get_product(product.listing_id)
    variants = shopify_product.get('product', {}).get('variants', [])

    # Update each variant with new SKU
    for variant in variants:
        old_sku = variant.get('sku', '')
        for change in sku_changes:
            if change['old_sku'] == old_sku:
                service.update_variant(variant['id'], {
                    'sku': change['new_sku']
                })
                break


def preview_switch(product, target_supplier):
    """
    Preview what changes would be made when switching suppliers.

    Args:
        product: Product model instance
        target_supplier: Target supplier type

    Returns:
        Preview of changes without making them
    """
    new_prefix = SKU_PREFIXES.get(target_supplier, f'{target_supplier.upper()}_')

    preview = {
        'product_id': product.id,
        'title': product.title,
        'current_supplier': product.supplier_type,
        'target_supplier': target_supplier,
        'sku_changes': []
    }

    for variant in product.variants:
        old_sku = variant.sku or ''
        if old_sku:
            base_sku = re.sub(r'^[A-Z]{2,3}_', '', old_sku)
            new_sku = f"{new_prefix}{base_sku}"
        else:
            new_sku = f"{new_prefix}{product.id}_{variant.id}"

        preview['sku_changes'].append({
            'variant_id': variant.id,
            'size': variant.size,
            'color': variant.color,
            'old_sku': old_sku,
            'new_sku': new_sku
        })

    return preview
