"""
Application configuration module.
Manages environment-specific settings and API credentials.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class."""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///pod_manager.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # OAuth Providers
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')

    ETSY_API_KEY = os.getenv('ETSY_API_KEY', '')
    ETSY_API_SECRET = os.getenv('ETSY_API_SECRET', '')
    ETSY_REDIRECT_URI = os.getenv('ETSY_REDIRECT_URI', 'http://localhost:5000/api/auth/etsy/callback')

    SHOPIFY_API_KEY = os.getenv('SHOPIFY_API_KEY', '')
    SHOPIFY_API_SECRET = os.getenv('SHOPIFY_API_SECRET', '')

    # Print on Demand Suppliers
    GELATO_API_KEY = os.getenv('GELATO_API_KEY', '')
    GELATO_API_URL = 'https://api.gelato.com/v3'
    GELATO_CLIENT_ID = os.getenv('GELATO_CLIENT_ID', '')
    GELATO_CLIENT_SECRET = os.getenv('GELATO_CLIENT_SECRET', '')
    GELATO_REDIRECT_URI = os.getenv(
        'GELATO_REDIRECT_URI',
        'http://localhost:5000/api/auth/gelato/callback'
    )
    GELATO_OAUTH_SCOPE = os.getenv('GELATO_OAUTH_SCOPE', '')
    GELATO_OAUTH_AUTHORIZE_URL = os.getenv(
        'GELATO_OAUTH_AUTHORIZE_URL',
        'https://api.gelato.com/oauth/authorize'
    )
    GELATO_OAUTH_TOKEN_URL = os.getenv(
        'GELATO_OAUTH_TOKEN_URL',
        'https://api.gelato.com/oauth/token'
    )

    PRINTIFY_API_KEY = os.getenv('PRINTIFY_API_KEY', '')
    PRINTIFY_API_URL = 'https://api.printify.com/v1'

    PRINTFUL_API_KEY = os.getenv('PRINTFUL_API_KEY', '')
    PRINTFUL_API_URL = 'https://api.printful.com'
    PRINTFUL_CLIENT_ID = os.getenv('PRINTFUL_CLIENT_ID', '')
    PRINTFUL_CLIENT_SECRET = os.getenv('PRINTFUL_CLIENT_SECRET', '')

    # Frontend URL (for CORS and OAuth redirects)
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    # Backend URL (for OAuth redirect URIs)
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')

    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False

    # Override with stronger defaults
    RATELIMIT_DEFAULT = "1000 per day"


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
