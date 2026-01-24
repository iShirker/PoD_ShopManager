"""
Discounts blueprint.
Discount programs and product mappings.
"""
from flask import Blueprint

discounts_bp = Blueprint('discounts', __name__)

from app.blueprints.discounts import routes
