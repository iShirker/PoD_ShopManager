"""
Authentication blueprint.
Handles user registration, login, OAuth, and profile management.
"""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from app.blueprints.auth import routes
