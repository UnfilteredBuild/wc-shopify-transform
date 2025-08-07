import streamlit as st
import pandas as pd
import re
from datetime import datetime
import io

def transform_wc_to_shopify_streamlit(df):
    """
    Transform WooCommerce export DataFrame to Shopify import format
    """
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
        # Create handle from product name (URL-friendly)
        handle = re.sub(r'[^\w\s-]', '', str(row['Name'])).strip()
        handle = re.sub(r'[-\s]+', '-', handle).lower()
        
        # Extract images and create multiple rows if needed
        images = []
        if pd.notna(row['Images']) and row['Images']:
            images = [img.strip() for img in str(row['Images']).split(',')]
        
        # Convert weight from lbs to grams
        weight_grams = 0
        if pd.notna(row['Weight (lbs)']) and row['Weight (lbs)']:
            weight_grams = int(float(row['Weight (lbs)']) * 453.592)
        
        # Convert tags
        tags = ""
        if pd.notna(row['Tags']) and row['Tags']:
            tag_list = [tag.strip().replace('#', '') for tag in str(row['Tags']).split(',')]
            tags = ', '.join(tag_list)
        
        # Determine published status
        published = 'TRUE' if row['Published'] != -1 else 'FALSE'
        status = 'active' if published == 'TRUE' else 'archived'
        
        # Process description - remove all line feeds, carriage returns, and other whitespace characters
        description = ''
        if pd.notna(row['Description']):
            # Convert to string and remove all types of line breaks
            desc_str = str(row['Description'])
            # Remove literal \n strings, actual newlines, carriage returns, and other line break characters
            description = re.sub(r'\\n|\n|\r|\x0b|\x0c|\x85|\u2028|\u2029', '', desc_str)
        
        # Handle pricing logic
        # In WooCommerce: Sale price is the discounted price, Regular price is the original price
        # In Shopify: Variant Price is the selling price, Compare At Price is the original price
        variant_price = row['Sale price'] if pd.notna(row['Sale price']) and row['Sale price'] else row['Regular price']
        compare_at_price = row['Regular price'] if pd.notna(row['Sale price']) and row['Sale price'] and row['Sale price'] != row['Regular price'] else ''
        
        # Main product row
        new_row = {
            'Handle': handle,
            'Title': row['Name'],
            'Body (HTML)': description,
            'Vendor': '', # Don't touch this line
            'Product Category': row['Categories'] if pd.notna(row['Categories']) else '',
            'Type': '', # Don't touch this line
            'Tags': tags,
            'Published': published,
            'Option1 Name': '',
            'Option1 Value': '',
            'Option2 Name': '',
            'Option2 Value': '',
            'Option3 Name': '',
            'Option3 Value': '',
            'Variant SKU': row['SKU'],
            'Variant Grams': weight_grams,
            'Variant Inventory Tracker': 'shopify',
            'Variant Inventory Qty': row['Stock'] if pd.notna(row['Stock']) and row['In stock?'] else 0,
            'Variant Inventory Policy': 'deny',
            'Variant Fulfillment Service': 'manual',
            'Variant Price': variant_price if pd.notna(variant_price) else 0,
            'Variant Compare At Price': compare_at_price,
            'Variant Requires Shipping': 'TRUE',
            'Variant Taxable': 'TRUE' if row['Tax status'] == 'taxable' else 'FALSE',
            'Variant Barcode': '',
            'Image Src': images[0] if images else '',
            'Image Position': '1' if images else '',
            'Image Alt Text': row['Name'] if images else '',
            'Gift Card': 'FALSE',
            'SEO Title': row['Name'],
            'SEO Description': row['Short description'] if pd.notna(row['Short description']) else '',
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
            image_row['Image Alt Text'] = row['Name']
            
            shopify_df = pd.concat([shopify_df, pd.DataFrame([image_row])], ignore_index=True)
    
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
            # Show key columns for preview
            preview_cols = ['Handle', 'Title', 'Variant SKU', 'Variant Price', 'Tags', 'Image Src']
            available_cols = [col for col in preview_cols if col in transformed_df.columns]
            st.dataframe(transformed_df[available_cols].head(10), use_container_width=True)
        
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