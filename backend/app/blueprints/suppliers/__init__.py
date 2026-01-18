"""
Suppliers blueprint.
Handles POD supplier connections and management.
"""
from flask import Blueprint

suppliers_bp = Blueprint('suppliers', __name__)

from app.blueprints.suppliers import routes
