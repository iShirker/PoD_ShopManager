"""
Settings blueprint.
Billing, subscription, usage.
"""
from flask import Blueprint

settings_bp = Blueprint('settings', __name__)

from app.blueprints.settings import routes
