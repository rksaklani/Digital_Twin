"""
Utility functions for the Digital Twin project.
"""

import os
from pathlib import Path
from typing import Union


def get_project_root() -> Path:
    """Get the project root directory.
    
    Assumes this file is in services/ directory, so project root is parent.
    """
    # Get the directory where this file is located
    current_file = Path(__file__).resolve()
    # Go up from services/ to project root
    project_root = current_file.parent.parent
    return project_root


def resolve_path(path: Union[str, Path], base: Path = None) -> Path:
    """Resolve a path relative to project root.
    
    Args:
        path: Path string (can be relative or absolute)
        base: Base directory to resolve from (defaults to project root)
    
    Returns:
        Resolved Path object
    """
    if base is None:
        base = get_project_root()
    
    path_obj = Path(path)
    
    # If absolute path, return as-is
    if path_obj.is_absolute():
        return path_obj
    
    # Resolve relative to base
    return (base / path_obj).resolve()


def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
    
    Returns:
        Path object of the directory
    """
    path_obj = resolve_path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def ensure_file_dir(file_path: Union[str, Path]) -> Path:
    """Ensure the parent directory of a file exists.
    
    Args:
        file_path: File path
    
    Returns:
        Path object of the file
    """
    file_path_obj = resolve_path(file_path)
    file_path_obj.parent.mkdir(parents=True, exist_ok=True)
    return file_path_obj
