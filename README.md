# WooCommerce to Shopify Transform

## Overview
This project provides a Jupyter notebook-based environment for transforming WooCommerce product export data into Shopify import format. Designed specifically for Card Giants' product migration needs, it handles the conversion of trading card product data from WooCommerce CSV exports to Shopify-compatible import files.

## Project Structure
- **`shopify_scripts.ipynb`** - Main development notebook containing the transformation logic
- **`inputs/`** - Directory containing WooCommerce export CSV files
- **`outputs/`** - Directory where transformed Shopify import files are saved
- **`CLAUDE.md`** - Project instructions and development guidance

## Features
- **Automated Data Transformation**: Converts WooCommerce product data to Shopify format
- **Dynamic File Naming**: Generates timestamped output files to prevent overwrites
- **Product Handle Generation**: Creates URL-friendly product handles from names
- **Image Management**: Handles multiple product images with proper positioning
- **Price Conversion**: Properly maps WooCommerce sale/regular prices to Shopify pricing structure
- **Tag Processing**: Converts and cleans product tags
- **Weight Conversion**: Converts weights from pounds to grams
- **Description Cleaning**: Removes line feeds and formatting issues from product descriptions

## Usage
1. Place your WooCommerce export CSV file in the `inputs/` directory
2. Open `shopify_scripts.ipynb` in Jupyter
3. Run all cells to execute the transformation
4. Find your transformed Shopify import file in the `outputs/` directory

## Output Format
The transformation creates CSV files compatible with Shopify's product import format, including all necessary fields for:
- Product information (title, description, handle)
- Variants and pricing
- Inventory tracking
- Images and SEO data
- Publishing status and categorization

## Data Source
The project is designed to work with WooCommerce product exports containing trading card data, including product IDs, SKUs, names, descriptions, pricing, categories, and metadata.