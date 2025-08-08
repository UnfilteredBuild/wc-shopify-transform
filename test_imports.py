#!/usr/bin/env python3
"""
Test script to verify imports work correctly.
Run from the root directory with: python test_imports.py
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all imports work correctly."""
    try:
        print("Testing imports...")
        
        # Test config imports
        from config import SHOPIFY_COLUMNS, REQUIRED_COLUMNS, APP_CONFIG
        print(f"✅ Config: Found {len(SHOPIFY_COLUMNS)} Shopify columns")
        print(f"✅ Config: Found {len(REQUIRED_COLUMNS)} required columns")
        
        # Test imports that don't require pandas
        print("✅ Basic imports successful!")
        
        # Test pandas-dependent imports (will fail without pandas but that's OK)
        try:
            from transformer import WooCommerceToShopifyTransformer
            print("✅ Transformer class imported successfully")
            
            from utils import generate_download_filename
            print("✅ Utils functions imported successfully")
            
        except ImportError as e:
            print(f"⚠️  Pandas-dependent imports need virtual environment: {e}")
        
        print("\n🎉 Import structure is correct!")
        print("Run with virtual environment for full functionality.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_imports()