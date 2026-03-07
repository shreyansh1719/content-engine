"""
Font Pairing Engine Improvements for Professional Ad Typography
Provides reliable font selection and pairing
"""
import os
import logging
import json
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

        # Load font mapping
        self.font_mapping = self._load_font_mapping()
    
        # Initialize font pairings
        self.font_pairings = self._initialize_font_pairings()
    
        # Initialize brand-specific fonts
        self.brand_fonts = self._initialize_brand_fonts()
    
        # Initialize industry-specific fonts
        self.industry_fonts = self._initialize_industry_fonts()
    
        # Validate and load system fonts
        self.available_fonts = self._discover_available_fonts()

        self.font_directories
        self.font_pairings = self._initialize_font_pairings()
        self.brand_fonts = self._initialize_brand_fonts()
        self.industry_fonts = self._initialize_industry_fonts()
        self.available_fonts = self._discover_available_fonts()
        
        # Log font setup results
        self.logger.info(f"Font setup complete. Found {len(self.available_fonts)} fonts.")
    
    """
Add this _initialize_font_pairings method to font_pairing.py to resolve the key error
"""

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




    """
Add these methods to font_pairing.py to resolve remaining initialization issues
"""

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
        },
        
        "l'oreal": {
            "headline": ["Helvetica Neue-Light", "Arial-Light", "Didot-Light"],
            "subheadline": ["Helvetica Neue", "Arial", "Didot"],
            "body": ["Helvetica Neue-Light", "Arial-Light", "Didot-Light"],
            "cta": ["Helvetica Neue-Medium", "Arial-Bold", "Didot"],
            "brand": ["Helvetica Neue-Bold", "Arial-Bold", "Didot-Bold"]
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
        },
        
        "cosmetics": {
            "headline": ["Helvetica Neue-Light", "Didot-Light", "Arial-Light", "Times New Roman-Light"],
            "subheadline": ["Helvetica Neue", "Didot", "Arial", "Times New Roman"],
            "body": ["Helvetica Neue-Light", "Didot-Light", "Arial-Light", "Times New Roman"],
            "cta": ["Helvetica Neue-Medium", "Didot", "Arial-Bold", "Times New Roman-Bold"],
            "brand": ["Helvetica Neue-Bold", "Didot-Bold", "Arial-Bold", "Times New Roman-Bold"]
        },
        
        "skincare": {
            "headline": ["Helvetica Neue-Light", "Didot-Light", "Arial-Light", "Times New Roman-Light"],
            "subheadline": ["Helvetica Neue", "Didot", "Arial", "Times New Roman"],
            "body": ["Helvetica Neue-Light", "Didot-Light", "Arial-Light", "Times New Roman"],
            "cta": ["Helvetica Neue-Medium", "Didot", "Arial-Bold", "Times New Roman-Bold"],
            "brand": ["Helvetica Neue-Bold", "Didot-Bold", "Arial-Bold", "Times New Roman-Bold"]
        }
    }




    def _setup_font_directories(self, custom_directory: Optional[str] = None) -> List[str]:
        """
        Setup font directories to search for fonts.
    
        Args:
            custom_directory: Optional custom directory to include
        
        Returns:
            List of directories to search
        """
        # Get project root directory
        try:
            from . import font_config
            custom_fonts_dir = font_config.FONTS_DIRECTORY
            self.logger.info(f"Using configured fonts directory: {custom_fonts_dir}")
        except ImportError:
            custom_fonts_dir = None
            self.logger.warning("No font_config.py found, using default locations")
    
        # Always start with the custom directory
        directories = []
    
        # Add the provided custom directory with highest priority
        if custom_directory and os.path.exists(custom_directory):
            directories.append(custom_directory)
            self.logger.info(f"Added custom font directory: {custom_directory}")
    
        # Add the configured fonts directory with next priority
        if custom_fonts_dir and os.path.exists(custom_fonts_dir):
            directories.append(custom_fonts_dir)
            self.logger.info(f"Added configured font directory: {custom_fonts_dir}")
        
        # Add current directory and sibling directories
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        # Add direct font folders
        potential_font_dirs = [
            os.path.join(parent_dir, 'fonts'),  # Main project fonts dir
            os.path.join(current_dir, 'fonts'),  # Module fonts dir
            os.path.join(os.path.dirname(parent_dir), 'fonts'),  # One level up
        ]
    
        for dir_path in potential_font_dirs:
            if os.path.exists(dir_path):
                directories.append(dir_path)
                self.logger.info(f"Added project font directory: {dir_path}")
    
        # Add system directories with lowest priority
        system_directories = [
            '/usr/share/fonts/truetype/',
            '/usr/share/fonts/',
            '/Library/Fonts/',
            'C:\\Windows\\Fonts\\',
            os.path.join(os.path.expanduser('~'), 'Library/Fonts'),
            os.path.join(os.path.expanduser('~'), '.fonts')
        ]
    
        for sys_dir in system_directories:
            if os.path.exists(sys_dir):
                directories.append(sys_dir)
                self.logger.info(f"Added system font directory: {sys_dir}")
    
        # Log all font directories
        self.logger.info(f"Font search directories: {directories}")
        return directories
    


    def _discover_available_fonts(self) -> List[str]:
        """
    Discover available fonts in all configured directories.
    
    Returns:
        List of available font names
    """
        available_fonts = []
    
    # Check each font directory
        for directory in self.font_directories:
            if not os.path.exists(directory):
                continue
            
        # Check main directory
            try:
                for file in os.listdir(directory):
                    if file.lower().endswith(('.ttf', '.otf')):
                        available_fonts.append(file)
                    
            # Check subdirectories
                for subdir in ['display', 'sans', 'serif', 'fallback', 'mono', 'variable']:
                    subdir_path = os.path.join(directory, subdir)
                    if os.path.exists(subdir_path):
                        for file in os.listdir(subdir_path):
                            if file.lower().endswith(('.ttf', '.otf')):
                                available_fonts.append(file)
            except Exception as e:
                self.logger.warning(f"Error scanning directory {directory}: {str(e)}")
    
        self.logger.info(f"Discovered {len(available_fonts)} available fonts")
        return available_fonts

    def _load_font_mapping(self) -> Dict[str, List[str]]:
        """
        Load font mapping from JSON file or use default.
    
        Returns:
            Dictionary mapping commercial fonts to open-source alternatives
        """
        default_mapping = {
            "SF Pro Display-Bold": ["OpenSans-Bold.ttf", "Roboto-Bold.ttf", "Montserrat-Bold.ttf"],
            "SF Pro Display-Light": ["OpenSans-Light.ttf", "Roboto-Light.ttf", "Montserrat-Light.ttf"],
            "SF Pro Display": ["OpenSans-Regular.ttf", "Roboto-Regular.ttf", "Montserrat-Regular.ttf"],
            "Helvetica Neue-Bold": ["OpenSans-Bold.ttf", "Roboto-Bold.ttf", "Montserrat-Bold.ttf"],
            "Helvetica Neue-Light": ["OpenSans-Light.ttf", "Roboto-Light.ttf", "Montserrat-Light.ttf"],
            "Helvetica Neue": ["OpenSans-Regular.ttf", "Roboto-Regular.ttf", "Montserrat-Regular.ttf"],
            "Arial-Bold": ["LiberationSans-Bold.ttf", "OpenSans-Bold.ttf", "Montserrat-Bold.ttf"],
            "Arial-Black": ["LiberationSans-Bold.ttf", "OpenSans-ExtraBold.ttf", "Montserrat-Black.ttf"],
            "Arial": ["LiberationSans-Regular.ttf", "OpenSans-Regular.ttf", "Montserrat-Regular.ttf"],
            "Futura-Bold": ["Montserrat-Bold.ttf", "OpenSans-Bold.ttf"],
            "Futura-Light": ["Montserrat-Light.ttf", "OpenSans-Light.ttf"],
            "Didot-Bold": ["PlayfairDisplay-Bold.ttf", "Lora-Bold.ttf", "Georgia-Bold.ttf"],
            "Didot-Light": ["PlayfairDisplay-Regular.ttf", "Lora-Regular.ttf", "Georgia.ttf"],
            "Didot": ["PlayfairDisplay-Regular.ttf", "Lora-Regular.ttf", "Georgia.ttf"],
            "Impact": ["OpenSans-ExtraBold.ttf", "Montserrat-Black.ttf"],
            "Times New Roman-Bold": ["LiberationSerif-Bold.ttf", "Georgia-Bold.ttf"],
            "Times New Roman": ["LiberationSerif-Regular.ttf", "Georgia.ttf"],
            "Gotham-Bold": ["Montserrat-Bold.ttf", "OpenSans-Bold.ttf"],
            "Gotham-Book": ["Montserrat-Medium.ttf", "OpenSans-Regular.ttf"],
            "Gotham-Light": ["Montserrat-Light.ttf", "OpenSans-Light.ttf"]
        }
    
        # Try to load from file
        mapping_paths = []
        for directory in self.font_directories:
            mapping_paths.append(os.path.join(directory, "font_mapping.json"))
            
        # Add direct paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        mapping_paths.extend([
            os.path.join(current_dir, "font_mapping.json"),
            os.path.join(os.path.dirname(current_dir), "fonts", "font_mapping.json"),
            os.path.join(os.path.dirname(current_dir), "font_mapping.json")
        ])
    
        # Try each mapping path
        for mapping_file in mapping_paths:
            try:
                if os.path.exists(mapping_file):
                    with open(mapping_file, 'r') as f:
                        mapping = json.load(f)
                    self.logger.info(f"Loaded font mapping from {mapping_file}")
                    return mapping
            except Exception as e:
                self.logger.warning(f"Could not load font mapping from {mapping_file}: {str(e)}")
    
        self.logger.warning("Using default font mapping")
        return default_mapping

    def _load_font(self, font_name: str, size: int) -> Optional[ImageFont.FreeTypeFont]:
        """
        Load a font with a streamlined approach.
        
        Args:
            font_name: Font name to load
            size: Font size
            
        Returns:
            Loaded font or None if loading fails
        """
        self.logger.debug(f"Attempting to load font: {font_name} at size {size}")
        
        # Check if this font+size is already cached
        cache_key = f"{font_name}_{size}"
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
            
        # Standard font name formats to try
        font_variations = [
            font_name,
            font_name.replace(' ', ''),
            font_name.replace('-', ''),
            font_name.replace(' ', '-'),
            font_name.replace('-', ' ')
        ]
        
        # Standard extensions to try
        extensions = ['.ttf', '.otf', '.TTF', '.OTF', '']
        
        # First try mapped alternatives
        font_mapped = self._get_mapped_font_file(font_name)
        if font_mapped:
            for directory in self.font_directories:
                # Try subdirectories first
                for subdir in ['display', 'sans', 'serif', 'fallback', 'mono', 'variable']:
                    subdir_path = os.path.join(directory, subdir)
                    if os.path.exists(subdir_path):
                        font_path = os.path.join(subdir_path, font_mapped)
                        if os.path.exists(font_path):
                            try:
                                font = ImageFont.truetype(font_path, size)
                                self.font_cache[cache_key] = font
                                self.logger.info(f"Loaded mapped font: {font_path}")
                                return font
                            except Exception as e:
                                self.logger.debug(f"Failed to load mapped font {font_path}: {str(e)}")
                
                # Also try in main directory
                font_path = os.path.join(directory, font_mapped)
                if os.path.exists(font_path):
                    try:
                        font = ImageFont.truetype(font_path, size)
                        self.font_cache[cache_key] = font
                        self.logger.info(f"Loaded mapped font: {font_path}")
                        return font
                    except Exception as e:
                        self.logger.debug(f"Failed to load mapped font {font_path}: {str(e)}")
        
        # Try direct variations with extensions
        for directory in self.font_directories:
            if not os.path.exists(directory):
                continue
                
            # Try subdirectories first
            for subdir in ['display', 'sans', 'serif', 'fallback', 'mono', 'variable']:
                subdir_path = os.path.join(directory, subdir)
                if not os.path.exists(subdir_path):
                    continue
                    
                # Try all variations with all extensions
                for variant in font_variations:
                    for ext in extensions:
                        font_path = os.path.join(subdir_path, f"{variant}{ext}")
                        if os.path.exists(font_path):
                            try:
                                font = ImageFont.truetype(font_path, size)
                                self.font_cache[cache_key] = font
                                self.logger.info(f"Loaded font: {font_path}")
                                return font
                            except Exception as e:
                                self.logger.debug(f"Failed to load font {font_path}: {str(e)}")
            
            # Also try in the main directory
            for variant in font_variations:
                for ext in extensions:
                    font_path = os.path.join(directory, f"{variant}{ext}")
                    if os.path.exists(font_path):
                        try:
                            font = ImageFont.truetype(font_path, size)
                            self.font_cache[cache_key] = font
                            self.logger.info(f"Loaded font: {font_path}")
                            return font
                        except Exception as e:
                            self.logger.debug(f"Failed to load font {font_path}: {str(e)}")
        
        # Try mapped alternatives from the whole mapping
        mapped_alternatives = []
        for mapped_name, alternatives in self.font_mapping.items():
            mapped_alternatives.extend(alternatives)
        
        # Make unique
        mapped_alternatives = list(set(mapped_alternatives))
        
        # Try these alternatives in all directories
        for alt in mapped_alternatives:
            for directory in self.font_directories:
                if not os.path.exists(directory):
                    continue
                
                # Try subdirectories
                for subdir in ['display', 'sans', 'serif', 'fallback', 'mono', 'variable']:
                    subdir_path = os.path.join(directory, subdir)
                    if not os.path.exists(subdir_path):
                        continue
                        
                    font_path = os.path.join(subdir_path, alt)
                    if os.path.exists(font_path):
                        try:
                            font = ImageFont.truetype(font_path, size)
                            self.font_cache[cache_key] = font
                            self.logger.info(f"Loaded alternative font: {font_path}")
                            return font
                        except Exception as e:
                            self.logger.debug(f"Failed to load alternative font {font_path}: {str(e)}")
                
                # Try main directory
                font_path = os.path.join(directory, alt)
                if os.path.exists(font_path):
                    try:
                        font = ImageFont.truetype(font_path, size)
                        self.font_cache[cache_key] = font
                        self.logger.info(f"Loaded alternative font: {font_path}")
                        return font
                    except Exception as e:
                        self.logger.debug(f"Failed to load alternative font {font_path}: {str(e)}")
        
        # Last resort - use PIL's default font
        try:
            default_font = ImageFont.load_default()
            self.font_cache[cache_key] = default_font
            self.logger.warning(f"Using PIL default font as last resort for {font_name}")
            return default_font
        except Exception as e:
            self.logger.error(f"Failed to load default font: {str(e)}")
            return None

    def _get_mapped_font_file(self, font_name: str) -> Optional[str]:
        """
        Get mapped font filename from the mapping.
        
        Args:
            font_name: Font name to look up
            
        Returns:
            Mapped font filename or None if not found
        """
        # Direct lookup
        if font_name in self.font_mapping:
            alternatives = self.font_mapping[font_name]
            if alternatives:
                return alternatives[0]
        
        # Try variations
        font_variations = [
            font_name,
            font_name.replace(' ', ''),
            font_name.replace('-', ''),
            font_name.replace(' ', '-'),
            font_name.replace('-', ' ')
        ]
        
        for variant in font_variations:
            if variant in self.font_mapping:
                alternatives = self.font_mapping[variant]
                if alternatives:
                    return alternatives[0]
        
        # Try partial match
        for mapped_name, alternatives in self.font_mapping.items():
            if mapped_name in font_name or font_name in mapped_name:
                if alternatives:
                    return alternatives[0]
        
        # No mapping found
        return None

    def validate_font_directories(self) -> 'FontPairingEngine':
        """
        Validate font directories and log availability.
        
        Returns:
            Self for method chaining
        """
        self.logger.info("Validating font directory structure...")
        
        found_fonts = {}
        
        # Check each directory
        for directory in self.font_directories:
            if os.path.exists(directory):
                self.logger.info(f"Font directory exists: {directory}")
                
                # Check for font files in main directory
                main_fonts = [f for f in os.listdir(directory) 
                            if f.lower().endswith(('.ttf', '.otf'))]
                found_fonts[directory] = len(main_fonts)
                
                # Check subdirectories
                expected_subdirs = ['display', 'sans', 'serif', 'fallback', 'mono', 'variable']
                for subdir in expected_subdirs:
                    subdir_path = os.path.join(directory, subdir)
                    if os.path.exists(subdir_path):
                        # Count fonts in this subdirectory
                        subdir_fonts = [f for f in os.listdir(subdir_path) 
                                      if f.lower().endswith(('.ttf', '.otf'))]
                        found_fonts[subdir_path] = len(subdir_fonts)
                        self.logger.info(f"  - {subdir}: {len(subdir_fonts)} fonts")
            else:
                self.logger.warning(f"Font directory does not exist: {directory}")
        
        # Test load some common fonts
        self.logger.info("Testing font loading capability:")
        test_fonts = ["Arial", "Arial-Bold", "Montserrat", "Montserrat-Bold", "OpenSans", "OpenSans-Bold"]
        for font_name in test_fonts:
            test_font = self._load_font(font_name, 36)
            result = "SUCCESS" if test_font is not None else "FAILED"
            self.logger.info(f"  - {font_name}: {result}")
        
        # Determine if we have enough fonts for the system to function
        font_count = sum(found_fonts.values())
        if font_count < 3:
            self.logger.warning(f"Only {font_count} fonts found, system may not function properly.")
            self.logger.warning("Consider downloading and installing free fonts like Montserrat, Open Sans, or Roboto.")
        else:
            self.logger.info(f"Found {font_count} fonts, system should function properly.")
        
        return self

    def debug_fonts(self) -> 'FontPairingEngine':
        """
        Debug detailed font information to help diagnose issues.
        
        Returns:
            Self for method chaining
        """
        self.logger.info("==== FONT SYSTEM DEBUG INFORMATION ====")
        
        # 1. Check font directories
        self.logger.info("Font directories:")
        for i, directory in enumerate(self.font_directories):
            exists = os.path.exists(directory)
            self.logger.info(f"  {i+1}. {directory} - {'EXISTS' if exists else 'MISSING'}")
            
            if exists:
                # List some fonts in this directory
                try:
                    files = os.listdir(directory)
                    fonts = [f for f in files if f.lower().endswith(('.ttf', '.otf'))]
                    self.logger.info(f"    Found {len(fonts)} font files")
                    if fonts:
                        self.logger.info(f"    Examples: {', '.join(fonts[:5])}")
                except Exception as e:
                    self.logger.error(f"Error reading directory: {str(e)}")
        
        # 2. Check font mapping
        self.logger.info("Font mapping:")
        for i, (font_name, alternatives) in enumerate(list(self.font_mapping.items())[:10]):
            self.logger.info(f"  {i+1}. {font_name} → {', '.join(alternatives)}")
        
        # 3. Test font loading
        self.logger.info("Font loading tests:")
        test_fonts = [
            "Arial", "Arial-Bold", 
            "Helvetica Neue", "Helvetica Neue-Bold",
            "Montserrat", "Montserrat-Bold",
            "OpenSans", "OpenSans-Bold",
            "Roboto", "Roboto-Bold"
        ]
        
        for font_name in test_fonts:
            font = self._load_font(font_name, 36)
            result = "SUCCESS" if font is not None else "FAILED"
            self.logger.info(f"  {font_name}: {result}")
        
        # 4. Check for common fallback fonts
        self.logger.info("Fallback font availability:")
        fallbacks = ["Montserrat-Regular.ttf", "OpenSans-Regular.ttf", "Roboto-Regular.ttf", "LiberationSans-Regular.ttf"]
        
        for fallback in fallbacks:
            found = False
            for directory in self.font_directories:
                path = os.path.join(directory, fallback)
                if os.path.exists(path):
                    found = True
                    self.logger.info(f"  {fallback}: FOUND at {path}")
                    break
            
            if not found:
                self.logger.warning(f"  {fallback}: NOT FOUND")
        
        self.logger.info("====================================")
        return self

    # The rest of the class remains unchanged...
    # (methods like _initialize_font_pairings, _initialize_brand_fonts, 
    #  _initialize_industry_fonts, _discover_available_fonts, etc.)
    
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
                self.logger.info(f"Using brand-specific fonts for: {brand_key}")
        
        # Check for industry-specific fonts next
        if not font_list and industry:
            industry_key = self._find_matching_industry(industry)
            if industry_key and industry_key in self.industry_fonts:
                font_list = self.industry_fonts[industry_key]
                self.logger.info(f"Using industry-specific fonts for: {industry_key}")
        
        # Fall back to style-based fonts
        if not font_list:
            # Map style to a known pairing
            pairing_key = self._map_style_to_pairing(style)
            if pairing_key in self.font_pairings:
                font_list = self.font_pairings[pairing_key]
                self.logger.info(f"Using style-based fonts for: {pairing_key}")
            else:
                # Use modern as default
                font_list = self.font_pairings["modern"]
                self.logger.info(f"Using default modern fonts (style '{style}' not found)")
        
        # Load fonts for each element
        fonts = {}
        success_count = 0
        for element in ['headline', 'subheadline', 'body', 'cta', 'brand']:
            element_font = self._load_font_for_element(
                element, 
                font_list.get(element, []), 
                font_list.get('fallbacks', []),
                sizes[element]
            )
            
            if element_font:
                fonts[element] = element_font
                success_count += 1
            else:
                self.logger.warning(f"Failed to load font for {element}")
        
        self.logger.info(f"Loaded {success_count}/5 fonts for typography")
        
        # Ensure we have at least a minimal set of fonts
        if success_count < 5:
            self.logger.warning("Not all fonts were loaded, using emergency fallbacks")
            # Try to load basic system fonts
            for element in ['headline', 'subheadline', 'body', 'cta', 'brand']:
                if element not in fonts or fonts[element] is None:
                    # Try a sequence of reliable fallbacks
                    for fallback in ["Montserrat", "OpenSans", "Arial", "Helvetica"]:
                        emergency_font = self._load_font(fallback, sizes[element])
                        if emergency_font:
                            fonts[element] = emergency_font
                            self.logger.info(f"Using emergency fallback {fallback} for {element}")
                            break
        
        return fonts
    
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
        cache_key = f"{element}_{size}_{','.join(font_list[:2] if font_list else ['default'])}"
    
        # Check cache
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
    
        # Try each font in the list
        for font_name in font_list:
            font = self._load_font(font_name, size)
            if font:
                # Cache the result
                self.font_cache[cache_key] = font
                self.logger.info(f"Loaded font for {element}: {font_name}")
                return font
    
        # Try fallbacks
        for font_name in fallbacks:
            font = self._load_font(font_name, size)
            if font:
                # Cache the result
                self.font_cache[cache_key] = font
                self.logger.info(f"Using fallback font for {element}: {font_name}")
                return font
    
        # Last resort - try project bundled fonts
        project_fallbacks = [
            "OpenSans-Regular.ttf",
            "Roboto-Regular.ttf",
            "LiberationSans-Regular.ttf",
            "Montserrat-Regular.ttf"
        ]
    
        for fallback in project_fallbacks:
            font = self._load_font(fallback, size)
            if font:
                self.font_cache[cache_key] = font
                self.logger.info(f"Using project fallback font for {element}: {fallback}")
                return font
    
        # Try PIL default font as absolute last resort
        try:
            default_font = ImageFont.load_default()
            self.logger.warning(f"Using PIL default font for {element} as last resort")
            self.font_cache[cache_key] = default_font
            return default_font
        except Exception as e:
            self.logger.error(f"Could not load any fonts for {element}: {str(e)}")
            return None

    def _find_matching_brand(self, brand_name: str) -> Optional[str]:
        """Find a matching brand in the brand fonts database."""
        if not brand_name or not self.brand_fonts:
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
            "lv": "louis vuitton",
            "l'oréal": "l'oreal",
            "loreal": "l'oreal"
        }
        
        for alias, brand_key in brand_aliases.items():
            if alias in brand_lower and brand_key in self.brand_fonts:
                return brand_key
                
        return None
    
    def _find_matching_industry(self, industry: str) -> Optional[str]:
        """Find a matching industry in the industry fonts database."""
        if not industry or not self.industry_fonts:
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
            "skincare": "skincare",
            "makeup": "cosmetics",
            "haircare": "beauty",
            "perfume": "beauty",
            "face cream": "skincare",
            
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
        """Map a style name to a font pairing."""
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