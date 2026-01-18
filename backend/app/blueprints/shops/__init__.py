"""
Shops blueprint.
Handles Etsy and Shopify shop connections and management.
"""
from flask import Blueprint

shops_bp = Blueprint('shops', __name__)

from app.blueprints.shops import routes
