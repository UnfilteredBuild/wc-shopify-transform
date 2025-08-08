"""
Streamlit app for transforming WooCommerce product exports to Shopify import format.
"""

import streamlit as st
import pandas as pd

from config import APP_CONFIG, USER_INSTRUCTIONS, EXPECTED_CSV_FORMAT
from transformer import WooCommerceToShopifyTransformer
from utils import (
    setup_page_config, display_app_header, create_sidebar_instructions,
    display_file_info, display_preview_section, display_success_message,
    display_error_message, display_transformation_stats, generate_download_filename,
    dataframe_to_csv_string, display_csv_format_help, display_footer
)


def main():
    """Main application function."""
    # Setup page configuration
    setup_page_config(
        APP_CONFIG['page_title'],
        APP_CONFIG['page_icon'],
        APP_CONFIG['layout']
    )
    
    # Display header
    display_app_header(
        APP_CONFIG['page_title'],
        "Transform your WooCommerce product export into Shopify import format"
    )
    
    # Create sidebar with instructions
    create_sidebar_instructions(USER_INSTRUCTIONS)
    
    # Main content layout
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
            display_file_info(uploaded_file)
    
    # Process uploaded file
    if uploaded_file is not None:
        process_uploaded_file(uploaded_file)
    else:
        display_upload_help()
    
    # Display footer
    display_footer()


def process_uploaded_file(uploaded_file):
    """Process the uploaded CSV file."""
    try:
        # Read the uploaded file
        df = pd.read_csv(uploaded_file)
        display_success_message(f"Successfully loaded {len(df)} products!")
        
        # Show preview of original data
        display_preview_section(df, "🔍 Preview Original Data", expanded=False)
        
        # Transform the data
        with st.spinner("🔄 Transforming data..."):
            transformer = WooCommerceToShopifyTransformer()
            transformed_df = transformer.transform(df)
        
        display_success_message(f"Transformation complete! Generated {len(transformed_df)} rows for Shopify import.")
        
        # Show preview of transformed data
        display_preview_section(transformed_df, "👀 Preview Transformed Data", expanded=True)
        
        # Create download section
        create_download_section(transformed_df)
        
        # Show transformation statistics
        display_transformation_stats(df, transformed_df)
        
    except Exception as e:
        display_error_message(e)


def create_download_section(transformed_df: pd.DataFrame):
    """Create the download section with CSV download button."""
    download_filename = generate_download_filename()
    csv_data = dataframe_to_csv_string(transformed_df)
    
    st.download_button(
        label="📥 Download Shopify CSV",
        data=csv_data,
        file_name=download_filename,
        mime="text/csv",
        type="primary",
        help="Download the transformed CSV file ready for Shopify import"
    )


def display_upload_help():
    """Display help information when no file is uploaded."""
    st.info("👆 Please upload a WooCommerce CSV export file to get started!")
    display_csv_format_help(EXPECTED_CSV_FORMAT)


if __name__ == "__main__":
    main()