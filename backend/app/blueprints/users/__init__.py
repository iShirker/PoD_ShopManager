"""
Users blueprint.
Handles user profile management.
"""
from flask import Blueprint

users_bp = Blueprint('users', __name__)

from app.blueprints.users import routes
