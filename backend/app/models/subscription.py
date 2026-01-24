"""
Subscription and usage models for plan enforcement.
"""
from datetime import datetime
from app import db


class SubscriptionPlan(db.Model):
    """Subscription plan definitions (starter, growth, scale, free_trial)."""

    __tablename__ = 'subscription_plans'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price_monthly = db.Column(db.Numeric(10, 2), nullable=False)
    price_yearly = db.Column(db.Numeric(10, 2), nullable=True)
    limits = db.Column(db.JSON, nullable=False)  # stores, products, listings, orders_monthly, storage_mb, mockups_monthly, etc.
    features = db.Column(db.JSON, nullable=True)  # feature flags
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
            'price_monthly': float(self.price_monthly) if self.price_monthly else 0,
            'price_yearly': float(self.price_yearly) if self.price_yearly else None,
            'limits': self.limits,
            'features': self.features,
            'is_active': self.is_active,
        }


class UserSubscription(db.Model):
    """Current subscription for a user."""

    __tablename__ = 'user_subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, index=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # trialing, active, past_due, canceled
    billing_interval = db.Column(db.String(20), nullable=True)  # monthly, yearly
    trial_ends_at = db.Column(db.DateTime, nullable=True)
    current_period_start = db.Column(db.DateTime, nullable=False)
    current_period_end = db.Column(db.DateTime, nullable=False)
    canceled_at = db.Column(db.DateTime, nullable=True)
    auto_renew = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    plan = db.relationship('SubscriptionPlan', backref='user_subscriptions')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'plan': self.plan.to_dict() if self.plan else None,
            'status': self.status,
            'billing_interval': self.billing_interval or 'monthly',
            'trial_ends_at': self.trial_ends_at.isoformat() if self.trial_ends_at else None,
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'canceled_at': self.canceled_at.isoformat() if self.canceled_at else None,
            'auto_renew': self.auto_renew if self.auto_renew is not None else True,
        }


class UsageRecord(db.Model):
    """Usage tracking per user per period (for limits and overages)."""

    __tablename__ = 'usage_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    stores_connected = db.Column(db.Integer, default=0)
    products_count = db.Column(db.Integer, default=0)
    listings_count = db.Column(db.Integer, default=0)
    orders_processed = db.Column(db.Integer, default=0)
    mockups_generated = db.Column(db.Integer, default=0)
    storage_bytes = db.Column(db.BigInteger, default=0)
    seo_suggestions_used = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'period_start', name='uq_usage_user_period'),)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'stores_connected': self.stores_connected,
            'products_count': self.products_count,
            'listings_count': self.listings_count,
            'orders_processed': self.orders_processed,
            'mockups_generated': self.mockups_generated,
            'storage_bytes': self.storage_bytes,
            'seo_suggestions_used': self.seo_suggestions_used,
        }
