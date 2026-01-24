"""
Listings blueprint.
Unified view of Etsy/Shopify listings (shop products) across all user shops.
"""
from flask import Blueprint

listings_bp = Blueprint('listings', __name__)

from app.blueprints.listings import routes
