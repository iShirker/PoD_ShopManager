"""
Flask application factory.
Creates and configures the Flask application with all extensions and blueprints.
"""
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)


def create_app(config_name='default'):
    """
    Application factory function.

    Args:
        config_name: Configuration to use (development, production, testing)

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)

    # CORS configuration
    frontend_url = app.config.get('FRONTEND_URL', 'http://localhost:3000')
    
    # Ensure no trailing slash for CORS matching
    frontend_url = frontend_url.rstrip('/')
    
    # Log CORS configuration for debugging
    app.logger.info(f"CORS configured for frontend: {frontend_url}")
    
    # Configure CORS - allow all API routes
    # Use a simpler configuration that's more reliable
    CORS(app, 
         origins=[frontend_url],
         methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"],
         supports_credentials=True,
         expose_headers=["Content-Type", "Authorization"])
    
    # Add error handler to ensure CORS headers are set even on errors
    @app.errorhandler(Exception)
    def handle_error(e):
        """Handle all errors and ensure CORS headers are set."""
        from flask import jsonify
        import traceback
        
        app.logger.error(f"Error: {str(e)}\n{traceback.format_exc()}")
        
        # Create error response
        if hasattr(e, 'code') and e.code:
            status_code = e.code
        elif hasattr(e, 'status_code'):
            status_code = e.status_code
        else:
            status_code = 500
        
        response = jsonify({
            'error': str(e) if status_code < 500 else 'Internal server error',
            'message': str(e) if status_code < 500 else 'An unexpected error occurred'
        })
        response.status_code = status_code
        
        # Ensure CORS headers are set on error responses
        origin = request.headers.get('Origin')
        if origin == frontend_url:
            response.headers.add('Access-Control-Allow-Origin', frontend_url)
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        
        return response

    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.users import users_bp
    from app.blueprints.suppliers import suppliers_bp
    from app.blueprints.shops import shops_bp
    from app.blueprints.products import products_bp
    from app.blueprints.templates import templates_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
    app.register_blueprint(shops_bp, url_prefix='/api/shops')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(templates_bp, url_prefix='/api/templates')

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'message': 'Token has expired', 'error': 'token_expired'}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'message': 'Invalid token', 'error': 'invalid_token'}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'message': 'Authorization required', 'error': 'authorization_required'}, 401

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'POD Manager API is running'}

    # Run startup migrations and create database tables
    with app.app_context():
        # Run migrations first to handle schema changes
        from app.migrations import run_startup_migrations
        run_startup_migrations(db, app)

        # Then create any new tables
        db.create_all()

    return app
