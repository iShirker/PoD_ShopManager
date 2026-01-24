"""
Orders blueprint.
Orders from Etsy/Shopify and fulfillment.
"""
from flask import Blueprint

orders_bp = Blueprint('orders', __name__)

from app.blueprints.orders import routes
