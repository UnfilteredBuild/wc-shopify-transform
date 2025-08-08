import streamlit as st
import pandas as pd
import re
from datetime import datetime
import io

def transform_wc_to_shopify_streamlit(df):
    """
    Transform WooCommerce export DataFrame to Shopify import format
    """
    # Debug: Print column names and first few rows
    # st.write("**Debug Info:**")
    # st.write(f"Columns in uploaded file: {list(df.columns)}")
    # st.write("First row data:")
    # st.write(df.iloc[0].to_dict())
    
    # Check for required columns
    required_columns = ['Name', 'SKU', 'Description', 'Categories', 'Tags', 'Images', 
                       'Regular price', 'Sale price', 'Weight (lbs)', 'Stock', 'Published', 'Tax status']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Create empty Shopify DataFrame with required columns
    shopify_columns = [
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
    
    shopify_df = pd.DataFrame(columns=shopify_columns)
    
    for idx, row in df.iterrows():
        # Create handle from product name (URL-friendly) with safe access
        product_name = row.get('Name', '')
        handle = re.sub(r'[^\w\s-]', '', str(product_name)).strip()
        handle = re.sub(r'[-\s]+', '-', handle).lower()
        
        # Extract images and create multiple rows if needed
        images = []
        if pd.notna(row.get('Images', '')) and row.get('Images', ''):
            images = [img.strip() for img in str(row['Images']).split(',')]
        
        # Convert weight from lbs to grams
        weight_grams = 0
        weight_lbs = row.get('Weight (lbs)', 0)
        if pd.notna(weight_lbs) and weight_lbs:
            weight_grams = int(float(weight_lbs) * 453.592)
        
        # Convert tags
        tags = ""
        if pd.notna(row.get('Tags', '')) and row.get('Tags', ''):
            tag_list = [tag.strip().replace('#', '') for tag in str(row['Tags']).split(',')]
            tags = ', '.join(tag_list)
        
        # Process categories - clean and dedupe
        # categories = ""
        # if pd.notna(row.get('Categories', '')) and row.get('Categories', ''):
        #     # Split categories by common separators
        #     cat_string = str(row['Categories'])
        #     # Split by comma, semicolon, or > (common WooCommerce separators)
        #     category_list = re.split(r'[,;>]', cat_string)
            
        #     # Clean each category: remove special chars, trim whitespace, remove duplicates
        #     cleaned_categories = []
        #     seen_categories = set()
            
        #     for cat in category_list:
        #         # Remove special characters except spaces, hyphens, and alphanumeric
        #         clean_cat = re.sub(r'[^\w\s\-]', '', cat.strip())
        #         # Remove extra whitespace
        #         clean_cat = re.sub(r'\s+', ' ', clean_cat).strip()
                
        #         # Only add if not empty and not already seen (case-insensitive)
        #         if clean_cat and clean_cat.lower() not in seen_categories:
        #             cleaned_categories.append(clean_cat)
        #             seen_categories.add(clean_cat.lower())
            # categories = ', '.join(cleaned_categories)
        
        # Determine published status
        published_val = row.get('Published', 1)
        published = 'TRUE' if published_val != -1 else 'FALSE'
        status = 'active' if published == 'TRUE' else 'archived'
        
        # Process description - remove all line feeds, carriage returns, and other whitespace characters
        description = ''
        if pd.notna(row['Description']):
            # Convert to string and remove all types of line breaks
            desc_str = str(row['Description'])
            # Remove literal \n strings, actual newlines, carriage returns, and other line break characters
            description = re.sub(r'\\n|\n|\r|\x0b|\x0c|\x85|\u2028|\u2029', '', desc_str)
        
        # Handle pricing logic with safe access
        # In WooCommerce: Sale price is the discounted price, Regular price is the original price
        # In Shopify: Variant Price is the selling price, Compare At Price is the original price
        sale_price = row.get('Sale price', '')
        regular_price = row.get('Regular price', '')
        
        # Convert empty strings to None for proper handling
        sale_price = sale_price if pd.notna(sale_price) and str(sale_price).strip() != '' else None
        regular_price = regular_price if pd.notna(regular_price) and str(regular_price).strip() != '' else None
        
        # Determine variant price (use sale price if available, otherwise regular price)
        variant_price = sale_price if sale_price is not None else regular_price
        variant_price = variant_price if variant_price is not None else 0
        
        # Compare at price (original price when on sale)
        compare_at_price = regular_price if sale_price is not None and regular_price is not None and sale_price != regular_price else None
        compare_at_price = compare_at_price if compare_at_price is not None else ''
        
        # Safely get other fields
        stock_qty = row.get('Stock', 0)
        stock_qty = stock_qty if pd.notna(stock_qty) and str(stock_qty).strip() != '' else 0
        in_stock = row.get('In stock?', True)
        
        # Main product row with safe access
        new_row = {
            'Handle': handle,
            'Title': product_name,
            'Body (HTML)': description,
            'Vendor': '', # Don't touch this line
            'Product Category': '', # don't touch this line
            'Type': '', # Don't touch this line
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
            'Google Shopping / MPN': '', # Don't touch this line
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
            'Status': status
        }
        
        shopify_df = pd.concat([shopify_df, pd.DataFrame([new_row])], ignore_index=True)
        
        # Add additional rows for extra images
        for i, image in enumerate(images[1:], 2):
            image_row = {col: '' for col in shopify_columns}
            image_row['Handle'] = handle
            image_row['Image Src'] = image
            image_row['Image Position'] = str(i)
            image_row['Image Alt Text'] = product_name
            
            shopify_df = pd.concat([shopify_df, pd.DataFrame([image_row])], ignore_index=True)
    
    # Clean up data types to prevent conversion errors
    # Convert numeric columns, replacing empty strings with proper values
    numeric_columns = ['Variant Price', 'Variant Compare At Price', 'Variant Grams', 'Variant Inventory Qty']
    
    for col in numeric_columns:
        if col in shopify_df.columns:
            # Replace empty strings and None values with 0 for numeric columns
            shopify_df[col] = shopify_df[col].apply(lambda x: 0 if pd.isna(x) or x == '' or x is None else x)
            # Convert to numeric, coercing errors to 0
            shopify_df[col] = pd.to_numeric(shopify_df[col], errors='coerce').fillna(0)
    
    # Handle Compare At Price specially - it can be empty
    if 'Variant Compare At Price' in shopify_df.columns:
        shopify_df['Variant Compare At Price'] = shopify_df['Variant Compare At Price'].apply(
            lambda x: '' if pd.isna(x) or x == 0 or x == '0' else str(x)
        )
    
    return shopify_df

# Streamlit App
st.set_page_config(
    page_title="WooCommerce to Shopify Transformer",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 WooCommerce to Shopify Transformer")
st.markdown("Transform your WooCommerce product export into Shopify import format")

# Sidebar with instructions
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
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
    """)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Upload WooCommerce CSV")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type="csv",
        help="Upload your WooCommerce product export CSV file"
    )

with col2:
    if uploaded_file:
        st.header("File Info")
        st.info(f"**Filename:** {uploaded_file.name}")
        st.info(f"**Size:** {uploaded_file.size:,} bytes")

if uploaded_file is not None:
    try:
        # Read the uploaded file
        df = pd.read_csv(uploaded_file)
        
        st.success(f"✅ Successfully loaded {len(df)} products!")
        
        # Show preview of original data
        with st.expander("🔍 Preview Original Data", expanded=False):
            st.dataframe(df.head(), use_container_width=True)
        
        # Transform the data
        with st.spinner("🔄 Transforming data..."):
            transformed_df = transform_wc_to_shopify_streamlit(df)
        
        st.success(f"✅ Transformation complete! Generated {len(transformed_df)} rows for Shopify import.")
        
        # Show preview of transformed data
        with st.expander("👀 Preview Transformed Data", expanded=True):
            st.dataframe(transformed_df.head(10), use_container_width=True)
        
        # Generate download filename with timestamp
        current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        download_filename = f"shopify_transformed_{current_datetime}.csv"
        
        # Convert DataFrame to CSV for download
        csv_buffer = io.StringIO()
        transformed_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        # Download button
        st.download_button(
            label="📥 Download Shopify CSV",
            data=csv_data,
            file_name=download_filename,
            mime="text/csv",
            type="primary",
            help="Download the transformed CSV file ready for Shopify import"
        )
        
        # Show some stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Original Products", len(df))
        with col2:
            st.metric("Shopify Rows", len(transformed_df))
        with col3:
            products_with_images = len([row for _, row in transformed_df.iterrows() if row['Image Src']])
            st.metric("Products with Images", products_with_images)
        with col4:
            active_products = len([row for _, row in transformed_df.iterrows() if row['Status'] == 'active'])
            st.metric("Active Products", active_products)
            
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.error("Please make sure your CSV file has the expected WooCommerce export format.")

else:
    st.info("👆 Please upload a WooCommerce CSV export file to get started!")
    
    # Show sample data format
    with st.expander("📄 Expected CSV Format", expanded=False):
        st.markdown("""
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
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Made for Card Giants • Transform with confidence 🚀"
    "</div>", 
    unsafe_allow_html=True
)