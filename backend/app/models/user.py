"""
User model for authentication and profile management.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """User model for storing user account information."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    username = db.Column(db.String(100), unique=True, nullable=True)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)

    # OAuth provider info
    oauth_provider = db.Column(db.String(50), nullable=True)  # google, etsy, shopify, etc.
    oauth_provider_id = db.Column(db.String(255), nullable=True)

    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)

    # UI preference
    preferred_theme = db.Column(db.String(20), nullable=True, default='5')

    # Subscription
    free_trial_used_at = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    supplier_connections = db.relationship('SupplierConnection', backref='user', lazy='dynamic',
                                           cascade='all, delete-orphan')
    shops = db.relationship('Shop', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    templates = db.relationship('ListingTemplate', backref='user', lazy='dynamic',
                                cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_sensitive=False):
        """
        Convert user to dictionary representation.

        Args:
            include_sensitive: Include sensitive fields like OAuth tokens

        Returns:
            Dictionary representation of user
        """
        data = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'avatar_url': self.avatar_url,
            'oauth_provider': self.oauth_provider,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'preferred_theme': self.preferred_theme or '5',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        return data

    def __repr__(self):
        return f'<User {self.email}>'
