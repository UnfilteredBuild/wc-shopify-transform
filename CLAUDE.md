# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Shopify scripts development environment for Card Giants, focused on creating and testing Shopify automation scripts. The repository contains a Jupyter notebook-based development workflow and supporting data files.

## Development Environment

- **Primary Development**: Use `shopify_scripts.ipynb` Jupyter notebook for script development and testing
- **Data Source**: `wc_export.csv` contains WooCommerce product export data (likely for migration/import scripts)

## Common Commands

Since this is a Jupyter notebook-based project, use the built-in notebook execution environment:
- Execute cells individually using Shift+Enter in the notebook
- For Python dependencies, install via: `pip install [package-name]` in a notebook cell
- To run the full notebook: "Run All" from the notebook interface

## Architecture

This is a lightweight development setup with:
- **shopify_scripts.ipynb**: Main development notebook for Shopify script prototyping and testing
- **wc_export.csv**: Product data export (CSV format) containing WooCommerce product information including IDs, SKUs, names, descriptions, pricing, categories, and metadata

The notebook is structured for iterative development of Shopify automation scripts, likely for:
- Product data migration from WooCommerce to Shopify
- Bulk product operations
- Shopify API integrations

## Data Context

The CSV file contains trading card product data with fields for:
- Product identification (ID, SKU, GTIN)
- Product details (name, description, pricing)
- Inventory management (stock, weight, dimensions)
- Categorization and tagging
- Image URLs and cross-selling relationships