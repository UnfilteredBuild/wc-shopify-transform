"""
Version management for the WooCommerce to Shopify Transformer application.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

# Version file path
VERSION_FILE = os.path.join(os.path.dirname(__file__), '..', 'version.json')

# Default version structure
DEFAULT_VERSION = {
    "major": 1,
    "minor": 0,
    "patch": 0,
    "build": 0,
    "last_updated": datetime.now().isoformat(),
    "release_notes": "Initial version"
}


class VersionManager:
    """Manages application version information."""
    
    def __init__(self):
        self.version_data = self._load_version()
    
    def _load_version(self) -> Dict[str, Any]:
        """Load version data from file, create if doesn't exist."""
        try:
            if os.path.exists(VERSION_FILE):
                with open(VERSION_FILE, 'r') as f:
                    return json.load(f)
            else:
                # Create default version file
                self._save_version(DEFAULT_VERSION)
                return DEFAULT_VERSION.copy()
        except (json.JSONDecodeError, IOError):
            return DEFAULT_VERSION.copy()
    
    def _save_version(self, version_data: Dict[str, Any]) -> None:
        """Save version data to file."""
        try:
            with open(VERSION_FILE, 'w') as f:
                json.dump(version_data, f, indent=2)
        except IOError:
            pass  # Silently fail if can't save
    
    def get_version_string(self) -> str:
        """Get formatted version string."""
        return f"v{self.version_data['major']}.{self.version_data['minor']}.{self.version_data['patch']}.{self.version_data['build']}"
    
    def get_version_info(self) -> Dict[str, Any]:
        """Get complete version information."""
        return self.version_data.copy()
    
    def increment_patch(self, release_notes: str = "") -> str:
        """Increment patch version."""
        self.version_data['patch'] += 1
        self.version_data['last_updated'] = datetime.now().isoformat()
        if release_notes:
            self.version_data['release_notes'] = release_notes
        self._save_version(self.version_data)
        return self.get_version_string()
    
    def increment_minor(self, release_notes: str = "") -> str:
        """Increment minor version and reset patch."""
        self.version_data['minor'] += 1
        self.version_data['patch'] = 0
        self.version_data['last_updated'] = datetime.now().isoformat()
        if release_notes:
            self.version_data['release_notes'] = release_notes
        self._save_version(self.version_data)
        return self.get_version_string()
    
    def increment_major(self, release_notes: str = "") -> str:
        """Increment major version and reset minor and patch."""
        self.version_data['major'] += 1
        self.version_data['minor'] = 0
        self.version_data['patch'] = 0
        self.version_data['last_updated'] = datetime.now().isoformat()
        if release_notes:
            self.version_data['release_notes'] = release_notes
        self._save_version(self.version_data)
        return self.get_version_string()
    
    def increment_build(self) -> str:
        """Increment build number."""
        self.version_data['build'] += 1
        self.version_data['last_updated'] = datetime.now().isoformat()
        self._save_version(self.version_data)
        return self.get_version_string()


# Global version manager instance
version_manager = VersionManager()