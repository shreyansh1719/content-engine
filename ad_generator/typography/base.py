"""
Shared base classes and utilities for typography system
This file contains common utilities to avoid circular imports
"""
import os
import logging
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image, ImageDraw, ImageFont

class TypographyBase:
    """Base class with shared utilities for typography components."""
    
    def __init__(self):
        """Initialize base typography utilities."""
        self.logger = logging.getLogger(__name__)
        
        # Common font directories
        self.font_directories = [
            '',  # Current directory
            '/usr/share/fonts/truetype/',
            '/usr/share/fonts/',
            '/Library/Fonts/',
            'C:\\Windows\\Fonts\\',
            os.path.join(os.path.expanduser('~'), 'Library/Fonts'),
            os.path.join(os.path.expanduser('~'), '.fonts')
        ]
    
    def get_text_dimensions(self, text: str, font) -> Tuple[int, int]:
        """Get dimensions of text with given font."""
        try:
            # Try getbbox method first (Pillow >= 8.0.0)
            bbox = font.getbbox(text)
            if bbox:
                return bbox[2] - bbox[0], bbox[3] - bbox[1]
        except (AttributeError, TypeError):
            try:
                # Try older PIL method
                return font.getsize(text)
            except:
                # Estimate based on character count
                size = getattr(font, 'size', 12)
                return int(len(text) * size * 0.6), int(size * 1.2)
    
    def _extract_font_name(self, filename: str) -> str:
        """Extract font name from filename."""
        # Remove extension
        name = os.path.splitext(filename)[0]
        
        # Clean up common suffixes and separators
        name = name.replace('_', ' ').replace('-', ' ').strip()
        
        return name
    
    def _extract_font_family(self, font_name: str) -> str:
        """Extract font family from font name."""
        # Common weight/style indicators
        weight_indicators = ['Bold', 'Light', 'Thin', 'Black', 'Regular', 'Medium', 'Heavy', 'Semibold']
        style_indicators = ['Italic', 'Oblique']
        
        # Split name by spaces
        parts = font_name.split()
        
        # Remove weight and style parts to get family
        family_parts = []
        for part in parts:
            if part not in weight_indicators and part not in style_indicators:
                family_parts.append(part)
        
        # Join remaining parts to form family
        family = ' '.join(family_parts)
        
        # Handle special case where nothing was extracted
        if not family:
            family = font_name
        
        return family

# Common utilities that can be used by various typography components
def load_font(font_name: str, size: int, font_directories: List[str]) -> Optional[ImageFont.FreeTypeFont]:
    """
    Load a font by name and size.
    
    Args:
        font_name: Font name with optional weight
        size: Font size
        font_directories: List of directories to search for fonts
        
    Returns:
        Font object or None if not found
    """
    # Try with various extensions
    for ext in ['', '.ttf', '.otf', '.TTF', '.OTF']:
        for directory in font_directories:
            try:
                font_path = os.path.join(directory, f"{font_name}{ext}")
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size)
            except (OSError, IOError):
                continue
    
    # Try splitting font name and weight
    if '-' in font_name:
        font_family, weight = font_name.split('-', 1)
        # Try different naming conventions
        alternate_names = [
            f"{font_family} {weight}",
            f"{font_family}{weight}",
            f"{font_family}_{weight}"
        ]
        
        for alt_name in alternate_names:
            for ext in ['', '.ttf', '.otf', '.TTF', '.OTF']:
                for directory in font_directories:
                    try:
                        font_path = os.path.join(directory, f"{alt_name}{ext}")
                        if os.path.exists(font_path):
                            return ImageFont.truetype(font_path, size)
                    except (OSError, IOError):
                        continue
    
    # Last resort: default font
    try:
        return ImageFont.load_default()
    except:
        return None

# Common constants for typography system
DEFAULT_PREMIUM_FONTS = {
    'modern': {
        'headline': ['Helvetica Neue-Bold', 'SF Pro Display-Bold', 'Arial-Bold', 'Gotham-Bold', 'Montserrat-Bold', 'OpenSans-Bold'],
        'subheadline': ['Helvetica Neue-Regular', 'SF Pro Text', 'Arial', 'Gotham-Medium', 'Montserrat', 'OpenSans'],
        'body': ['Helvetica Neue-Light', 'SF Pro Text-Light', 'Arial', 'Gotham-Book', 'Montserrat-Light', 'OpenSans-Light'],
        'cta': ['Helvetica Neue-Bold', 'SF Pro Text-Semibold', 'Arial-Bold', 'Gotham-Bold', 'Montserrat-Bold', 'OpenSans-Bold']
    },
    'luxury': {
        'headline': ['Didot-Bold', 'Bodoni-Bold', 'Georgia-Bold', 'Playfair Display-Bold', 'TimesNewRoman-Bold', 'Garamond-Bold'],
        'subheadline': ['Didot', 'Bodoni', 'Georgia', 'Playfair Display', 'TimesNewRoman', 'Garamond'],
        'body': ['Didot-Light', 'Bodoni-Light', 'Georgia', 'Playfair Display-Light', 'TimesNewRoman', 'Garamond'],
        'cta': ['Didot-Bold', 'Bodoni-Bold', 'Georgia-Bold', 'Playfair Display-Bold', 'TimesNewRoman-Bold', 'Garamond-Bold']
    },
    'minimal': {
        'headline': ['Futura-Bold', 'Helvetica Neue-Light', 'Montserrat-Light', 'Gotham-Light', 'OpenSans-Light'],
        'subheadline': ['Futura-Medium', 'Helvetica Neue-Light', 'Montserrat-Light', 'Gotham-Light', 'OpenSans-Light'],
        'body': ['Futura-Light', 'Helvetica Neue-Light', 'Montserrat-Light', 'Gotham-Light', 'OpenSans-Light'],
        'cta': ['Futura-Medium', 'Helvetica Neue', 'Montserrat', 'Gotham-Book', 'OpenSans']
    },
    'bold': {
        'headline': ['Impact', 'Helvetica Neue-Black', 'SF Pro Display-Black', 'Montserrat-Black', 'Arial-Black', 'Gotham-Black'],
        'subheadline': ['Helvetica Neue-Bold', 'SF Pro Display-Bold', 'Montserrat-Bold', 'Arial-Bold', 'Gotham-Bold', 'OpenSans-Bold'],
        'body': ['Helvetica Neue', 'SF Pro Text', 'Montserrat', 'Arial', 'Gotham-Book', 'OpenSans'],
        'cta': ['Helvetica Neue-Bold', 'SF Pro Display-Bold', 'Montserrat-Bold', 'Arial-Bold', 'Gotham-Bold', 'OpenSans-Bold']
    },
    'elegant': {
        'headline': ['Baskerville-Bold', 'Garamond-Bold', 'Georgia-Bold', 'TimesNewRoman-Bold', 'Didot-Bold'],
        'subheadline': ['Baskerville', 'Garamond', 'Georgia', 'TimesNewRoman', 'Didot'],
        'body': ['Baskerville', 'Garamond', 'Georgia', 'TimesNewRoman', 'Didot'],
        'cta': ['Baskerville-Bold', 'Garamond-Bold', 'Georgia-Bold', 'TimesNewRoman-Bold', 'Didot-Bold']
    },
    'technical': {
        'headline': ['SF Pro Display-Bold', 'Roboto-Bold', 'SourceSansPro-Bold', 'Calibri-Bold', 'Helvetica Neue-Bold', 'Arial-Bold'],
        'subheadline': ['SF Pro Text', 'Roboto', 'SourceSansPro', 'Calibri', 'Helvetica Neue', 'Arial'],
        'body': ['SF Pro Text-Light', 'Roboto-Light', 'SourceSansPro-Light', 'Calibri', 'Helvetica Neue-Light', 'Arial'],
        'cta': ['SF Pro Display-Bold', 'Roboto-Bold', 'SourceSansPro-Bold', 'Calibri-Bold', 'Helvetica Neue-Bold', 'Arial-Bold']
    }
}
import os
import logging
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image, ImageDraw, ImageFont

class TypographyBase:
    """Base class with shared utilities for typography components."""
    
    def __init__(self):
        """Initialize base typography utilities."""
        self.logger = logging.getLogger(__name__)
        
        # Common font directories
        self.font_directories = [
            '',  # Current directory
            '/usr/share/fonts/truetype/',
            '/usr/share/fonts/',
            '/Library/Fonts/',
            'C:\\Windows\\Fonts\\',
            os.path.join(os.path.expanduser('~'), 'Library/Fonts'),
            os.path.join(os.path.expanduser('~'), '.fonts')
        ]
    
    def get_text_dimensions(self, text: str, font) -> Tuple[int, int]:
        """Get dimensions of text with given font."""
        try:
            # Try getbbox method first (Pillow >= 8.0.0)
            bbox = font.getbbox(text)
            if bbox:
                return bbox[2] - bbox[0], bbox[3] - bbox[1]
        except (AttributeError, TypeError):
            try:
                # Try older PIL method
                return font.getsize(text)
            except:
                # Estimate based on character count
                size = getattr(font, 'size', 12)
                return int(len(text) * size * 0.6), int(size * 1.2)
    
    def _extract_font_name(self, filename: str) -> str:
        """Extract font name from filename."""
        # Remove extension
        name = os.path.splitext(filename)[0]
        
        # Clean up common suffixes and separators
        name = name.replace('_', ' ').replace('-', ' ').strip()
        
        return name
    
    def _extract_font_family(self, font_name: str) -> str:
        """Extract font family from font name."""
        # Common weight/style indicators
        weight_indicators = ['Bold', 'Light', 'Thin', 'Black', 'Regular', 'Medium', 'Heavy', 'Semibold']
        style_indicators = ['Italic', 'Oblique']
        
        # Split name by spaces
        parts = font_name.split()
        
        # Remove weight and style parts to get family
        family_parts = []
        for part in parts:
            if part not in weight_indicators and part not in style_indicators:
                family_parts.append(part)
        
        # Join remaining parts to form family
        family = ' '.join(family_parts)
        
        # Handle special case where nothing was extracted
        if not family:
            family = font_name
        
        return family

# Common utilities that can be used by various typography components
def load_font(font_name: str, size: int, font_directories: List[str]) -> Optional[ImageFont.FreeTypeFont]:
    """
    Load a font by name and size.
    
    Args:
        font_name: Font name with optional weight
        size: Font size
        font_directories: List of directories to search for fonts
        
    Returns:
        Font object or None if not found
    """
    # Try with various extensions
    for ext in ['', '.ttf', '.otf', '.TTF', '.OTF']:
        for directory in font_directories:
            try:
                font_path = os.path.join(directory, f"{font_name}{ext}")
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size)
            except (OSError, IOError):
                continue
    
    # Try splitting font name and weight
    if '-' in font_name:
        font_family, weight = font_name.split('-', 1)
        # Try different naming conventions
        alternate_names = [
            f"{font_family} {weight}",
            f"{font_family}{weight}",
            f"{font_family}_{weight}"
        ]
        
        for alt_name in alternate_names:
            for ext in ['', '.ttf', '.otf', '.TTF', '.OTF']:
                for directory in font_directories:
                    try:
                        font_path = os.path.join(directory, f"{alt_name}{ext}")
                        if os.path.exists(font_path):
                            return ImageFont.truetype(font_path, size)
                    except (OSError, IOError):
                        continue
    
    # Last resort: default font
    try:
        return ImageFont.load_default()
    except:
        return None

# Common constants for typography system
DEFAULT_PREMIUM_FONTS = {
    'modern': {
        'headline': ['Helvetica Neue-Bold', 'SF Pro Display-Bold', 'Arial-Bold', 'Gotham-Bold', 'Montserrat-Bold', 'OpenSans-Bold'],
        'subheadline': ['Helvetica Neue-Regular', 'SF Pro Text', 'Arial', 'Gotham-Medium', 'Montserrat', 'OpenSans'],
        'body': ['Helvetica Neue-Light', 'SF Pro Text-Light', 'Arial', 'Gotham-Book', 'Montserrat-Light', 'OpenSans-Light'],
        'cta': ['Helvetica Neue-Bold', 'SF Pro Text-Semibold', 'Arial-Bold', 'Gotham-Bold', 'Montserrat-Bold', 'OpenSans-Bold']
    },
    'luxury': {
        'headline': ['Didot-Bold', 'Bodoni-Bold', 'Georgia-Bold', 'Playfair Display-Bold', 'TimesNewRoman-Bold', 'Garamond-Bold'],
        'subheadline': ['Didot', 'Bodoni', 'Georgia', 'Playfair Display', 'TimesNewRoman', 'Garamond'],
        'body': ['Didot-Light', 'Bodoni-Light', 'Georgia', 'Playfair Display-Light', 'TimesNewRoman', 'Garamond'],
        'cta': ['Didot-Bold', 'Bodoni-Bold', 'Georgia-Bold', 'Playfair Display-Bold', 'TimesNewRoman-Bold', 'Garamond-Bold']
    },
    'minimal': {
        'headline': ['Futura-Bold', 'Helvetica Neue-Light', 'Montserrat-Light', 'Gotham-Light', 'OpenSans-Light'],
        'subheadline': ['Futura-Medium', 'Helvetica Neue-Light', 'Montserrat-Light', 'Gotham-Light', 'OpenSans-Light'],
        'body': ['Futura-Light', 'Helvetica Neue-Light', 'Montserrat-Light', 'Gotham-Light', 'OpenSans-Light'],
        'cta': ['Futura-Medium', 'Helvetica Neue', 'Montserrat', 'Gotham-Book', 'OpenSans']
    },
    'bold': {
        'headline': ['Impact', 'Helvetica Neue-Black', 'SF Pro Display-Black', 'Montserrat-Black', 'Arial-Black', 'Gotham-Black'],
        'subheadline': ['Helvetica Neue-Bold', 'SF Pro Display-Bold', 'Montserrat-Bold', 'Arial-Bold', 'Gotham-Bold', 'OpenSans-Bold'],
        'body': ['Helvetica Neue', 'SF Pro Text', 'Montserrat', 'Arial', 'Gotham-Book', 'OpenSans'],
        'cta': ['Helvetica Neue-Bold', 'SF Pro Display-Bold', 'Montserrat-Bold', 'Arial-Bold', 'Gotham-Bold', 'OpenSans-Bold']
    },
    'elegant': {
        'headline': ['Baskerville-Bold', 'Garamond-Bold', 'Georgia-Bold', 'TimesNewRoman-Bold', 'Didot-Bold'],
        'subheadline': ['Baskerville', 'Garamond', 'Georgia', 'TimesNewRoman', 'Didot'],
        'body': ['Baskerville', 'Garamond', 'Georgia', 'TimesNewRoman', 'Didot'],
        'cta': ['Baskerville-Bold', 'Garamond-Bold', 'Georgia-Bold', 'TimesNewRoman-Bold', 'Didot-Bold']
    },
    'technical': {
        'headline': ['SF Pro Display-Bold', 'Roboto-Bold', 'SourceSansPro-Bold', 'Calibri-Bold', 'Helvetica Neue-Bold', 'Arial-Bold'],
        'subheadline': ['SF Pro Text', 'Roboto', 'SourceSansPro', 'Calibri', 'Helvetica Neue', 'Arial'],
        'body': ['SF Pro Text-Light', 'Roboto-Light', 'SourceSansPro-Light', 'Calibri', 'Helvetica Neue-Light', 'Arial'],
        'cta': ['SF Pro Display-Bold', 'Roboto-Bold', 'SourceSansPro-Bold', 'Calibri-Bold', 'Helvetica Neue-Bold', 'Arial-Bold']
    }
}