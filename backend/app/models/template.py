"""
Listing template models for creating reusable product templates.
"""
from datetime import datetime
from app import db


class ListingTemplate(db.Model):
    """
    Model for listing templates that combine products from different suppliers.
    Users can use templates to quickly create listings with multiple options.
    """

    __tablename__ = 'listing_templates'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Template info
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Listing defaults
    default_title = db.Column(db.String(500), nullable=True)
    default_description = db.Column(db.Text, nullable=True)
    default_tags = db.Column(db.JSON, default=list)
    default_price_markup = db.Column(db.Float, default=0)  # Percentage markup
    default_price_fixed = db.Column(db.Float, nullable=True)  # Fixed price override

    # Target platforms
    target_platforms = db.Column(db.JSON, default=list)  # ['etsy', 'shopify']

    # Category mappings
    etsy_category = db.Column(db.String(255), nullable=True)
    shopify_category = db.Column(db.String(255), nullable=True)

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    template_products = db.relationship('TemplateProduct', backref='template', lazy='dynamic',
                                        cascade='all, delete-orphan')

    def to_dict(self, include_products=False):
        """Convert template to dictionary."""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'default_title': self.default_title,
            'default_description': self.default_description,
            'default_tags': self.default_tags,
            'default_price_markup': self.default_price_markup,
            'default_price_fixed': self.default_price_fixed,
            'target_platforms': self.target_platforms,
            'etsy_category': self.etsy_category,
            'shopify_category': self.shopify_category,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_products:
            data['products'] = [p.to_dict(include_colors=True) for p in self.template_products]

        return data

    def __repr__(self):
        return f'<ListingTemplate {self.name}>'


class TemplateProduct(db.Model):
    """
    Model for products included in a listing template.
    Each template can have multiple products from different suppliers.
    """

    __tablename__ = 'template_products'

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('listing_templates.id'), nullable=False,
                            index=True)
    supplier_product_id = db.Column(db.Integer, db.ForeignKey('supplier_products.id'), nullable=True)

    # Product reference (can be direct supplier product or custom)
    supplier_type = db.Column(db.String(50), nullable=False)
    external_product_id = db.Column(db.String(255), nullable=True)  # Supplier's product ID

    # Product info for the template
    product_name = db.Column(db.String(500), nullable=False)
    product_type = db.Column(db.String(255), nullable=True)  # e.g., "Gildan 18000"
    alias_name = db.Column(db.String(255), nullable=True)  # Unique alias name within template

    # Variant selection
    selected_sizes = db.Column(db.JSON, default=list)  # List of selected sizes

    # Pricing configuration
    # Pricing mode: 'per_config' (per size+color), 'per_size', 'per_color', or 'global'
    pricing_mode = db.Column(db.String(20), default='global')
    # Prices stored as JSON:
    # - per_config: { "S_Black": 29.99, "M_Black": 31.99, ... }
    # - per_size: { "S": 29.99, "M": 31.99, ... }
    # - per_color: { "Black": 29.99, "White": 30.99, ... }
    # - global: single price for all variants
    prices = db.Column(db.JSON, default=dict)
    global_price = db.Column(db.Float, nullable=True)  # Used when pricing_mode is 'global'

    # Legacy pricing fields (kept for backward compatibility)
    price_override = db.Column(db.Float, nullable=True)
    price_markup = db.Column(db.Float, nullable=True)

    # Display order
    display_order = db.Column(db.Integer, default=0)

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    colors = db.relationship('TemplateColor', backref='template_product', lazy='dynamic',
                             cascade='all, delete-orphan')
    supplier_product = db.relationship('SupplierProduct', backref='template_usages')

    def to_dict(self, include_colors=False):
        """Convert template product to dictionary."""
        data = {
            'id': self.id,
            'template_id': self.template_id,
            'supplier_product_id': self.supplier_product_id,
            'supplier_type': self.supplier_type,
            'external_product_id': self.external_product_id,
            'product_name': self.product_name,
            'product_type': self.product_type,
            'alias_name': self.alias_name,
            'selected_sizes': self.selected_sizes,
            'pricing_mode': self.pricing_mode,
            'prices': self.prices or {},
            'global_price': self.global_price,
            'price_override': self.price_override,
            'price_markup': self.price_markup,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_colors:
            data['colors'] = [c.to_dict() for c in self.colors]

        return data

    def __repr__(self):
        return f'<TemplateProduct {self.product_name}>'


class TemplateColor(db.Model):
    """
    Model for color selections in template products.
    Allows users to select specific colors for each product in a template.
    """

    __tablename__ = 'template_colors'

    id = db.Column(db.Integer, primary_key=True)
    template_product_id = db.Column(db.Integer, db.ForeignKey('template_products.id'),
                                    nullable=False, index=True)

    # Color info
    color_name = db.Column(db.String(100), nullable=False)
    color_hex = db.Column(db.String(10), nullable=True)
    supplier_color_id = db.Column(db.String(255), nullable=True)  # Supplier's color ID

    # Display name override
    display_name = db.Column(db.String(100), nullable=True)

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert template color to dictionary."""
        return {
            'id': self.id,
            'template_product_id': self.template_product_id,
            'color_name': self.color_name,
            'color_hex': self.color_hex,
            'supplier_color_id': self.supplier_color_id,
            'display_name': self.display_name or self.color_name,
            'is_active': self.is_active
        }

    def __repr__(self):
        return f'<TemplateColor {self.color_name}>'
