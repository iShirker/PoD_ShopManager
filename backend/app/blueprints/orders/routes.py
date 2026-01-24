"""
Orders and fulfillment routes.
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.blueprints.orders import orders_bp
from app.models import Order, OrderItem, Fulfillment


@orders_bp.route('', methods=['GET'])
@jwt_required()
def list_orders():
    """
    List orders for current user.

    Query params: page, per_page, platform, shop_id, status
    """
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    platform = request.args.get('platform', '')
    shop_id = request.args.get('shop_id', type=int)
    status = request.args.get('status', '')

    query = Order.query.filter_by(user_id=user_id)
    if platform:
        query = query.filter(Order.platform == platform)
    if shop_id:
        query = query.filter(Order.shop_id == shop_id)
    if status:
        query = query.filter(Order.status == status)

    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'orders': [o.to_dict(include_items=True) for o in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        },
    })


@orders_bp.route('/fulfillment', methods=['GET'])
@jwt_required()
def list_fulfillment():
    """
    List orders/items pending fulfillment.
    """
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Order.query.filter(
        Order.user_id == user_id,
        Order.status.in_(['pending', 'processing']),
    )
    pagination = query.order_by(Order.created_at.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'orders': [o.to_dict(include_items=True) for o in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        },
    })


@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get single order with items and fulfillments."""
    user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    d = order.to_dict(include_items=True)
    for item in d.get('items', []):
        oi = OrderItem.query.get(item['id'])
        if oi and oi.fulfillments:
            item['fulfillments'] = [f.to_dict() for f in oi.fulfillments]
    return jsonify(d)
