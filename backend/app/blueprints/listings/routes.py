"""
Listings routes.
Unified view of Etsy/Shopify listings (shop products) across all user shops.
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.blueprints.listings import listings_bp
from app.models import Shop, Product


@listings_bp.route('', methods=['GET'])
@jwt_required()
def list_listings():
    """
    List all listings (shop products) across user's shops.

    Query params:
        page, per_page, shop_id, supplier, search
    """
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    shop_id = request.args.get('shop_id', type=int)
    supplier = request.args.get('supplier', '')
    search = request.args.get('search', '')

    shop_ids = [s.id for s in Shop.query.filter_by(user_id=user_id).all()]
    if not shop_ids:
        return jsonify({
            'listings': [],
            'pagination': {
                'page': 1,
                'per_page': per_page,
                'total': 0,
                'pages': 0,
                'has_next': False,
                'has_prev': False,
            },
            'shops': [],
        })

    query = Product.query.filter(Product.shop_id.in_(shop_ids))
    if shop_id:
        query = query.filter(Product.shop_id == shop_id)
    if supplier:
        query = query.filter(Product.supplier_type == supplier)
    if search:
        query = query.filter(
            db.or_(
                Product.title.ilike(f'%{search}%'),
                Product.sku.ilike(f'%{search}%'),
            )
        )

    pagination = query.order_by(Product.updated_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    items = pagination.items
    shops_map = {s.id: s for s in Shop.query.filter(Shop.id.in_(shop_ids)).all()}

    listings_data = []
    for p in items:
        d = p.to_dict(include_variants=True)
        d['shop_id'] = p.shop_id
        d['shop_name'] = shops_map.get(p.shop_id).shop_name if shops_map.get(p.shop_id) else None
        d['shop_type'] = shops_map.get(p.shop_id).shop_type if shops_map.get(p.shop_id) else None
        listings_data.append(d)

    return jsonify({
        'listings': listings_data,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        },
        'shops': [{'id': s.id, 'shop_name': s.shop_name, 'shop_type': s.shop_type} for s in Shop.query.filter_by(user_id=user_id).all()],
    })


@listings_bp.route('/<int:listing_id>', methods=['GET'])
@jwt_required()
def get_listing(listing_id):
    """Get a single listing by ID. Must belong to user's shop."""
    user_id = get_jwt_identity()
    shop_ids = [s.id for s in Shop.query.filter_by(user_id=user_id).all()]
    product = Product.query.filter(
        Product.id == listing_id,
        Product.shop_id.in_(shop_ids),
    ).first()
    if not product:
        return jsonify({'error': 'Listing not found'}), 404
    d = product.to_dict(include_variants=True)
    d['shop_id'] = product.shop_id
    shop = Shop.query.get(product.shop_id)
    d['shop_name'] = shop.shop_name if shop else None
    d['shop_type'] = shop.shop_type if shop else None
    return jsonify(d)
