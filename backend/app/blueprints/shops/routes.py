"""
Shop management routes.
Handles connecting, managing, and syncing Etsy/Shopify shops.
"""
from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.blueprints.shops import shops_bp
from app.models import Shop, ShopType, Product, ProductVariant
from app.services.shops import (
    get_etsy_shops, get_shopify_shop_info,
    sync_etsy_listings, sync_shopify_products
)


@shops_bp.route('', methods=['GET'])
@jwt_required()
def list_shops():
    """
    List all connected shops for current user.

    Returns:
        List of shops with basic stats
    """
    user_id = get_jwt_identity()
    shops = Shop.query.filter_by(user_id=user_id).all()

    return jsonify({
        'shops': [s.to_dict() for s in shops]
    })


@shops_bp.route('/<int:shop_id>', methods=['GET'])
@jwt_required()
def get_shop(shop_id):
    """
    Get specific shop details.

    Args:
        shop_id: Shop ID

    Returns:
        Shop details
    """
    user_id = get_jwt_identity()
    shop = Shop.query.filter_by(id=shop_id, user_id=user_id).first()

    if not shop:
        return jsonify({'error': 'Shop not found'}), 404

    return jsonify(shop.to_dict(include_tokens=True))


@shops_bp.route('/etsy/connect', methods=['POST'])
@jwt_required()
def connect_etsy_shop():
    """
    Connect an Etsy shop using OAuth tokens.

    Request body:
        access_token: Etsy OAuth access token
        refresh_token: Etsy OAuth refresh token
        shop_id: Optional specific shop ID (if user has multiple)

    Returns:
        Connected shop details
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    access_token = data.get('access_token')
    refresh_token = data.get('refresh_token')
    shop_id = data.get('shop_id')

    if not access_token:
        return jsonify({'error': 'Access token is required'}), 400

    try:
        # Get shops from Etsy
        etsy_shops = get_etsy_shops(access_token)

        if not etsy_shops:
            return jsonify({'error': 'No Etsy shops found'}), 404

        # If multiple shops and no shop_id specified, return list
        if len(etsy_shops) > 1 and not shop_id:
            return jsonify({
                'message': 'Multiple shops found. Please specify shop_id.',
                'shops': etsy_shops
            }), 400

        # Use specified or first shop
        etsy_shop = None
        if shop_id:
            etsy_shop = next((s for s in etsy_shops if str(s['shop_id']) == str(shop_id)), None)
        if not etsy_shop:
            etsy_shop = etsy_shops[0]

        # Check if already connected
        existing = Shop.query.filter_by(
            user_id=user_id,
            shop_type=ShopType.ETSY.value,
            shop_id=str(etsy_shop['shop_id'])
        ).first()

        if existing:
            # Update tokens
            existing.access_token = access_token
            existing.refresh_token = refresh_token
            existing.is_connected = True
            existing.connection_error = None
            db.session.commit()
            return jsonify({
                'message': 'Etsy shop reconnected',
                'shop': existing.to_dict()
            })

        # Create new shop connection
        shop = Shop(
            user_id=user_id,
            shop_type=ShopType.ETSY.value,
            shop_name=etsy_shop['shop_name'],
            shop_id=str(etsy_shop['shop_id']),
            shop_url=etsy_shop.get('url'),
            access_token=access_token,
            refresh_token=refresh_token,
            is_connected=True,
            is_active=True
        )
        db.session.add(shop)
        db.session.commit()

        return jsonify({
            'message': 'Etsy shop connected',
            'shop': shop.to_dict()
        }), 201

    except Exception as e:
        return jsonify({'error': f'Failed to connect shop: {str(e)}'}), 500


@shops_bp.route('/shopify/connect', methods=['POST'])
@jwt_required()
def connect_shopify_shop():
    """
    Connect a Shopify shop using OAuth tokens.

    Request body:
        access_token: Shopify access token
        shop_domain: Shopify shop domain (mystore.myshopify.com)

    Returns:
        Connected shop details
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    access_token = data.get('access_token')
    shop_domain = data.get('shop_domain', '').strip()

    if not access_token or not shop_domain:
        return jsonify({'error': 'Access token and shop domain are required'}), 400

    # Normalize domain
    if not shop_domain.endswith('.myshopify.com'):
        shop_domain = f"{shop_domain}.myshopify.com"

    try:
        # Get shop info from Shopify
        shop_info = get_shopify_shop_info(shop_domain, access_token)

        if not shop_info:
            return jsonify({'error': 'Could not fetch shop information'}), 400

        # Check if already connected
        existing = Shop.query.filter_by(
            user_id=user_id,
            shop_type=ShopType.SHOPIFY.value,
            shopify_domain=shop_domain
        ).first()

        if existing:
            # Update tokens
            existing.access_token = access_token
            existing.is_connected = True
            existing.connection_error = None
            db.session.commit()
            return jsonify({
                'message': 'Shopify shop reconnected',
                'shop': existing.to_dict()
            })

        # Create new shop connection
        shop = Shop(
            user_id=user_id,
            shop_type=ShopType.SHOPIFY.value,
            shop_name=shop_info.get('name', shop_domain),
            shop_id=str(shop_info.get('id', shop_domain)),
            shop_url=f"https://{shop_domain}",
            shopify_domain=shop_domain,
            access_token=access_token,
            is_connected=True,
            is_active=True
        )
        db.session.add(shop)
        db.session.commit()

        return jsonify({
            'message': 'Shopify shop connected',
            'shop': shop.to_dict()
        }), 201

    except Exception as e:
        return jsonify({'error': f'Failed to connect shop: {str(e)}'}), 500


@shops_bp.route('/<int:shop_id>/disconnect', methods=['POST'])
@jwt_required()
def disconnect_shop(shop_id):
    """
    Disconnect a shop.

    Args:
        shop_id: Shop ID

    Returns:
        Success message
    """
    user_id = get_jwt_identity()
    shop = Shop.query.filter_by(id=shop_id, user_id=user_id).first()

    if not shop:
        return jsonify({'error': 'Shop not found'}), 404

    shop.access_token = None
    shop.refresh_token = None
    shop.is_connected = False
    db.session.commit()

    return jsonify({'message': 'Shop disconnected'})


@shops_bp.route('/<int:shop_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_shop(shop_id):
    """
    Delete a shop and all its products.

    Args:
        shop_id: Shop ID

    Returns:
        Success message
    """
    user_id = get_jwt_identity()
    shop = Shop.query.filter_by(id=shop_id, user_id=user_id).first()

    if not shop:
        return jsonify({'error': 'Shop not found'}), 404

    db.session.delete(shop)
    db.session.commit()

    return jsonify({'message': 'Shop deleted'})


@shops_bp.route('/<int:shop_id>/sync', methods=['POST'])
@jwt_required()
def sync_shop(shop_id):
    """
    Sync listings from a shop.

    Args:
        shop_id: Shop ID

    Returns:
        Sync status and results
    """
    user_id = get_jwt_identity()
    shop = Shop.query.filter_by(id=shop_id, user_id=user_id, is_connected=True).first()

    if not shop:
        return jsonify({'error': 'Shop not found or not connected'}), 404

    try:
        if shop.shop_type == ShopType.ETSY.value:
            result = sync_etsy_listings(shop)
        elif shop.shop_type == ShopType.SHOPIFY.value:
            result = sync_shopify_products(shop)
        else:
            return jsonify({'error': 'Unsupported shop type'}), 400

        shop.last_sync = datetime.utcnow()
        shop.total_listings = result.get('total', 0)
        shop.pod_listings = result.get('pod_count', 0)
        shop.connection_error = None
        db.session.commit()

        return jsonify({
            'message': 'Sync completed',
            'total_listings': result.get('total', 0),
            'pod_listings': result.get('pod_count', 0),
            'last_sync': shop.last_sync.isoformat()
        })

    except Exception as e:
        shop.connection_error = str(e)
        db.session.commit()
        return jsonify({'error': f'Sync failed: {str(e)}'}), 500


@shops_bp.route('/<int:shop_id>/products', methods=['GET'])
@jwt_required()
def get_shop_products(shop_id):
    """
    Get products from a shop.

    Args:
        shop_id: Shop ID

    Query params:
        page: Page number (default 1)
        per_page: Items per page (default 20)
        supplier: Filter by supplier type
        search: Search in title/SKU

    Returns:
        Paginated list of products
    """
    user_id = get_jwt_identity()
    shop = Shop.query.filter_by(id=shop_id, user_id=user_id).first()

    if not shop:
        return jsonify({'error': 'Shop not found'}), 404

    # Pagination and filters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    supplier = request.args.get('supplier', '')
    search = request.args.get('search', '')

    query = Product.query.filter_by(shop_id=shop.id)

    if supplier:
        query = query.filter(Product.supplier_type == supplier)

    if search:
        query = query.filter(
            db.or_(
                Product.title.ilike(f'%{search}%'),
                Product.sku.ilike(f'%{search}%')
            )
        )

    pagination = query.order_by(Product.title).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'products': [p.to_dict(include_variants=True) for p in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })


@shops_bp.route('/<int:shop_id>/products/<int:product_id>', methods=['GET'])
@jwt_required()
def get_shop_product(shop_id, product_id):
    """
    Get specific product details.

    Args:
        shop_id: Shop ID
        product_id: Product ID

    Returns:
        Product details with variants
    """
    user_id = get_jwt_identity()
    shop = Shop.query.filter_by(id=shop_id, user_id=user_id).first()

    if not shop:
        return jsonify({'error': 'Shop not found'}), 404

    product = Product.query.filter_by(id=product_id, shop_id=shop.id).first()

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    return jsonify(product.to_dict(include_variants=True))
