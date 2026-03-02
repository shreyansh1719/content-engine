# Utilities Module
"""
Utilities Module

This module provides common utility functions used across the video ad generation system.
It handles file operations, logging, encoding, and other shared functionality.
"""

import os
import logging
import json
import base64
import requests
from typing import Dict, Any, Optional
import time
from datetime import datetime

def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    Set up a logger with standardized formatting.
    
    Args:
        name: Name of the logger
        level: Logging level
        
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Check if logger already has handlers
    if not logger.handlers:
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add formatter to console handler
        console_handler.setFormatter(formatter)
        
        # Add console handler to logger
        logger.addHandler(console_handler)
        
        # Create file handler
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.FileHandler(f'logs/{name}_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        
        # Add file handler to logger
        logger.addHandler(file_handler)
    
    return logger

def load_config(config_path: str = 'config.json') -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
    """
    # Default configuration
    default_config = {
        'openai_api_key': os.environ.get('OPENAI_API_KEY', ''),
        'runway_api_key': os.environ.get('RUNWAY_API_KEY', ''),
        'output_dir': 'output',
        'brands': {}
    }
    
    try:
        # Check if config file exists
        if not os.path.exists(config_path):
            # Create default config file
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
        
        # Load config file
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update with environment variables if they exist
        if os.environ.get('OPENAI_API_KEY') and not config.get('openai_api_key'):
            config['openai_api_key'] = os.environ.get('OPENAI_API_KEY')
            
        if os.environ.get('RUNWAY_API_KEY') and not config.get('runway_api_key'):
            config['runway_api_key'] = os.environ.get('RUNWAY_API_KEY')
        
        return config
        
    except Exception as e:
        logger = setup_logger('utils')
        logger.error(f"Error loading configuration: {e}")
        
        # Return default config
        return default_config

def encode_image_to_base64(image_path: str) -> str:
    """
    Encode an image file to base64 string.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded string
    """
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def download_file(url: str, output_path: str) -> str:
    """
    Download a file from a URL to a local path.
    
    Args:
        url: URL of the file to download
        output_path: Path to save the file
        
    Returns:
        Local path to the downloaded file
    """
    logger = setup_logger('utils')
    
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Download the file
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get file size for progress tracking
        file_size = int(response.headers.get('content-length', 0))
        
        # Write the file
        with open(output_path, 'wb') as f:
            if file_size > 0:
                logger.info(f"Downloading {url} ({file_size/1024/1024:.1f} MB)")
                
                # Track download progress
                downloaded = 0
                last_percent = 0
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Log progress every 10%
                        percent = int(downloaded / file_size * 100)
                        if percent >= last_percent + 10:
                            logger.info(f"Download progress: {percent}%")
                            last_percent = percent
            else:
                logger.info(f"Downloading {url} (unknown size)")
                f.write(response.content)
        
        logger.info(f"Download complete: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise

def integrate_typography_system(brand_name: str, text_data: Dict[str, str], image_size: tuple) -> Dict[str, Any]:
    """
    Integrate with the existing typography system in the project.
    
    Args:
        brand_name: Name of the brand
        text_data: Dictionary of text elements (headline, subheadline, etc.)
        image_size: Size of the image (width, height)
        
    Returns:
        Typography configuration for video overlay
    """
    logger = setup_logger('utils')
    
    try:
        # Import the typography system components if available
        try:
            from ad_generator.typography.typography_system import TypographySystem
            from brand_overlay.brand_typography import BrandTypographyManager
            from typography_effects import TypographyEffectsEngine
            
            logger.info("Using existing typography system for text styling")
            
            # Initialize typography system
            typography = TypographySystem()
            
            # Get brand-specific typography style
            # This will analyze the brand and determine appropriate styling
            style = typography.get_style_preview(
                brand_name=brand_name,
                industry=None,  # Let the system determine this
                brand_level=None  # Let the system determine this
            )
            
            # Extract key styling parameters for video text overlay
            text_styling = {
                'font_family': style.get('font', 'Arial'),
                'color_scheme': style.get('color_scheme', 'brand_colors'),
                'text_effects': style.get('text_treatments', {}),
                'text_placement': style.get('text_placement', 'centered'),
                'typography_style': style
            }
            
            return text_styling
            
        except ImportError:
            logger.info("Existing typography system not found, using default text styling")
            return {
                'font_family': 'Arial',
                'color_scheme': 'brand_colors',
                'text_effects': {
                    'headline': 'simple',
                    'subheadline': 'simple',
                    'body': 'simple',
                    'cta': 'simple'
                },
                'text_placement': 'centered'
            }
            
    except Exception as e:
        logger.error(f"Error integrating typography system: {e}")
        # Return default styling
        return {
            'font_family': 'Arial',
            'color_scheme': 'brand_colors',
            'text_effects': {
                'headline': 'simple',
                'subheadline': 'simple',
                'body': 'simple',
                'cta': 'simple'
            },
            'text_placement': 'centered'
        }

def generate_unique_filename(prefix: str, extension: str = '.mp4') -> str:
    """
    Generate a unique filename with timestamp and random string.
    
    Args:
        prefix: Prefix for the filename
        extension: File extension
        
    Returns:
        Unique filename
    """
    import uuid
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_id = uuid.uuid4().hex[:8]
    return f"{prefix}_{timestamp}_{random_id}{extension}"

def clean_text_for_tts(text: str) -> str:
    """
    Clean text for text-to-speech processing.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    # Replace common symbols that TTS engines might struggle with
    replacements = {
        '&': 'and',
        '%': 'percent',
        '@': 'at',
        '#': 'number',
        '+': 'plus',
        '=': 'equals',
        '_': ' ',
        '*': '',
        '...': ', '
    }
    
    result = text
    for symbol, replacement in replacements.items():
        result = result.replace(symbol, replacement)
    
    # Remove multiple spaces
    result = ' '.join(result.split())
    
    return result

if __name__ == "__main__":
    # Test the utilities
    logger = setup_logger('utils_test')
    logger.info("Testing utilities module")
    
    # Test configuration loading
    config = load_config()
    logger.info(f"Configuration loaded: {len(config)} keys")
    
    # Test typography integration
    typography = integrate_typography_system("Example Brand", {"headline": "Test Headline"}, (1920, 1080))
    logger.info(f"Typography integration result: {typography.get('font_family', 'unknown')}")
    
    logger.info("Utilities module tests completed")