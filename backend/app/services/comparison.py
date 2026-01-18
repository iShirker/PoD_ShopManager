"""
Product comparison service.
Handles price comparison across different POD suppliers.
"""
from app.models import SupplierProduct, SupplierType
from app.services.suppliers.gelato import get_gelato_product_pricing, get_gelato_shipping_cost
from app.services.suppliers.printify import get_printify_product_pricing, get_printify_shipping_cost
from app.services.suppliers.printful import get_printful_product_pricing, get_printful_shipping_cost


# Product type mappings between suppliers
PRODUCT_TYPE_MAPPINGS = {
    'gildan 18000': {
        'gelato': 'gildan-18000-heavy-blend-sweatshirt',
        'printify': '145',  # Blueprint ID
        'printful': '380'   # Product ID
    },
    'gildan 18500': {
        'gelato': 'gildan-18500-heavy-blend-hoodie',
        'printify': '77',
        'printful': '146'
    },
    'gildan 5000': {
        'gelato': 'gildan-5000-heavy-cotton-tee',
        'printify': '6',
        'printful': '71'
    },
    'gildan 64000': {
        'gelato': 'gildan-64000-softstyle-tee',
        'printify': '12',
        'printful': '19'
    },
    'bella canvas 3001': {
        'gelato': 'bella-canvas-3001-unisex-tee',
        'printify': '5',
        'printful': '586'
    },
    'bella canvas 3413': {
        'gelato': 'bella-canvas-3413-triblend',
        'printify': '162',
        'printful': '587'
    },
    'comfort colors 1717': {
        'gelato': 'comfort-colors-1717',
        'printify': '428',
        'printful': '638'
    },
}


def compare_product_prices(product, connection_map, detailed=False):
    """
    Compare product prices across connected suppliers.

    Args:
        product: Product model instance
        connection_map: Dict of supplier_type -> SupplierConnection
        detailed: Include detailed variant pricing

    Returns:
        Comparison data dictionary
    """
    if not product.product_type:
        return None

    # Normalize product type for lookup
    product_type_key = product.product_type.lower().split('(')[0].strip()

    # Get mapping for this product type
    type_mapping = None
    for key, mapping in PRODUCT_TYPE_MAPPINGS.items():
        if key in product_type_key:
            type_mapping = mapping
            break

    if not type_mapping:
        return None

    comparison = {
        'product_id': product.id,
        'title': product.title,
        'product_type': product.product_type,
        'current_supplier': product.supplier_type,
        'current_sku': product.sku,
        'listing_price': product.price,
        'suppliers': {}
    }

    # Get pricing from each connected supplier
    for supplier_type, connection in connection_map.items():
        supplier_product_id = type_mapping.get(supplier_type)
        if not supplier_product_id:
            continue

        pricing = _get_supplier_pricing(
            supplier_type,
            connection,
            supplier_product_id,
            detailed
        )

        if pricing:
            comparison['suppliers'][supplier_type] = pricing

    # Calculate best option and potential savings
    if comparison['suppliers']:
        best_supplier = None
        best_total = float('inf')

        for supplier, data in comparison['suppliers'].items():
            total = (data.get('base_price', 0) or 0) + (data.get('shipping_first_item', 0) or 0)
            if total < best_total and total > 0:
                best_total = total
                best_supplier = supplier

        comparison['best_supplier'] = best_supplier
        comparison['best_total_cost'] = best_total

        # Calculate savings vs current
        current_pricing = comparison['suppliers'].get(product.supplier_type, {})
        current_total = (
            (current_pricing.get('base_price', 0) or 0) +
            (current_pricing.get('shipping_first_item', 0) or 0)
        )

        if current_total > 0 and best_total < current_total:
            comparison['potential_savings'] = round(current_total - best_total, 2)
            comparison['savings_percent'] = round(
                ((current_total - best_total) / current_total) * 100, 1
            )
        else:
            comparison['potential_savings'] = 0
            comparison['savings_percent'] = 0

    return comparison


def _get_supplier_pricing(supplier_type, connection, product_id, detailed=False):
    """
    Get pricing from a specific supplier.

    Args:
        supplier_type: Type of supplier
        connection: SupplierConnection instance
        product_id: Supplier-specific product ID
        detailed: Include variant details

    Returns:
        Pricing dictionary or None
    """
    try:
        if supplier_type == SupplierType.GELATO.value:
            pricing = get_gelato_product_pricing(
                connection.api_key,
                product_id,
                access_token=connection.access_token
            )
            shipping = get_gelato_shipping_cost(
                connection.api_key,
                product_id,
                access_token=connection.access_token
            )

        elif supplier_type == SupplierType.PRINTIFY.value:
            # Printify needs blueprint ID and print provider
            pricing = get_printify_product_pricing(connection.api_key, product_id, '99')  # Default provider
            shipping = get_printify_shipping_cost(connection.api_key, product_id, '99')

        elif supplier_type == SupplierType.PRINTFUL.value:
            pricing = get_printful_product_pricing(connection.api_key, product_id)
            shipping = get_printful_shipping_cost(connection.api_key, product_id)

        else:
            return None

        if not pricing:
            return None

        result = {
            'supplier_product_id': product_id,
            'base_price': pricing.get('base_price'),
            'currency': pricing.get('currency', 'USD'),
            'shipping_first_item': shipping.get('first_item') if shipping else None,
            'shipping_additional_item': shipping.get('additional_item') if shipping else None
        }

        if detailed and pricing.get('variants'):
            result['variants'] = pricing['variants']

        return result

    except Exception:
        return None


def find_matching_supplier_products(product, connections):
    """
    Find matching products from supplier catalogs.

    Args:
        product: Product model instance
        connections: List of SupplierConnection instances

    Returns:
        List of matching products by supplier
    """
    if not product.product_type:
        return []

    # Normalize product type for search
    product_type_key = product.product_type.lower().split('(')[0].strip()

    matches = []

    for connection in connections:
        # Skip current supplier
        if connection.supplier_type == product.supplier_type:
            continue

        # Search supplier products
        supplier_products = SupplierProduct.query.filter_by(
            supplier_connection_id=connection.id,
            is_active=True
        ).all()

        for sp in supplier_products:
            if sp.product_type and product_type_key in sp.product_type.lower():
                matches.append({
                    'supplier': connection.supplier_type,
                    'product': sp.to_dict()
                })
            elif sp.name and product_type_key in sp.name.lower():
                matches.append({
                    'supplier': connection.supplier_type,
                    'product': sp.to_dict()
                })

    return matches


def get_comparison_summary(products, connection_map):
    """
    Get summary of potential savings across all products.

    Args:
        products: List of Product instances
        connection_map: Dict of supplier_type -> SupplierConnection

    Returns:
        Summary dictionary
    """
    summary = {
        'total_products': len(products),
        'products_with_savings': 0,
        'total_potential_savings': 0,
        'by_supplier': {},
        'by_product_type': {}
    }

    for supplier in SupplierType:
        summary['by_supplier'][supplier.value] = {
            'current_count': 0,
            'potential_savings': 0
        }

    for product in products:
        # Count by current supplier
        if product.supplier_type:
            if product.supplier_type in summary['by_supplier']:
                summary['by_supplier'][product.supplier_type]['current_count'] += 1

        # Get comparison
        comparison = compare_product_prices(product, connection_map)
        if comparison and comparison.get('potential_savings', 0) > 0:
            summary['products_with_savings'] += 1
            summary['total_potential_savings'] += comparison['potential_savings']

            if product.supplier_type in summary['by_supplier']:
                summary['by_supplier'][product.supplier_type]['potential_savings'] += comparison['potential_savings']

            # Track by product type
            product_type = product.product_type or 'Unknown'
            if product_type not in summary['by_product_type']:
                summary['by_product_type'][product_type] = {
                    'count': 0,
                    'potential_savings': 0,
                    'best_supplier': None
                }
            summary['by_product_type'][product_type]['count'] += 1
            summary['by_product_type'][product_type]['potential_savings'] += comparison['potential_savings']
            if comparison.get('best_supplier'):
                summary['by_product_type'][product_type]['best_supplier'] = comparison['best_supplier']

    summary['total_potential_savings'] = round(summary['total_potential_savings'], 2)

    return summary
