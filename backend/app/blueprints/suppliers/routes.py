"""
Supplier connection routes.
Handles connecting, managing, and syncing POD suppliers.
Supports multiple accounts per supplier type.
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
        List of supplier connections grouped by type
    """
    user_id = get_jwt_identity()
    connections = SupplierConnection.query.filter_by(user_id=user_id).all()

    return jsonify({
        'suppliers': [c.to_dict(include_tokens=True) for c in connections]
    })


@suppliers_bp.route('/<supplier_type>', methods=['GET'])
@jwt_required()
def get_supplier_connections(supplier_type):
    """
    Get all connections for a specific supplier type.

    Args:
        supplier_type: Type of supplier (gelato, printify, printful)

    Returns:
        List of supplier connections for this type
    """
    user_id = get_jwt_identity()

    if supplier_type not in [s.value for s in SupplierType]:
        return jsonify({'error': 'Invalid supplier type'}), 400

    connections = SupplierConnection.query.filter_by(
        user_id=user_id,
        supplier_type=supplier_type
    ).all()

    return jsonify({
        'connections': [c.to_dict(include_tokens=True) for c in connections]
    })


@suppliers_bp.route('/connection/<int:connection_id>', methods=['GET'])
@jwt_required()
def get_connection(connection_id):
    """
    Get a specific supplier connection by ID.

    Args:
        connection_id: Connection ID

    Returns:
        Supplier connection details
    """
    user_id = get_jwt_identity()

    connection = SupplierConnection.query.filter_by(
        id=connection_id,
        user_id=user_id
    ).first()

    if not connection:
        return jsonify({'error': 'Connection not found'}), 404

    return jsonify(connection.to_dict(include_tokens=True))


@suppliers_bp.route('/<supplier_type>/connect', methods=['POST'])
@jwt_required()
def connect_supplier(supplier_type):
    """
    Connect a POD supplier using API credentials.
    Creates a new connection (allows multiple accounts per supplier).

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
    
    # Log token preview for debugging (first 10 and last 10 chars)
    if len(api_key) > 20:
        token_preview = f"{api_key[:10]}...{api_key[-10:]}"
    else:
        token_preview = "***"
    current_app.logger.info(f"Connecting {supplier_type} with token: {token_preview}")

    # Validate connection based on supplier type
    try:
        if supplier_type == SupplierType.GELATO.value:
            is_valid, result = validate_gelato_connection(api_key)
        elif supplier_type == SupplierType.PRINTIFY.value:
            if not shop_id:
                # Try to get shop ID from API
                is_valid, result = validate_printify_connection(api_key)
                if is_valid and 'shops' in result:
                    shops = result['shops']
                    if isinstance(shops, list) and len(shops) == 1:
                        shop_id = str(shops[0].get('id'))
                    elif isinstance(shops, list) and len(shops) > 1:
                        return jsonify({
                            'error': 'Multiple shops found. Please specify shop_id.',
                            'shops': shops
                        }), 400
            else:
                is_valid, result = validate_printify_connection(api_key, shop_id)
        elif supplier_type == SupplierType.PRINTFUL.value:
            is_valid, result = validate_printful_connection(api_key)
        else:
            return jsonify({'error': 'Unsupported supplier type'}), 400

        if not is_valid:
            error_msg = result.get('error', 'Connection validation failed')
            details = result.get('details')
            return jsonify({
                'error': error_msg,
                'details': details or error_msg
            }), 401

    except Exception as e:
        import traceback
        current_app.logger.error(f"Supplier connection error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'error': f'Connection failed: {str(e)}',
            'details': str(e)
        }), 500

    # Check if this exact API key already exists for this user
    existing = SupplierConnection.query.filter_by(
        user_id=user_id,
        supplier_type=supplier_type,
        api_key=api_key
    ).first()

    if existing:
        return jsonify({
            'error': 'This account is already connected',
            'connection': existing.to_dict(include_tokens=True)
        }), 409

    # Create new connection
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

    # Set account info from validation result (fetched from API)
    connection.account_name = result.get('account_name') or result.get('store_name') or result.get('shop_name') or f"{supplier_type.capitalize()} Account"
    connection.account_email = result.get('email') or result.get('account_email')
    connection.account_id = result.get('account_id') or result.get('user_id') or result.get('store_id') or result.get('shop_id')

    db.session.commit()

    return jsonify({
        'message': f'{supplier_type.capitalize()} connected successfully',
        'connection': connection.to_dict(include_tokens=True)
    }), 201


@suppliers_bp.route('/connection/<int:connection_id>/disconnect', methods=['POST'])
@jwt_required()
def disconnect_connection(connection_id):
    """
    Disconnect (delete) a supplier connection.

    Args:
        connection_id: Connection ID

    Returns:
        Success message
    """
    user_id = get_jwt_identity()

    connection = SupplierConnection.query.filter_by(
        id=connection_id,
        user_id=user_id
    ).first()

    if not connection:
        return jsonify({'error': 'Connection not found'}), 404

    supplier_type = connection.supplier_type
    account_name = connection.account_name or supplier_type

    # Delete the connection entirely
    db.session.delete(connection)
    db.session.commit()

    return jsonify({
        'message': f'{account_name} disconnected successfully'
    })


@suppliers_bp.route('/connection/<int:connection_id>/activate', methods=['POST'])
@jwt_required()
def activate_connection(connection_id):
    """
    Activate a supplier connection.

    Args:
        connection_id: Connection ID

    Returns:
        Updated connection
    """
    user_id = get_jwt_identity()

    connection = SupplierConnection.query.filter_by(
        id=connection_id,
        user_id=user_id
    ).first()

    if not connection:
        return jsonify({'error': 'Connection not found'}), 404

    connection.is_active = True
    connection.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': f'{connection.account_name or connection.supplier_type} activated',
        'connection': connection.to_dict(include_tokens=True)
    })


@suppliers_bp.route('/connection/<int:connection_id>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_connection(connection_id):
    """
    Deactivate a supplier connection.

    Args:
        connection_id: Connection ID

    Returns:
        Updated connection
    """
    user_id = get_jwt_identity()

    connection = SupplierConnection.query.filter_by(
        id=connection_id,
        user_id=user_id
    ).first()

    if not connection:
        return jsonify({'error': 'Connection not found'}), 404

    connection.is_active = False
    connection.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': f'{connection.account_name or connection.supplier_type} deactivated',
        'connection': connection.to_dict(include_tokens=True)
    })


@suppliers_bp.route('/connection/<int:connection_id>/sync', methods=['POST'])
@jwt_required()
def sync_connection(connection_id):
    """
    Sync products from a supplier connection.

    Args:
        connection_id: Connection ID

    Returns:
        Sync status and product count
    """
    user_id = get_jwt_identity()

    connection = SupplierConnection.query.filter_by(
        id=connection_id,
        user_id=user_id,
        is_connected=True
    ).first()

    if not connection:
        return jsonify({'error': 'Connection not found'}), 404

    if not connection.is_active:
        return jsonify({'error': 'Connection is deactivated'}), 400

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


@suppliers_bp.route('/connection/<int:connection_id>/products', methods=['GET'])
@jwt_required()
def get_connection_products(connection_id):
    """
    Get products from a specific connection.

    Args:
        connection_id: Connection ID

    Query params:
        page: Page number (default 1)
        per_page: Items per page (default 20)
        search: Search term for product name/type
        category: Filter by category

    Returns:
        Paginated list of supplier products
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


# Legacy routes for backwards compatibility
@suppliers_bp.route('/<supplier_type>/disconnect', methods=['POST'])
@jwt_required()
def disconnect_supplier(supplier_type):
    """
    Disconnect all connections for a supplier type.
    Legacy endpoint - prefer using /connection/<id>/disconnect
    """
    user_id = get_jwt_identity()

    if supplier_type not in [s.value for s in SupplierType]:
        return jsonify({'error': 'Invalid supplier type'}), 400

    connections = SupplierConnection.query.filter_by(
        user_id=user_id,
        supplier_type=supplier_type
    ).all()

    if not connections:
        return jsonify({'error': 'Supplier not connected'}), 404

    for connection in connections:
        db.session.delete(connection)

    db.session.commit()

    return jsonify({'message': f'{supplier_type.capitalize()} disconnected successfully'})


@suppliers_bp.route('/<supplier_type>/sync', methods=['POST'])
@jwt_required()
def sync_supplier(supplier_type):
    """
    Sync products from all active connections of a supplier type.
    Legacy endpoint - prefer using /connection/<id>/sync
    """
    user_id = get_jwt_identity()

    if supplier_type not in [s.value for s in SupplierType]:
        return jsonify({'error': 'Invalid supplier type'}), 400

    connections = SupplierConnection.query.filter_by(
        user_id=user_id,
        supplier_type=supplier_type,
        is_connected=True,
        is_active=True
    ).all()

    if not connections:
        return jsonify({'error': 'No active connections for this supplier'}), 404

    total_synced = 0
    errors = []

    for connection in connections:
        try:
            result = sync_supplier_products(connection)
            connection.last_sync = datetime.utcnow()
            connection.connection_error = None
            total_synced += result.get('count', 0)
        except Exception as e:
            connection.connection_error = str(e)
            errors.append(f"{connection.account_name}: {str(e)}")

    db.session.commit()

    response = {
        'message': 'Sync completed',
        'products_synced': total_synced,
    }

    if errors:
        response['errors'] = errors

    return jsonify(response)


@suppliers_bp.route('/<supplier_type>/products', methods=['GET'])
@jwt_required()
def get_supplier_products(supplier_type):
    """
    Get products from all connections of a supplier type.
    Legacy endpoint - prefer using /connection/<id>/products
    """
    user_id = get_jwt_identity()

    if supplier_type not in [s.value for s in SupplierType]:
        return jsonify({'error': 'Invalid supplier type'}), 400

    connections = SupplierConnection.query.filter_by(
        user_id=user_id,
        supplier_type=supplier_type,
        is_connected=True
    ).all()

    if not connections:
        return jsonify({'error': 'Supplier not connected'}), 404

    connection_ids = [c.id for c in connections]

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')

    query = SupplierProduct.query.filter(
        SupplierProduct.supplier_connection_id.in_(connection_ids),
        SupplierProduct.is_active == True
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
    """
    user_id = get_jwt_identity()

    if supplier_type not in [s.value for s in SupplierType]:
        return jsonify({'error': 'Invalid supplier type'}), 400

    connections = SupplierConnection.query.filter_by(
        user_id=user_id,
        supplier_type=supplier_type,
        is_connected=True
    ).all()

    if not connections:
        return jsonify({'error': 'Supplier not connected'}), 404

    connection_ids = [c.id for c in connections]

    product = SupplierProduct.query.filter(
        SupplierProduct.supplier_connection_id.in_(connection_ids),
        SupplierProduct.id == product_id
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
        Status of each supplier type with connection counts
    """
    user_id = get_jwt_identity()

    connections = SupplierConnection.query.filter_by(user_id=user_id).all()

    # Group connections by supplier type
    by_type = {}
    for conn in connections:
        if conn.supplier_type not in by_type:
            by_type[conn.supplier_type] = []
        by_type[conn.supplier_type].append(conn)

    status = {}
    for supplier in SupplierType:
        conns = by_type.get(supplier.value, [])
        active_conns = [c for c in conns if c.is_connected and c.is_active]
        status[supplier.value] = {
            'is_connected': len(active_conns) > 0,
            'connection_count': len(conns),
            'active_count': len(active_conns),
            'last_sync': max((c.last_sync for c in conns if c.last_sync), default=None),
            'has_error': any(c.connection_error for c in conns),
        }
        if status[supplier.value]['last_sync']:
            status[supplier.value]['last_sync'] = status[supplier.value]['last_sync'].isoformat()

    return jsonify({'suppliers': status})
