"""
Supplier product synchronization service.
Handles syncing product catalogs from POD suppliers.
"""
from datetime import datetime
from app import db
from app.models import SupplierConnection, SupplierProduct, SupplierType
from app.services.suppliers.gelato import GelatoService
from app.services.suppliers.printify import PrintifyService
from app.services.suppliers.printful import PrintfulService


def sync_supplier_products(connection):
    """
    Sync products from a supplier to local database.

    Args:
        connection: SupplierConnection instance

    Returns:
        Dict with sync results
    """
    if connection.supplier_type == SupplierType.GELATO.value:
        return _sync_gelato_products(connection)
    elif connection.supplier_type == SupplierType.PRINTIFY.value:
        return _sync_printify_products(connection)
    elif connection.supplier_type == SupplierType.PRINTFUL.value:
        return _sync_printful_products(connection)
    else:
        raise ValueError(f"Unsupported supplier type: {connection.supplier_type}")


def _sync_gelato_products(connection):
    """Sync products from Gelato."""
    service = GelatoService(api_key=connection.api_key, access_token=connection.access_token)
    count = 0

    try:
        # Fetch products from Gelato catalog
        offset = 0
        limit = 100

        while True:
            products_response = service.get_products(
                store_id=connection.store_id,
                limit=limit,
                offset=offset
            )

            products = products_response.get('products', [])
            if not products:
                break

            for product in products:
                _upsert_supplier_product(
                    connection=connection,
                    supplier_product_id=product.get('uid'),
                    data={
                        'name': product.get('title', product.get('name', '')),
                        'description': product.get('description'),
                        'product_type': product.get('productType'),
                        'brand': product.get('brand'),
                        'category': product.get('category'),
                        'catalog_id': product.get('catalogId'),
                        'base_price': product.get('price'),
                        'currency': product.get('currency', 'USD'),
                        'available_sizes': product.get('sizes', []),
                        'available_colors': product.get('colors', []),
                        'thumbnail_url': product.get('imageUrl'),
                        'images': product.get('images', [])
                    }
                )
                count += 1

            offset += limit
            if len(products) < limit:
                break

        return {'count': count, 'status': 'success'}

    except Exception as e:
        raise Exception(f"Failed to sync Gelato products: {str(e)}")


def _sync_printify_products(connection):
    """Sync products/blueprints from Printify."""
    service = PrintifyService(connection.api_key)
    count = 0

    try:
        # Fetch blueprints (product catalog)
        blueprints = service.get_blueprints()

        for blueprint in blueprints:
            blueprint_id = blueprint.get('id')

            # Get print providers for this blueprint
            try:
                providers = service.get_blueprint_print_providers(blueprint_id)

                # Use first available provider for pricing
                if providers:
                    provider = providers[0]
                    provider_id = provider.get('id')

                    # Get variants with pricing
                    try:
                        variants_data = service.get_print_provider_variants(
                            blueprint_id, provider_id
                        )
                        variants = variants_data.get('variants', [])

                        # Extract sizes and colors
                        sizes = list(set(v.get('size', '') for v in variants if v.get('size')))
                        colors = [
                            {'name': v.get('color', ''), 'hex': v.get('color_code')}
                            for v in variants if v.get('color')
                        ]
                        # Remove duplicates
                        seen_colors = set()
                        unique_colors = []
                        for c in colors:
                            if c['name'] not in seen_colors:
                                seen_colors.add(c['name'])
                                unique_colors.append(c)

                        # Get base price (minimum variant price)
                        prices = [v.get('price', 0) for v in variants]
                        base_price = min(prices) / 100 if prices else None  # Convert cents to dollars

                        _upsert_supplier_product(
                            connection=connection,
                            supplier_product_id=str(blueprint_id),
                            data={
                                'name': blueprint.get('title', ''),
                                'description': blueprint.get('description'),
                                'product_type': blueprint.get('model'),
                                'brand': blueprint.get('brand'),
                                'category': blueprint.get('category'),
                                'blueprint_id': str(blueprint_id),
                                'base_price': base_price,
                                'currency': 'USD',
                                'available_sizes': sizes,
                                'available_colors': unique_colors,
                                'thumbnail_url': blueprint.get('images', [{}])[0].get('src')
                                    if blueprint.get('images') else None,
                                'images': [img.get('src') for img in blueprint.get('images', [])]
                            }
                        )
                        count += 1

                    except Exception:
                        # Skip if we can't get variant pricing
                        pass

            except Exception:
                # Skip if we can't get providers
                pass

        return {'count': count, 'status': 'success'}

    except Exception as e:
        raise Exception(f"Failed to sync Printify products: {str(e)}")


def _sync_printful_products(connection):
    """Sync products from Printful."""
    service = PrintfulService(connection.api_key)
    count = 0

    try:
        # Fetch product catalog
        products = service.get_products()

        for product in products:
            product_id = product.get('id')

            # Get detailed product info with variants
            try:
                details = service.get_product(product_id)
                product_info = details.get('product', {})
                variants = details.get('variants', [])

                # Extract sizes and colors
                sizes = list(set(v.get('size', '') for v in variants if v.get('size')))
                colors = [
                    {'name': v.get('color', ''), 'hex': v.get('color_code')}
                    for v in variants if v.get('color')
                ]
                # Remove duplicates
                seen_colors = set()
                unique_colors = []
                for c in colors:
                    if c['name'] not in seen_colors:
                        seen_colors.add(c['name'])
                        unique_colors.append(c)

                # Get base price (minimum variant price)
                prices = [float(v.get('price', 0)) for v in variants]
                base_price = min(prices) if prices else None

                _upsert_supplier_product(
                    connection=connection,
                    supplier_product_id=str(product_id),
                    data={
                        'name': product_info.get('title', product.get('title', '')),
                        'description': product_info.get('description'),
                        'product_type': product_info.get('type'),
                        'brand': product_info.get('brand'),
                        'category': product_info.get('type_name'),
                        'base_price': base_price,
                        'currency': 'USD',
                        'available_sizes': sizes,
                        'available_colors': unique_colors,
                        'thumbnail_url': product_info.get('image'),
                        'images': [product_info.get('image')] if product_info.get('image') else []
                    }
                )
                count += 1

            except Exception:
                # Skip if we can't get product details
                pass

        return {'count': count, 'status': 'success'}

    except Exception as e:
        raise Exception(f"Failed to sync Printful products: {str(e)}")


def _upsert_supplier_product(connection, supplier_product_id, data):
    """
    Create or update a supplier product.

    Args:
        connection: SupplierConnection instance
        supplier_product_id: Supplier's product ID
        data: Product data dictionary
    """
    product = SupplierProduct.query.filter_by(
        supplier_connection_id=connection.id,
        supplier_product_id=supplier_product_id
    ).first()

    if not product:
        product = SupplierProduct(
            supplier_connection_id=connection.id,
            supplier_product_id=supplier_product_id
        )
        db.session.add(product)

    # Update fields
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.product_type = data.get('product_type', product.product_type)
    product.brand = data.get('brand', product.brand)
    product.category = data.get('category', product.category)
    product.blueprint_id = data.get('blueprint_id', product.blueprint_id)
    product.catalog_id = data.get('catalog_id', product.catalog_id)
    product.base_price = data.get('base_price', product.base_price)
    product.currency = data.get('currency', product.currency)
    product.available_sizes = data.get('available_sizes', product.available_sizes)
    product.available_colors = data.get('available_colors', product.available_colors)
    product.thumbnail_url = data.get('thumbnail_url', product.thumbnail_url)
    product.images = data.get('images', product.images)
    product.is_active = True
    product.updated_at = datetime.utcnow()

    db.session.commit()
