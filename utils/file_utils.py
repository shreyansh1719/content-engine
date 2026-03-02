"""
Utility functions for file handling and module integration
"""

import os
import importlib.util
import sys
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

def get_module_path(module_name: str) -> Optional[str]:
    """
    Get the file path of a module.
    
    Args:
        module_name: Name of the module
        
    Returns:
        Path to the module or None if not found
    """
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is not None and spec.origin is not None:
            return os.path.dirname(os.path.abspath(spec.origin))
        return None
    except (ImportError, AttributeError):
        return None

def import_module_from_path(module_name: str, module_path: str) -> Optional[Any]:
    """
    Import a module from a specific file path.
    
    Args:
        module_name: Name to assign to the module
        module_path: Path to the module file
        
    Returns:
        Imported module or None if import fails
    """
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None:
            return None
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Error importing module {module_name} from {module_path}: {e}")
        return None

def ensure_module_directory_in_path(directory: str) -> None:
    """
    Ensure that a directory is in the Python module search path.
    
    Args:
        directory: Directory to add to path
    """
    abs_directory = os.path.abspath(directory)
    if abs_directory not in sys.path:
        sys.path.insert(0, abs_directory)
        logger.info(f"Added {abs_directory} to Python path")

def find_file_in_project(filename: str, start_dir: Optional[str] = None) -> Optional[str]:
    """
    Find a file by recursively searching through the project directory.
    
    Args:
        filename: Name of the file to find
        start_dir: Directory to start search from (defaults to current directory)
        
    Returns:
        Full path to the file or None if not found
    """
    if start_dir is None:
        start_dir = os.getcwd()
    
    for root, _, files in os.walk(start_dir):
        if filename in files:
            return os.path.join(root, filename)
    
    return None

def ensure_file_importable(file_path: str, module_name: str) -> bool:
    """
    Ensure a Python file can be imported by adding its directory to sys.path if needed.
    
    Args:
        file_path: Path to the Python file
        module_name: Name of the module to import
        
    Returns:
        True if file can be imported, False otherwise
    """
    if not os.path.exists(file_path):
        logger.error(f"File {file_path} does not exist")
        return False
    
    # Add directory to path if needed
    directory = os.path.dirname(os.path.abspath(file_path))
    ensure_module_directory_in_path(directory)
    
    # Attempt to import
    try:
        import_module_from_path(module_name, file_path)
        return True
    except Exception as e:
        logger.error(f"Failed to import {module_name} from {file_path}: {e}")
        return False