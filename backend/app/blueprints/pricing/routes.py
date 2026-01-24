"""
Pricing and profitability routes.
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.blueprints.pricing import pricing_bp
from app.models import ProductPricingRule, PlatformFeeStructure, UserProduct


# Etsy: 6.5% transaction, $0.20 listing, payment processing ~3%+$0.25
# Shopify: 0% if using Shopify Payments, else transaction fees; payment processing
def _etsy_fees(price_usd, is_offsite_ad=False, offsite_rate=0.15):
    listing = 0.20
    tx = float(price_usd) * 0.065
    payment_pct = 0.03
    payment_fixed = 0.25
    payment = float(price_usd) * payment_pct + payment_fixed
    offsite = float(price_usd) * offsite_rate if is_offsite_ad else 0
    return {
        'listing_fee': round(listing, 2),
        'transaction_fee': round(tx, 2),
        'payment_processing_fee': round(payment, 2),
        'offsite_ads_fee': round(offsite, 2),
        'total_fees': round(listing + tx + payment + offsite, 2),
        'net': round(float(price_usd) - (listing + tx + payment + offsite), 2),
    }


def _shopify_fees(price_usd, has_shopify_payments=True):
    if has_shopify_payments:
        # Usually 2.9% + $0.30
        payment = float(price_usd) * 0.029 + 0.30
    else:
        payment = float(price_usd) * 0.02  # approx
    return {
        'transaction_fee': 0,
        'payment_processing_fee': round(payment, 2),
        'total_fees': round(payment, 2),
        'net': round(float(price_usd) - payment, 2),
    }


@pricing_bp.route('/calculator', methods=['GET', 'POST'])
@jwt_required()
def calculator():
    """
    Fee calculator.

    GET params or POST body:
        platform: etsy | shopify
        price: float
        cost: float (optional, for margin)
        is_offsite_ad: bool (Etsy)
        has_shopify_payments: bool (Shopify)
    """
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = request.args

    platform = (data.get('platform') or 'etsy').lower()
    try:
        price = float(data.get('price') or 0)
    except (TypeError, ValueError):
        price = 0
    try:
        cost = float(data.get('cost') or 0)
    except (TypeError, ValueError):
        cost = 0

    if platform == 'etsy':
        is_offsite = data.get('is_offsite_ad') in (True, 'true', '1')
        fees = _etsy_fees(price, is_offsite_ad=is_offsite)
        fees['platform'] = 'etsy'
    else:
        use_sp = data.get('has_shopify_payments') not in (False, 'false', '0')
        fees = _shopify_fees(price, has_shopify_payments=use_sp)
        fees['platform'] = 'shopify'

    fees['price'] = price
    fees['cost'] = cost
    if price and cost:
        fees['gross_profit'] = round(fees['net'] - cost, 2)
        fees['margin_percent'] = round((fees['net'] - cost) / price * 100, 1) if price else 0

    return jsonify(fees)


@pricing_bp.route('/rules', methods=['GET'])
@jwt_required()
def list_rules():
    """List pricing rules for current user."""
    user_id = get_jwt_identity()
    rules = ProductPricingRule.query.filter_by(user_id=user_id).all()
    return jsonify({'rules': [r.to_dict() for r in rules]})


@pricing_bp.route('/rules', methods=['POST'])
@jwt_required()
def create_rule():
    """Create a pricing rule."""
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    rule = ProductPricingRule(
        user_id=user_id,
        user_product_id=data.get('user_product_id'),
        product_id=data.get('product_id'),
        base_cost=data.get('base_cost'),
        markup_percentage=data.get('markup_percentage'),
        markup_fixed=data.get('markup_fixed'),
        min_price=data.get('min_price'),
        target_margin=data.get('target_margin'),
        final_price=data.get('final_price'),
        currency=data.get('currency', 'USD'),
    )
    db.session.add(rule)
    db.session.commit()
    return jsonify(rule.to_dict()), 201


@pricing_bp.route('/rules/<int:rule_id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required()
def rule_detail(rule_id):
    """Get, update, or delete a pricing rule."""
    user_id = get_jwt_identity()
    rule = ProductPricingRule.query.filter_by(id=rule_id, user_id=user_id).first()
    if not rule:
        return jsonify({'error': 'Pricing rule not found'}), 404

    if request.method == 'GET':
        return jsonify(rule.to_dict())

    if request.method == 'DELETE':
        db.session.delete(rule)
        db.session.commit()
        return jsonify({'message': 'Deleted'}), 200

    data = request.get_json() or {}
    for k in ('base_cost', 'markup_percentage', 'markup_fixed', 'min_price', 'target_margin', 'platform_fees', 'final_price', 'currency'):
        if k in data:
            setattr(rule, k, data[k])
    db.session.commit()
    return jsonify(rule.to_dict())
