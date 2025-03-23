"""
Font Pairing Engine for Professional Ad Typography
Provides intelligent font selection and pairing
"""
import os
import logging
from typing import Dict, List, Tuple, Any, Optional, Union
from PIL import ImageFont

class FontPairingEngine:
    """
    Engine for intelligent font selection and pairing.
    Creates harmonious typography combinations for professional ads.
    """
    
    def __init__(self, fonts_directory: Optional[str] = None):
        """
        Initialize the font pairing engine.
        
        Args:
            fonts_directory: Optional custom fonts directory
        """
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize font directories
        self.font_directories = self._setup_font_directories(fonts_directory)
        
        # Cache for loaded fonts
        self.font_cache = {}
        
        # Initialize font pairings
        self.font_pairings = self._initialize_font_pairings()
        
        # Initialize brand-specific fonts
        self.brand_fonts = self._initialize_brand_fonts()
        
        # Initialize industry-specific fonts
        self.industry_fonts = self._initialize_industry_fonts()
        
        # Validate and load system fonts
        self.available_fonts = self._discover_available_fonts()
    
    def _setup_font_directories(self, custom_directory: Optional[str] = None) -> List[str]:
        """
        Setup font directories to search for fonts.
        
        Args:
            custom_directory: Optional custom directory to include
            
        Returns:
            List of directories to search
        """
        directories = [
            '',  # Current directory
            '/usr/share/fonts/truetype/',
            '/usr/share/fonts/',
            '/Library/Fonts/',
            'C:\\Windows\\Fonts\\',
            os.path.join(os.path.expanduser('~'), 'Library/Fonts'),
            os.path.join(os.path.expanduser('~'), '.fonts')
        ]
        
        # Add custom directory if provided
        if custom_directory and os.path.exists(custom_directory):
            directories.insert(0, custom_directory)
        
        return directories
    
    def _initialize_font_pairings(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize professional font pairings for different styles.
        
        Returns:
            Dictionary of font pairings
        """
        return {
            "modern": {
                "description": "Clean, modern sans-serif pairing",
                "headline": ["SF Pro Display-Bold", "Helvetica Neue-Bold", "Arial-Bold", "Montserrat-Bold"],
                "subheadline": ["SF Pro Text", "Helvetica Neue", "Arial", "Montserrat"],
                "body": ["SF Pro Text-Light", "Helvetica Neue-Light", "Arial", "Montserrat-Light"],
                "cta": ["SF Pro Display-Bold", "Helvetica Neue-Bold", "Arial-Bold", "Montserrat-Bold"],
                "brand": ["SF Pro Display-Bold", "Helvetica Neue-Bold", "Arial-Bold", "Montserrat-Bold"],
                "fallbacks": ["Arial-Bold", "Verdana-Bold", "Tahoma-Bold"]
            },
            
            "luxury": {
                "description": "Elegant serif pairing for luxury brands",
                "headline": ["Didot-Bold", "Baskerville-Bold", "Times New Roman-Bold", "Georgia-Bold"],
                "subheadline": ["Didot", "Baskerville", "Times New Roman", "Georgia"],
                "body": ["Didot-Light", "Baskerville", "Times New Roman", "Georgia"],
                "cta": ["Didot-Bold", "Baskerville-Bold", "Times New Roman-Bold", "Georgia-Bold"],
                "brand": ["Didot-Bold", "Baskerville-Bold", "Times New Roman-Bold", "Georgia-Bold"],
                "fallbacks": ["Times New Roman-Bold", "Georgia-Bold", "Cambria-Bold"]
            },
            
            "contrast": {
                "description": "Contrasting serif/sans-serif pairing",
                "headline": ["Playfair Display-Bold", "Georgia-Bold", "Times New Roman-Bold"],
                "subheadline": ["Montserrat", "Helvetica Neue", "Arial"],
                "body": ["Montserrat-Light", "Helvetica Neue-Light", "Arial"],
                "cta": ["Montserrat-Bold", "Helvetica Neue-Bold", "Arial-Bold"],
                "brand": ["Playfair Display-Bold", "Georgia-Bold", "Times New Roman-Bold"],
                "fallbacks": ["Georgia-Bold", "Arial-Bold", "Verdana-Bold"]
            },
            
            "minimal": {
                "description": "Minimal, clean typography with a single font family",
                "headline": ["Helvetica Neue-Light", "SF Pro Display-Light", "Arial-Light", "Montserrat-Light"],
                "subheadline": ["Helvetica Neue-Light", "SF Pro Text-Light", "Arial-Light", "Montserrat-Light"],
                "body": ["Helvetica Neue-Light", "SF Pro Text-Light", "Arial-Light", "Montserrat-Light"],
                "cta": ["Helvetica Neue", "SF Pro Text", "Arial", "Montserrat"],
                "brand": ["Helvetica Neue-Light", "SF Pro Display-Light", "Arial-Light", "Montserrat-Light"],
                "fallbacks": ["Arial-Light", "Verdana", "Tahoma"]
            },
            
            "bold": {
                "description": "Bold, impactful typography",
                "headline": ["Impact", "Helvetica Neue-Black", "Arial-Black", "Montserrat-Black"],
                "subheadline": ["Helvetica Neue-Bold", "Arial-Bold", "Montserrat-Bold"],
                "body": ["Helvetica Neue", "Arial", "Montserrat"],
                "cta": ["Helvetica Neue-Bold", "Arial-Bold", "Montserrat-Bold"],
                "brand": ["Helvetica Neue-Black", "Arial-Black", "Montserrat-Black"],
                "fallbacks": ["Arial-Black", "Verdana-Bold", "Tahoma-Bold"]
            },
            
            "elegant": {
                "description": "Elegant, sophisticated typography",
                "headline": ["Baskerville-Bold", "Garamond-Bold", "Georgia-Bold", "Times New Roman-Bold"],
                "subheadline": ["Baskerville", "Garamond", "Georgia", "Times New Roman"],
                "body": ["Baskerville", "Garamond", "Georgia", "Times New Roman"],
                "cta": ["Baskerville-Bold", "Garamond-Bold", "Georgia-Bold", "Times New Roman-Bold"],
                "brand": ["Baskerville-Bold", "Garamond-Bold", "Georgia-Bold", "Times New Roman-Bold"],
                "fallbacks": ["Times New Roman-Bold", "Georgia-Bold", "Cambria-Bold"]
            },
            
            "creative": {
                "description": "Creative, distinctive typography",
                "headline": ["Futura-Bold", "Avenir-Bold", "Century Gothic-Bold"],
                "subheadline": ["Futura", "Avenir", "Century Gothic"],
                "body": ["Futura-Light", "Avenir-Light", "Century Gothic"],
                "cta": ["Futura-Bold", "Avenir-Bold", "Century Gothic-Bold"],
                "brand": ["Futura-Bold", "Avenir-Bold", "Century Gothic-Bold"],
                "fallbacks": ["Arial-Bold", "Verdana-Bold", "Tahoma-Bold"]
            },
            
            "technical": {
                "description": "Clean, technical typography",
                "headline": ["Roboto-Bold", "SF Pro Display-Bold", "Arial-Bold"],
                "subheadline": ["Roboto", "SF Pro Text", "Arial"],
                "body": ["Roboto-Light", "SF Pro Text-Light", "Arial"],
                "cta": ["Roboto-Bold", "SF Pro Display-Bold", "Arial-Bold"],
                "brand": ["Roboto-Bold", "SF Pro Display-Bold", "Arial-Bold"],
                "fallbacks": ["Arial-Bold", "Verdana-Bold", "Tahoma-Bold"]
            },
            
            "playful": {
                "description": "Fun, playful typography",
                "headline": ["Quicksand-Bold", "Comic Sans MS-Bold", "Avenir-Bold"],
                "subheadline": ["Quicksand", "Comic Sans MS", "Avenir"],
                "body": ["Quicksand-Light", "Comic Sans MS", "Avenir-Light"],
                "cta": ["Quicksand-Bold", "Comic Sans MS-Bold", "Avenir-Bold"],
                "brand": ["Quicksand-Bold", "Comic Sans MS-Bold", "Avenir-Bold"],
                "fallbacks": ["Arial-Bold", "Verdana-Bold", "Tahoma-Bold"]
            }
        }
    
    def _initialize_brand_fonts(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Initialize brand-specific fonts for recognizable brands.
        
        Returns:
            Dictionary of brand fonts
        """
        return {
            "apple": {
                "headline": ["SF Pro Display-Bold", "SF Pro Display-Light", "Helvetica Neue-Light"],
                "subheadline": ["SF Pro Text", "Helvetica Neue"],
                "body": ["SF Pro Text-Light", "Helvetica Neue-Light"],
                "cta": ["SF Pro Text", "Helvetica Neue"],
                "brand": ["SF Pro Display-Medium", "Helvetica Neue-Medium"]
            },
            
            "nike": {
                "headline": ["Futura-Bold", "Helvetica Neue-Bold", "Arial-Bold"],
                "subheadline": ["Futura-Medium", "Helvetica Neue", "Arial"],
                "body": ["Futura-Medium", "Helvetica Neue", "Arial"],
                "cta": ["Futura-Bold", "Helvetica Neue-Bold", "Arial-Bold"],
                "brand": ["Futura-Bold", "Helvetica Neue-Bold", "Arial-Bold"]
            },
            
            "coca-cola": {
                "headline": ["Gotham-Bold", "Helvetica Neue-Bold", "Arial-Bold"],
                "subheadline": ["Gotham-Book", "Helvetica Neue", "Arial"],
                "body": ["Gotham-Book", "Helvetica Neue", "Arial"],
                "cta": ["Gotham-Bold", "Helvetica Neue-Bold", "Arial-Bold"],
                "brand": ["Gotham-Bold", "Helvetica Neue-Bold", "Arial-Bold"]
            },
            
            "mercedes": {
                "headline": ["Corporate-Bold", "Helvetica Neue-Light", "Arial-Light"],
                "subheadline": ["Corporate", "Helvetica Neue-Light", "Arial-Light"],
                "body": ["Corporate-Light", "Helvetica Neue-Light", "Arial-Light"],
                "cta": ["Corporate", "Helvetica Neue", "Arial"],
                "brand": ["Corporate-Bold", "Helvetica Neue-Bold", "Arial-Bold"]
            },
            
            "louis vuitton": {
                "headline": ["Futura-Light", "Didot-Light", "Times New Roman-Light"],
                "subheadline": ["Futura-Light", "Didot", "Times New Roman"],
                "body": ["Futura-Light", "Didot-Light", "Times New Roman"],
                "cta": ["Futura-Medium", "Didot", "Times New Roman"],
                "brand": ["Futura-Medium", "Didot-Bold", "Times New Roman-Bold"]
            },
            
            "google": {
                "headline": ["Product Sans-Bold", "Roboto-Bold", "Arial-Bold"],
                "subheadline": ["Product Sans", "Roboto", "Arial"],
                "body": ["Product Sans-Light", "Roboto-Light", "Arial"],
                "cta": ["Product Sans", "Roboto", "Arial"],
                "brand": ["Product Sans-Bold", "Roboto-Bold", "Arial-Bold"]
            },
            
            "adidas": {
                "headline": ["AdiHaus-Bold", "Helvetica Neue-Bold", "Arial-Bold"],
                "subheadline": ["AdiHaus", "Helvetica Neue", "Arial"],
                "body": ["AdiHaus", "Helvetica Neue", "Arial"],
                "cta": ["AdiHaus-Bold", "Helvetica Neue-Bold", "Arial-Bold"],
                "brand": ["AdiHaus-Bold", "Helvetica Neue-Bold", "Arial-Bold"]
            }
        }
    
    def _initialize_industry_fonts(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Initialize industry-specific font recommendations.
        
        Returns:
            Dictionary of industry font recommendations
        """
        return {
            "technology": {
                "headline": ["SF Pro Display-Bold", "Roboto-Bold", "Helvetica Neue-Bold", "Arial-Bold"],
                "subheadline": ["SF Pro Text", "Roboto", "Helvetica Neue", "Arial"],
                "body": ["SF Pro Text-Light", "Roboto-Light", "Helvetica Neue-Light", "Arial"],
                "cta": ["SF Pro Display-Bold", "Roboto-Bold", "Helvetica Neue-Bold", "Arial-Bold"],
                "brand": ["SF Pro Display-Bold", "Roboto-Bold", "Helvetica Neue-Bold", "Arial-Bold"]
            },
            
            "fashion": {
                "headline": ["Didot-Light", "Futura-Light", "Helvetica Neue-Light", "Times New Roman-Light"],
                "subheadline": ["Futura-Light", "Didot", "Helvetica Neue-Light", "Times New Roman"],
                "body": ["Futura-Light", "Helvetica Neue-Light", "Times New Roman", "Arial-Light"],
                "cta": ["Futura-Medium", "Helvetica Neue", "Times New Roman-Bold", "Arial"],
                "brand": ["Didot", "Futura-Light", "Helvetica Neue-Light", "Times New Roman-Bold"]
            },
            
            "luxury": {
                "headline": ["Didot-Bold", "Baskerville-Bold", "Times New Roman-Bold", "Georgia-Bold"],
                "subheadline": ["Didot", "Baskerville", "Times New Roman", "Georgia"],
                "body": ["Didot-Light", "Baskerville", "Times New Roman", "Georgia"],
                "cta": ["Didot-Bold", "Baskerville-Bold", "Times New Roman-Bold", "Georgia-Bold"],
                "brand": ["Didot-Bold", "Baskerville-Bold", "Times New Roman-Bold", "Georgia-Bold"]
            },
            
            "food": {
                "headline": ["Gotham-Bold", "Montserrat-Bold", "Arial-Bold", "Helvetica Neue-Bold"],
                "subheadline": ["Gotham-Book", "Montserrat", "Arial", "Helvetica Neue"],
                "body": ["Gotham-Light", "Montserrat-Light", "Arial", "Helvetica Neue-Light"],
                "cta": ["Gotham-Bold", "Montserrat-Bold", "Arial-Bold", "Helvetica Neue-Bold"],
                "brand": ["Gotham-Bold", "Montserrat-Bold", "Arial-Bold", "Helvetica Neue-Bold"]
            },
            
            "beauty": {
                "headline": ["Helvetica Neue-Light", "Didot-Light", "Gotham-Light", "Times New Roman-Light"],
                "subheadline": ["Helvetica Neue-Light", "Didot", "Gotham-Light", "Times New Roman"],
                "body": ["Helvetica Neue-Light", "Gotham-Light", "Times New Roman", "Arial-Light"],
                "cta": ["Helvetica Neue", "Gotham-Book", "Times New Roman", "Arial"],
                "brand": ["Helvetica Neue-Light", "Didot", "Gotham-Light", "Times New Roman-Bold"]
            },
            
            "automotive": {
                "headline": ["Gotham-Bold", "Helvetica Neue-Bold", "Arial-Bold", "Montserrat-Bold"],
                "subheadline": ["Gotham-Book", "Helvetica Neue", "Arial", "Montserrat"],
                "body": ["Gotham-Light", "Helvetica Neue-Light", "Arial", "Montserrat-Light"],
                "cta": ["Gotham-Bold", "Helvetica Neue-Bold", "Arial-Bold", "Montserrat-Bold"],
                "brand": ["Gotham-Bold", "Helvetica Neue-Bold", "Arial-Bold", "Montserrat-Bold"]
            },
            
            "health": {
                "headline": ["Montserrat-Bold", "Helvetica Neue-Bold", "Arial-Bold", "Gotham-Bold"],
                "subheadline": ["Montserrat", "Helvetica Neue", "Arial", "Gotham-Book"],
                "body": ["Montserrat-Light", "Helvetica Neue-Light", "Arial", "Gotham-Light"],
                "cta": ["Montserrat-Bold", "Helvetica Neue-Bold", "Arial-Bold", "Gotham-Bold"],
                "brand": ["Montserrat-Bold", "Helvetica Neue-Bold", "Arial-Bold", "Gotham-Bold"]
            },
            
            "finance": {
                "headline": ["Montserrat-Bold", "Helvetica Neue-Bold", "Arial-Bold", "Gotham-Bold"],
                "subheadline": ["Montserrat", "Helvetica Neue", "Arial", "Gotham-Book"],
                "body": ["Montserrat-Light", "Helvetica Neue-Light", "Arial", "Gotham-Light"],
                "cta": ["Montserrat-Bold", "Helvetica Neue-Bold", "Arial-Bold", "Gotham-Bold"],
                "brand": ["Montserrat-Bold", "Helvetica Neue-Bold", "Arial-Bold", "Gotham-Bold"]
            }
        }
    
    def _discover_available_fonts(self) -> List[str]:
        """
        Discover available fonts on the system.
        
        Returns:
            List of available font names
        """
        available_fonts = []
        
        # Scan directories for font files
        for directory in self.font_directories:
            if not os.path.exists(directory):
                continue
                
            try:
                for filename in os.listdir(directory):
                    if filename.lower().endswith(('.ttf', '.otf', '.ttc')):
                        # Add the font name without extension
                        font_name = os.path.splitext(filename)[0]
                        available_fonts.append(font_name)
            except:
                pass
        
        # Load default fonts if none found
        if not available_fonts:
            available_fonts = ["Arial", "Arial-Bold", "Times New Roman", "Times New Roman-Bold", 
                              "Verdana", "Verdana-Bold", "Courier New", "Courier New-Bold"]
        
        return available_fonts
    
    def get_font_pairing(self,
                        style: str,
                        brand_name: Optional[str] = None,
                        industry: Optional[str] = None,
                        text_elements: Optional[Dict[str, str]] = None) -> Dict[str, ImageFont.FreeTypeFont]:
        """
        Get a font pairing based on style, brand, and industry.
        
        Args:
            style: Typography style name (e.g., 'modern', 'luxury')
            brand_name: Optional brand name for brand-specific fonts
            industry: Optional industry for industry-specific fonts
            text_elements: Optional dictionary with text for optimization
            
        Returns:
            Dictionary with fonts for each element
        """
        # Text size configuration - these will be refined by the responsive scaling module
        sizes = {
            'headline': 36,
            'subheadline': 24,
            'body': 18,
            'cta': 22,
            'brand': 28
        }
        
        # Get font list based on hierarchy: brand > industry > style
        font_list = None
        
        # Check for brand-specific fonts first
        if brand_name:
            brand_key = self._find_matching_brand(brand_name)
            if brand_key and brand_key in self.brand_fonts:
                font_list = self.brand_fonts[brand_key]
        
        # Check for industry-specific fonts next
        if not font_list and industry:
            industry_key = self._find_matching_industry(industry)
            if industry_key and industry_key in self.industry_fonts:
                font_list = self.industry_fonts[industry_key]
        
        # Fall back to style-based fonts
        if not font_list:
            # Map style to a known pairing
            pairing_key = self._map_style_to_pairing(style)
            font_list = self.font_pairings[pairing_key]
        
        # Load fonts for each element
        fonts = {}
        for element in ['headline', 'subheadline', 'body', 'cta', 'brand']:
            element_font = self._load_font_for_element(
                element, 
                font_list.get(element, []), 
                font_list.get('fallbacks', []),
                sizes[element]
            )
            
            if element_font:
                fonts[element] = element_font
        
        return fonts
    
    def _find_matching_brand(self, brand_name: str) -> Optional[str]:
        """
        Find a matching brand in the brand fonts database.
        
        Args:
            brand_name: Brand name to match
            
        Returns:
            Matched brand key or None if not found
        """
        if not brand_name:
            return None
            
        brand_lower = brand_name.lower()
        
        # Direct match
        if brand_lower in self.brand_fonts:
            return brand_lower
        
        # Partial match
        for brand_key in self.brand_fonts.keys():
            if brand_key in brand_lower or brand_lower in brand_key:
                return brand_key
                
        # Check for common brand variations and aliases
        brand_aliases = {
            "iphone": "apple",
            "macbook": "apple",
            "ipad": "apple",
            "imac": "apple",
            "airpods": "apple",
            "just do it": "nike",
            "galaxy": "samsung",
            "coca cola": "coca-cola",
            "coke": "coca-cola",
            "lv": "louis vuitton"
        }
        
        for alias, brand_key in brand_aliases.items():
            if alias in brand_lower and brand_key in self.brand_fonts:
                return brand_key
                
        return None
    
    def _find_matching_industry(self, industry: str) -> Optional[str]:
        """
        Find a matching industry in the industry fonts database.
        
        Args:
            industry: Industry to match
            
        Returns:
            Matched industry key or None if not found
        """
        if not industry:
            return None
            
        industry_lower = industry.lower()
        
        # Direct match
        if industry_lower in self.industry_fonts:
            return industry_lower
        
        # Partial match
        for industry_key in self.industry_fonts.keys():
            if industry_key in industry_lower or industry_lower in industry_key:
                return industry_key
        
        # Check for industry categories and aliases
        industry_categories = {
            "tech": "technology",
            "software": "technology",
            "computer": "technology",
            "smartphone": "technology",
            "electronics": "technology",
            "digital": "technology",
            
            "clothes": "fashion",
            "apparel": "fashion",
            "clothing": "fashion",
            "shoes": "fashion",
            "wear": "fashion",
            "dress": "fashion",
            
            "high-end": "luxury",
            "premium": "luxury",
            "exclusive": "luxury",
            "watches": "luxury",
            "jewelry": "luxury",
            
            "restaurant": "food",
            "dining": "food",
            "cuisine": "food",
            "beverage": "food",
            "drink": "food",
            
            "cosmetics": "beauty",
            "skincare": "beauty",
            "makeup": "beauty",
            "haircare": "beauty",
            "perfume": "beauty",
            
            "car": "automotive",
            "vehicle": "automotive",
            "cars": "automotive",
            "auto": "automotive",
            
            "medical": "health",
            "healthcare": "health",
            "wellness": "health",
            "fitness": "health",
            
            "banking": "finance",
            "investment": "finance",
            "insurance": "finance"
        }
        
        for category, industry_key in industry_categories.items():
            if category in industry_lower and industry_key in self.industry_fonts:
                return industry_key
        
        return None
    
    def _map_style_to_pairing(self, style: str) -> str:
        """
        Map a style name to a font pairing.
        
        Args:
            style: Style name
            
        Returns:
            Font pairing key
        """
        if not style:
            return "modern"
            
        style_lower = style.lower()
        
        # Direct match
        if style_lower in self.font_pairings:
            return style_lower
        
        # Map to a similar style
        style_mapping = {
            "sans": "modern",
            "sans-serif": "modern",
            "clean": "modern",
            "professional": "modern",
            "corporate": "modern",
            
            "serif": "luxury",
            "high-end": "luxury",
            "premium": "luxury",
            "upscale": "luxury",
            "expensive": "luxury",
            
            "mix": "contrast",
            "mixed": "contrast",
            "hybrid": "contrast",
            "sophisticated": "contrast",
            
            "simple": "minimal",
            "minimalist": "minimal",
            "light": "minimal",
            "thin": "minimal",
            
            "strong": "bold",
            "heavy": "bold",
            "powerful": "bold",
            "impactful": "bold",
            
            "classic": "elegant",
            "classy": "elegant",
            "refined": "elegant",
            "sophisticated": "elegant",
            
            "fun": "playful",
            "friendly": "playful",
            "casual": "playful",
            "approachable": "playful",
            
            "tech": "technical",
            "functional": "technical",
            "efficient": "technical",
            "digital": "technical",
            
            "artistic": "creative",
            "unique": "creative",
            "distinctive": "creative",
            "unconventional": "creative"
        }
        
        for keyword, pairing in style_mapping.items():
            if keyword in style_lower:
                return pairing
        
        # Default to modern
        return "modern"
    
    def _load_font_for_element(self,
                              element: str,
                              font_list: List[str],
                              fallbacks: List[str],
                              size: int) -> Optional[ImageFont.FreeTypeFont]:
        """
        Load a font for a specific element, trying each option in order.
        
        Args:
            element: Element name (headline, subheadline, etc.)
            font_list: List of font names to try
            fallbacks: List of fallback font names
            size: Font size
            
        Returns:
            Loaded font or None
        """
        # Cache key
        cache_key = f"{element}_{size}_{','.join(font_list[:2])}"
        
        # Check cache
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        # Try each font in the list
        for font_name in font_list:
            font = self._load_font(font_name, size)
            if font:
                # Cache the result
                self.font_cache[cache_key] = font
                return font
        
        # Try fallbacks
        for font_name in fallbacks:
            font = self._load_font(font_name, size)
            if font:
                # Cache the result
                self.font_cache[cache_key] = font
                return font
        
        # Last resort - try standard fonts
        standard_fonts = {
            'headline': ['Arial-Bold', 'Helvetica-Bold', 'Verdana-Bold', 'Tahoma-Bold'],
            'subheadline': ['Arial', 'Helvetica', 'Verdana', 'Tahoma'],
            'body': ['Arial', 'Helvetica', 'Verdana', 'Tahoma'],
            'cta': ['Arial-Bold', 'Helvetica-Bold', 'Verdana-Bold', 'Tahoma-Bold'],
            'brand': ['Arial-Bold', 'Helvetica-Bold', 'Verdana-Bold', 'Tahoma-Bold']
        }
        
        for font_name in standard_fonts.get(element, ['Arial']):
            font = self._load_font(font_name, size)
            if font:
                # Cache the result
                self.font_cache[cache_key] = font
                return font
        
        # Last resort: default font
        try:
            default_font = ImageFont.load_default()
            self.font_cache[cache_key] = default_font
            return default_font
        except:
            self.logger.warning(f"Could not load any fonts for {element}")
            return None
    
    def _load_font(self, font_name: str, size: int) -> Optional[ImageFont.FreeTypeFont]:
        """
        Load a font by name and size.
        
        Args:
            font_name: Font name with optional weight
            size: Font size
            
        Returns:
            Font object or None if not found
        """
        try:
            # Try different naming conventions
            variants = [
                font_name,
                font_name.replace('-', ''),
                font_name.replace('-', ' '),
                font_name.replace(' ', ''),
                font_name.replace(' ', '-')
            ]
            
            # Try with various extensions
            for name_variant in variants:
                for ext in ['', '.ttf', '.otf', '.TTF', '.OTF']:
                    for directory in self.font_directories:
                        try:
                            font_path = os.path.join(directory, f"{name_variant}{ext}")
                            if os.path.exists(font_path):
                                return ImageFont.truetype(font_path, size)
                        except (OSError, IOError):
                            continue
            
            # Try splitting font name and weight
            if '-' in font_name:
                font_family, weight = font_name.split('-', 1)
                
                # Try different combinations
                combinations = [
                    f"{font_family} {weight}",
                    f"{font_family}{weight}",
                    f"{font_family}_{weight}"
                ]
                
                for combo in combinations:
                    for ext in ['', '.ttf', '.otf', '.TTF', '.OTF']:
                        for directory in self.font_directories:
                            try:
                                font_path = os.path.join(directory, f"{combo}{ext}")
                                if os.path.exists(font_path):
                                    return ImageFont.truetype(font_path, size)
                            except (OSError, IOError):
                                continue
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error loading font {font_name}: {str(e)}")
            return None
    
    def get_available_fonts(self) -> List[str]:
        """
        Get list of available fonts.
        
        Returns:
            List of available font names
        """
        return self.available_fonts
    
    def get_available_pairings(self) -> Dict[str, Dict[str, Any]]:
        """
        Get available font pairings.
        
        Returns:
            Dictionary of available font pairings
        """
        return self.font_pairings 
