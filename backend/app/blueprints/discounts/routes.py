"""
Discount program routes.
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.blueprints.discounts import discounts_bp
from app.models import DiscountProgram, ProductDiscountMapping


@discounts_bp.route('', methods=['GET'])
@jwt_required()
def list_programs():
    """List discount programs for current user."""
    user_id = get_jwt_identity()
    programs = DiscountProgram.query.filter_by(user_id=user_id).order_by(DiscountProgram.created_at.desc()).all()
    return jsonify({'programs': [p.to_dict(include_mappings=True) for p in programs]})


@discounts_bp.route('', methods=['POST'])
@jwt_required()
def create_program():
    """Create a discount program."""
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    if not data.get('discount_type'):
        return jsonify({'error': 'discount_type is required'}), 400

    from datetime import datetime
    def _parse_dt(s):
        if not s:
            return None
        try:
            s = str(s).replace('Z', '+00:00')
            return datetime.fromisoformat(s)
        except Exception:
            return None
    program = DiscountProgram(
        user_id=user_id,
        name=data['name'],
        description=data.get('description'),
        discount_type=data['discount_type'],
        discount_value=data.get('discount_value'),
        start_date=_parse_dt(data.get('start_date')),
        end_date=_parse_dt(data.get('end_date')),
        is_recurring=bool(data.get('is_recurring')),
        recurrence_pattern=data.get('recurrence_pattern'),
        min_margin_required=data.get('min_margin_required'),
        is_active=data.get('is_active', True),
    )
    db.session.add(program)
    db.session.commit()
    return jsonify(program.to_dict(include_mappings=True)), 201


@discounts_bp.route('/<int:program_id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required()
def program_detail(program_id):
    """Get, update, or delete a discount program."""
    user_id = get_jwt_identity()
    program = DiscountProgram.query.filter_by(id=program_id, user_id=user_id).first()
    if not program:
        return jsonify({'error': 'Discount program not found'}), 404

    if request.method == 'GET':
        return jsonify(program.to_dict(include_mappings=True))

    if request.method == 'DELETE':
        db.session.delete(program)
        db.session.commit()
        return jsonify({'message': 'Deleted'}), 200

    data = request.get_json() or {}
    from datetime import datetime
    def _parse_dt(s):
        if not s:
            return None
        try:
            return datetime.fromisoformat(str(s).replace('Z', '+00:00'))
        except Exception:
            return None
    for k in ('name', 'description', 'discount_type', 'discount_value', 'is_recurring', 'recurrence_pattern', 'min_margin_required', 'is_active'):
        if k in data:
            setattr(program, k, data[k])
    if 'start_date' in data:
        program.start_date = _parse_dt(data['start_date'])
    if 'end_date' in data:
        program.end_date = _parse_dt(data['end_date'])
    db.session.commit()
    return jsonify(program.to_dict(include_mappings=True))


@discounts_bp.route('/<int:program_id>/products', methods=['POST'])
@jwt_required()
def add_product_mapping(program_id):
    """Add product mapping to a discount program."""
    user_id = get_jwt_identity()
    program = DiscountProgram.query.filter_by(id=program_id, user_id=user_id).first()
    if not program:
        return jsonify({'error': 'Discount program not found'}), 404
    data = request.get_json() or {}
    user_product_id = data.get('user_product_id')
    product_id = data.get('product_id')
    if not user_product_id and not product_id:
        return jsonify({'error': 'user_product_id or product_id required'}), 400
    m = ProductDiscountMapping(
        discount_program_id=program.id,
        user_product_id=user_product_id,
        product_id=product_id,
        is_active=True,
    )
    db.session.add(m)
    db.session.commit()
    return jsonify(m.to_dict()), 201


@discounts_bp.route('/<int:program_id>/products/<int:mapping_id>', methods=['DELETE'])
@jwt_required()
def remove_product_mapping(program_id, mapping_id):
    """Remove product mapping from a discount program."""
    user_id = get_jwt_identity()
    program = DiscountProgram.query.filter_by(id=program_id, user_id=user_id).first()
    if not program:
        return jsonify({'error': 'Discount program not found'}), 404
    m = ProductDiscountMapping.query.filter_by(
        id=mapping_id,
        discount_program_id=program.id,
    ).first()
    if not m:
        return jsonify({'error': 'Mapping not found'}), 404
    db.session.delete(m)
    db.session.commit()
    return jsonify({'message': 'Removed'}), 200
