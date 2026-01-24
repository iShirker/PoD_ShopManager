"""
Discount program models.
"""
from datetime import datetime
from app import db


class DiscountProgram(db.Model):
    """Discount campaigns (scheduling, margin check, platform sync)."""

    __tablename__ = 'discount_programs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    discount_type = db.Column(db.String(50), nullable=False)  # percentage, fixed_amount, bogo
    discount_value = db.Column(db.Numeric(10, 2), nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.String(50), nullable=True)  # daily, weekly, monthly, yearly
    min_margin_required = db.Column(db.Numeric(5, 2), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    mappings = db.relationship('ProductDiscountMapping', backref='discount_program', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_mappings=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'discount_type': self.discount_type,
            'discount_value': float(self.discount_value) if self.discount_value else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_recurring': self.is_recurring,
            'recurrence_pattern': self.recurrence_pattern,
            'min_margin_required': float(self.min_margin_required) if self.min_margin_required else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_mappings:
            data['mappings'] = [m.to_dict() for m in self.mappings]
        return data


class ProductDiscountMapping(db.Model):
    """Link products to discount programs (one active discount per product)."""

    __tablename__ = 'product_discount_mappings'

    id = db.Column(db.Integer, primary_key=True)
    discount_program_id = db.Column(db.Integer, db.ForeignKey('discount_programs.id'), nullable=False, index=True)
    user_product_id = db.Column(db.Integer, db.ForeignKey('user_products.id'), nullable=True, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True, index=True)  # shop listing
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = ()

    def to_dict(self):
        return {
            'id': self.id,
            'discount_program_id': self.discount_program_id,
            'user_product_id': self.user_product_id,
            'product_id': self.product_id,
            'is_active': self.is_active,
        }
