"""
Template service.
Handles creating listings from templates.
"""
from datetime import datetime
from flask import current_app
from app import db
from app.models import (
    ListingTemplate, TemplateProduct, Shop, ShopType,
    Product, ProductVariant, SupplierConnection
)
from app.services.shops.etsy import EtsyService
from app.services.shops.shopify import ShopifyService


# SKU prefix mappings
SKU_PREFIXES = {
    'gelato': 'GEL_',
    'printify': 'PFY_',
    'printful': 'PFL_'
}


def create_listing_from_template(template, shop, title=None, description=None,
                                  price=None, tags=None, images=None):
    """
    Create a listing from a template.

    Args:
        template: ListingTemplate model instance
        shop: Shop model instance
        title: Optional title override
        description: Optional description override
        price: Optional price override
        tags: Optional tags override
        images: List of image URLs

    Returns:
        Created listing data
    """
    # Build listing data
    listing_title = title or template.default_title or f"New Listing from {template.name}"
    listing_description = description or template.default_description or ""
    listing_tags = tags or template.default_tags or []

    # Get template products
    template_products = template.template_products.filter_by(is_active=True).order_by(
        TemplateProduct.display_order
    ).all()

    if not template_products:
        raise ValueError("Template has no products")

    # Build variants from template products
    variants = []
    for tp in template_products:
        prefix = SKU_PREFIXES.get(tp.supplier_type, 'POD_')
        sizes = tp.selected_sizes or ['One Size']
        colors = tp.colors.filter_by(is_active=True).all()

        for size in sizes:
            for color in colors:
                sku = _generate_sku(prefix, tp.id, size, color.color_name)

                # Calculate price
                variant_price = price
                if not variant_price:
                    if tp.price_override:
                        variant_price = tp.price_override
                    elif template.default_price_fixed:
                        variant_price = template.default_price_fixed
                    elif tp.price_markup or template.default_price_markup:
                        markup = tp.price_markup or template.default_price_markup
                        # Would need base price from supplier to calculate
                        variant_price = 25.00  # Default fallback

                variants.append({
                    'supplier': tp.supplier_type,
                    'product_name': tp.product_name,
                    'size': size,
                    'color': color.display_name or color.color_name,
                    'color_hex': color.color_hex,
                    'sku': sku,
                    'price': variant_price,
                    'supplier_color_id': color.supplier_color_id
                })

    # Create listing based on shop type
    if shop.shop_type == ShopType.ETSY.value:
        return _create_etsy_listing(
            shop=shop,
            title=listing_title,
            description=listing_description,
            tags=listing_tags,
            variants=variants,
            images=images,
            category=template.etsy_category
        )
    elif shop.shop_type == ShopType.SHOPIFY.value:
        return _create_shopify_listing(
            shop=shop,
            title=listing_title,
            description=listing_description,
            tags=listing_tags,
            variants=variants,
            images=images,
            category=template.shopify_category
        )
    else:
        raise ValueError(f"Unsupported shop type: {shop.shop_type}")


def _generate_sku(prefix, product_id, size, color):
    """Generate a SKU from components."""
    # Clean up size and color for SKU
    size_clean = size.upper().replace(' ', '')
    color_clean = color.upper().replace(' ', '_').replace('-', '_')[:10]
    return f"{prefix}{product_id}_{size_clean}_{color_clean}"


def _create_etsy_listing(shop, title, description, tags, variants, images, category):
    """
    Create a listing on Etsy.

    Args:
        shop: Shop model instance
        title: Listing title
        description: Listing description
        tags: List of tags
        variants: List of variant dictionaries
        images: List of image URLs
        category: Etsy category ID

    Returns:
        Created listing data
    """
    service = EtsyService(shop.access_token)

    # Etsy has specific requirements
    # - Max 13 tags
    # - Title max 140 chars
    # - Description has specific formatting

    listing_data = {
        'title': title[:140],
        'description': description,
        'tags': tags[:13] if tags else [],
        'quantity': 999,  # High quantity for POD
        'price': variants[0]['price'] if variants else 25.00,
        'who_made': 'i_did',
        'when_made': 'made_to_order',
        'taxonomy_id': int(category) if category else None,
        'is_digital': False,
        'is_personalizable': False,
        'personalization_is_required': False,
        'should_auto_renew': True,
        'shipping_profile_id': None,  # Would need to be set
        'return_policy_id': None,  # Would need to be set
    }

    # Note: In production, you would:
    # 1. Create the listing
    # 2. Upload images
    # 3. Create inventory with variants

    # For now, return mock response
    current_app.logger.info(f"Would create Etsy listing: {title}")

    result = {
        'platform': 'etsy',
        'status': 'draft',  # Would be actual status
        'title': title,
        'variant_count': len(variants),
        'listing_data': listing_data,
        'variants': variants[:5]  # First 5 for preview
    }

    # Create local product record
    product = Product(
        shop_id=shop.id,
        listing_id=f"draft_{datetime.utcnow().timestamp()}",
        title=title,
        description=description,
        price=variants[0]['price'] if variants else None,
        supplier_type=variants[0]['supplier'] if variants else None,
        sku=variants[0]['sku'] if variants else None,
        is_active=False,  # Draft
        sync_status='pending'
    )
    db.session.add(product)

    # Add variants
    for v in variants:
        variant = ProductVariant(
            product=product,
            variant_id=f"draft_{v['sku']}",
            sku=v['sku'],
            size=v['size'],
            color=v['color'],
            price=v['price'],
            is_available=True
        )
        db.session.add(variant)

    db.session.commit()

    result['product_id'] = product.id
    return result


def _create_shopify_listing(shop, title, description, tags, variants, images, category):
    """
    Create a product on Shopify.

    Args:
        shop: Shop model instance
        title: Product title
        description: Product description (HTML)
        tags: List of tags
        variants: List of variant dictionaries
        images: List of image URLs
        category: Shopify collection name

    Returns:
        Created product data
    """
    service = ShopifyService(shop.shopify_domain, shop.access_token)

    # Build Shopify product structure
    shopify_variants = []
    for v in variants:
        shopify_variants.append({
            'title': f"{v['size']} / {v['color']}",
            'option1': v['size'],
            'option2': v['color'],
            'price': str(v['price']),
            'sku': v['sku'],
            'inventory_management': None,  # POD doesn't track inventory
            'inventory_policy': 'continue',
            'requires_shipping': True,
            'taxable': True,
        })

    product_data = {
        'title': title,
        'body_html': description,
        'vendor': 'POD Manager',
        'product_type': category or 'Apparel',
        'tags': ','.join(tags) if tags else '',
        'status': 'draft',  # Create as draft first
        'options': [
            {'name': 'Size'},
            {'name': 'Color'}
        ],
        'variants': shopify_variants,
    }

    # Note: In production, you would:
    # 1. Create the product
    # 2. Upload images
    # 3. Possibly add to collection

    current_app.logger.info(f"Would create Shopify product: {title}")

    result = {
        'platform': 'shopify',
        'status': 'draft',
        'title': title,
        'variant_count': len(variants),
        'product_data': product_data,
        'variants': variants[:5]
    }

    # Create local product record
    product = Product(
        shop_id=shop.id,
        listing_id=f"draft_{datetime.utcnow().timestamp()}",
        title=title,
        description=description,
        price=variants[0]['price'] if variants else None,
        supplier_type=variants[0]['supplier'] if variants else None,
        sku=variants[0]['sku'] if variants else None,
        category=category,
        is_active=False,
        sync_status='pending'
    )
    db.session.add(product)

    for v in variants:
        variant = ProductVariant(
            product=product,
            variant_id=f"draft_{v['sku']}",
            sku=v['sku'],
            size=v['size'],
            color=v['color'],
            price=v['price'],
            is_available=True
        )
        db.session.add(variant)

    db.session.commit()

    result['product_id'] = product.id
    return result


def duplicate_template(template, new_name=None):
    """
    Duplicate a template with all its products and colors.

    Args:
        template: ListingTemplate to duplicate
        new_name: Name for the new template

    Returns:
        New ListingTemplate instance
    """
    new_template = ListingTemplate(
        user_id=template.user_id,
        name=new_name or f"{template.name} (Copy)",
        description=template.description,
        default_title=template.default_title,
        default_description=template.default_description,
        default_tags=template.default_tags.copy() if template.default_tags else [],
        default_price_markup=template.default_price_markup,
        default_price_fixed=template.default_price_fixed,
        target_platforms=template.target_platforms.copy() if template.target_platforms else [],
        etsy_category=template.etsy_category,
        shopify_category=template.shopify_category,
        is_active=True
    )
    db.session.add(new_template)
    db.session.flush()  # Get ID for new template

    # Copy products
    for tp in template.template_products.all():
        new_tp = TemplateProduct(
            template_id=new_template.id,
            supplier_product_id=tp.supplier_product_id,
            supplier_type=tp.supplier_type,
            external_product_id=tp.external_product_id,
            product_name=tp.product_name,
            product_type=tp.product_type,
            selected_sizes=tp.selected_sizes.copy() if tp.selected_sizes else [],
            price_override=tp.price_override,
            price_markup=tp.price_markup,
            display_order=tp.display_order,
            is_active=tp.is_active
        )
        db.session.add(new_tp)
        db.session.flush()

        # Copy colors
        for color in tp.colors.all():
            from app.models import TemplateColor
            new_color = TemplateColor(
                template_product_id=new_tp.id,
                color_name=color.color_name,
                color_hex=color.color_hex,
                supplier_color_id=color.supplier_color_id,
                display_name=color.display_name,
                is_active=color.is_active
            )
            db.session.add(new_color)

    db.session.commit()
    return new_template
