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

## Version Management

This project includes an automated version management system that displays the current version in the UI and allows for easy version increments when releasing updates.

### Version Display
- The current version appears in the top-right corner of the Streamlit UI
- The version and release notes are also shown in the footer
- Version information includes the version number and last update date

### Incrementing Versions

#### Using the Command Line Script
Use the `increment_version.py` script to bump versions:

```bash
# Show current version
python increment_version.py --show

# Increment patch version (bug fixes)
python increment_version.py patch -m "Fixed weight conversion precision"

# Increment minor version (new features)
python increment_version.py minor -m "Added CSV validation and better error handling"

# Increment major version (breaking changes)
python increment_version.py major -m "Complete UI redesign and new transformation engine"

# Increment build number (internal builds)
python increment_version.py build
```

#### Using the UI (Admin Section)
The Streamlit app includes a "Version Control" section in the sidebar:
1. Expand the "🏷️ Version Control" section in the sidebar
2. Click the appropriate button:
   - **Patch 🐛** - Bug fixes and small improvements
   - **Minor ✨** - New features and enhancements
   - **Major 🎉** - Breaking changes and major releases
   - **Build 🔧** - Internal builds
3. Update release notes in the text area if needed
4. Click "Update Notes 📝" to save custom release notes

### Version Format
Versions follow semantic versioning: `v{major}.{minor}.{patch}.{build}`
- **Major**: Breaking changes, significant redesigns
- **Minor**: New features, backward-compatible changes
- **Patch**: Bug fixes, small improvements
- **Build**: Internal builds, development versions

### Version Storage
Version information is stored in `version.json` in the project root and is automatically created on first run.