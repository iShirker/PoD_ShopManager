"""
Analytics routes.
"""
from datetime import datetime, timedelta
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.blueprints.analytics import analytics_bp
from app.models import Order, Product, Shop, UserProduct


def _period():
    period = request.args.get('period', '30d')
    today = datetime.utcnow().date()
    if period == '7d':
        start = today - timedelta(days=7)
    elif period == '90d':
        start = today - timedelta(days=90)
    else:
        start = today - timedelta(days=30)
    return start, today


@analytics_bp.route('/overview', methods=['GET'])
@jwt_required()
def overview():
    """
    Analytics overview: revenue, orders, costs, profit.

    Query: period=7d|30d|90d
    """
    user_id = get_jwt_identity()
    start, end = _period()

    orders = Order.query.filter(
        Order.user_id == user_id,
        db.func.date(Order.created_at) >= start,
        db.func.date(Order.created_at) <= end,
        Order.status != 'canceled',
    ).all()

    total_revenue = sum(float(o.total_amount or 0) for o in orders)
    total_orders = len(orders)
    total_items = sum(sum(i.quantity for i in o.items) for o in orders)

    shop_ids = [s.id for s in Shop.query.filter_by(user_id=user_id).all()]
    listings_count = Product.query.filter(Product.shop_id.in_(shop_ids)).count() if shop_ids else 0
    products_count = UserProduct.query.filter_by(user_id=user_id, is_active=True).count()

    return jsonify({
        'period': {'start': start.isoformat(), 'end': end.isoformat()},
        'total_revenue': round(total_revenue, 2),
        'total_orders': total_orders,
        'total_items_sold': total_items,
        'listings_count': listings_count,
        'products_count': products_count,
        'total_costs': 0,
        'total_fees': 0,
        'net_profit': round(total_revenue, 2),
    })


@analytics_bp.route('/products', methods=['GET'])
@jwt_required()
def product_performance():
    """Product performance (placeholder)."""
    user_id = get_jwt_identity()
    return jsonify({
        'products': [],
        'period': {'start': None, 'end': None},
    })


@analytics_bp.route('/profitability', methods=['GET'])
@jwt_required()
def profitability():
    """Profitability reports (placeholder)."""
    user_id = get_jwt_identity()
    return jsonify({
        'by_product': [],
        'by_category': [],
        'period': {'start': None, 'end': None},
    })
