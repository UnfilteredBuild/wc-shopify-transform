#!/usr/bin/env python3
"""
Version increment script for WooCommerce to Shopify Transformer.
Run this script when you want to release a new version.
"""

import sys
import os
import argparse

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from version import version_manager


def main():
    """Main function to handle version increments."""
    parser = argparse.ArgumentParser(description='Increment application version')
    parser.add_argument('type', nargs='?', choices=['major', 'minor', 'patch', 'build'], 
                       help='Type of version increment')
    parser.add_argument('-m', '--message', type=str, default='', 
                       help='Release notes message')
    parser.add_argument('--show', action='store_true', 
                       help='Show current version without incrementing')
    
    args = parser.parse_args()
    
    if args.show:
        version_info = version_manager.get_version_info()
        print(f"Current version: {version_manager.get_version_string()}")
        print(f"Last updated: {version_info['last_updated']}")
        print(f"Release notes: {version_info.get('release_notes', 'No release notes')}")
        return
    
    if not args.type:
        parser.error("Version type is required when not using --show")
        return
    
    # Increment version based on type
    if args.type == 'major':
        new_version = version_manager.increment_major(args.message)
        print(f"🎉 Major version incremented to {new_version}")
    elif args.type == 'minor':
        new_version = version_manager.increment_minor(args.message)
        print(f"✨ Minor version incremented to {new_version}")
    elif args.type == 'patch':
        new_version = version_manager.increment_patch(args.message)
        print(f"🐛 Patch version incremented to {new_version}")
    elif args.type == 'build':
        new_version = version_manager.increment_build()
        print(f"🔧 Build number incremented to {new_version}")
    
    if args.message:
        print(f"Release notes: {args.message}")
    
    print("\n💡 Tip: Restart the Streamlit app to see the new version in the UI!")


if __name__ == '__main__':
    main()