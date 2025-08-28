"""
Streamlit app for transforming WooCommerce product exports to Shopify import format.
"""

import streamlit as st
import pandas as pd

from config import APP_CONFIG, USER_INSTRUCTIONS, CUSTOMER_INSTRUCTIONS, EXPECTED_CSV_FORMAT
from transformer import WooCommerceToShopifyTransformer
from customer_transformer import CustomerToShopifyTransformer
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
    
    # Initialize session state for import type
    if 'import_type' not in st.session_state:
        st.session_state.import_type = None
    
    # Display header
    display_app_header(
        APP_CONFIG['page_title'],
        "Transform your data for Shopify import"
    )
    
    # Show import type selection or the selected import interface
    if st.session_state.import_type is None:
        show_import_type_selection()
    elif st.session_state.import_type == 'products':
        show_product_import_interface()
    elif st.session_state.import_type == 'customers':
        show_customer_import_interface()
    
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


def show_import_type_selection():
    """Display the import type selection interface."""
    st.markdown("### Choose Import Type")
    st.markdown("Select the type of data you want to transform for Shopify:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            "🛍️ Product Import",
            help="Transform WooCommerce product export to Shopify format",
            use_container_width=True,
            type="primary"
        ):
            st.session_state.import_type = 'products'
            st.rerun()
    
    with col2:
        if st.button(
            "👥 Customer Import", 
            help="Transform customer data to Shopify format",
            use_container_width=True,
            type="primary"
        ):
            st.session_state.import_type = 'customers'
            st.rerun()


def show_product_import_interface():
    """Display the product import interface."""
    # Back button
    if st.button("← Back to Import Type Selection"):
        st.session_state.import_type = None
        st.rerun()
    
    st.header("Product Import")
    st.markdown("Transform your WooCommerce product export into Shopify import format")
    
    # Create sidebar with instructions
    create_sidebar_instructions(USER_INSTRUCTIONS)
    
    # Main content layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Upload WooCommerce CSV")
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            help="Upload your WooCommerce product export CSV file",
            key="product_uploader"
        )
    
    with col2:
        if uploaded_file:
            display_file_info(uploaded_file)
    
    # Process uploaded file
    if uploaded_file is not None:
        process_uploaded_file(uploaded_file)
    else:
        display_upload_help()


def show_customer_import_interface():
    """Display the customer import interface."""
    # Back button
    if st.button("← Back to Import Type Selection"):
        st.session_state.import_type = None
        st.rerun()
    
    st.header("Customer Import")
    st.markdown("Transform your customer data into Shopify import format")
    
    # Create sidebar with customer-specific instructions
    create_sidebar_instructions(CUSTOMER_INSTRUCTIONS)
    
    # Main content layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Upload Customer CSV")
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            help="Upload your customer data CSV file",
            key="customer_uploader"
        )
    
    with col2:
        if uploaded_file:
            display_file_info(uploaded_file)
    
    # Process uploaded file
    if uploaded_file is not None:
        process_customer_file(uploaded_file)
    else:
        display_customer_upload_help()


def process_customer_file(uploaded_file):
    """Process the uploaded customer CSV file."""
    try:
        # Read the uploaded file, preserving leading zeros in string fields
        string_columns = [
            'Default Address Zip', 'Phone', 'Default Address Province Code',
            'Default Address Country Code'
        ]
        dtype_dict = {}
        temp_df = pd.read_csv(uploaded_file, nrows=0)
        for col in string_columns:
            if col in temp_df.columns:
                dtype_dict[col] = str
        
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, dtype=dtype_dict)
        display_success_message(f"Successfully loaded {len(df)} customers!")
        
        display_preview_section(df, "🔍 Preview Original Customer Data", expanded=False)
        
        transformer = CustomerToShopifyTransformer()
        validation_result = transformer.validate_dataframe(df)
        
        if validation_result['valid']:
            display_success_message("Customer data validation passed!")
            with st.spinner("🔄 Transforming customer data..."):
                transformed_df = transformer.transform(df)
            display_success_message(f"Transformation complete! Generated {len(transformed_df)} rows for Shopify import.")
            display_preview_section(transformed_df, "👀 Preview Transformed Customer Data", expanded=True)
            create_customer_download_section(transformed_df)
        else:
            st.error("🚫 Customer data validation failed!")
            for error in validation_result['errors']:
                st.warning(error)

            has_fixable_zips = any('4-digit US zip codes' in error for error in validation_result['errors'])

            if has_fixable_zips:
                st.markdown("---")
                if st.button("🔧 Fix 4-digit Zip Codes", type="primary", use_container_width=True):
                    fixed_df = transformer.fix_4digit_zip_codes(df)
                    st.session_state.fixed_df = fixed_df
                    st.success("Zip codes fixed. Re-validating...")
                    
                    new_validation_result = transformer.validate_dataframe(fixed_df)
                    if new_validation_result['valid']:
                        st.success("✅ All validation errors resolved!")
                        with st.spinner("🔄 Transforming customer data..."):
                            transformed_df = transformer.transform(fixed_df)
                        display_preview_section(transformed_df, "👀 Preview Transformed Customer Data", expanded=True)
                        create_customer_download_section(transformed_df)
                    else:
                        st.error("❌ Some validation errors remain after fixing zip codes:")
                        for error in new_validation_result['errors']:
                            st.warning(error)

                if st.button("⏭️ Bypass Fixes and Download", use_container_width=True):
                    bypass_and_download(df, transformer)

            elif check_for_bypassable_errors(validation_result['errors']):
                 if st.button("⏭️ Bypass Fixes and Download", use_container_width=True):
                        bypass_and_download(df, transformer)
            else:
                st.warning("⚠️ Please fix the validation errors above before proceeding.")

    except Exception as e:
        display_error_message(e)

def bypass_and_download(df, transformer):
    """Fix 4-digit zips and download the CSV."""
    with st.spinner("🔧 Fixing 4-digit zip codes..."):
        fixed_df = transformer.fix_4digit_zip_codes(df)
    
    with st.spinner("🔄 Transforming customer data..."):
        transformed_df = transformer.transform(fixed_df)

    st.success(f"✅ Transformation complete! Generated {len(transformed_df)} rows for Shopify import.")
    st.warning("⚠️ Note: Some US addresses may have non-standard state codes that will need manual review in Shopify.")
    
    display_preview_section(transformed_df, "👀 Preview Transformed Customer Data", expanded=True)
    create_customer_download_section(transformed_df)












def create_customer_download_section(transformed_df: pd.DataFrame):
    """Create the download section for customer CSV."""
    download_filename = f"shopify_customers_{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    csv_data = dataframe_to_csv_string(transformed_df)
    
    st.download_button(
        label="📥 Download Shopify Customer CSV",
        data=csv_data,
        file_name=download_filename,
        mime="text/csv",
        type="primary",
        help="Download the transformed customer CSV file ready for Shopify import"
    )


def display_customer_upload_help():
    """Display help information for customer upload."""
    st.info("👆 Please upload a customer CSV file to get started!")
    
    st.markdown("**Expected Customer CSV Format:**")
    expected_format = [
        'First Name', 'Last Name', 'Email', 'Accepts Email Marketing',
        'Default Address Company', 'Default Address Address1', 'Default Address Address2',
        'Default Address City', 'Default Address Province Code', 'Default Address Country Code',
        'Default Address Zip', 'Phone', 'Role'
    ]
    
    st.code(', '.join(expected_format))


def display_upload_help():
    """Display help information when no file is uploaded."""
    st.info("👆 Please upload a WooCommerce CSV export file to get started!")
    display_csv_format_help(EXPECTED_CSV_FORMAT)


if __name__ == "__main__":
    main()