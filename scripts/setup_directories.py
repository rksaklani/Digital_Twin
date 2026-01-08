#!/usr/bin/env python3
"""
Setup script to create and validate directory structure.
"""

import sys
from pathlib import Path

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.utils import get_project_root, ensure_dir


def setup_directories():
    """Create all required directories if they don't exist."""
    project_root = get_project_root()
    
    directories = [
        "data/audio/raw",
        "data/audio/clean",
        "data/video",
        "models",
        "logs",
        "tmp",
    ]
    
    print("Setting up directory structure...")
    print(f"Project root: {project_root}\n")
    
    for dir_path in directories:
        full_path = ensure_dir(dir_path)
        print(f"[OK] {dir_path}/")
        
        # Create .gitkeep file if it doesn't exist
        gitkeep = full_path / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()
            print(f"   Created .gitkeep")
    
    print("\n[OK] Directory structure setup complete!")
    print("\nNext steps:")
    print("1. Place reference.wav in data/audio/clean/")
    print("2. Place face_source.mp4 in data/video/")
    print("3. Download models to models/ directory")
    print("4. See docs/directory_usage.md for details")


if __name__ == "__main__":
    setup_directories()
