"""
Configuration constants and settings for the WooCommerce to Shopify transformer.
"""

# Required columns in WooCommerce CSV export
REQUIRED_COLUMNS = [
    'Name', 'SKU', 'Description', 'Categories', 'Tags', 'Images',
    'Regular price', 'Sale price', 'Weight (lbs)', 'Stock', 'Published', 'Tax status'
]

# Shopify import CSV column structure
SHOPIFY_COLUMNS = [
    'Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type', 'Tags', 'Published',
    'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value',
    'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Qty',
    'Variant Inventory Policy', 'Variant Fulfillment Service', 'Variant Price', 'Variant Compare At Price',
    'Variant Requires Shipping', 'Variant Taxable', 'Variant Barcode', 'Image Src', 'Image Position',
    'Image Alt Text', 'Gift Card', 'SEO Title', 'SEO Description', 'Google Shopping / Google Product Category',
    'Google Shopping / Gender', 'Google Shopping / Age Group', 'Google Shopping / MPN',
    'Google Shopping / Condition', 'Google Shopping / Custom Product', 'Variant Image', 'Variant Weight Unit',
    'Variant Tax Code', 'Cost per item', 'Included / United States', 'Price / United States',
    'Compare At Price / United States', 'Included / International', 'Price / International',
    'Compare At Price / International', 'Status'
]

# App configuration
APP_CONFIG = {
    'page_title': 'WooCommerce to Shopify Transformer',
    'page_icon': '🛒',
    'layout': 'wide',
    'max_upload_size_mb': 200,
    'preview_rows': 10
}

# Instructions for users
USER_INSTRUCTIONS = """
1. **Export your products** from WooCommerce as CSV
2. **Upload the CSV file** using the file uploader
3. **Review the preview** of transformed data
4. **Download** the Shopify-ready CSV file

---

### 🔧 What this tool does:
- Creates Shopify-compatible product handles
- Converts weights from lbs to grams
- Maps WooCommerce prices to Shopify format
- Cleans product descriptions
- Handles multiple product images
- Converts tags and categories
"""

# Expected CSV format help text
EXPECTED_CSV_FORMAT = """
Your WooCommerce CSV should include these columns:
- `Name` - Product name
- `SKU` - Product SKU
- `Description` - Product description
- `Categories` - Product categories
- `Tags` - Product tags
- `Images` - Product images (comma-separated URLs)
- `Regular price` - Regular price
- `Sale price` - Sale price (if applicable)
- `Weight (lbs)` - Product weight in pounds
- `Stock` - Stock quantity
- `Published` - Published status
- `Tax status` - Tax status
"""