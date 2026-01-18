"""
User profile routes.
Handles viewing and editing user profiles.
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.blueprints.users import users_bp
from app.models import User


@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get current user's profile.

    Returns:
        User profile data with connected suppliers and shops count
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    profile = user.to_dict()
    profile['supplier_connections_count'] = user.supplier_connections.count()
    profile['shops_count'] = user.shops.count()
    profile['templates_count'] = user.templates.count()

    return jsonify(profile)


@users_bp.route('/me', methods=['PUT', 'PATCH'])
@jwt_required()
def update_profile():
    """
    Update current user's profile.

    Request body (all optional):
        username: New username
        first_name: First name
        last_name: Last name
        avatar_url: Profile picture URL

    Returns:
        Updated user profile
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Updatable fields
    allowed_fields = ['username', 'first_name', 'last_name', 'avatar_url']

    for field in allowed_fields:
        if field in data:
            # Validate username uniqueness
            if field == 'username' and data[field]:
                existing = User.query.filter(
                    User.username == data[field],
                    User.id != user.id
                ).first()
                if existing:
                    return jsonify({'error': 'Username already taken'}), 409

            setattr(user, field, data[field])

    db.session.commit()

    return jsonify({
        'message': 'Profile updated',
        'user': user.to_dict()
    })


@users_bp.route('/me/password', methods=['PUT'])
@jwt_required()
def change_password():
    """
    Change user's password.

    Request body:
        current_password: Current password
        new_password: New password (min 8 characters)

    Returns:
        Success message
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if not user.password_hash:
        return jsonify({'error': 'Cannot change password for OAuth accounts'}), 400

    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    if not current_password or not new_password:
        return jsonify({'error': 'Current and new passwords are required'}), 400

    if not user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401

    if len(new_password) < 8:
        return jsonify({'error': 'New password must be at least 8 characters'}), 400

    user.set_password(new_password)
    db.session.commit()

    return jsonify({'message': 'Password changed successfully'})


@users_bp.route('/me/email', methods=['PUT'])
@jwt_required()
def change_email():
    """
    Change user's email address.

    Request body:
        email: New email address
        password: Current password for verification

    Returns:
        Success message
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    new_email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not new_email:
        return jsonify({'error': 'New email is required'}), 400

    # Verify password if user has one
    if user.password_hash:
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        if not user.check_password(password):
            return jsonify({'error': 'Password is incorrect'}), 401

    # Check if email is taken
    if User.query.filter(User.email == new_email, User.id != user.id).first():
        return jsonify({'error': 'Email already in use'}), 409

    user.email = new_email
    user.is_verified = False  # Require re-verification
    db.session.commit()

    return jsonify({
        'message': 'Email changed successfully. Please verify your new email.',
        'user': user.to_dict()
    })


@users_bp.route('/me/deactivate', methods=['POST'])
@jwt_required()
def deactivate_account():
    """
    Deactivate user's account.

    Request body:
        password: Current password for verification (optional for OAuth accounts)

    Returns:
        Success message
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}
    password = data.get('password', '')

    # Verify password if user has one
    if user.password_hash:
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        if not user.check_password(password):
            return jsonify({'error': 'Password is incorrect'}), 401

    user.is_active = False
    db.session.commit()

    return jsonify({'message': 'Account deactivated successfully'})


@users_bp.route('/me/summary', methods=['GET'])
@jwt_required()
def get_user_summary():
    """
    Get summary of user's data.

    Returns:
        Summary including shops, suppliers, products, and templates count
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get counts
    shops = user.shops.all()
    total_products = sum(shop.total_listings for shop in shops)
    pod_products = sum(shop.pod_listings for shop in shops)

    return jsonify({
        'user': user.to_dict(),
        'summary': {
            'shops_count': len(shops),
            'supplier_connections_count': user.supplier_connections.filter_by(is_connected=True).count(),
            'total_products': total_products,
            'pod_products': pod_products,
            'templates_count': user.templates.count()
        }
    })
