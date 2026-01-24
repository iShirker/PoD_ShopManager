"""
Settings routes: billing, subscription, usage.
"""
from datetime import datetime, date, timedelta
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.blueprints.settings import settings_bp
from app.models import (
    SubscriptionPlan,
    UserSubscription,
    UsageRecord,
    Shop,
    UserProduct,
    Product,
    User,
)
from app import db


def _yearly_price(price_monthly: float) -> float:
    return round((float(price_monthly) * 11) + 0.10, 2)


@settings_bp.route('/billing', methods=['GET'])
@jwt_required()
def billing():
    """
    Subscription and usage for billing UI.

    Returns current plan, usage, and available plans.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    sub = UserSubscription.query.filter_by(user_id=user_id).first()
    plan = sub.plan if sub else None
    if not plan:
        plan = SubscriptionPlan.query.filter_by(slug='starter').first()
    free_trial_used = user is not None and user.free_trial_used_at is not None

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
        'free_trial_used': free_trial_used,
    })


@settings_bp.route('/billing/quote', methods=['POST'])
@jwt_required()
def billing_quote():
    """
    Get checkout quote for a selected plan and interval.

    Body: { "plan_id": int, "interval": "monthly" | "yearly" }
    Returns: { "subtotal", "prorated_credit", "total", "currency", "allowed" }
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    plan_id = data.get('plan_id')
    interval = (data.get('interval') or 'monthly').lower()
    if interval not in ('monthly', 'yearly'):
        return jsonify({'error': 'Invalid interval'}), 400
    if not plan_id:
        return jsonify({'error': 'plan_id required'}), 400

    plan = SubscriptionPlan.query.get(plan_id)
    if not plan or not plan.is_active:
        return jsonify({'error': 'Plan not found'}), 404

    sub = UserSubscription.query.filter_by(user_id=user_id).first()
    current_plan = sub.plan if sub else None
    current_interval = (sub.billing_interval or 'monthly').lower() if sub else None

    def plan_sort_key(p):
        if getattr(p, 'slug', None) == 'free_trial':
            return -1
        return float(p.price_monthly or 0)

    plans_asc = sorted(
        SubscriptionPlan.query.filter_by(is_active=True).all(),
        key=plan_sort_key,
    )
    current_idx = next((i for i, p in enumerate(plans_asc) if p.id == (current_plan.id if current_plan else None)), -1)
    selected_idx = next((i for i, p in enumerate(plans_asc) if p.id == plan_id), -1)
    if selected_idx < 0:
        return jsonify({'error': 'Plan not found'}), 404

    allowed = True
    if current_plan and selected_idx <= current_idx:
        allowed = False
    if current_interval == 'yearly' and interval != 'yearly':
        allowed = False
    if current_interval == 'yearly' and interval == 'yearly':
        curr_yr = _yearly_price(current_plan.price_monthly or 0)
        sel_yr = _yearly_price(plan.price_monthly or 0)
        if sel_yr <= curr_yr:
            allowed = False

    price_monthly = float(plan.price_monthly or 0)
    if price_monthly == 0:
        subtotal = 0.0
    elif interval == 'yearly':
        subtotal = _yearly_price(price_monthly)
    else:
        subtotal = price_monthly

    prorated_credit = 0.0
    if allowed and sub and current_plan and selected_idx > current_idx and price_monthly > 0:
        start = sub.current_period_start.date() if hasattr(sub.current_period_start, 'date') else sub.current_period_start
        end = sub.current_period_end.date() if hasattr(sub.current_period_end, 'date') else sub.current_period_end
        today = date.today()
        if end > today:
            total_days = (end - start).days or 1
            days_left = (end - today).days
            if current_interval == 'yearly':
                paid = _yearly_price(current_plan.price_monthly or 0)
            else:
                paid = float(current_plan.price_monthly or 0)
            prorated_credit = round(paid * (days_left / total_days), 2)

    total = max(0.0, round(subtotal - prorated_credit, 2))

    return jsonify({
        'subtotal': round(subtotal, 2),
        'prorated_credit': prorated_credit,
        'total': total,
        'currency': 'USD',
        'allowed': allowed,
    })


TRIAL_DAYS = 14


@settings_bp.route('/billing/start-trial', methods=['POST'])
@jwt_required()
def billing_start_trial():
    """
    Start free trial. Creates a subscription to free_trial plan.
    Allowed only once per user (free_trial_used_at).
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user.free_trial_used_at is not None:
        return jsonify({'error': 'Free trial already used'}), 400

    plan = SubscriptionPlan.query.filter_by(slug='free_trial', is_active=True).first()
    if not plan:
        return jsonify({'error': 'Free trial plan not available'}), 404

    now = datetime.utcnow()
    period_end = now + timedelta(days=TRIAL_DAYS)

    sub = UserSubscription.query.filter_by(user_id=user_id).first()
    if sub:
        sub.plan_id = plan.id
        sub.status = 'active'
        sub.billing_interval = 'monthly'
        sub.current_period_start = now
        sub.current_period_end = period_end
        sub.trial_ends_at = period_end
        sub.canceled_at = None
        sub.auto_renew = False  # Free trial cannot renew
    else:
        sub = UserSubscription(
            user_id=user_id,
            plan_id=plan.id,
            status='active',
            billing_interval='monthly',
            current_period_start=now,
            current_period_end=period_end,
            trial_ends_at=period_end,
            auto_renew=False,  # Free trial cannot renew
        )
        db.session.add(sub)

    user.free_trial_used_at = now
    db.session.commit()

    return jsonify({
        'message': 'Free trial started',
        'subscription': sub.to_dict(),
    })


@settings_bp.route('/billing/cancel', methods=['POST'])
@jwt_required()
def billing_cancel():
    """
    Disable auto-renew for the current subscription.
    """
    user_id = get_jwt_identity()
    sub = UserSubscription.query.filter_by(user_id=user_id).first()
    if not sub:
        return jsonify({'error': 'No active subscription'}), 404
    sub.auto_renew = False
    db.session.commit()
    return jsonify({
        'message': 'Auto-renew disabled',
        'subscription': sub.to_dict(),
    })
