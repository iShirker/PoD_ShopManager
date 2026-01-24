"""
Settings routes: billing, subscription, usage.
"""
from datetime import datetime, date, timedelta
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.blueprints.settings import settings_bp
from app.models import (
    SubscriptionPlan,
    UserSubscription,
    UsageRecord,
    Shop,
    UserProduct,
    Product,
)
from app import db


@settings_bp.route('/billing', methods=['GET'])
@jwt_required()
def billing():
    """
    Subscription and usage for billing UI.

    Returns current plan, usage, and available plans.
    """
    user_id = get_jwt_identity()
    sub = UserSubscription.query.filter_by(user_id=user_id).first()
    plan = sub.plan if sub else None
    if not plan:
        plan = SubscriptionPlan.query.filter_by(slug='starter').first()

    year, month = date.today().year, date.today().month
    period_start = date(year, month, 1)
    if month == 12:
        period_end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        period_end = date(year, month + 1, 1) - timedelta(days=1)

    usage = UsageRecord.query.filter_by(
        user_id=user_id,
        period_start=period_start,
    ).first()
    if not usage:
        shops = Shop.query.filter_by(user_id=user_id).all()
        shop_ids = [s.id for s in shops]
        listings_count = Product.query.filter(Product.shop_id.in_(shop_ids)).count() if shop_ids else 0
        usage = UsageRecord(
            user_id=user_id,
            period_start=period_start,
            period_end=period_end,
            stores_connected=len(shops),
            products_count=UserProduct.query.filter_by(user_id=user_id, is_active=True).count(),
            listings_count=listings_count,
            orders_processed=0,
            mockups_generated=0,
            storage_bytes=0,
            seo_suggestions_used=0,
        )
        db.session.add(usage)
        db.session.commit()

    plans = SubscriptionPlan.query.filter_by(is_active=True).order_by(SubscriptionPlan.price_monthly).all()

    return jsonify({
        'subscription': sub.to_dict() if sub else None,
        'plan': plan.to_dict() if plan else None,
        'usage': usage.to_dict(),
        'plans': [p.to_dict() for p in plans],
    })
