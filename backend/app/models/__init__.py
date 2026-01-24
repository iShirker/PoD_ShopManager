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
from app.models.subscription import SubscriptionPlan, UserSubscription, UsageRecord
from app.models.order import Order, OrderItem, Fulfillment
from app.models.pricing import PlatformFeeStructure, ProductPricingRule
from app.models.discount import DiscountProgram, ProductDiscountMapping

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
    'TemplateColor',
    'SubscriptionPlan',
    'UserSubscription',
    'UsageRecord',
    'Order',
    'OrderItem',
    'Fulfillment',
    'PlatformFeeStructure',
    'ProductPricingRule',
    'DiscountProgram',
    'ProductDiscountMapping',
]
