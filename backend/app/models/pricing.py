"""
Pricing and fee models.
"""
from datetime import datetime
from app import db


class PlatformFeeStructure(db.Model):
    """Platform fee definitions (Etsy, Shopify)."""

    __tablename__ = 'platform_fee_structures'

    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)
    fee_type = db.Column(db.String(50), nullable=False)  # listing, transaction, payment_processing, ads
    fee_percentage = db.Column(db.Numeric(5, 2), nullable=True)
    fee_fixed = db.Column(db.Numeric(10, 2), nullable=True)
    min_fee = db.Column(db.Numeric(10, 2), nullable=True)
    max_fee = db.Column(db.Numeric(10, 2), nullable=True)
    conditions = db.Column(db.JSON, nullable=True)
    effective_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'platform': self.platform,
            'fee_type': self.fee_type,
            'fee_percentage': float(self.fee_percentage) if self.fee_percentage else None,
            'fee_fixed': float(self.fee_fixed) if self.fee_fixed else None,
            'min_fee': float(self.min_fee) if self.min_fee else None,
            'max_fee': float(self.max_fee) if self.max_fee else None,
            'conditions': self.conditions,
            'is_active': self.is_active,
        }


class ProductPricingRule(db.Model):
    """Per-product or per-variant pricing rules."""

    __tablename__ = 'product_pricing_rules'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    user_product_id = db.Column(db.Integer, db.ForeignKey('user_products.id'), nullable=True, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True, index=True)  # shop listing
    base_cost = db.Column(db.Numeric(10, 2), nullable=True)
    markup_percentage = db.Column(db.Numeric(5, 2), nullable=True)
    markup_fixed = db.Column(db.Numeric(10, 2), nullable=True)
    min_price = db.Column(db.Numeric(10, 2), nullable=True)
    target_margin = db.Column(db.Numeric(5, 2), nullable=True)
    platform_fees = db.Column(db.Numeric(10, 2), nullable=True)
    final_price = db.Column(db.Numeric(10, 2), nullable=True)
    currency = db.Column(db.String(10), default='USD')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_product_id': self.user_product_id,
            'product_id': self.product_id,
            'base_cost': float(self.base_cost) if self.base_cost else None,
            'markup_percentage': float(self.markup_percentage) if self.markup_percentage else None,
            'markup_fixed': float(self.markup_fixed) if self.markup_fixed else None,
            'min_price': float(self.min_price) if self.min_price else None,
            'target_margin': float(self.target_margin) if self.target_margin else None,
            'platform_fees': float(self.platform_fees) if self.platform_fees else None,
            'final_price': float(self.final_price) if self.final_price else None,
            'currency': self.currency,
        }
