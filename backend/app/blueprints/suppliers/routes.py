"""
Supplier connection routes.
Handles connecting, managing, and syncing POD suppliers.
"""
from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.blueprints.suppliers import suppliers_bp
from app.models import SupplierConnection, SupplierType, SupplierProduct
from app.services.suppliers import (
    validate_gelato_connection,
    validate_printify_connection,
    validate_printful_connection,
    sync_supplier_products
)


@suppliers_bp.route('', methods=['GET'])
@jwt_required()
def list_suppliers():
    """
    List all supplier connections for current user.

    Returns:
        List of supplier connections
    """
    user_id = get_jwt_identity()
    connections = SupplierConnection.query.filter_by(user_id=user_id).all()

    return jsonify({
        'suppliers': [c.to_dict(include_tokens=True) for c in connections]
    })


@suppliers_bp.route('/<supplier_type>', methods=['GET'])
@jwt_required()
def get_supplier(supplier_type):
    """
    Get specific supplier connection.

    Args:
        supplier_type: Type of supplier (gelato, printify, printful)

    Returns:
        Supplier connection details
    """
    user_id = get_jwt_identity()

    if supplier_type not in [s.value for s in SupplierType]:
        return jsonify({'error': 'Invalid supplier type'}), 400

    connection = SupplierConnection.query.filter_by(
        user_id=user_id,
        supplier_type=supplier_type
    ).first()

    if not connection:
        return jsonify({'error': 'Supplier not connected'}), 404

    return jsonify(connection.to_dict(include_tokens=True))


@suppliers_bp.route('/<supplier_type>/connect', methods=['POST'])
@jwt_required()
def connect_supplier(supplier_type):
    """
    Connect a POD supplier using API credentials.

    Args:
        supplier_type: Type of supplier (gelato, printify, printful)

    Request body:
        api_key: API key or token
        shop_id: Optional shop/store ID (required for Printify)

    Returns:
        Connection status and details
    """
    user_id = get_jwt_identity()

    if supplier_type not in [s.value for s in SupplierType]:
        return jsonify({'error': 'Invalid supplier type'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    api_key = data.get('api_key', '').strip()
    shop_id = data.get('shop_id', '').strip()

    if not api_key:
        return jsonify({'error': 'API key is required'}), 400

    # Validate connection based on supplier type
    try:
        if supplier_type == SupplierType.GELATO.value:
            is_valid, result = validate_gelato_connection(api_key)
        elif supplier_type == SupplierType.PRINTIFY.value:
            if not shop_id:
                # Try to get shop ID from API
                is_valid, result = validate_printify_connection(api_key)
                if is_valid and 'shops' in result:
                    if len(result['shops']) == 1:
                        shop_id = str(result['shops'][0]['id'])
                    else:
                        return jsonify({
                            'error': 'Multiple shops found. Please specify shop_id.',
                            'shops': result['shops']
                        }), 400
            else:
                is_valid, result = validate_printify_connection(api_key, shop_id)
        elif supplier_type == SupplierType.PRINTFUL.value:
            is_valid, result = validate_printful_connection(api_key)
        else:
            return jsonify({'error': 'Unsupported supplier type'}), 400

        if not is_valid:
            return jsonify({
                'error': 'Invalid credentials',
                'details': result.get('error', 'Connection validation failed')
            }), 401

    except Exception as e:
        return jsonify({'error': f'Connection failed: {str(e)}'}), 500

    # Create or update connection
    connection = SupplierConnection.query.filter_by(
        user_id=user_id,
        supplier_type=supplier_type
    ).first()

    if not connection:
        connection = SupplierConnection(
            user_id=user_id,
            supplier_type=supplier_type
        )
        db.session.add(connection)

    connection.api_key = api_key
    connection.shop_id = shop_id if supplier_type == SupplierType.PRINTIFY.value else None
    connection.store_id = result.get('store_id') if supplier_type == SupplierType.GELATO.value else None
    connection.is_connected = True
    connection.is_active = True
    connection.connection_error = None
    connection.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'message': f'{supplier_type.capitalize()} connected successfully',
        'connection': connection.to_dict(include_tokens=True)
    }), 201


@suppliers_bp.route('/<supplier_type>/disconnect', methods=['POST'])
@jwt_required()
def disconnect_supplier(supplier_type):
    """
    Disconnect a POD supplier.

    Args:
        supplier_type: Type of supplier (gelato, printify, printful)

    Returns:
        Success message
    """
    user_id = get_jwt_identity()

    if supplier_type not in [s.value for s in SupplierType]:
        return jsonify({'error': 'Invalid supplier type'}), 400

    connection = SupplierConnection.query.filter_by(
        user_id=user_id,
        supplier_type=supplier_type
    ).first()

    if not connection:
        return jsonify({'error': 'Supplier not connected'}), 404

    # Clear credentials but keep the record
    connection.api_key = None
    connection.api_secret = None
    connection.access_token = None
    connection.refresh_token = None
    connection.is_connected = False
    connection.connection_error = None

    db.session.commit()

    return jsonify({'message': f'{supplier_type.capitalize()} disconnected successfully'})


@suppliers_bp.route('/<supplier_type>/sync', methods=['POST'])
@jwt_required()
def sync_supplier(supplier_type):
    """
    Sync products from a POD supplier.

    Args:
        supplier_type: Type of supplier (gelato, printify, printful)

    Returns:
        Sync status and product count
    """
    user_id = get_jwt_identity()

    if supplier_type not in [s.value for s in SupplierType]:
        return jsonify({'error': 'Invalid supplier type'}), 400

    connection = SupplierConnection.query.filter_by(
        user_id=user_id,
        supplier_type=supplier_type,
        is_connected=True
    ).first()

    if not connection:
        return jsonify({'error': 'Supplier not connected'}), 404

    try:
        result = sync_supplier_products(connection)

        connection.last_sync = datetime.utcnow()
        connection.connection_error = None
        db.session.commit()

        return jsonify({
            'message': 'Sync completed',
            'products_synced': result.get('count', 0),
            'last_sync': connection.last_sync.isoformat()
        })

    except Exception as e:
        connection.connection_error = str(e)
        db.session.commit()
        return jsonify({'error': f'Sync failed: {str(e)}'}), 500


@suppliers_bp.route('/<supplier_type>/products', methods=['GET'])
@jwt_required()
def get_supplier_products(supplier_type):
    """
    Get products available from a supplier.

    Args:
        supplier_type: Type of supplier (gelato, printify, printful)

    Query params:
        page: Page number (default 1)
        per_page: Items per page (default 20)
        search: Search term for product name/type
        category: Filter by category

    Returns:
        Paginated list of supplier products
    """
    user_id = get_jwt_identity()

    if supplier_type not in [s.value for s in SupplierType]:
        return jsonify({'error': 'Invalid supplier type'}), 400

    connection = SupplierConnection.query.filter_by(
        user_id=user_id,
        supplier_type=supplier_type,
        is_connected=True
    ).first()

    if not connection:
        return jsonify({'error': 'Supplier not connected'}), 404

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

    return jsonify({
        'products': [p.to_dict() for p in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })


@suppliers_bp.route('/<supplier_type>/products/<product_id>', methods=['GET'])
@jwt_required()
def get_supplier_product(supplier_type, product_id):
    """
    Get specific supplier product details.

    Args:
        supplier_type: Type of supplier
        product_id: Product ID

    Returns:
        Product details with pricing and variants
    """
    user_id = get_jwt_identity()

    if supplier_type not in [s.value for s in SupplierType]:
        return jsonify({'error': 'Invalid supplier type'}), 400

    connection = SupplierConnection.query.filter_by(
        user_id=user_id,
        supplier_type=supplier_type,
        is_connected=True
    ).first()

    if not connection:
        return jsonify({'error': 'Supplier not connected'}), 404

    product = SupplierProduct.query.filter_by(
        supplier_connection_id=connection.id,
        id=product_id
    ).first()

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    return jsonify(product.to_dict())


@suppliers_bp.route('/status', methods=['GET'])
@jwt_required()
def get_all_supplier_status():
    """
    Get connection status for all supported suppliers.

    Returns:
        Status of each supplier type
    """
    user_id = get_jwt_identity()

    connections = SupplierConnection.query.filter_by(user_id=user_id).all()
    connection_map = {c.supplier_type: c for c in connections}

    status = {}
    for supplier in SupplierType:
        conn = connection_map.get(supplier.value)
        status[supplier.value] = {
            'is_connected': conn.is_connected if conn else False,
            'last_sync': conn.last_sync.isoformat() if conn and conn.last_sync else None,
            'has_error': bool(conn.connection_error) if conn else False,
            'error': conn.connection_error if conn else None
        }

    return jsonify({'suppliers': status})
