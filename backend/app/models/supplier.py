"""
Supplier connection model for managing POD supplier integrations.
"""
from datetime import datetime
from enum import Enum
from app import db


class SupplierType(str, Enum):
    """Supported Print on Demand suppliers."""
    GELATO = 'gelato'
    PRINTIFY = 'printify'
    PRINTFUL = 'printful'


class SupplierConnection(db.Model):
    """Model for storing user's POD supplier connections."""

    __tablename__ = 'supplier_connections'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    supplier_type = db.Column(db.String(50), nullable=False)

    # Account identification
    account_name = db.Column(db.String(255), nullable=True)  # Display name for the account
    account_email = db.Column(db.String(255), nullable=True)  # Email associated with the account
    account_id = db.Column(db.String(255), nullable=True)  # Supplier's account/user ID

    # API credentials (encrypted in production)
    # Printify tokens can be 1000+ characters, so use TEXT for flexibility
    api_key = db.Column(db.Text, nullable=True)
    api_secret = db.Column(db.Text, nullable=True)
    access_token = db.Column(db.String(1000), nullable=True)
    refresh_token = db.Column(db.String(1000), nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)

    # Connection status
    is_active = db.Column(db.Boolean, default=True)
    is_connected = db.Column(db.Boolean, default=False)
    last_sync = db.Column(db.DateTime, nullable=True)
    connection_error = db.Column(db.Text, nullable=True)

    # Supplier-specific data
    shop_id = db.Column(db.String(255), nullable=True)  # For Printify shop ID
    store_id = db.Column(db.String(255), nullable=True)  # For Gelato store ID

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    products = db.relationship('SupplierProduct', backref='supplier_connection', lazy='dynamic',
                               cascade='all, delete-orphan')

    def to_dict(self, include_tokens=False):
        """
        Convert supplier connection to dictionary.

        Args:
            include_tokens: Include sensitive token data

        Returns:
            Dictionary representation
        """
        data = {
            'id': self.id,
            'supplier_type': self.supplier_type,
            'account_name': self.account_name,
            'account_email': self.account_email,
            'account_id': self.account_id,
            'is_active': self.is_active,
            'is_connected': self.is_connected,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'connection_error': self.connection_error,
            'shop_id': self.shop_id,
            'store_id': self.store_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_tokens:
            data['has_api_key'] = bool(self.api_key)
            data['has_access_token'] = bool(self.access_token)
            data['token_expires_at'] = self.token_expires_at.isoformat() if self.token_expires_at else None

        return data

    def __repr__(self):
        return f'<SupplierConnection {self.supplier_type} for user {self.user_id}>'
