"""
Product comparison and switching routes.
Handles supplier comparison and product migration between suppliers.
"""
from datetime import datetime
from flask import request, jsonify
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
    category = request.args.get('category', '')

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
    supplier_product_id = data.get('supplier_product_id')  # This is the SupplierProduct.id

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

    # Get supplier product
    supplier_product = SupplierProduct.query.filter_by(
        id=supplier_product_id,
        supplier_connection_id=supplier_connection_id
    ).first()

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
