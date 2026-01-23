"""
User Product models for managing user's product list.
Separate from shop products - these are products the user wants to track.
"""
from datetime import datetime
from app import db


class UserProduct(db.Model):
    """
    Model for products in user's product list.
    These are products the user wants to track and compare across suppliers.
    Not tied to any shop - this is the user's personal product catalog.
    """

    __tablename__ = 'user_products'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Product identification
    product_name = db.Column(db.String(500), nullable=False)
    product_type = db.Column(db.String(255), nullable=True)  # e.g., "Gildan 18000"
    brand = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(255), nullable=True)

    # Description
    description = db.Column(db.Text, nullable=True)

    # Images
    thumbnail_url = db.Column(db.String(500), nullable=True)
    images = db.Column(db.JSON, default=list)

    # Primary supplier (the one used when adding)
    primary_supplier_type = db.Column(db.String(50), nullable=True)
    primary_supplier_product_id = db.Column(db.String(255), nullable=True)
    primary_supplier_connection_id = db.Column(db.Integer, db.ForeignKey('supplier_connections.id'), nullable=True)

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    suppliers = db.relationship('UserProductSupplier', backref='user_product', lazy='dynamic',
                                cascade='all, delete-orphan')

    __table_args__ = (
        db.Index('idx_user_product_type', 'user_id', 'product_type'),
    )

    def to_dict(self, include_suppliers=False):
        """Convert user product to dictionary."""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'product_name': self.product_name,
            'product_type': self.product_type,
            'brand': self.brand,
            'category': self.category,
            'description': self.description,
            'thumbnail_url': self.thumbnail_url,
            'images': self.images,
            'primary_supplier_type': self.primary_supplier_type,
            'primary_supplier_product_id': self.primary_supplier_product_id,
            'primary_supplier_connection_id': self.primary_supplier_connection_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_suppliers:
            data['suppliers'] = [s.to_dict() for s in self.suppliers]

        return data

    def __repr__(self):
        return f'<UserProduct {self.product_name[:50]}>'


class UserProductSupplier(db.Model):
    """
    Model for tracking which suppliers have a specific user product.
    Links a UserProduct to SupplierProduct entries from different suppliers.
    """

    __tablename__ = 'user_product_suppliers'

    id = db.Column(db.Integer, primary_key=True)
    user_product_id = db.Column(db.Integer, db.ForeignKey('user_products.id'), nullable=False, index=True)
    supplier_connection_id = db.Column(db.Integer, db.ForeignKey('supplier_connections.id'), nullable=False, index=True)
    supplier_product_id = db.Column(db.Integer, db.ForeignKey('supplier_products.id'), nullable=True, index=True)

    # Supplier identification
    supplier_type = db.Column(db.String(50), nullable=False)
    supplier_product_external_id = db.Column(db.String(255), nullable=True)  # External ID from supplier API

    # Pricing info (cached from supplier product)
    base_price = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), default='USD')

    # Status
    is_available = db.Column(db.Boolean, default=True)
    last_checked = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_product_id', 'supplier_connection_id', name='unique_user_product_supplier'),
        db.Index('idx_user_product_supplier_type', 'user_product_id', 'supplier_type'),
    )

    def to_dict(self):
        """Convert user product supplier to dictionary."""
        return {
            'id': self.id,
            'user_product_id': self.user_product_id,
            'supplier_connection_id': self.supplier_connection_id,
            'supplier_product_id': self.supplier_product_id,
            'supplier_type': self.supplier_type,
            'supplier_product_external_id': self.supplier_product_external_id,
            'base_price': self.base_price,
            'currency': self.currency,
            'is_available': self.is_available,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<UserProductSupplier product_id={self.user_product_id} supplier={self.supplier_type}>'
