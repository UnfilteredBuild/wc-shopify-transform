"""
WooCommerce to Shopify data transformation module.
"""

import pandas as pd
import re
from typing import Dict, Any, List
from config import SHOPIFY_COLUMNS, REQUIRED_COLUMNS


class WooCommerceToShopifyTransformer:
    """Transforms WooCommerce product data to Shopify import format."""
    
    def __init__(self):
        self.shopify_columns = SHOPIFY_COLUMNS
        self.required_columns = REQUIRED_COLUMNS
    
    def validate_dataframe(self, df: pd.DataFrame) -> None:
        """Validate that the DataFrame has required columns."""
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
    
    def clean_string(self, text: str) -> str:
        """Remove special characters and normalize whitespace."""
        if not text or pd.isna(text):
            return ""
        # Remove special characters except spaces, hyphens, and alphanumeric
        clean_text = re.sub(r'[^\w\s\-]', '', str(text).strip())
        # Remove extra whitespace
        return re.sub(r'\s+', ' ', clean_text).strip()
    
    def create_handle(self, product_name: str) -> str:
        """Create a URL-friendly handle from product name."""
        if not product_name:
            return ""
        handle = re.sub(r'[^\w\s-]', '', str(product_name)).strip()
        return re.sub(r'[-\s]+', '-', handle).lower()
    
    def process_images(self, images_str: str) -> List[str]:
        """Process comma-separated image URLs."""
        if not images_str or pd.isna(images_str):
            return []
        return [img.strip() for img in str(images_str).split(',') if img.strip()]
    
    def convert_weight_to_grams(self, weight_lbs: Any) -> int:
        """Convert weight from pounds to grams."""
        if not weight_lbs or pd.isna(weight_lbs):
            return 0
        try:
            return int(float(weight_lbs) * 453.592)
        except (ValueError, TypeError):
            return 0
    
    def process_tags(self, tags_str: str) -> str:
        """Process and clean product tags."""
        if not tags_str or pd.isna(tags_str):
            return ""
        tag_list = [tag.strip().replace('#', '') for tag in str(tags_str).split(',')]
        return ', '.join([tag for tag in tag_list if tag])
    
    def process_categories(self, categories_str: str) -> str:
        """Process and deduplicate product categories."""
        if not categories_str or pd.isna(categories_str):
            return ""
        
        # Split categories by common separators
        category_list = re.split(r'[,;>]', str(categories_str))
        
        # Clean and dedupe categories
        cleaned_categories = []
        seen_categories = set()
        
        for cat in category_list:
            clean_cat = self.clean_string(cat)
            if clean_cat and clean_cat.lower() not in seen_categories:
                cleaned_categories.append(clean_cat)
                seen_categories.add(clean_cat.lower())
        
        return ', '.join(cleaned_categories)
    
    def process_description(self, description: str) -> str:
        """Clean product description by removing line breaks."""
        if not description or pd.isna(description):
            return ""
        desc_str = str(description)
        # Remove literal \n strings, actual newlines, carriage returns, and other line break characters
        return re.sub(r'\\n|\n|\r|\x0b|\x0c|\x85|\u2028|\u2029', '', desc_str)
    
    def process_pricing(self, row: pd.Series) -> tuple[Any, str]:
        """Process sale and regular prices to determine variant price and compare at price."""
        sale_price = row.get('Sale price', '')
        regular_price = row.get('Regular price', '')
        
        # Convert empty strings to None for proper handling
        sale_price = sale_price if pd.notna(sale_price) and str(sale_price).strip() != '' else None
        regular_price = regular_price if pd.notna(regular_price) and str(regular_price).strip() != '' else None
        
        # Determine variant price (use sale price if available, otherwise regular price)
        variant_price = sale_price if sale_price is not None else regular_price
        variant_price = variant_price if variant_price is not None else 0
        
        # Compare at price (original price when on sale)
        compare_at_price = regular_price if (sale_price is not None and 
                                          regular_price is not None and 
                                          sale_price != regular_price) else None
        return variant_price, compare_at_price if compare_at_price is not None else ''
    
    def transform_row(self, row: pd.Series) -> Dict[str, Any]:
        """Transform a single row from WooCommerce format to Shopify format."""
        # Basic product info
        product_name = row.get('Name', '')
        handle = self.create_handle(product_name)
        description = self.process_description(row.get('Description', ''))
        
        # Images
        images = self.process_images(row.get('Images', ''))
        
        # Weight conversion
        weight_grams = self.convert_weight_to_grams(row.get('Weight (lbs)', 0))
        
        # Tags and categories
        tags = self.process_tags(row.get('Tags', ''))
        # categories = self.process_categories(row.get('Categories', ''))
        
        # Published status
        published_val = row.get('Published', 1)
        published = 'TRUE' if published_val != -1 else 'FALSE'
        status = 'active' if published == 'TRUE' else 'archived'
        
        # Pricing
        variant_price, compare_at_price = self.process_pricing(row)
        
        # Stock
        stock_qty = row.get('Stock', 0)
        stock_qty = stock_qty if pd.notna(stock_qty) and str(stock_qty).strip() != '' else 0
        in_stock = row.get('In stock?', True)
        
        return {
            'Handle': handle,
            'Title': product_name,
            'Body (HTML)': description,
            'Vendor': '',
            'Product Category': '',
            'Type': '',
            'Tags': tags,
            'Published': published,
            'Option1 Name': '',
            'Option1 Value': '',
            'Option2 Name': '',
            'Option2 Value': '',
            'Option3 Name': '',
            'Option3 Value': '',
            'Variant SKU': row.get('SKU', ''),
            'Variant Grams': weight_grams,
            'Variant Inventory Tracker': 'shopify',
            'Variant Inventory Qty': stock_qty if in_stock else 0,
            'Variant Inventory Policy': 'deny',
            'Variant Fulfillment Service': 'manual',
            'Variant Price': variant_price,
            'Variant Compare At Price': compare_at_price,
            'Variant Requires Shipping': 'TRUE',
            'Variant Taxable': 'TRUE' if row.get('Tax status', '') == 'taxable' else 'FALSE',
            'Variant Barcode': '',
            'Image Src': images[0] if images else '',
            'Image Position': '1' if images else '',
            'Image Alt Text': product_name if images else '',
            'Gift Card': 'FALSE',
            'SEO Title': product_name,
            'SEO Description': row.get('Short description', ''),
            'Google Shopping / Google Product Category': '',
            'Google Shopping / Gender': '',
            'Google Shopping / Age Group': '',
            'Google Shopping / MPN': '',
            'Google Shopping / Condition': '',
            'Google Shopping / Custom Product': '',
            'Variant Image': '',
            'Variant Weight Unit': 'g',
            'Variant Tax Code': '',
            'Cost per item': '',
            'Included / United States': 'TRUE',
            'Price / United States': '',
            'Compare At Price / United States': '',
            'Included / International': 'TRUE',
            'Price / International': '',
            'Compare At Price / International': '',
            'Status': status,
            'images': images,  # Keep for additional image processing
            'product_name': product_name  # Keep for image alt text
        }
    
    def create_additional_image_rows(self, base_row: Dict[str, Any], images: List[str]) -> List[Dict[str, Any]]:
        """Create additional rows for extra product images."""
        additional_rows = []
        handle = base_row.get('Handle', '')
        # Use Title instead of product_name since that's what's in the Shopify columns
        product_name = base_row.get('Title', base_row.get('product_name', ''))
        
        for i, image in enumerate(images[1:], 2):
            image_row = {col: '' for col in self.shopify_columns}
            image_row.update({
                'Handle': handle,
                'Image Src': image,
                'Image Position': str(i),
                'Image Alt Text': product_name
            })
            additional_rows.append(image_row)
        
        return additional_rows
    
    def clean_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean numeric columns to prevent conversion errors."""
        numeric_columns = ['Variant Price', 'Variant Compare At Price', 'Variant Grams', 'Variant Inventory Qty']
        
        for col in numeric_columns:
            if col in df.columns:
                # Replace empty strings and None values with 0 for numeric columns
                df[col] = df[col].apply(lambda x: 0 if pd.isna(x) or x == '' or x is None else x)
                # Convert to numeric, coercing errors to 0
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Handle Compare At Price specially - it can be empty
        if 'Variant Compare At Price' in df.columns:
            df['Variant Compare At Price'] = df['Variant Compare At Price'].apply(
                lambda x: '' if pd.isna(x) or x == 0 or x == '0' else str(x)
            )
        
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform WooCommerce DataFrame to Shopify import format."""
        # Validate input
        self.validate_dataframe(df)
        
        # Create empty Shopify DataFrame
        shopify_df = pd.DataFrame(columns=self.shopify_columns)
        
        # Transform each row
        for idx, row in df.iterrows():
            # Transform main product row
            transformed_row = self.transform_row(row)
            
            # Extract images and additional data
            images = transformed_row.pop('images', [])
            product_name = transformed_row.pop('product_name', '')
            
            # Add main product row
            shopify_df = pd.concat([shopify_df, pd.DataFrame([transformed_row])], ignore_index=True)
            
            # Add additional rows for extra images
            if len(images) > 1:
                # Create a copy that includes the Title for additional image rows
                row_with_title = transformed_row.copy()
                row_with_title['Title'] = transformed_row.get('Title', '')
                additional_rows = self.create_additional_image_rows(row_with_title, images)
                for additional_row in additional_rows:
                    shopify_df = pd.concat([shopify_df, pd.DataFrame([additional_row])], ignore_index=True)
        
        # Clean up data types
        shopify_df = self.clean_numeric_columns(shopify_df)
        
        return shopify_df