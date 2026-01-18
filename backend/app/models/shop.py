"""
Shop model for managing Etsy and Shopify store connections.
"""
from datetime import datetime
from enum import Enum
from app import db


class ShopType(str, Enum):
    """Supported marketplace platforms."""
    ETSY = 'etsy'
    SHOPIFY = 'shopify'


class Shop(db.Model):
    """Model for storing user's marketplace shop connections."""

    __tablename__ = 'shops'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    shop_type = db.Column(db.String(50), nullable=False)

    # Shop identification
    shop_name = db.Column(db.String(255), nullable=False)
    shop_id = db.Column(db.String(255), nullable=False)  # Platform-specific ID
    shop_url = db.Column(db.String(500), nullable=True)

    # OAuth credentials
    access_token = db.Column(db.String(1000), nullable=True)
    refresh_token = db.Column(db.String(1000), nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)

    # Shopify-specific
    shopify_domain = db.Column(db.String(255), nullable=True)  # mystore.myshopify.com

    # Connection status
    is_active = db.Column(db.Boolean, default=True)
    is_connected = db.Column(db.Boolean, default=False)
    last_sync = db.Column(db.DateTime, nullable=True)
    connection_error = db.Column(db.Text, nullable=True)

    # Statistics
    total_listings = db.Column(db.Integer, default=0)
    pod_listings = db.Column(db.Integer, default=0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    products = db.relationship('Product', backref='shop', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'shop_type', 'shop_id', name='unique_user_shop'),
    )

    def to_dict(self, include_tokens=False):
        """
        Convert shop to dictionary.

        Args:
            include_tokens: Include sensitive token data

        Returns:
            Dictionary representation
        """
        data = {
            'id': self.id,
            'shop_type': self.shop_type,
            'shop_name': self.shop_name,
            'shop_id': self.shop_id,
            'shop_url': self.shop_url,
            'shopify_domain': self.shopify_domain,
            'is_active': self.is_active,
            'is_connected': self.is_connected,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'connection_error': self.connection_error,
            'total_listings': self.total_listings,
            'pod_listings': self.pod_listings,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_tokens:
            data['has_access_token'] = bool(self.access_token)
            data['token_expires_at'] = self.token_expires_at.isoformat() if self.token_expires_at else None

        return data

    def __repr__(self):
        return f'<Shop {self.shop_name} ({self.shop_type})>'
