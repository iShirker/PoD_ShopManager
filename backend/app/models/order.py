"""
Order and fulfillment models.
"""
from datetime import datetime
from app import db


class Order(db.Model):
    """Orders from Etsy or Shopify."""

    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    order_number = db.Column(db.String(255), unique=True, nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # etsy, shopify
    platform_order_id = db.Column(db.String(255), nullable=True, index=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=True, index=True)
    customer_name = db.Column(db.String(255), nullable=True)
    customer_email = db.Column(db.String(255), nullable=True)
    shipping_address = db.Column(db.JSON, nullable=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=True)
    currency = db.Column(db.String(10), default='USD')
    status = db.Column(db.String(50), default='pending')  # pending, processing, fulfilled, canceled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    shop = db.relationship('Shop', backref='orders')
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_items=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'order_number': self.order_number,
            'platform': self.platform,
            'platform_order_id': self.platform_order_id,
            'shop_id': self.shop_id,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'currency': self.currency,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_items:
            data['items'] = [i.to_dict() for i in self.items]
        return data


class OrderItem(db.Model):
    """Line items in an order."""

    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True, index=True)  # shop listing
    user_product_id = db.Column(db.Integer, db.ForeignKey('user_products.id'), nullable=True, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=True)
    sku = db.Column(db.String(255), nullable=True)
    customization_data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref='order_items')
    user_product = db.relationship('UserProduct', backref='order_items')
    fulfillments = db.relationship('Fulfillment', backref='order_item', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'user_product_id': self.user_product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'sku': self.sku,
            'customization_data': self.customization_data,
        }


class Fulfillment(db.Model):
    """Fulfillment record (routed to PoD supplier)."""

    __tablename__ = 'fulfillments'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_items.id'), nullable=False, index=True)
    supplier_type = db.Column(db.String(50), nullable=True)  # gelato, printify, printful
    supplier_connection_id = db.Column(db.Integer, db.ForeignKey('supplier_connections.id'), nullable=True, index=True)
    supplier_order_id = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='pending')  # pending, processing, shipped, delivered, failed
    tracking_number = db.Column(db.String(255), nullable=True)
    shipping_cost = db.Column(db.Numeric(10, 2), nullable=True)
    fulfillment_cost = db.Column(db.Numeric(10, 2), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = db.relationship('Order', backref='fulfillments')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'order_item_id': self.order_item_id,
            'supplier_type': self.supplier_type,
            'supplier_connection_id': self.supplier_connection_id,
            'supplier_order_id': self.supplier_order_id,
            'status': self.status,
            'tracking_number': self.tracking_number,
            'shipping_cost': float(self.shipping_cost) if self.shipping_cost else None,
            'fulfillment_cost': float(self.fulfillment_cost) if self.fulfillment_cost else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
