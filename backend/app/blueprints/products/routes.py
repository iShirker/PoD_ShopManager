"""
Product comparison and switching routes.
Handles supplier comparison and product migration between suppliers.
"""
import re
import requests
from datetime import datetime
from flask import request, jsonify, make_response, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.blueprints.products import products_bp
from app.models import (
    User, Product, Shop, SupplierConnection, SupplierProduct, SupplierType,
    UserProduct, UserProductSupplier
)
from app.services.comparison import (
    compare_product_prices,
    find_matching_supplier_products,
    get_comparison_summary
)
from app.services.switching import switch_product_supplier


def _strip_html(text):
    """Strip HTML tags from text."""
    if not text:
        return None
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', str(text))
    # Decode common HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    return text.strip()


@products_bp.route('/compare', methods=['GET'])
@jwt_required()
def compare_products():
    """
    Get price comparison across suppliers for user's products.

    Query params:
        product_type: Filter by product type (e.g., "Gildan 18000")
        shop_id: Filter by shop
        supplier: Current supplier to compare from

    Returns:
        List of products with price comparisons across suppliers
    """
    user_id = get_jwt_identity()

    # Get filters
    product_type = request.args.get('product_type', '')
    shop_id = request.args.get('shop_id', type=int)
    current_supplier = request.args.get('supplier', '')

    # Get user's shops
    shops_query = Shop.query.filter_by(user_id=user_id, is_connected=True)
    if shop_id:
        shops_query = shops_query.filter_by(id=shop_id)
    shops = shops_query.all()

    if not shops:
        return jsonify({'error': 'No connected shops found'}), 404

    shop_ids = [s.id for s in shops]

    # Get POD products from shops
    query = Product.query.filter(
        Product.shop_id.in_(shop_ids),
        Product.supplier_type.isnot(None)
    )

    if product_type:
        query = query.filter(Product.product_type.ilike(f'%{product_type}%'))

    if current_supplier:
        query = query.filter(Product.supplier_type == current_supplier)

    products = query.all()

    if not products:
        return jsonify({
            'products': [],
            'message': 'No POD products found'
        })

    # Get user's supplier connections
    connections = SupplierConnection.query.filter_by(
        user_id=user_id,
        is_connected=True
    ).all()

    connection_map = {c.supplier_type: c for c in connections}

    # Build comparison data
    comparisons = []
    for product in products:
        comparison = compare_product_prices(product, connection_map)
        if comparison:
            comparisons.append(comparison)

    return jsonify({
        'products': comparisons,
        'total': len(comparisons),
        'suppliers_connected': list(connection_map.keys())
    })


@products_bp.route('/compare/summary', methods=['GET'])
@jwt_required()
def get_comparison_overview():
    """
    Get summary of potential savings across all products.

    Returns:
        Summary with total potential savings and products by supplier
    """
    user_id = get_jwt_identity()

    # Get user's shops
    shops = Shop.query.filter_by(user_id=user_id, is_connected=True).all()
    if not shops:
        return jsonify({'error': 'No connected shops found'}), 404

    shop_ids = [s.id for s in shops]

    # Get all POD products
    products = Product.query.filter(
        Product.shop_id.in_(shop_ids),
        Product.supplier_type.isnot(None)
    ).all()

    # Get supplier connections
    connections = SupplierConnection.query.filter_by(
        user_id=user_id,
        is_connected=True
    ).all()
    connection_map = {c.supplier_type: c for c in connections}

    summary = get_comparison_summary(products, connection_map)

    return jsonify(summary)


@products_bp.route('/compare/<int:product_id>', methods=['GET'])
@jwt_required()
def compare_single_product(product_id):
    """
    Get detailed price comparison for a single product.

    Args:
        product_id: Product ID

    Returns:
        Detailed comparison across all connected suppliers
    """
    user_id = get_jwt_identity()

    # Verify product belongs to user
    product = Product.query.join(Shop).filter(
        Product.id == product_id,
        Shop.user_id == user_id
    ).first()

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Get supplier connections
    connections = SupplierConnection.query.filter_by(
        user_id=user_id,
        is_connected=True
    ).all()
    connection_map = {c.supplier_type: c for c in connections}

    comparison = compare_product_prices(product, connection_map, detailed=True)

    if not comparison:
        return jsonify({'error': 'Unable to compare product'}), 400

    return jsonify(comparison)


@products_bp.route('/switch', methods=['POST'])
@jwt_required()
def switch_supplier():
    """
    Switch a product to a different supplier.

    Request body:
        product_id: Product ID to switch
        target_supplier: Supplier to switch to (gelato, printify, printful)
        target_product_id: Optional specific supplier product ID to use

    Returns:
        Switch result with updated product info
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    product_id = data.get('product_id')
    target_supplier = data.get('target_supplier')
    target_product_id = data.get('target_product_id')

    if not product_id or not target_supplier:
        return jsonify({'error': 'product_id and target_supplier are required'}), 400

    if target_supplier not in [s.value for s in SupplierType]:
        return jsonify({'error': 'Invalid target supplier'}), 400

    # Verify product belongs to user
    product = Product.query.join(Shop).filter(
        Product.id == product_id,
        Shop.user_id == user_id
    ).first()

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Get target supplier connection
    connection = SupplierConnection.query.filter_by(
        user_id=user_id,
        supplier_type=target_supplier,
        is_connected=True
    ).first()

    if not connection:
        return jsonify({'error': f'{target_supplier} is not connected'}), 400

    try:
        result = switch_product_supplier(
            product=product,
            target_connection=connection,
            target_product_id=target_product_id
        )

        return jsonify({
            'message': f'Product switched to {target_supplier}',
            'product': product.to_dict(include_variants=True),
            'changes': result
        })

    except Exception as e:
        return jsonify({'error': f'Switch failed: {str(e)}'}), 500


@products_bp.route('/switch/bulk', methods=['POST'])
@jwt_required()
def bulk_switch_supplier():
    """
    Switch multiple products to a different supplier.

    Request body:
        product_ids: List of product IDs to switch
        target_supplier: Supplier to switch to
        product_type: Optional product type filter

    Returns:
        Bulk switch results
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    product_ids = data.get('product_ids', [])
    target_supplier = data.get('target_supplier')
    product_type = data.get('product_type')

    if not target_supplier:
        return jsonify({'error': 'target_supplier is required'}), 400

    if target_supplier not in [s.value for s in SupplierType]:
        return jsonify({'error': 'Invalid target supplier'}), 400

    # Get target supplier connection
    connection = SupplierConnection.query.filter_by(
        user_id=user_id,
        supplier_type=target_supplier,
        is_connected=True
    ).first()

    if not connection:
        return jsonify({'error': f'{target_supplier} is not connected'}), 400

    # Get products
    query = Product.query.join(Shop).filter(Shop.user_id == user_id)

    if product_ids:
        query = query.filter(Product.id.in_(product_ids))
    elif product_type:
        query = query.filter(Product.product_type.ilike(f'%{product_type}%'))
    else:
        return jsonify({'error': 'product_ids or product_type is required'}), 400

    products = query.all()

    if not products:
        return jsonify({'error': 'No products found'}), 404

    # Switch each product
    results = {
        'success': [],
        'failed': [],
        'total': len(products)
    }

    for product in products:
        try:
            switch_product_supplier(product, connection)
            results['success'].append({
                'id': product.id,
                'title': product.title
            })
        except Exception as e:
            results['failed'].append({
                'id': product.id,
                'title': product.title,
                'error': str(e)
            })

    return jsonify({
        'message': f"Switched {len(results['success'])} of {results['total']} products",
        'results': results
    })


@products_bp.route('/types', methods=['GET'])
@jwt_required()
def get_product_types():
    """
    Get unique product types from user's products.

    Returns:
        List of product types with counts
    """
    user_id = get_jwt_identity()

    # Get user's shops
    shops = Shop.query.filter_by(user_id=user_id).all()
    shop_ids = [s.id for s in shops]

    # Get distinct product types with counts
    results = db.session.query(
        Product.product_type,
        Product.supplier_type,
        db.func.count(Product.id)
    ).filter(
        Product.shop_id.in_(shop_ids),
        Product.product_type.isnot(None)
    ).group_by(
        Product.product_type,
        Product.supplier_type
    ).all()

    # Organize by product type
    types = {}
    for product_type, supplier, count in results:
        if product_type not in types:
            types[product_type] = {
                'product_type': product_type,
                'total': 0,
                'by_supplier': {}
            }
        types[product_type]['total'] += count
        types[product_type]['by_supplier'][supplier] = count

    return jsonify({
        'product_types': list(types.values())
    })


@products_bp.route('/match/<int:product_id>', methods=['GET'])
@jwt_required()
def find_matching_products(product_id):
    """
    Find matching products from other suppliers.

    Args:
        product_id: Product ID to find matches for

    Returns:
        List of matching products from connected suppliers
    """
    user_id = get_jwt_identity()

    # Verify product belongs to user
    product = Product.query.join(Shop).filter(
        Product.id == product_id,
        Shop.user_id == user_id
    ).first()

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Get supplier connections
    connections = SupplierConnection.query.filter_by(
        user_id=user_id,
        is_connected=True
    ).all()

    matches = find_matching_supplier_products(product, connections)

    return jsonify({
        'product': product.to_dict(),
        'matches': matches
    })


# User Product Management Routes

@products_bp.route('/user/list', methods=['GET'])
@jwt_required()
def get_user_products():
    """
    Get user's product list.

    Query params:
        page: Page number (default 1)
        per_page: Items per page (default 20)
        search: Search term
        category: Filter by category
        supplier: Filter by supplier type

    Returns:
        Paginated list of user products
    """
    user_id = get_jwt_identity()

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    supplier = request.args.get('supplier', '')

    query = UserProduct.query.filter_by(user_id=user_id, is_active=True)

    if search:
        query = query.filter(
            db.or_(
                UserProduct.product_name.ilike(f'%{search}%'),
                UserProduct.product_type.ilike(f'%{search}%'),
                UserProduct.brand.ilike(f'%{search}%')
            )
        )

    if category:
        query = query.filter(UserProduct.category == category)

    if supplier:
        query = query.filter(UserProduct.primary_supplier_type == supplier)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Get supplier info for each product
    products_data = []
    for product in pagination.items:
        product_dict = product.to_dict(include_suppliers=True)
        # Count suppliers
        product_dict['supplier_count'] = product.suppliers.count()
        products_data.append(product_dict)

    return jsonify({
        'products': products_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })


@products_bp.route('/user/catalog/<int:connection_id>', methods=['GET'])
@jwt_required()
def get_supplier_catalog(connection_id):
    """
    Get supplier catalog with categories and search.
    If no products are in database, fetches directly from API.

    Args:
        connection_id: Supplier connection ID

    Query params:
        page: Page number (default 1)
        per_page: Items per page (default 20)
        search: Search term
        category: Filter by category

    Returns:
        Paginated catalog with categories
    """
    user_id = get_jwt_identity()

    connection = SupplierConnection.query.filter_by(
        id=connection_id,
        user_id=user_id,
        is_connected=True
    ).first()

    if not connection:
        return jsonify({'error': 'Connection not found'}), 404

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '').strip()  # Strip whitespace and handle empty string
    # If category is empty string, treat as None (show all)
    if not category:
        category = None

    # Check if products exist in database
    product_count = SupplierProduct.query.filter_by(
        supplier_connection_id=connection.id,
        is_active=True
    ).count()

    # If no products in database, fetch from API directly
    if product_count == 0:
        try:
            if connection.supplier_type == SupplierType.GELATO.value:
                from app.services.suppliers.gelato import GelatoService
                service = GelatoService(
                    api_key=connection.api_key,
                    access_token=connection.access_token
                )
                
                # First, fetch a larger sample of products to collect all categories
                # Fetch first 200 products to get comprehensive category list
                all_categories = set()
                category_sample_products = []
                try:
                    for sample_offset in range(0, 200, 100):  # Fetch in batches of 100
                        sample_response = service.get_products(
                            store_id=connection.store_id,
                            limit=100,
                            offset=sample_offset
                        )
                        sample_products = (
                            sample_response.get('products', []) or
                            sample_response.get('data', []) or
                            sample_response.get('items', []) or
                            (sample_response if isinstance(sample_response, list) else [])
                        )
                        if not sample_products:
                            break
                        category_sample_products.extend(sample_products)
                        # Extract categories from sample (quick pass without full details)
                        for sample_product in sample_products:
                            if isinstance(sample_product, dict):
                                sample_category = (
                                    sample_product.get('category') or
                                    sample_product.get('productCategory') or
                                    sample_product.get('productTypeUid')
                                )
                                if sample_category:
                                    all_categories.add(sample_category)
                        if len(sample_products) < 100:
                            break
                except Exception as sample_error:
                    current_app.logger.warning(f"Could not fetch category sample: {str(sample_error)}")
                
                # Now fetch the actual page of products
                offset = (page - 1) * per_page
                products_response = service.get_products(
                    store_id=connection.store_id,
                    limit=per_page,
                    offset=offset
                )
                
                # Parse Gelato products
                products = (
                    products_response.get('products', []) or
                    products_response.get('data', []) or
                    products_response.get('items', []) or
                    (products_response if isinstance(products_response, list) else [])
                )
                
                # Log for debugging
                current_app.logger.info(f"Gelato API response type: {type(products_response)}, products count: {len(products) if isinstance(products, list) else 'N/A'}")
                if products and len(products) > 0:
                    sample_product = products[0]
                    if isinstance(sample_product, dict):
                        current_app.logger.info(f"Sample Gelato product keys: {list(sample_product.keys())}")
                
                # Convert to SupplierProduct format
                catalog_products = []
                
                if not products or len(products) == 0:
                    current_app.logger.warning(f"No Gelato products found in response. Response keys: {list(products_response.keys()) if isinstance(products_response, dict) else 'Not a dict'}")
                
                for product in products:
                    if not isinstance(product, dict):
                        current_app.logger.warning(f"Skipping non-dict product: {type(product)}")
                        continue
                    
                    # Gelato v3 API structure: products have productUid, productNameUid, productTypeUid, dimensions
                    # The /products endpoint returns minimal data - we need to fetch full product details
                    product_uid = product.get('productUid') or product.get('uid') or product.get('id')
                    product_name_uid = product.get('productNameUid')
                    product_type_uid = product.get('productTypeUid')
                    
                    # Try to fetch full product details for better info
                    # Fetch details for all products on current page (limited by per_page, typically 20)
                    product_details = None
                    try:
                        if product_uid:
                            from app.services.suppliers.gelato import GelatoService
                            detail_service = GelatoService(
                                api_key=connection.api_key,
                                access_token=connection.access_token
                            )
                            product_details = detail_service.get_product(product_uid)
                            current_app.logger.debug(f"Fetched Gelato product details for {product_uid}")
                            
                            # Extract category from detailed product info
                            if isinstance(product_details, dict):
                                detail_category = (
                                    product_details.get('category') or
                                    product_details.get('productCategory') or
                                    product_details.get('categoryName') or
                                    product_details.get('category_name') or
                                    product_details.get('product', {}).get('category') or
                                    product_details.get('data', {}).get('category')
                                )
                                if detail_category:
                                    all_categories.add(detail_category)
                    except Exception as detail_error:
                        current_app.logger.warning(f"Could not fetch Gelato product details for {product_uid}: {str(detail_error)}")
                        product_details = None
                    
                    # Use product details if available, otherwise use the basic product data
                    product_data = product_details if product_details else product
                    
                    # Check for nested product data in the details
                    if isinstance(product_data, dict):
                        product_data = product_data.get('product') or product_data.get('data') or product_data
                    
                    # Apply search filter
                    if search:
                        # Try to get name from various places
                        name = (
                            product_data.get('title') or 
                            product_data.get('name') or 
                            product_data.get('productName') or
                            product_data.get('displayName') or
                            product.get('productName') or
                            # Use productNameUid as fallback (e.g., "canvas" -> "Canvas")
                            (product_name_uid.replace('_', ' ').title() if product_name_uid else None) or
                            str(product_uid) if product_uid else ''
                        )
                        product_type = (
                            product_data.get('productType') or 
                            product_data.get('type') or
                            product_data.get('product_type') or
                            product.get('productType') or
                            # Use productTypeUid as fallback
                            (product_type_uid.replace('_', ' ').title() if product_type_uid else None) or
                            ''
                        )
                        brand = product_data.get('brand') or product.get('brand') or ''
                        if search.lower() not in name.lower() and search.lower() not in product_type.lower() and search.lower() not in brand.lower():
                            continue
                    
                    # Apply category filter
                    # For Gelato, category might be in product_data from detailed fetch
                    product_category = (
                        product_data.get('category') or 
                        product_data.get('productCategory') or
                        product_data.get('categoryName') or
                        product_data.get('category_name') or
                        product.get('category') or
                        product.get('productCategory') or
                        product.get('categoryName') or
                        product_type_uid  # Use productTypeUid as fallback category
                    )
                    # Normalize category for comparison (strip whitespace, handle None/empty)
                    if product_category:
                        normalized_product_category = product_category.strip() or None
                    else:
                        normalized_product_category = None
                    
                    # Filter by category: if category is specified, only include matching products
                    if category is not None:
                        # Compare normalized values (case-insensitive for better matching)
                        if normalized_product_category and normalized_product_category.lower() != category.lower():
                            continue
                        elif not normalized_product_category:
                            # If product has no category but we're filtering by category, skip it
                            continue
                    
                    # Add to categories set (will be used for dropdown)
                    if normalized_product_category:
                        all_categories.add(normalized_product_category)
                    
                    # Extract thumbnail URL - handle various formats, check both product and product_data
                    thumbnail_url = None
                    images_list = product_data.get('images', []) or product.get('images', []) or []
                    
                    # Try different image field names in product_data first, then product
                    for source in [product_data, product]:
                        if source.get('imageUrl'):
                            thumbnail_url = source.get('imageUrl')
                            break
                        elif source.get('thumbnailUrl'):
                            thumbnail_url = source.get('thumbnailUrl')
                            break
                        elif source.get('image'):
                            img_val = source.get('image')
                            if isinstance(img_val, str):
                                thumbnail_url = img_val
                                break
                            elif isinstance(img_val, dict):
                                thumbnail_url = img_val.get('url') or img_val.get('src') or img_val.get('imageUrl')
                                if thumbnail_url:
                                    break
                        elif source.get('thumbnail'):
                            thumbnail_url = source.get('thumbnail')
                            break
                        elif source.get('image_url'):
                            thumbnail_url = source.get('image_url')
                            break
                        elif source.get('thumbnail_url'):
                            thumbnail_url = source.get('thumbnail_url')
                            break
                    
                    # If images is an array, get first image
                    if not thumbnail_url and images_list and len(images_list) > 0:
                        first_image = images_list[0]
                        if isinstance(first_image, str):
                            thumbnail_url = first_image
                        elif isinstance(first_image, dict):
                            thumbnail_url = (
                                first_image.get('url') or 
                                first_image.get('src') or
                                first_image.get('imageUrl') or 
                                first_image.get('thumbnailUrl') or
                                first_image.get('image') or
                                first_image.get('thumbnail')
                            )
                    
                    # Check for nested image structures (Gelato might have images in product.image or product.media)
                    if not thumbnail_url:
                        for source in [product_data, product]:
                            if source.get('media') and isinstance(source.get('media'), dict):
                                media = source.get('media')
                                thumbnail_url = media.get('imageUrl') or media.get('thumbnailUrl') or media.get('url')
                                if thumbnail_url:
                                    break
                            elif source.get('image') and isinstance(source.get('image'), dict):
                                img_obj = source.get('image')
                                thumbnail_url = img_obj.get('url') or img_obj.get('src') or img_obj.get('imageUrl')
                                if thumbnail_url:
                                    break
                    
                    # Extract name - try multiple fields from product_data first
                    # For Gelato, productNameUid might be the product name (e.g., "canvas")
                    product_name = (
                        product_data.get('title') or 
                        product_data.get('name') or 
                        product_data.get('productName') or
                        product_data.get('displayName') or
                        product.get('productName') or
                        product.get('title') or 
                        product.get('name') or
                        # Use productNameUid as fallback (e.g., "canvas" -> "Canvas")
                        (product_name_uid.replace('_', ' ').title() if product_name_uid else None) or
                        f"Product {product_uid[:20]}..." if product_uid else 'Unknown Product'
                    )
                    
                    # Extract description
                    product_description = (
                        product_data.get('description') or
                        product_data.get('desc') or
                        product_data.get('productDescription') or
                        product.get('description') or
                        product.get('desc') or
                        None
                    )
                    
                    # Extract product type
                    # For Gelato, productTypeUid might be the type
                    product_type_value = (
                        product_data.get('productType') or 
                        product_data.get('type') or
                        product_data.get('product_type') or
                        product_data.get('model') or
                        product.get('productType') or 
                        product.get('type') or
                        product.get('product_type') or
                        product.get('model') or
                        # Use productTypeUid as fallback
                        (product_type_uid.replace('_', ' ').title() if product_type_uid else None)
                    )
                    
                    # Extract dimensions info for Gelato
                    dimensions_info = []
                    if product.get('dimensions') and isinstance(product.get('dimensions'), list):
                        for dim in product.get('dimensions'):
                            if isinstance(dim, dict):
                                dim_name = dim.get('nameFormatted') or dim.get('name', '')
                                dim_value = dim.get('valueFormatted') or dim.get('value', '')
                                if dim_name and dim_value:
                                    dimensions_info.append(f"{dim_name}: {dim_value}")
                    
                    # Add dimensions to description if we don't have a description
                    if not product_description and dimensions_info:
                        product_description = "; ".join(dimensions_info)
                    
                    catalog_products.append({
                        'id': None,  # Not in database yet
                        'supplier_connection_id': connection.id,
                        'supplier_product_id': str(product_uid or product.get('id') or ''),
                        'name': product_name,
                        'description': _strip_html(product_description) if product_description else None,
                        'product_type': product_type_value,
                        'brand': product_data.get('brand') or product.get('brand'),
                        'category': normalized_product_category,
                        'base_price': product_data.get('price') or product_data.get('basePrice') or product_data.get('base_price') or product.get('price') or product.get('basePrice'),
                        'currency': product_data.get('currency') or product.get('currency', 'USD'),
                        'available_sizes': product_data.get('sizes', []) or product_data.get('availableSizes', []) or product_data.get('available_sizes', []) or product.get('sizes', []) or product.get('availableSizes', []),
                        'available_colors': product_data.get('colors', []) or product_data.get('availableColors', []) or product_data.get('available_colors', []) or product.get('colors', []) or product.get('availableColors', []),
                        'thumbnail_url': thumbnail_url,
                        'images': images_list,
                        'is_active': True
                    })
                
                # Simple pagination for API results
                total = len(catalog_products)  # Approximate, API doesn't always return total
                start_idx = 0
                end_idx = per_page
                
                return jsonify({
                    'products': catalog_products[start_idx:end_idx],
                    'categories': sorted(all_categories),
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'pages': (total + per_page - 1) // per_page if total > 0 else 1,
                        'has_next': end_idx < total,
                        'has_prev': page > 1
                    },
                    'supplier': {
                        'type': connection.supplier_type,
                        'name': connection.account_name or connection.account_email or connection.supplier_type,
                        'account_name': connection.account_name,
                        'account_email': connection.account_email,
                        'account_id': connection.account_id
                    },
                    'needs_sync': True  # Indicate that products should be synced
                })
            elif connection.supplier_type == SupplierType.PRINTIFY.value:
                from app.services.suppliers.printify import PrintifyService
                service = PrintifyService(connection.api_key)
                blueprints_response = service.get_blueprints()
                
                # Handle different response formats
                blueprints = []
                if isinstance(blueprints_response, list):
                    blueprints = blueprints_response
                elif isinstance(blueprints_response, dict):
                    blueprints = blueprints_response.get('blueprints', []) or blueprints_response.get('data', []) or blueprints_response.get('items', [])
                
                # Convert blueprints to catalog format
                catalog_products = []
                all_categories = set()
                
                current_app.logger.info(f"Printify: Processing {len(blueprints)} blueprints, category filter: {category}")
                
                for blueprint in blueprints:
                    if not isinstance(blueprint, dict):
                        continue
                        
                    if search:
                        name = blueprint.get('title', '') or blueprint.get('name', '')
                        if search.lower() not in name.lower():
                            continue
                    
                    # Extract category from blueprint - check multiple possible field names
                    blueprint_category = (
                        blueprint.get('category') or
                        blueprint.get('categoryName') or
                        blueprint.get('category_name') or
                        blueprint.get('productCategory') or
                        blueprint.get('type') or
                        blueprint.get('productType')
                    )
                    # Normalize category for comparison (strip whitespace, handle None/empty)
                    if blueprint_category:
                        normalized_blueprint_category = blueprint_category.strip() or None
                    else:
                        normalized_blueprint_category = None
                    
                    # Log for debugging if no category found
                    if not normalized_blueprint_category and len(catalog_products) < 3:
                        current_app.logger.debug(f"Printify blueprint {blueprint.get('id')} has no category. Keys: {list(blueprint.keys())}")
                    
                    # Filter by category: if category is specified, only include matching products
                    # When category is None (All Categories), show all products
                    if category is not None:
                        # Compare normalized values (case-insensitive for better matching)
                        if normalized_blueprint_category:
                            if normalized_blueprint_category.lower() != category.lower():
                                continue
                        else:
                            # If product has no category but we're filtering by a specific category, skip it
                            continue
                    
                    if normalized_blueprint_category:
                        all_categories.add(normalized_blueprint_category)
                    
                    # Extract thumbnail URL from images
                    thumbnail_url = None
                    images_list = blueprint.get('images', []) or []
                    if images_list:
                        if isinstance(images_list[0], str):
                            thumbnail_url = images_list[0]
                        elif isinstance(images_list[0], dict):
                            thumbnail_url = images_list[0].get('url') or images_list[0].get('src') or images_list[0].get('imageUrl')
                    
                    # Only add to catalog if it passed the filter (or no filter applied)
                    catalog_products.append({
                        'id': None,
                        'supplier_connection_id': connection.id,
                        'supplier_product_id': str(blueprint_id or ''),
                        'blueprint_id': str(blueprint_id or ''),
                        'name': (blueprint_data.get('title') or blueprint_data.get('name') or 
                                blueprint.get('title', '') or blueprint.get('name', '')),
                        'description': blueprint_data.get('description') or blueprint.get('description'),  # Keep HTML for Printify
                        'product_type': blueprint_data.get('model') or blueprint_data.get('title') or blueprint.get('model') or blueprint.get('title', ''),
                        'brand': blueprint_data.get('brand') or blueprint.get('brand'),
                        'category': normalized_blueprint_category,
                        'base_price': None,  # Pricing varies by provider
                        'currency': 'USD',
                        'available_sizes': [],
                        'available_colors': [],
                        'thumbnail_url': thumbnail_url,
                        'images': images_list,
                        'is_active': True
                    })
                
                # Paginate
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                total = len(catalog_products)
                
                current_app.logger.info(f"Printify: Returning {len(catalog_products[start_idx:end_idx])} products out of {total} total, categories: {sorted(all_categories)}")
                
                return jsonify({
                    'products': catalog_products[start_idx:end_idx],
                    'categories': sorted(all_categories),
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'pages': (total + per_page - 1) // per_page if total > 0 else 1,
                        'has_next': end_idx < total,
                        'has_prev': page > 1
                    },
                    'supplier': {
                        'type': connection.supplier_type,
                        'name': connection.account_name or connection.account_email or connection.supplier_type,
                        'account_name': connection.account_name,
                        'account_email': connection.account_email,
                        'account_id': connection.account_id
                    },
                    'needs_sync': True
                })
            elif connection.supplier_type == SupplierType.PRINTFUL.value:
                from app.services.suppliers.printful import PrintfulService
                from app.services.oauth import refresh_printful_token
                
                if not connection.access_token:
                    raise ValueError("Printful access token is missing")
                
                access_token = connection.access_token
                
                try:
                    service = PrintfulService(access_token)
                    products_response = service.get_products()
                    current_app.logger.info(f"Printful API response type: {type(products_response)}, is None: {products_response is None}")
                    if isinstance(products_response, dict):
                        current_app.logger.info(f"Printful response keys: {list(products_response.keys())}")
                except requests.exceptions.HTTPError as http_error:
                    # Handle 401 Unauthorized - try to refresh token
                    if http_error.response.status_code == 401 and connection.refresh_token:
                        current_app.logger.info("Printful access token expired, attempting refresh...")
                        try:
                            token_data = refresh_printful_token(connection.refresh_token)
                            new_access_token = token_data.get('access_token')
                            if new_access_token:
                                # Update connection with new token
                                connection.access_token = new_access_token
                                if token_data.get('refresh_token'):
                                    connection.refresh_token = token_data.get('refresh_token')
                                db.session.commit()
                                current_app.logger.info("Printful token refreshed successfully")
                                
                                # Retry with new token
                                service = PrintfulService(new_access_token)
                                products_response = service.get_products()
                                current_app.logger.info(f"Printful API response type after refresh: {type(products_response)}")
                            else:
                                raise ValueError("Failed to refresh Printful token: no access_token in response")
                        except Exception as refresh_error:
                            current_app.logger.error(f"Failed to refresh Printful token: {str(refresh_error)}", exc_info=True)
                            raise ValueError(f"Printful access token expired and refresh failed. Please reconnect your Printful account. Error: {str(refresh_error)}")
                    else:
                        # Other HTTP errors or no refresh token
                        error_msg = f"Printful API error: {http_error.response.status_code}"
                        if http_error.response.status_code == 401:
                            error_msg += " - Unauthorized. Access token may be invalid or expired."
                        current_app.logger.error(f"{error_msg}: {str(http_error)}", exc_info=True)
                        raise ValueError(error_msg)
                except Exception as api_error:
                    current_app.logger.error(f"Printful API call failed: {str(api_error)}", exc_info=True)
                    raise
                
                # Handle different response formats
                # Note: PrintfulService._request already extracts 'result', so get_products() should return list directly
                products = []
                if products_response is None:
                    current_app.logger.warning("Printful products_response is None")
                    products = []
                elif isinstance(products_response, list):
                    products = products_response
                    current_app.logger.info(f"Printful returned list with {len(products)} items")
                elif isinstance(products_response, dict):
                    # Double-check in case result wasn't extracted
                    products = products_response.get('result', []) or products_response.get('data', []) or products_response.get('items', [])
                    current_app.logger.info(f"Printful returned dict, extracted {len(products)} products")
                    if not products:
                        current_app.logger.warning(f"Printful dict had no products. Keys: {list(products_response.keys())}")
                else:
                    current_app.logger.warning(f"Unexpected Printful products response type: {type(products_response)}, value: {str(products_response)[:200]}")
                    products = []
                
                catalog_products = []
                all_categories = set()
                
                current_app.logger.info(f"Printful: Processing {len(products)} products, category filter: {category}")
                
                for product in products:
                    if not isinstance(product, dict):
                        continue
                    
                    # Printful product structure:
                    # - name: Product name (may contain model number)
                    # - type: Product type (e.g., "DIRECT-TO-FABRIC")
                    # - type_name: Category name
                    # - brand: Manufacturer/brand (e.g., "Gildan")
                    # - model: Model number (may be in name or separate field)
                    
                    product_name = product.get('name', '')
                    product_brand = product.get('brand') or product.get('manufacturer')
                    product_type_value = product.get('type')  # This is the type like "DIRECT-TO-FABRIC"
                    product_category = product.get('type_name') or product.get('category') or product.get('type')  # Category should be type_name
                    product_model = product.get('model') or product.get('model_number')
                    
                    # Calculate name without brand for model extraction
                    name_without_brand = product_name.replace(product_brand, '').strip() if product_brand and product_brand in product_name else product_name
                    
                    # Try to extract model from name if not provided (e.g., "Gildan 18000" -> "18000")
                    if not product_model and product_name and product_brand:
                        # Remove brand from name and see if there's a model number
                        import re
                        model_match = re.search(r'\b(\d{4,})\b', name_without_brand)
                        if model_match:
                            product_model = model_match.group(1)
                    
                    # Build product_type as "Brand Model" (e.g., "Gildan 18000")
                    if product_brand and product_model:
                        product_type_display = f"{product_brand} {product_model}"
                    elif product_brand:
                        product_type_display = product_brand
                    elif product_model:
                        product_type_display = product_model
                    else:
                        product_type_display = product_type_value or ''
                        
                    if search:
                        search_lower = search.lower()
                        if (search_lower not in product_name.lower() and 
                            search_lower not in (product_brand or '').lower() and
                            search_lower not in (product_model or '').lower() and
                            search_lower not in (product_type_display or '').lower()):
                            continue
                    
                    # Normalize category for comparison (strip whitespace, handle None/empty)
                    if product_category:
                        normalized_product_category = product_category.strip() or None
                    else:
                        normalized_product_category = None
                    
                    # Filter by category: if category is specified, only include matching products
                    if category is not None:
                        # Compare normalized values (case-insensitive for better matching)
                        if normalized_product_category and normalized_product_category.lower() != category.lower():
                            continue
                        elif not normalized_product_category:
                            # If product has no category but we're filtering by category, skip it
                            continue
                    
                    if normalized_product_category:
                        all_categories.add(normalized_product_category)
                    
                    # Extract thumbnail URL
                    thumbnail_url = None
                    images_list = product.get('images', []) or []
                    if product.get('image'):
                        thumbnail_url = product.get('image')
                    elif images_list:
                        if isinstance(images_list[0], str):
                            thumbnail_url = images_list[0]
                        elif isinstance(images_list[0], dict):
                            thumbnail_url = images_list[0].get('url') or images_list[0].get('src') or images_list[0].get('image')
                    
                    catalog_products.append({
                        'id': None,
                        'supplier_connection_id': connection.id,
                        'supplier_product_id': str(product.get('id', '')),
                        'name': product_name,
                        'description': _strip_html(product.get('description')) if product.get('description') else None,
                        'product_type': product_type_display,  # "Brand Model" format
                        'brand': product_brand,
                        'category': normalized_product_category,  # Use type_name for category
                        'base_price': None,
                        'currency': 'USD',
                        'available_sizes': [],
                        'available_colors': [],
                        'thumbnail_url': thumbnail_url,
                        'images': images_list,
                        'is_active': True
                    })
                
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                total = len(catalog_products)
                
                return jsonify({
                    'products': catalog_products[start_idx:end_idx],
                    'categories': sorted(all_categories),
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'pages': (total + per_page - 1) // per_page if total > 0 else 1,
                        'has_next': end_idx < total,
                        'has_prev': page > 1
                    },
                    'supplier': {
                        'type': connection.supplier_type,
                        'name': connection.account_name or connection.account_email or connection.supplier_type,
                        'account_name': connection.account_name,
                        'account_email': connection.account_email,
                        'account_id': connection.account_id
                    },
                    'needs_sync': True
                })
        except Exception as e:
            current_app.logger.error(f"Error fetching catalog from API: {str(e)}", exc_info=True)
            # Return error with CORS headers
            from flask import make_response
            response = make_response(jsonify({
                'error': f'Failed to fetch catalog from {connection.supplier_type} API',
                'details': str(e)
            }), 500)
            # Add CORS headers
            response.headers['Access-Control-Allow-Origin'] = current_app.config.get('FRONTEND_URL', '*')
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response

    # Use database products
    query = SupplierProduct.query.filter_by(
        supplier_connection_id=connection.id,
        is_active=True
    )

    if search:
        query = query.filter(
            db.or_(
                SupplierProduct.name.ilike(f'%{search}%'),
                SupplierProduct.product_type.ilike(f'%{search}%'),
                SupplierProduct.brand.ilike(f'%{search}%')
            )
        )

    if category:
        query = query.filter(SupplierProduct.category == category)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Get unique categories
    categories = db.session.query(SupplierProduct.category).filter(
        SupplierProduct.supplier_connection_id == connection.id,
        SupplierProduct.is_active == True,
        SupplierProduct.category.isnot(None)
    ).distinct().all()
    categories_list = [c[0] for c in categories if c[0]]

    return jsonify({
        'products': [p.to_dict() for p in pagination.items],
        'categories': sorted(categories_list),
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        },
        'supplier': {
            'type': connection.supplier_type,
            'name': connection.account_name or connection.account_email or connection.supplier_type,
            'account_name': connection.account_name,
            'account_email': connection.account_email,
            'account_id': connection.account_id
        }
    })


@products_bp.route('/user/add', methods=['POST'])
@jwt_required()
def add_user_product():
    """
    Add a product to user's list and check for matches from other suppliers.

    Request body:
        supplier_connection_id: Supplier connection ID
        supplier_product_id: Supplier product ID (from SupplierProduct table)
        product_name: Product name (optional, will use supplier product name if not provided)

    Returns:
        Created user product with matched suppliers
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    supplier_connection_id = data.get('supplier_connection_id')
    supplier_product_id = data.get('supplier_product_id')  # Can be database ID or external ID
    supplier_product_external_id = data.get('supplier_product_external_id')  # External ID from supplier API

    if not supplier_connection_id or not supplier_product_id:
        return jsonify({'error': 'supplier_connection_id and supplier_product_id are required'}), 400

    # Verify connection belongs to user
    connection = SupplierConnection.query.filter_by(
        id=supplier_connection_id,
        user_id=user_id,
        is_connected=True
    ).first()

    if not connection:
        return jsonify({'error': 'Connection not found'}), 404

    # Try to get supplier product from database
    # First try by database ID (if it's a number)
    supplier_product = None
    if isinstance(supplier_product_id, int) or (isinstance(supplier_product_id, str) and supplier_product_id.isdigit()):
        supplier_product = SupplierProduct.query.filter_by(
            id=int(supplier_product_id),
            supplier_connection_id=supplier_connection_id
        ).first()
    
    # If not found, try by external supplier_product_id
    if not supplier_product and supplier_product_external_id:
        supplier_product = SupplierProduct.query.filter_by(
            supplier_product_id=str(supplier_product_external_id),
            supplier_connection_id=supplier_connection_id
        ).first()
    
    # If still not found, try using supplier_product_id as external ID
    if not supplier_product:
        supplier_product = SupplierProduct.query.filter_by(
            supplier_product_id=str(supplier_product_id),
            supplier_connection_id=supplier_connection_id
        ).first()

    # If product not in database, fetch from API and create it
    if not supplier_product:
        try:
            from app.services.suppliers.sync import _upsert_supplier_product
            from datetime import datetime
            
            # Use external ID if provided, otherwise use supplier_product_id
            external_id = str(supplier_product_external_id or supplier_product_id)
            
            if connection.supplier_type == SupplierType.GELATO.value:
                from app.services.suppliers.gelato import GelatoService
                service = GelatoService(
                    api_key=connection.api_key,
                    access_token=connection.access_token
                )
                # Fetch the specific product
                try:
                    product_data = service.get_product(external_id)
                except:
                    # If get_product fails, try fetching all and finding it
                    products_response = service.get_products(
                        store_id=connection.store_id,
                        limit=1000,
                        offset=0
                    )
                    products = (
                        products_response.get('products', []) or
                        products_response.get('data', []) or
                        products_response.get('items', []) or
                        (products_response if isinstance(products_response, list) else [])
                    )
                    product_data = next((p for p in products if str(p.get('uid') or p.get('id') or '') == external_id), None)
                    if not product_data:
                        return jsonify({'error': 'Product not found in supplier catalog'}), 404
                
                # Create supplier product entry
                _upsert_supplier_product(
                    connection=connection,
                    supplier_product_id=external_id,
                    data={
                        'name': product_data.get('title') or product_data.get('name') or '',
                        'description': product_data.get('description'),
                        'product_type': product_data.get('productType') or product_data.get('type'),
                        'brand': product_data.get('brand'),
                        'category': product_data.get('category'),
                        'catalog_id': product_data.get('catalogId') or product_data.get('catalog_id'),
                        'base_price': product_data.get('price') or product_data.get('basePrice'),
                        'currency': product_data.get('currency', 'USD'),
                        'available_sizes': product_data.get('sizes', []) or product_data.get('availableSizes', []),
                        'available_colors': product_data.get('colors', []) or product_data.get('availableColors', []),
                        'thumbnail_url': product_data.get('imageUrl') or product_data.get('thumbnailUrl') or product_data.get('image'),
                        'images': product_data.get('images', [])
                    }
                )
                
                # Reload the product
                supplier_product = SupplierProduct.query.filter_by(
                    supplier_product_id=external_id,
                    supplier_connection_id=supplier_connection_id
                ).first()
            else:
                return jsonify({'error': 'Product not synced. Please sync the supplier connection first.'}), 404
        except Exception as e:
            current_app.logger.error(f"Error creating supplier product from API: {str(e)}")
            return jsonify({'error': f'Failed to fetch product from supplier: {str(e)}'}), 500

    if not supplier_product:
        return jsonify({'error': 'Supplier product not found'}), 404

    # Check if product already exists (by product_type)
    existing_product = None
    if supplier_product.product_type:
        existing_product = UserProduct.query.filter_by(
            user_id=user_id,
            product_type=supplier_product.product_type,
            is_active=True
        ).first()

    if existing_product:
        # Add this supplier to existing product
        existing_supplier = UserProductSupplier.query.filter_by(
            user_product_id=existing_product.id,
            supplier_connection_id=supplier_connection_id
        ).first()

        if not existing_supplier:
            existing_supplier = UserProductSupplier(
                user_product_id=existing_product.id,
                supplier_connection_id=supplier_connection_id,
                supplier_product_id=supplier_product.id,
                supplier_type=connection.supplier_type,
                supplier_product_external_id=supplier_product.supplier_product_id,
                base_price=supplier_product.base_price,
                currency=supplier_product.currency,
                is_available=True
            )
            db.session.add(existing_supplier)

        existing_product.updated_at = datetime.utcnow()
        db.session.commit()

        # Find matches from other suppliers
        matches = _find_matching_suppliers_for_product(existing_product, user_id)

        return jsonify({
            'message': 'Product already exists, supplier added',
            'product': existing_product.to_dict(include_suppliers=True),
            'matches_found': matches
        })

    # Create new user product
    user_product = UserProduct(
        user_id=user_id,
        product_name=data.get('product_name') or supplier_product.name,
        product_type=supplier_product.product_type,
        brand=supplier_product.brand,
        category=supplier_product.category,
        description=supplier_product.description,
        thumbnail_url=supplier_product.thumbnail_url,
        images=supplier_product.images or [],
        primary_supplier_type=connection.supplier_type,
        primary_supplier_product_id=supplier_product.supplier_product_id,
        primary_supplier_connection_id=supplier_connection_id
    )
    db.session.add(user_product)
    db.session.flush()  # Get the ID

    # Add primary supplier
    user_product_supplier = UserProductSupplier(
        user_product_id=user_product.id,
        supplier_connection_id=supplier_connection_id,
        supplier_product_id=supplier_product.id,
        supplier_type=connection.supplier_type,
        supplier_product_external_id=supplier_product.supplier_product_id,
        base_price=supplier_product.base_price,
        currency=supplier_product.currency,
        is_available=True
    )
    db.session.add(user_product_supplier)

    db.session.commit()

    # Find matches from other suppliers
    matches = _find_matching_suppliers_for_product(user_product, user_id)

    return jsonify({
        'message': 'Product added successfully',
        'product': user_product.to_dict(include_suppliers=True),
        'matches_found': matches
    }), 201


def _find_matching_suppliers_for_product(user_product, user_id):
    """
    Find matching products from other suppliers for a user product.

    Args:
        user_product: UserProduct instance
        user_id: User ID

    Returns:
        List of matched suppliers
    """
    if not user_product.product_type:
        return []

    # Get all connected suppliers for this user
    connections = SupplierConnection.query.filter_by(
        user_id=user_id,
        is_connected=True
    ).all()

    matches = []
    for connection in connections:
        # Skip if already added
        existing = UserProductSupplier.query.filter_by(
            user_product_id=user_product.id,
            supplier_connection_id=connection.id
        ).first()

        if existing:
            continue

        # Find matching product by product_type
        matching_product = SupplierProduct.query.filter_by(
            supplier_connection_id=connection.id,
            product_type=user_product.product_type,
            is_active=True
        ).first()

        if matching_product:
            # Add to user product suppliers
            user_product_supplier = UserProductSupplier(
                user_product_id=user_product.id,
                supplier_connection_id=connection.id,
                supplier_product_id=matching_product.id,
                supplier_type=connection.supplier_type,
                supplier_product_external_id=matching_product.supplier_product_id,
                base_price=matching_product.base_price,
                currency=matching_product.currency,
                is_available=True
            )
            db.session.add(user_product_supplier)
            matches.append({
                'supplier_type': connection.supplier_type,
                'supplier_name': connection.account_name or connection.supplier_type,
                'product_name': matching_product.name,
                'base_price': matching_product.base_price
            })

    if matches:
        db.session.commit()

    return matches


@products_bp.route('/user/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_user_product(product_id):
    """
    Delete a product from user's list.

    Args:
        product_id: User product ID

    Returns:
        Success message
    """
    user_id = get_jwt_identity()

    product = UserProduct.query.filter_by(
        id=product_id,
        user_id=user_id
    ).first()

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    product.is_active = False
    db.session.commit()

    return jsonify({'message': 'Product removed from list'})


@products_bp.route('/user/<int:product_id>/suppliers', methods=['GET'])
@jwt_required()
def get_product_suppliers(product_id):
    """
    Get all suppliers that have this product.

    Args:
        product_id: User product ID

    Returns:
        List of suppliers with pricing
    """
    user_id = get_jwt_identity()

    product = UserProduct.query.filter_by(
        id=product_id,
        user_id=user_id
    ).first()

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    suppliers = []
    for ups in product.suppliers.all():
        connection = SupplierConnection.query.get(ups.supplier_connection_id)
        supplier_product = SupplierProduct.query.get(ups.supplier_product_id) if ups.supplier_product_id else None

        suppliers.append({
            'id': ups.id,
            'supplier_type': ups.supplier_type,
            'supplier_name': connection.account_name if connection else ups.supplier_type,
            'base_price': ups.base_price,
            'currency': ups.currency,
            'is_available': ups.is_available,
            'product_name': supplier_product.name if supplier_product else None,
            'thumbnail_url': supplier_product.thumbnail_url if supplier_product else None
        })

    return jsonify({
        'product': product.to_dict(),
        'suppliers': suppliers
    })
