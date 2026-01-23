"""
Database models package.
Exports all models for easy importing.
"""
from app.models.user import User
from app.models.supplier import SupplierConnection, SupplierType
from app.models.shop import Shop, ShopType
from app.models.product import Product, ProductVariant, SupplierProduct
from app.models.user_product import UserProduct, UserProductSupplier
from app.models.template import ListingTemplate, TemplateProduct, TemplateColor

__all__ = [
    'User',
    'SupplierConnection',
    'SupplierType',
    'Shop',
    'ShopType',
    'Product',
    'ProductVariant',
    'SupplierProduct',
    'UserProduct',
    'UserProductSupplier',
    'ListingTemplate',
    'TemplateProduct',
    'TemplateColor'
]
