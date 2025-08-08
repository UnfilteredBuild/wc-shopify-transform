"""
Utility functions for the WooCommerce to Shopify transformer.
"""

import streamlit as st
import pandas as pd
import io
from datetime import datetime
# from typing import Tuple  # Reserved for future use


def display_file_info(uploaded_file) -> None:
    """Display information about the uploaded file."""
    st.header("File Info")
    st.info(f"**Filename:** {uploaded_file.name}")
    st.info(f"**Size:** {uploaded_file.size:,} bytes")


def display_transformation_stats(original_df: pd.DataFrame, transformed_df: pd.DataFrame) -> None:
    """Display statistics about the transformation."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Original Products", len(original_df))
    
    with col2:
        st.metric("Shopify Rows", len(transformed_df))
    
    with col3:
        products_with_images = len([row for _, row in transformed_df.iterrows() if row['Image Src']])
        st.metric("Products with Images", products_with_images)
    
    with col4:
        active_products = len([row for _, row in transformed_df.iterrows() if row['Status'] == 'active'])
        st.metric("Active Products", active_products)


def generate_download_filename() -> str:
    """Generate a timestamped filename for the output CSV."""
    current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    return f"shopify_transformed_{current_datetime}.csv"


def dataframe_to_csv_string(df: pd.DataFrame) -> str:
    """Convert DataFrame to CSV string for download."""
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()


def display_preview_section(df: pd.DataFrame, title: str, expanded: bool = False) -> None:
    """Display a preview section for a DataFrame."""
    with st.expander(title, expanded=expanded):
        st.dataframe(df.head(10), use_container_width=True)


def display_error_message(error: Exception) -> None:
    """Display a formatted error message."""
    st.error(f"❌ Error processing file: {str(error)}")
    if "Missing required columns" in str(error):
        st.error("Please make sure your CSV file has the expected WooCommerce export format.")
    else:
        st.error("Please check your CSV file format and try again.")


def display_success_message(message: str) -> None:
    """Display a formatted success message."""
    st.success(f"✅ {message}")


def create_sidebar_instructions(instructions: str) -> None:
    """Create the sidebar with instructions."""
    with st.sidebar:
        st.header("📋 Instructions")
        st.markdown(instructions)


def display_csv_format_help(format_text: str) -> None:
    """Display help about expected CSV format."""
    with st.expander("📄 Expected CSV Format", expanded=False):
        st.markdown(format_text)


def setup_page_config(title: str, icon: str, layout: str) -> None:
    """Setup Streamlit page configuration."""
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout=layout
    )


def display_app_header(title: str, subtitle: str) -> None:
    """Display the main app header."""
    st.title(title)
    st.markdown(subtitle)


def display_footer() -> None:
    """Display the app footer."""
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Made for Card Giants • Transform with confidence 🚀"
        "</div>",
        unsafe_allow_html=True
    )