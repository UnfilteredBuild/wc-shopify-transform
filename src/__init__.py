"""
WooCommerce to Shopify Transformer Package
"""

from transformer import WooCommerceToShopifyTransformer
from customer_transformer import CustomerToShopifyTransformer
from config import APP_CONFIG, USER_INSTRUCTIONS, CUSTOMER_INSTRUCTIONS, EXPECTED_CSV_FORMAT
from utils import *

__version__ = "1.0.0"
__author__ = "Card Giants"
__description__ = "Transform WooCommerce product exports to Shopify import format"