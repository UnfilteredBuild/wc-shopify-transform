"""
Utility functions for the WooCommerce to Shopify transformer.
"""

import streamlit as st
import pandas as pd
import io
from datetime import datetime
from version import version_manager
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
        
        # Version management section (admin)
        st.markdown("---")
        display_version_management()


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
    """Display the main app header with version."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(title)
        st.markdown(subtitle)
    with col2:
        version_info = version_manager.get_version_info()
        version_string = version_manager.get_version_string()
        st.markdown(
            f"<div style='text-align: right; margin-top: 20px;'>"
            f"<span style='color: #666; font-size: 14px;'>{version_string}</span><br>"
            f"<span style='color: #999; font-size: 12px;'>Updated: {version_info['last_updated'][:10]}</span>"
            f"</div>",
            unsafe_allow_html=True
        )


def display_footer() -> None:
    """Display the app footer with version info."""
    st.markdown("---")
    version_info = version_manager.get_version_info()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            "<div style='text-align: center; color: #666;'>"
            "Made for Card Giants • Transform with confidence 🚀<br>"
            f"<small style='color: #999;'>{version_manager.get_version_string()} • {version_info.get('release_notes', 'No release notes')}</small>"
            "</div>",
            unsafe_allow_html=True
        )


def display_version_management() -> None:
    """Display version management section in sidebar."""
    with st.expander("🏷️ Version Control", expanded=False):
        version_info = version_manager.get_version_info()
        current_version = version_manager.get_version_string()
        
        st.markdown(f"**Current:** {current_version}")
        st.markdown(f"**Updated:** {version_info['last_updated'][:16].replace('T', ' ')}")
        
        # Version increment buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Patch 🐛", help="Bug fixes, small improvements"):
                version_manager.increment_patch("Bug fixes and improvements")
                st.success(f"Updated to {version_manager.get_version_string()}")
                st.rerun()
            
            if st.button("Major 🎉", help="Breaking changes, major features"):
                version_manager.increment_major("Major version release")
                st.success(f"Updated to {version_manager.get_version_string()}")
                st.rerun()
        
        with col2:
            if st.button("Minor ✨", help="New features, enhancements"):
                version_manager.increment_minor("New features and enhancements")
                st.success(f"Updated to {version_manager.get_version_string()}")
                st.rerun()
            
            if st.button("Build 🔧", help="Internal builds"):
                version_manager.increment_build()
                st.success(f"Updated to {version_manager.get_version_string()}")
                st.rerun()
        
        # Custom release notes
        release_notes = st.text_area("Release Notes", 
                                   value=version_info.get('release_notes', ''), 
                                   height=50,
                                   help="Add custom release notes")
        
        if st.button("Update Notes 📝"):
            version_info['release_notes'] = release_notes
            version_manager._save_version(version_info)
            st.success("Release notes updated!")
            st.rerun()