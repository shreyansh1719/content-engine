"""
Font Manager for ad generation system.
Handles font discovery and loading for typography.
"""
import os
import logging
from typing import Dict, List, Optional, Any
from PIL import ImageFont

class FontManager:
    """Manages font discovery and loading for professional typography."""
    
    def __init__(self):
        """Initialize the font manager."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize font directories to search
        self.font_directories = [
            '',  # Current directory
            '/usr/share/fonts/truetype/',
            '/usr/share/fonts/',
            '/Library/Fonts/',
            'C:\\Windows\\Fonts\\',
            os.path.join(os.path.expanduser('~'), 'Library/Fonts'),
            os.path.join(os.path.expanduser('~'), '.fonts')
        ]
        
        # Initialize font styles
        self.font_styles = self._setup_font_styles()
        
        # Initialize brand-specific fonts
        self.brand_fonts = {}
        
        # Cache for loaded fonts
        self.font_cache = {}
    
    def _setup_font_styles(self) -> Dict[str, Dict[str, List[str]]]:
        """Setup font mappings for different typography styles."""
        return {
            'modern': {
                'headline': ['Helvetica-Bold', 'Arial-Bold', 'Gotham-Bold', 'Montserrat-Bold', 'OpenSans-Bold'],
                'subheadline': ['Helvetica', 'Arial', 'Gotham-Medium', 'Montserrat', 'OpenSans'],
                'body': ['Helvetica-Light', 'Arial', 'Gotham-Book', 'Montserrat-Light', 'OpenSans-Light'],
                'cta': ['Helvetica-Bold', 'Arial-Bold', 'Gotham-Bold', 'Montserrat-Bold', 'OpenSans-Bold']
            },
            'luxury': {
                'headline': ['Didot-Bold', 'Georgia-Bold', 'Playfair-Bold', 'TimesNewRoman-Bold', 'Garamond-Bold'],
                'subheadline': ['Didot', 'Georgia', 'Playfair', 'TimesNewRoman', 'Garamond'],
                'body': ['Didot-Light', 'Georgia', 'Playfair-Light', 'TimesNewRoman', 'Garamond'],
                'cta': ['Didot-Bold', 'Georgia-Bold', 'Playfair-Bold', 'TimesNewRoman-Bold', 'Garamond-Bold']
            },
            'minimal': {
                'headline': ['Futura-Bold', 'Helvetica-Light', 'Montserrat-Light', 'Gotham-Light', 'OpenSans-Light'],
                'subheadline': ['Futura-Medium', 'Helvetica-Light', 'Montserrat-Light', 'Gotham-Light', 'OpenSans-Light'],
                'body': ['Futura-Light', 'Helvetica-Light', 'Montserrat-Light', 'Gotham-Light', 'OpenSans-Light'],
                'cta': ['Futura-Medium', 'Helvetica', 'Montserrat', 'Gotham-Book', 'OpenSans']
            },
            'bold': {
                'headline': ['Impact', 'Helvetica-Black', 'Montserrat-Black', 'Arial-Black', 'Gotham-Black'],
                'subheadline': ['Helvetica-Bold', 'Montserrat-Bold', 'Arial-Bold', 'Gotham-Bold', 'OpenSans-Bold'],
                'body': ['Helvetica', 'Montserrat', 'Arial', 'Gotham-Book', 'OpenSans'],
                'cta': ['Helvetica-Bold', 'Montserrat-Bold', 'Arial-Bold', 'Gotham-Bold', 'OpenSans-Bold']
            },
            'elegant': {
                'headline': ['Baskerville-Bold', 'Garamond-Bold', 'Georgia-Bold', 'TimesNewRoman-Bold', 'Didot-Bold'],
                'subheadline': ['Baskerville', 'Garamond', 'Georgia', 'TimesNewRoman', 'Didot'],
                'body': ['Baskerville', 'Garamond', 'Georgia', 'TimesNewRoman', 'Didot'],
                'cta': ['Baskerville-Bold', 'Garamond-Bold', 'Georgia-Bold', 'TimesNewRoman-Bold', 'Didot-Bold']
            },
            'technical': {
                'headline': ['Roboto-Bold', 'SourceSansPro-Bold', 'Calibri-Bold', 'Helvetica-Bold', 'Arial-Bold'],
                'subheadline': ['Roboto', 'SourceSansPro', 'Calibri', 'Helvetica', 'Arial'],
                'body': ['Roboto-Light', 'SourceSansPro-Light', 'Calibri', 'Helvetica-Light', 'Arial'],
                'cta': ['Roboto-Bold', 'SourceSansPro-Bold', 'Calibri-Bold', 'Helvetica-Bold', 'Arial-Bold']
            }
        }
    
    def get_font(self, style: str, element: str, size: int, brand: str = None) -> Optional[ImageFont.FreeTypeFont]:
        """
        Get appropriate font based on style, element type, and brand.
        
        Args:
            style: Typography style ('modern', 'luxury', 'minimal', etc.)
            element: Element type ('headline', 'subheadline', 'body', 'cta')
            size: Font size
            brand: Brand name for brand-specific fonts (optional)
            
        Returns:
            Font object
        """
        # Check for brand-specific font first
        if brand and brand.lower() in self.brand_fonts:
            brand_font = self.brand_fonts[brand.lower()].get(element)
            if brand_font:
                font = self._load_specific_font(brand_font, size)
                if font:
                    return font
        
        # Check cache
        cache_key = f"{style}_{element}_{size}"
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        # Map style to closest available
        style_key = self._map_style_to_key(style)
        
        # Get font list for this style and element
        font_list = self.font_styles.get(style_key, {}).get(element, ['Arial-Bold', 'Helvetica-Bold'])
        
        # Try each font in the list
        for font_name in font_list:
            font = self._load_font(font_name, size)
            if font:
                # Cache for future use
                self.font_cache[cache_key] = font
                return font
        
        # Fallback to generic fonts
        font = self._load_generic_font(element, size)
        if font:
            # Cache for future use
            self.font_cache[cache_key] = font
            return font
        
        # Last resort: default font
        try:
            default_font = ImageFont.load_default()
            self.font_cache[cache_key] = default_font
            return default_font
        except:
            self.logger.warning(f"Could not load any fonts for {style} {element}")
            return None
    
    def _map_style_to_key(self, style: str) -> str:
        """Map style name to a valid style key."""
        style_lower = style.lower()
        
        if 'modern' in style_lower or 'sans' in style_lower:
            return 'modern'
        elif 'luxury' in style_lower or 'premium' in style_lower or 'high-end' in style_lower:
            return 'luxury'
        elif 'minimal' in style_lower or 'clean' in style_lower or 'simple' in style_lower:
            return 'minimal'
        elif 'bold' in style_lower or 'strong' in style_lower or 'powerful' in style_lower:
            return 'bold'
        elif 'elegant' in style_lower or 'sophisticated' in style_lower or 'classic' in style_lower:
            return 'elegant'
        elif 'technical' in style_lower or 'digital' in style_lower or 'tech' in style_lower:
            return 'technical'
        else:
            # Default to modern
            return 'modern'
    
    def _load_font(self, font_name: str, size: int) -> Optional[ImageFont.FreeTypeFont]:
        """Load font by searching in font directories."""
        # Try with various extensions
        for ext in ['', '.ttf', '.otf', '.TTF', '.OTF']:
            for directory in self.font_directories:
                try:
                    font_path = os.path.join(directory, f"{font_name}{ext}")
                    if os.path.exists(font_path):
                        return ImageFont.truetype(font_path, size)
                except (OSError, IOError):
                    continue
        
        return None
    
    def _load_specific_font(self, font_path: str, size: int) -> Optional[ImageFont.FreeTypeFont]:
        """Load a specific font from a path."""
        try:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            pass
        
        return None
    
    def _load_generic_font(self, element: str, size: int) -> Optional[ImageFont.FreeTypeFont]:
        """Load a generic font based on element type."""
        generic_fonts = {
            'headline': ['Arial-Bold', 'Helvetica-Bold', 'OpenSans-Bold', 'Verdana-Bold'],
            'subheadline': ['Arial', 'Helvetica', 'OpenSans', 'Verdana'],
            'body': ['Arial', 'Helvetica', 'OpenSans', 'Verdana'],
            'cta': ['Arial-Bold', 'Helvetica-Bold', 'OpenSans-Bold', 'Verdana-Bold']
        }
        
        # Try generic fonts
        for font_name in generic_fonts.get(element, ['Arial']):
            font = self._load_font(font_name, size)
            if font:
                return font
        
        return None
    
    def register_brand_font(self, brand: str, font_mapping: Dict[str, str]) -> bool:
        """
        Register brand-specific fonts.
        
        Args:
            brand: Brand name
            font_mapping: Dictionary mapping element types to font paths
            
        Returns:
            Success status
        """
        try:
            brand_lower = brand.lower()
            
            # Verify fonts exist
            valid_fonts = {}
            for element, font_path in font_mapping.items():
                if os.path.exists(font_path):
                    valid_fonts[element] = font_path
                else:
                    self.logger.warning(f"Font not found for {brand}: {font_path}")
            
            if valid_fonts:
                self.brand_fonts[brand_lower] = valid_fonts
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Error registering brand font: {str(e)}")
            return False
    
    def get_available_styles(self) -> List[str]:
        """Get list of available typography styles."""
        return list(self.font_styles.keys())