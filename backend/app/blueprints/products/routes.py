"""
Product comparison and switching routes.
Handles supplier comparison and product migration between suppliers.
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.blueprints.products import products_bp
from app.models import (
    User, Product, Shop, SupplierConnection, SupplierProduct, SupplierType
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
