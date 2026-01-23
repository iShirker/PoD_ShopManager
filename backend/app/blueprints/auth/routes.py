"""
Authentication routes.
Handles registration, login, OAuth callbacks, and token refresh.
"""
import secrets
from datetime import datetime, timedelta
from flask import request, jsonify, current_app, redirect, url_for
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt
)
from app import db, limiter
from app.blueprints.auth import auth_bp
from app.models import User
from app.services.oauth import (
    get_google_auth_url, exchange_google_code,
    get_etsy_auth_url, exchange_etsy_code,
    get_shopify_auth_url, exchange_shopify_code,
    get_printify_auth_url, exchange_printify_code, get_printify_shops,
    get_printful_auth_url, exchange_printful_code, get_printful_stores,
    get_gelato_auth_url, exchange_gelato_code
)
from app.models import SupplierConnection, Shop
from app.services.suppliers.gelato import GelatoService
from app.services.shops.shopify import get_shopify_shop_info


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """
    Register a new user with email and password.

    Request body:
        email: User's email address
        password: User's password (min 8 characters)
        username: Optional username
        first_name: Optional first name
        last_name: Optional last name

    Returns:
        User data with access and refresh tokens
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    # Create user
    user = User(
        email=email,
        username=data.get('username'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        is_verified=False
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'message': 'Registration successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """
    Login with email and password.

    Request body:
        email: User's email address
        password: User's password

    Returns:
        User data with access and refresh tokens
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    })


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token.

    Returns:
        New access token
    """
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)

    return jsonify({
        'access_token': access_token
    })


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user (client should discard tokens).

    Returns:
        Success message
    """
    # In a more complete implementation, you would blacklist the token
    return jsonify({'message': 'Logout successful'})


# OAuth Routes - Google
@auth_bp.route('/google/authorize')
def google_authorize():
    """Redirect to Google OAuth authorization page."""
    state = secrets.token_urlsafe(32)
    auth_url = get_google_auth_url(state)
    return jsonify({'auth_url': auth_url, 'state': state})


@auth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback."""
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')

    if error:
        return redirect(f"{current_app.config['FRONTEND_URL']}/auth/error?error={error}")

    if not code:
        return redirect(f"{current_app.config['FRONTEND_URL']}/auth/error?error=no_code")

    try:
        user_info = exchange_google_code(code)

        # Find or create user
        user = User.query.filter_by(email=user_info['email']).first()

        if not user:
            user = User(
                email=user_info['email'],
                first_name=user_info.get('given_name'),
                last_name=user_info.get('family_name'),
                avatar_url=user_info.get('picture'),
                oauth_provider='google',
                oauth_provider_id=user_info['id'],
                is_verified=user_info.get('verified_email', False)
            )
            db.session.add(user)
        else:
            user.oauth_provider = 'google'
            user.oauth_provider_id = user_info['id']
            if not user.avatar_url:
                user.avatar_url = user_info.get('picture')

        user.last_login = datetime.utcnow()
        db.session.commit()

        # Generate tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        # Redirect to frontend with tokens
        return redirect(
            f"{current_app.config['FRONTEND_URL']}/auth/callback"
            f"?access_token={access_token}&refresh_token={refresh_token}"
        )

    except Exception as e:
        current_app.logger.error(f"Google OAuth error: {str(e)}")
        return redirect(f"{current_app.config['FRONTEND_URL']}/auth/error?error=oauth_failed")


# OAuth Routes - Etsy
@auth_bp.route('/etsy/authorize')
@jwt_required(optional=True)
def etsy_authorize():
    """Redirect to Etsy OAuth authorization page."""
    state = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(64)
    auth_url = get_etsy_auth_url(state, code_verifier)
    return jsonify({
        'auth_url': auth_url,
        'state': state,
        'code_verifier': code_verifier
    })


@auth_bp.route('/etsy/callback')
def etsy_callback():
    """Handle Etsy OAuth callback."""
    code = request.args.get('code')
    state = request.args.get('state')
    code_verifier = request.args.get('code_verifier')
    error = request.args.get('error')

    if error:
        return redirect(f"{current_app.config['FRONTEND_URL']}/auth/error?error={error}")

    if not code:
        return redirect(f"{current_app.config['FRONTEND_URL']}/auth/error?error=no_code")

    try:
        token_data, user_info = exchange_etsy_code(code, code_verifier)

        # Find or create user
        user = User.query.filter_by(
            oauth_provider='etsy',
            oauth_provider_id=str(user_info['user_id'])
        ).first()

        if not user:
            # Check if email exists (Etsy might not provide email)
            email = user_info.get('primary_email') or f"etsy_{user_info['user_id']}@placeholder.local"
            user = User.query.filter_by(email=email).first()

            if not user:
                user = User(
                    email=email,
                    username=user_info.get('login_name'),
                    first_name=user_info.get('first_name'),
                    last_name=user_info.get('last_name'),
                    avatar_url=user_info.get('image_url_75x75'),
                    oauth_provider='etsy',
                    oauth_provider_id=str(user_info['user_id']),
                    is_verified=True
                )
                db.session.add(user)

        user.last_login = datetime.utcnow()
        db.session.commit()

        # Generate tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return redirect(
            f"{current_app.config['FRONTEND_URL']}/auth/callback"
            f"?access_token={access_token}&refresh_token={refresh_token}"
            f"&etsy_token={token_data['access_token']}"
        )

    except Exception as e:
        current_app.logger.error(f"Etsy OAuth error: {str(e)}")
        return redirect(f"{current_app.config['FRONTEND_URL']}/auth/error?error=oauth_failed")


# OAuth Routes - Shopify
@auth_bp.route('/shopify/authorize')
@jwt_required()
def shopify_authorize():
    """
    Redirect to Shopify OAuth authorization page for app installation.
    User must be logged in to connect a Shopify store.
    """
    shop_domain = request.args.get('shop')
    if not shop_domain:
        return jsonify({'error': 'Shop domain is required'}), 400

    user_id = get_jwt_identity()
    # Include user_id in state for callback
    state = f"{secrets.token_urlsafe(32)}:{user_id}"
    auth_url = get_shopify_auth_url(shop_domain, state)
    return jsonify({'auth_url': auth_url, 'state': state})


@auth_bp.route('/shopify/callback')
def shopify_callback():
    """
    Handle Shopify OAuth callback after app installation.
    Creates or updates shop connection in database.
    """
    code = request.args.get('code')
    shop = request.args.get('shop')
    state = request.args.get('state')

    if not code or not shop:
        return redirect(f"{current_app.config['FRONTEND_URL']}/auth/error?error=missing_params")

    try:
        # Extract user_id from state
        user_id = state.split(':')[1] if state and ':' in state else None

        if not user_id:
            return redirect(f"{current_app.config['FRONTEND_URL']}/auth/error?error=no_user")

        # Exchange code for access token
        token_data = exchange_shopify_code(shop, code)
        access_token = token_data.get('access_token')

        if not access_token:
            return redirect(f"{current_app.config['FRONTEND_URL']}/auth/error?error=no_token")

        # Get shop info from Shopify API
        shop_info = get_shopify_shop_info(shop, access_token)

        if not shop_info:
            return redirect(f"{current_app.config['FRONTEND_URL']}/auth/error?error=shop_info_failed")

        # Clean up shop domain
        shop_domain = shop if shop.endswith('.myshopify.com') else f"{shop}.myshopify.com"
        shop_id = str(shop_info.get('id', shop_domain))
        shop_name = shop_info.get('name', shop_domain.replace('.myshopify.com', ''))

        # Check if shop already exists for this user
        existing_shop = Shop.query.filter_by(
            user_id=user_id,
            shop_type='shopify',
            shopify_domain=shop_domain
        ).first()

        if existing_shop:
            # Update existing shop connection
            existing_shop.access_token = access_token
            existing_shop.shop_name = shop_name
            existing_shop.shop_id = shop_id
            existing_shop.shop_url = f"https://{shop_domain}"
            existing_shop.is_connected = True
            existing_shop.connection_error = None
            existing_shop.last_sync = datetime.utcnow()
            shop_record = existing_shop
        else:
            # Create new shop connection
            shop_record = Shop(
                user_id=user_id,
                shop_type='shopify',
                shop_name=shop_name,
                shop_id=shop_id,
                shop_url=f"https://{shop_domain}",
                shopify_domain=shop_domain,
                access_token=access_token,
                is_connected=True,
                is_active=True,
                last_sync=datetime.utcnow()
            )
            db.session.add(shop_record)

        db.session.commit()

        # Redirect to frontend with success
        return redirect(
            f"{current_app.config['FRONTEND_URL']}/shops/callback"
            f"?shop={shop}&shop_id={shop_record.id}&success=true"
        )

    except Exception as e:
        current_app.logger.error(f"Shopify OAuth error: {str(e)}")
        return redirect(f"{current_app.config['FRONTEND_URL']}/auth/error?error=oauth_failed")


@auth_bp.route('/shopify/webhooks/app_uninstalled', methods=['POST'])
def shopify_app_uninstalled():
    """
    Handle Shopify app uninstalled webhook.
    Marks the shop as disconnected when the app is uninstalled.
    """
    try:
        shop_domain = request.headers.get('X-Shopify-Shop-Domain')

        if not shop_domain:
            return jsonify({'error': 'Missing shop domain'}), 400

        # Find and update the shop
        shop = Shop.query.filter_by(
            shop_type='shopify',
            shopify_domain=shop_domain
        ).first()

        if shop:
            shop.is_connected = False
            shop.access_token = None
            shop.connection_error = 'App was uninstalled from Shopify'
            db.session.commit()
            current_app.logger.info(f"Shopify app uninstalled from {shop_domain}")

        return jsonify({'status': 'ok'}), 200

    except Exception as e:
        current_app.logger.error(f"Shopify webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# OAuth Routes - POD Suppliers

# Gelato OAuth
@auth_bp.route('/gelato/authorize')
@jwt_required()
def gelato_authorize():
    """Redirect to Gelato OAuth authorization page."""
    state = secrets.token_urlsafe(32)
    user_id = get_jwt_identity()
    auth_url = get_gelato_auth_url(f"{state}:{user_id}")
    return jsonify({'auth_url': auth_url, 'state': state})


@auth_bp.route('/gelato/callback')
def gelato_callback():
    """Handle Gelato OAuth callback."""
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')

    if error:
        return redirect(f"{current_app.config['FRONTEND_URL']}/suppliers/callback?error={error}")

    if not code:
        return redirect(f"{current_app.config['FRONTEND_URL']}/suppliers/callback?error=no_code")

    try:
        user_id = state.split(':')[1] if state and ':' in state else None

        token_data = exchange_gelato_code(code)
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')
        expires_in = token_data.get('expires_in')

        if not user_id:
            return redirect(f"{current_app.config['FRONTEND_URL']}/suppliers/callback?error=no_user")

        service = GelatoService(access_token=access_token)
        stores = service.get_stores().get('stores', [])

        connection = SupplierConnection.query.filter_by(
            user_id=user_id,
            supplier_type='gelato'
        ).first()

        if not connection:
            connection = SupplierConnection(
                user_id=user_id,
                supplier_type='gelato'
            )
            db.session.add(connection)

        connection.access_token = access_token
        connection.refresh_token = refresh_token
        connection.token_expires_at = (
            datetime.utcnow() + timedelta(seconds=expires_in)
            if expires_in else None
        )
        connection.is_connected = True
        connection.connection_error = None
        connection.last_sync = datetime.utcnow()

        if stores:
            connection.store_id = str(stores[0].get('id'))

        db.session.commit()

        return redirect(
            f"{current_app.config['FRONTEND_URL']}/suppliers/callback"
            f"?supplier=gelato&success=true&stores={len(stores)}"
        )

    except Exception as e:
        current_app.logger.error(f"Gelato OAuth error: {str(e)}")
        return redirect(f"{current_app.config['FRONTEND_URL']}/suppliers/callback?error=oauth_failed")


# Printify OAuth
@auth_bp.route('/printify/authorize')
@jwt_required()
def printify_authorize():
    """Redirect to Printify OAuth authorization page."""
    state = secrets.token_urlsafe(32)
    user_id = get_jwt_identity()
    # Store user_id in state for callback
    auth_url = get_printify_auth_url(f"{state}:{user_id}")
    return jsonify({'auth_url': auth_url, 'state': state})


@auth_bp.route('/printify/callback')
def printify_callback():
    """Handle Printify OAuth callback."""
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')

    if error:
        return redirect(f"{current_app.config['FRONTEND_URL']}/suppliers/callback?error={error}")

    if not code:
        return redirect(f"{current_app.config['FRONTEND_URL']}/suppliers/callback?error=no_code")

    try:
        # Extract user_id from state
        user_id = state.split(':')[1] if ':' in state else None

        # Exchange code for tokens
        token_data = exchange_printify_code(code)
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')

        if not user_id:
            return redirect(f"{current_app.config['FRONTEND_URL']}/suppliers/callback?error=no_user")

        # Get shops from Printify
        shops = get_printify_shops(access_token)

        # Create or update supplier connection
        connection = SupplierConnection.query.filter_by(
            user_id=user_id,
            supplier_type='printify'
        ).first()

        if not connection:
            connection = SupplierConnection(
                user_id=user_id,
                supplier_type='printify'
            )
            db.session.add(connection)

        connection.access_token = access_token
        connection.refresh_token = refresh_token
        connection.is_connected = True
        connection.connection_error = None
        connection.last_sync = datetime.utcnow()

        # Store shop info if available
        if shops:
            connection.shop_id = str(shops[0].get('id'))

        db.session.commit()

        return redirect(
            f"{current_app.config['FRONTEND_URL']}/suppliers/callback"
            f"?supplier=printify&success=true&shops={len(shops)}"
        )

    except Exception as e:
        current_app.logger.error(f"Printify OAuth error: {str(e)}")
        return redirect(f"{current_app.config['FRONTEND_URL']}/suppliers/callback?error=oauth_failed")


# Printful OAuth
@auth_bp.route('/printful/authorize')
@jwt_required()
def printful_authorize():
    """Redirect to Printful OAuth authorization page."""
    state = secrets.token_urlsafe(32)
    user_id = get_jwt_identity()
    # Store user_id in state for callback
    auth_url = get_printful_auth_url(f"{state}:{user_id}")
    return jsonify({'auth_url': auth_url, 'state': state})


@auth_bp.route('/printful/callback')
def printful_callback():
    """Handle Printful OAuth callback."""
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')

    if error:
        return redirect(f"{current_app.config['FRONTEND_URL']}/suppliers/callback?error={error}")

    if not code:
        return redirect(f"{current_app.config['FRONTEND_URL']}/suppliers/callback?error=no_code")

    try:
        # Extract user_id from state
        user_id = state.split(':')[1] if ':' in state else None

        # Exchange code for tokens
        token_data = exchange_printful_code(code)
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')

        if not user_id:
            return redirect(f"{current_app.config['FRONTEND_URL']}/suppliers/callback?error=no_user")

        # Get stores from Printful
        stores_response = get_printful_stores(access_token)
        stores = stores_response.get('result', [])

        # Get store info for account details
        # Use first store from stores list, or try to get store details via API
        store_info = None
        if stores:
            # Use first store as the primary store
            first_store = stores[0]
            store_info = first_store
            
            # Try to get detailed store info if we have store ID
            store_id = first_store.get('id')
            if store_id:
                try:
                    from app.services.suppliers.printful import PrintfulService
                    service = PrintfulService(access_token)
                    # Try to get detailed store info using stores/{id} endpoint
                    detailed_store = service._request('GET', f'stores/{store_id}')
                    if detailed_store:
                        store_info = detailed_store
                except Exception as e:
                    # If detailed store info fails, use basic store info from list
                    current_app.logger.warning(f"Could not get detailed store info: {str(e)}")
                    store_info = first_store

        # Create or update supplier connection
        connection = SupplierConnection.query.filter_by(
            user_id=user_id,
            supplier_type='printful'
        ).first()

        if not connection:
            connection = SupplierConnection(
                user_id=user_id,
                supplier_type='printful'
            )
            db.session.add(connection)

        connection.access_token = access_token
        connection.refresh_token = refresh_token
        connection.is_connected = True
        connection.connection_error = None
        connection.last_sync = datetime.utcnow()

        # Extract and store account information
        if store_info:
            connection.account_name = store_info.get('name') or 'Printful Store'
            connection.account_email = store_info.get('email') or store_info.get('owner_email') or store_info.get('contact_email')
            connection.account_id = str(store_info.get('id')) if store_info.get('id') else None
            connection.store_id = str(store_info.get('id')) if store_info.get('id') else None

        # Store store info if available
        if stores:
            connection.shop_id = str(stores[0].get('id'))

        db.session.commit()

        return redirect(
            f"{current_app.config['FRONTEND_URL']}/suppliers/callback"
            f"?supplier=printful&success=true&stores={len(stores)}"
        )

    except Exception as e:
        current_app.logger.error(f"Printful OAuth error: {str(e)}", exc_info=True)
        error_message = str(e)
        # Log more details for debugging
        current_app.logger.error(f"Printful OAuth error details - Code: {code[:20] if code else 'None'}..., State: {state}, User ID: {user_id}")
        return redirect(f"{current_app.config['FRONTEND_URL']}/suppliers/callback?error=oauth_failed&details={error_message[:100]}")
