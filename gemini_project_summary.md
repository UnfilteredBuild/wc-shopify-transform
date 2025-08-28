### Project Overview

This project is a data transformation tool designed to convert WooCommerce product and customer data into a Shopify-compatible CSV format for easy import. It features a Streamlit web interface for user-friendly operation.

### Key Components and Files

*   **`src/app.py`**: The main entry point for the Streamlit application. It handles the UI, file uploads, and orchestrates the transformation process.
*   **`src/transformer.py`**: Contains the `WooCommerceToShopifyTransformer` class, which is responsible for the core logic of transforming product data.
*   **`src/customer_transformer.py`**: Contains the `CustomerToShopifyTransformer` class, which handles the transformation and validation of customer data.
*   **`src/utils.py`**: A collection of helper functions for the Streamlit UI, such as displaying headers, footers, file information, and handling data downloads.
*   **`src/config.py`**: Stores configuration constants, including required column names, Shopify column structure, and UI text.
*   **`src/version.py`**: Manages the application's versioning.
*   **`CLAUDE.md`**: Provides development guidance, primarily for a Jupyter Notebook-based workflow.
*   **`test_*.py`**: Pytest files for unit testing the transformers.

### Core Functionality

1.  **Data Transformation**:
    *   **Products**: Converts WooCommerce product CSVs to a Shopify-compliant format. This includes:
        *   Creating Shopify-compatible product handles.
        *   Converting weight from pounds to grams.
        *   Mapping pricing (regular and sale) to Shopify's format.
        *   Cleaning and formatting product descriptions.
        *   Handling multiple product images.
    *   **Customers**: Transforms customer CSVs, with a focus on data validation and cleaning. This includes:
        *   Validating and fixing US zip codes (e.g., adding leading zeros).
        *   Validating US state codes.
        *   Converting email marketing preferences.
        *   Creating customer tags based on their roles.

2.  **Streamlit UI**:
    *   Provides a user-friendly web interface for uploading CSV files.
    *   Displays data previews (original and transformed).
    *   Shows validation results and statistics.
    *   Allows users to download the transformed CSV files.
    *   Includes version management in the UI.

3.  **Versioning**:
    *   The application uses semantic versioning (`major.minor.patch.build`).
    *   The version can be incremented via a command-line script (`increment_version.py`) or through the Streamlit UI.
    *   Version information is stored in `version.json`.

### Development and Testing

*   The project was initially developed in a Jupyter Notebook (`notebooks/shopify_scripts_old.ipynb`) and later migrated to a Streamlit application.
*   The `test_` files indicate that the project uses `pytest` for unit testing the transformation logic.
