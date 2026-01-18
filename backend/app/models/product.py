"""
Product models for managing listings and supplier products.
"""
from datetime import datetime
from app import db


class Product(db.Model):
    """
    Model for products/listings from Etsy or Shopify.
    Represents the actual listing in the marketplace.
    """

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False, index=True)

    # Listing identification
    listing_id = db.Column(db.String(255), nullable=False)  # Platform-specific listing ID
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # SKU pattern used to identify supplier
    sku = db.Column(db.String(255), nullable=True, index=True)
    sku_pattern = db.Column(db.String(100), nullable=True)  # gelato_, printify_, printful_

    # Identified supplier
    supplier_type = db.Column(db.String(50), nullable=True)
    supplier_product_id = db.Column(db.String(255), nullable=True)

    # Pricing
    price = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), default='USD')

    # Product details
    product_type = db.Column(db.String(255), nullable=True)  # e.g., "Gildan 18000"
    category = db.Column(db.String(255), nullable=True)

    # Images
    thumbnail_url = db.Column(db.String(500), nullable=True)
    images = db.Column(db.JSON, default=list)

    # Status
    is_active = db.Column(db.Boolean, default=True)
    sync_status = db.Column(db.String(50), default='pending')  # pending, synced, error
    sync_error = db.Column(db.Text, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    variants = db.relationship('ProductVariant', backref='product', lazy='dynamic',
                               cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('shop_id', 'listing_id', name='unique_shop_listing'),
    )

    def to_dict(self, include_variants=False):
        """Convert product to dictionary."""
        data = {
            'id': self.id,
            'shop_id': self.shop_id,
            'listing_id': self.listing_id,
            'title': self.title,
            'description': self.description,
            'sku': self.sku,
            'sku_pattern': self.sku_pattern,
            'supplier_type': self.supplier_type,
            'supplier_product_id': self.supplier_product_id,
            'price': self.price,
            'currency': self.currency,
            'product_type': self.product_type,
            'category': self.category,
            'thumbnail_url': self.thumbnail_url,
            'images': self.images,
            'is_active': self.is_active,
            'sync_status': self.sync_status,
            'sync_error': self.sync_error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_synced_at': self.last_synced_at.isoformat() if self.last_synced_at else None
        }

        if include_variants:
            data['variants'] = [v.to_dict() for v in self.variants]

        return data

    def __repr__(self):
        return f'<Product {self.title[:50]}>'


class ProductVariant(db.Model):
    """Model for product variants (size, color combinations)."""

    __tablename__ = 'product_variants'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)

    # Variant identification
    variant_id = db.Column(db.String(255), nullable=False)  # Platform variant ID
    sku = db.Column(db.String(255), nullable=True)

    # Variant attributes
    size = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(100), nullable=True)
    color_hex = db.Column(db.String(10), nullable=True)

    # Pricing
    price = db.Column(db.Float, nullable=True)
    compare_at_price = db.Column(db.Float, nullable=True)

    # Inventory
    quantity = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert variant to dictionary."""
        return {
            'id': self.id,
            'variant_id': self.variant_id,
            'sku': self.sku,
            'size': self.size,
            'color': self.color,
            'color_hex': self.color_hex,
            'price': self.price,
            'compare_at_price': self.compare_at_price,
            'quantity': self.quantity,
            'is_available': self.is_available
        }

    def __repr__(self):
        return f'<ProductVariant {self.size} {self.color}>'


class SupplierProduct(db.Model):
    """
    Model for products available from POD suppliers.
    Used for price comparison and product switching.
    """

    __tablename__ = 'supplier_products'

    id = db.Column(db.Integer, primary_key=True)
    supplier_connection_id = db.Column(db.Integer, db.ForeignKey('supplier_connections.id'),
                                       nullable=False, index=True)

    # Product identification
    supplier_product_id = db.Column(db.String(255), nullable=False)
    blueprint_id = db.Column(db.String(255), nullable=True)  # Printify blueprint
    catalog_id = db.Column(db.String(255), nullable=True)  # Gelato catalog

    # Product info
    name = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)
    product_type = db.Column(db.String(255), nullable=True)  # e.g., "Gildan 18000"
    brand = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(255), nullable=True)

    # Pricing (base prices)
    base_price = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), default='USD')

    # Shipping costs
    shipping_first_item = db.Column(db.Float, nullable=True)
    shipping_additional_item = db.Column(db.Float, nullable=True)
    shipping_country = db.Column(db.String(10), default='US')  # Default shipping destination

    # Available variants
    available_sizes = db.Column(db.JSON, default=list)
    available_colors = db.Column(db.JSON, default=list)

    # Images
    thumbnail_url = db.Column(db.String(500), nullable=True)
    images = db.Column(db.JSON, default=list)

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('supplier_connection_id', 'supplier_product_id',
                            name='unique_supplier_product'),
    )

    def to_dict(self):
        """Convert supplier product to dictionary."""
        return {
            'id': self.id,
            'supplier_connection_id': self.supplier_connection_id,
            'supplier_product_id': self.supplier_product_id,
            'blueprint_id': self.blueprint_id,
            'catalog_id': self.catalog_id,
            'name': self.name,
            'description': self.description,
            'product_type': self.product_type,
            'brand': self.brand,
            'category': self.category,
            'base_price': self.base_price,
            'currency': self.currency,
            'shipping_first_item': self.shipping_first_item,
            'shipping_additional_item': self.shipping_additional_item,
            'shipping_country': self.shipping_country,
            'available_sizes': self.available_sizes,
            'available_colors': self.available_colors,
            'thumbnail_url': self.thumbnail_url,
            'images': self.images,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<SupplierProduct {self.name}>'
