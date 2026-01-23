"""
Listing template routes.
Handles creating, managing, and using listing templates.
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.blueprints.templates import templates_bp
from app.models import (
    ListingTemplate, TemplateProduct, TemplateColor,
    SupplierProduct, SupplierConnection, Shop
)
from app.services.templates import create_listing_from_template


@templates_bp.route('', methods=['GET'])
@jwt_required()
def list_templates():
    """
    List all listing templates for current user.

    Query params:
        include_products: Include template products in response

    Returns:
        List of templates
    """
    user_id = get_jwt_identity()
    include_products = request.args.get('include_products', 'false').lower() == 'true'

    templates = ListingTemplate.query.filter_by(user_id=user_id, is_active=True).all()

    return jsonify({
        'templates': [t.to_dict(include_products=include_products) for t in templates]
    })


@templates_bp.route('/<int:template_id>', methods=['GET'])
@jwt_required()
def get_template(template_id):
    """
    Get specific template with all details.

    Args:
        template_id: Template ID

    Returns:
        Template details with products and colors
    """
    user_id = get_jwt_identity()

    template = ListingTemplate.query.filter_by(
        id=template_id,
        user_id=user_id
    ).first()

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    return jsonify(template.to_dict(include_products=True))


@templates_bp.route('', methods=['POST'])
@jwt_required()
def create_template():
    """
    Create a new listing template.

    Request body:
        name: Template name
        description: Optional description
        default_title: Default listing title
        default_description: Default listing description
        default_tags: List of default tags
        default_price_markup: Percentage markup (e.g., 50 for 50%)
        target_platforms: List of platforms ['etsy', 'shopify']
        etsy_category: Etsy category ID
        shopify_category: Shopify collection name

    Returns:
        Created template
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Template name is required'}), 400

    template = ListingTemplate(
        user_id=user_id,
        name=name,
        description=data.get('description'),
        default_title=data.get('default_title'),
        default_description=data.get('default_description'),
        default_tags=data.get('default_tags', []),
        default_price_markup=data.get('default_price_markup', 0),
        default_price_fixed=data.get('default_price_fixed'),
        target_platforms=data.get('target_platforms', ['etsy']),
        etsy_category=data.get('etsy_category'),
        shopify_category=data.get('shopify_category'),
        is_active=True
    )

    db.session.add(template)
    db.session.commit()

    return jsonify({
        'message': 'Template created',
        'template': template.to_dict()
    }), 201


@templates_bp.route('/<int:template_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_template(template_id):
    """
    Update a listing template.

    Args:
        template_id: Template ID

    Request body:
        Any template fields to update

    Returns:
        Updated template
    """
    user_id = get_jwt_identity()

    template = ListingTemplate.query.filter_by(
        id=template_id,
        user_id=user_id
    ).first()

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Updatable fields
    allowed_fields = [
        'name', 'description', 'default_title', 'default_description',
        'default_tags', 'default_price_markup', 'default_price_fixed',
        'target_platforms', 'etsy_category', 'shopify_category', 'is_active'
    ]

    for field in allowed_fields:
        if field in data:
            setattr(template, field, data[field])

    db.session.commit()

    return jsonify({
        'message': 'Template updated',
        'template': template.to_dict()
    })


@templates_bp.route('/<int:template_id>', methods=['DELETE'])
@jwt_required()
def delete_template(template_id):
    """
    Delete a listing template.

    Args:
        template_id: Template ID

    Returns:
        Success message
    """
    user_id = get_jwt_identity()

    template = ListingTemplate.query.filter_by(
        id=template_id,
        user_id=user_id
    ).first()

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    # Soft delete
    template.is_active = False
    db.session.commit()

    return jsonify({'message': 'Template deleted'})


@templates_bp.route('/<int:template_id>/products', methods=['POST'])
@jwt_required()
def add_template_product(template_id):
    """
    Add a product to a template.

    Args:
        template_id: Template ID

    Request body:
        supplier_type: Supplier type (gelato, printify, printful)
        supplier_product_id: ID of supplier product (from our DB) or external_product_id
        external_product_id: Supplier's product ID
        product_name: Display name for the product
        product_type: Product type (e.g., "Gildan 18000")
        selected_sizes: List of sizes to include
        price_override: Fixed price override
        price_markup: Percentage markup for this product

    Returns:
        Created template product
    """
    user_id = get_jwt_identity()

    template = ListingTemplate.query.filter_by(
        id=template_id,
        user_id=user_id
    ).first()

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    supplier_type = data.get('supplier_type')
    if not supplier_type:
        return jsonify({'error': 'supplier_type is required'}), 400

    # Verify user has this supplier connected
    connection = SupplierConnection.query.filter_by(
        user_id=user_id,
        supplier_type=supplier_type,
        is_connected=True
    ).first()

    if not connection:
        return jsonify({'error': f'{supplier_type} is not connected'}), 400

    # Get or validate supplier product
    supplier_product_id = data.get('supplier_product_id')
    external_product_id = data.get('external_product_id')

    if supplier_product_id:
        supplier_product = SupplierProduct.query.filter_by(
            id=supplier_product_id,
            supplier_connection_id=connection.id
        ).first()
        if supplier_product:
            external_product_id = supplier_product.supplier_product_id

    # Get display order
    max_order = db.session.query(db.func.max(TemplateProduct.display_order)).filter_by(
        template_id=template.id
    ).scalar() or 0

    # Validate alias_name uniqueness within template
    alias_name = data.get('alias_name', '').strip()
    if alias_name:
        existing = TemplateProduct.query.filter_by(
            template_id=template.id,
            alias_name=alias_name
        ).first()
        if existing:
            return jsonify({'error': f'Alias name "{alias_name}" already exists in this template'}), 400

    # Handle selected_sizes - can be string (comma-separated) or list
    selected_sizes = data.get('selected_sizes', [])
    if isinstance(selected_sizes, str):
        selected_sizes = [s.strip() for s in selected_sizes.split(',') if s.strip()]

    template_product = TemplateProduct(
        template_id=template.id,
        supplier_product_id=supplier_product_id,
        supplier_type=supplier_type,
        external_product_id=external_product_id,
        product_name=data.get('product_name', ''),
        product_type=data.get('product_type'),
        alias_name=alias_name or None,
        selected_sizes=selected_sizes,
        pricing_mode=data.get('pricing_mode', 'global'),
        prices=data.get('prices', {}),
        global_price=data.get('global_price'),
        price_override=data.get('price_override'),
        price_markup=data.get('price_markup'),
        display_order=max_order + 1,
        is_active=True
    )

    db.session.add(template_product)
    db.session.commit()

    return jsonify({
        'message': 'Product added to template',
        'product': template_product.to_dict()
    }), 201


@templates_bp.route('/<int:template_id>/products/<int:product_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_template_product(template_id, product_id):
    """
    Update a template product.

    Args:
        template_id: Template ID
        product_id: Template product ID

    Returns:
        Updated template product
    """
    user_id = get_jwt_identity()

    template = ListingTemplate.query.filter_by(
        id=template_id,
        user_id=user_id
    ).first()

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    template_product = TemplateProduct.query.filter_by(
        id=product_id,
        template_id=template.id
    ).first()

    if not template_product:
        return jsonify({'error': 'Product not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Validate alias_name uniqueness if being updated
    if 'alias_name' in data:
        alias_name = data.get('alias_name', '').strip()
        if alias_name:
            existing = TemplateProduct.query.filter_by(
                template_id=template.id,
                alias_name=alias_name
            ).first()
            if existing and existing.id != template_product.id:
                return jsonify({'error': f'Alias name "{alias_name}" already exists in this template'}), 400
        template_product.alias_name = alias_name or None

    # Handle selected_sizes - can be string (comma-separated) or list
    if 'selected_sizes' in data:
        selected_sizes = data['selected_sizes']
        if isinstance(selected_sizes, str):
            selected_sizes = [s.strip() for s in selected_sizes.split(',') if s.strip()]
        template_product.selected_sizes = selected_sizes

    # Updatable fields
    allowed_fields = [
        'product_name', 'product_type',
        'pricing_mode', 'prices', 'global_price',
        'price_override', 'price_markup', 'display_order', 'is_active'
    ]

    for field in allowed_fields:
        if field in data:
            setattr(template_product, field, data[field])

    db.session.commit()

    return jsonify({
        'message': 'Product updated',
        'product': template_product.to_dict(include_colors=True)
    })


@templates_bp.route('/<int:template_id>/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_template_product(template_id, product_id):
    """
    Remove a product from a template.

    Args:
        template_id: Template ID
        product_id: Template product ID

    Returns:
        Success message
    """
    user_id = get_jwt_identity()

    template = ListingTemplate.query.filter_by(
        id=template_id,
        user_id=user_id
    ).first()

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    template_product = TemplateProduct.query.filter_by(
        id=product_id,
        template_id=template.id
    ).first()

    if not template_product:
        return jsonify({'error': 'Product not found'}), 404

    db.session.delete(template_product)
    db.session.commit()

    return jsonify({'message': 'Product removed from template'})


@templates_bp.route('/<int:template_id>/products/<int:product_id>/colors', methods=['POST'])
@jwt_required()
def add_template_color(template_id, product_id):
    """
    Add a color to a template product.

    Args:
        template_id: Template ID
        product_id: Template product ID

    Request body:
        color_name: Color name
        color_hex: Hex color code
        supplier_color_id: Supplier's color ID
        display_name: Optional display name override

    Returns:
        Created color
    """
    user_id = get_jwt_identity()

    template = ListingTemplate.query.filter_by(
        id=template_id,
        user_id=user_id
    ).first()

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    template_product = TemplateProduct.query.filter_by(
        id=product_id,
        template_id=template.id
    ).first()

    if not template_product:
        return jsonify({'error': 'Product not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    color_name = data.get('color_name', '').strip()
    if not color_name:
        return jsonify({'error': 'color_name is required'}), 400

    color = TemplateColor(
        template_product_id=template_product.id,
        color_name=color_name,
        color_hex=data.get('color_hex'),
        supplier_color_id=data.get('supplier_color_id'),
        display_name=data.get('display_name'),
        is_active=True
    )

    db.session.add(color)
    db.session.commit()

    return jsonify({
        'message': 'Color added',
        'color': color.to_dict()
    }), 201


@templates_bp.route('/<int:template_id>/products/<int:product_id>/colors/<int:color_id>', methods=['DELETE'])
@jwt_required()
def delete_template_color(template_id, product_id, color_id):
    """
    Remove a color from a template product.

    Args:
        template_id: Template ID
        product_id: Template product ID
        color_id: Color ID

    Returns:
        Success message
    """
    user_id = get_jwt_identity()

    template = ListingTemplate.query.filter_by(
        id=template_id,
        user_id=user_id
    ).first()

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    color = TemplateColor.query.filter_by(id=color_id).first()

    if not color:
        return jsonify({'error': 'Color not found'}), 404

    # Verify color belongs to this template
    template_product = TemplateProduct.query.filter_by(
        id=color.template_product_id,
        template_id=template.id
    ).first()

    if not template_product:
        return jsonify({'error': 'Color not found'}), 404

    db.session.delete(color)
    db.session.commit()

    return jsonify({'message': 'Color removed'})


@templates_bp.route('/<int:template_id>/create-listing', methods=['POST'])
@jwt_required()
def create_listing(template_id):
    """
    Create a listing from a template.

    Args:
        template_id: Template ID

    Request body:
        shop_id: Target shop ID
        title: Listing title (overrides template default)
        description: Listing description
        price: Listing price
        tags: List of tags
        images: List of image URLs

    Returns:
        Created listing details
    """
    user_id = get_jwt_identity()

    template = ListingTemplate.query.filter_by(
        id=template_id,
        user_id=user_id
    ).first()

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    shop_id = data.get('shop_id')
    if not shop_id:
        return jsonify({'error': 'shop_id is required'}), 400

    shop = Shop.query.filter_by(
        id=shop_id,
        user_id=user_id,
        is_connected=True
    ).first()

    if not shop:
        return jsonify({'error': 'Shop not found or not connected'}), 404

    try:
        result = create_listing_from_template(
            template=template,
            shop=shop,
            title=data.get('title'),
            description=data.get('description'),
            price=data.get('price'),
            tags=data.get('tags'),
            images=data.get('images', [])
        )

        return jsonify({
            'message': 'Listing created',
            'listing': result
        }), 201

    except Exception as e:
        return jsonify({'error': f'Failed to create listing: {str(e)}'}), 500


@templates_bp.route('/<int:template_id>/preview', methods=['POST'])
@jwt_required()
def preview_listing(template_id):
    """
    Preview a listing from a template without creating it.

    Args:
        template_id: Template ID

    Request body:
        Same as create-listing

    Returns:
        Preview of what the listing would look like
    """
    user_id = get_jwt_identity()

    template = ListingTemplate.query.filter_by(
        id=template_id,
        user_id=user_id
    ).first()

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    data = request.get_json() or {}

    # Build preview
    preview = {
        'title': data.get('title') or template.default_title or '',
        'description': data.get('description') or template.default_description or '',
        'tags': data.get('tags') or template.default_tags or [],
        'products': [],
        'variants': []
    }

    # Add products from template
    for tp in template.template_products.filter_by(is_active=True):
        product_info = {
            'supplier': tp.supplier_type,
            'product_name': tp.product_name,
            'product_type': tp.product_type,
            'sizes': tp.selected_sizes,
            'colors': [c.to_dict() for c in tp.colors.filter_by(is_active=True)]
        }
        preview['products'].append(product_info)

        # Generate variant combinations
        for size in tp.selected_sizes or ['One Size']:
            for color in tp.colors.filter_by(is_active=True):
                preview['variants'].append({
                    'supplier': tp.supplier_type,
                    'product': tp.product_name,
                    'size': size,
                    'color': color.display_name or color.color_name,
                    'sku': f"{tp.supplier_type[:3].upper()}_{tp.id}_{size}_{color.color_name}".replace(' ', '_')
                })

    return jsonify({'preview': preview})


@templates_bp.route('/<int:template_id>/products/<int:product_id>/pricing', methods=['GET'])
@jwt_required()
def get_template_product_pricing(template_id, product_id):
    """
    Get pricing calculations for a template product.
    Shows cost, price, and profit for each configuration.

    Args:
        template_id: Template ID
        product_id: Template product ID

    Query params:
        view: 'config' (per size+color), 'size' (per size), or 'color' (per color)

    Returns:
        Pricing data organized by the requested view
    """
    user_id = get_jwt_identity()
    view_mode = request.args.get('view', 'config')  # config, size, or color

    template = ListingTemplate.query.filter_by(
        id=template_id,
        user_id=user_id
    ).first()

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    template_product = TemplateProduct.query.filter_by(
        id=product_id,
        template_id=template.id
    ).first()

    if not template_product:
        return jsonify({'error': 'Product not found'}), 404

    # Get supplier product for cost calculation
    supplier_product = None
    if template_product.supplier_product_id:
        supplier_product = SupplierProduct.query.get(template_product.supplier_product_id)

    # Get base cost from supplier product
    base_cost = supplier_product.base_price if supplier_product else 0
    shipping_cost = supplier_product.shipping_first_item if supplier_product else 0
    total_cost_per_item = base_cost + shipping_cost

    # Get sizes and colors
    sizes = template_product.selected_sizes or ['One Size']
    colors = [c for c in template_product.colors.filter_by(is_active=True)]

    if not sizes or not colors:
        return jsonify({
            'error': 'Product must have at least one size and one color configured'
        }), 400

    # Calculate pricing for each configuration
    pricing_data = {
        'product_id': template_product.id,
        'product_name': template_product.product_name,
        'alias_name': template_product.alias_name,
        'pricing_mode': template_product.pricing_mode,
        'base_cost': base_cost,
        'shipping_cost': shipping_cost,
        'total_cost': total_cost_per_item,
        'view_mode': view_mode,
        'data': {}
    }

    def get_price_for_config(size, color):
        """Get the price for a specific size+color configuration."""
        prices = template_product.prices or {}
        
        if template_product.pricing_mode == 'per_config':
            config_key = f"{size}_{color.color_name}"
            return prices.get(config_key) or template_product.global_price
        elif template_product.pricing_mode == 'per_size':
            return prices.get(size) or template_product.global_price
        elif template_product.pricing_mode == 'per_color':
            return prices.get(color.color_name) or template_product.global_price
        else:  # global
            return template_product.global_price

    if view_mode == 'config':
        # Per configuration (size + color)
        for size in sizes:
            for color in colors:
                config_key = f"{size}_{color.color_name}"
                price = get_price_for_config(size, color) or 0
                profit = price - total_cost_per_item
                
                pricing_data['data'][config_key] = {
                    'size': size,
                    'color': color.color_name,
                    'color_hex': color.color_hex,
                    'cost': round(total_cost_per_item, 2),
                    'price': round(price, 2),
                    'profit': round(profit, 2),
                    'profit_margin': round((profit / price * 100) if price > 0 else 0, 2)
                }
    
    elif view_mode == 'size':
        # Per size (aggregate across colors)
        for size in sizes:
            size_prices = []
            for color in colors:
                price = get_price_for_config(size, color)
                if price:
                    size_prices.append(price)
            
            avg_price = sum(size_prices) / len(size_prices) if size_prices else 0
            profit = avg_price - total_cost_per_item
            
            pricing_data['data'][size] = {
                'size': size,
                'cost': round(total_cost_per_item, 2),
                'price': round(avg_price, 2),
                'profit': round(profit, 2),
                'profit_margin': round((profit / avg_price * 100) if avg_price > 0 else 0, 2),
                'config_count': len(colors)
            }
    
    elif view_mode == 'color':
        # Per color (aggregate across sizes)
        for color in colors:
            color_prices = []
            for size in sizes:
                price = get_price_for_config(size, color)
                if price:
                    color_prices.append(price)
            
            avg_price = sum(color_prices) / len(color_prices) if color_prices else 0
            profit = avg_price - total_cost_per_item
            
            pricing_data['data'][color.color_name] = {
                'color': color.color_name,
                'color_hex': color.color_hex,
                'cost': round(total_cost_per_item, 2),
                'price': round(avg_price, 2),
                'profit': round(profit, 2),
                'profit_margin': round((profit / avg_price * 100) if avg_price > 0 else 0, 2),
                'config_count': len(sizes)
            }

    return jsonify(pricing_data)
