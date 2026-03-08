"""
Brand Typography Manager for Professional Ad Generation
Provides brand-specific typography styles and rules based on brand identity
"""
import os
import logging
import re
from typing import Dict, List, Tuple, Any, Optional, Union
import numpy as np
from PIL import Image, ImageColor

class BrandTypographyManager:
    """
    Manages typography rules and styles specific to different brands and industries.
    Provides intelligent style selection for professional advertising typography.
    """
    
    def __init__(self, fonts_directory: Optional[str] = None):
        """
        Initialize the brand typography manager.
        
        Args:
            fonts_directory: Optional custom fonts directory
        """
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize directories
        self.fonts_directory = fonts_directory
        
        # Load style presets
        self.style_presets = self._load_style_presets()
        
        # Load industry typographic standards
        self.industry_standards = self._load_industry_standards()
        
        # Load brand-specific style guides
        self.brand_style_guides = self._load_brand_style_guides()
    
    def _load_style_presets(self) -> Dict[str, Dict[str, Any]]:
        """
        Load typography style presets for different design approaches.
        
        Returns:
            Dictionary of style presets
        """
        return {
            "modern": {
                "description": "Clean, minimal typography with sans-serif fonts",
                "fonts": {
                    "headline": ["SF Pro Display-Bold", "Helvetica Neue-Bold", "Arial-Bold"],
                    "subheadline": ["SF Pro Text", "Helvetica Neue", "Arial"],
                    "body": ["SF Pro Text-Light", "Helvetica Neue-Light", "Arial"],
                    "cta": ["SF Pro Display-Semibold", "Helvetica Neue-Bold", "Arial-Bold"],
                    "brand": ["SF Pro Display-Bold", "Helvetica Neue-Bold", "Arial-Bold"],
                },
                "text_treatments": {
                    "headline": "clean_gradient",
                    "subheadline": "simple",
                    "body": "simple",
                    "cta": "simple",
                    "brand": "simple"
                },
                "text_placement": "centered",
                "text_proportions": {
                    "headline_size": 0.08,  # Relative to image height
                    "subheadline_size": 0.04,
                    "body_size": 0.032,
                    "cta_size": 0.038,
                    "brand_size": 0.05
                },
                "layout_spacing": {
                    "headline_to_subheadline": 0.025,  # Relative to image height
                    "subheadline_to_body": 0.02,
                    "body_to_cta": 0.04
                },
                "cta_style": "rounded",
                "background_style": "none",
                "color_strategy": "brand_colors"
            },
            
            "luxury": {
                "description": "Elegant, sophisticated typography with serif fonts",
                "fonts": {
                    "headline": ["Didot-Bold", "Baskerville-Bold", "Times New Roman-Bold"],
                    "subheadline": ["Didot", "Baskerville", "Times New Roman"],
                    "body": ["Didot-Light", "Baskerville", "Times New Roman"],
                    "cta": ["Didot-Bold", "Baskerville-Bold", "Times New Roman-Bold"],
                    "brand": ["Didot-Bold", "Baskerville-Bold", "Times New Roman-Bold"],
                },
                "text_treatments": {
                    "headline": "elegant_serif",
                    "subheadline": "simple",
                    "body": "simple",
                    "cta": "simple",
                    "brand": "simple"
                },
                "text_placement": "bottom_centered",
                "text_proportions": {
                    "headline_size": 0.07,
                    "subheadline_size": 0.035,
                    "body_size": 0.03,
                    "cta_size": 0.035,
                    "brand_size": 0.045
                },
                "layout_spacing": {
                    "headline_to_subheadline": 0.02,
                    "subheadline_to_body": 0.015,
                    "body_to_cta": 0.035
                },
                "cta_style": "minimal_line",
                "background_style": "none",
                "color_strategy": "monochromatic"
            },
            
            "bold": {
                "description": "Strong, impactful typography with heavy fonts",
                "fonts": {
                    "headline": ["Impact", "Helvetica Neue-Black", "Arial-Black"],
                    "subheadline": ["Helvetica Neue-Bold", "Arial-Bold"],
                    "body": ["Helvetica Neue", "Arial"],
                    "cta": ["Helvetica Neue-Bold", "Arial-Bold"],
                    "brand": ["Helvetica Neue-Black", "Arial-Black"],
                },
                "text_treatments": {
                    "headline": "dynamic_bold",
                    "subheadline": "simple",
                    "body": "simple",
                    "cta": "simple",
                    "brand": "simple"
                },
                "text_placement": "dynamic",
                "text_proportions": {
                    "headline_size": 0.09,
                    "subheadline_size": 0.045,
                    "body_size": 0.035,
                    "cta_size": 0.04,
                    "brand_size": 0.05
                },
                "layout_spacing": {
                    "headline_to_subheadline": 0.02,
                    "subheadline_to_body": 0.02,
                    "body_to_cta": 0.03
                },
                "cta_style": "pill",
                "background_style": "none",
                "color_strategy": "contrasting"
            },
            
            "minimalist": {
                "description": "Ultra-clean typography with light fonts and ample whitespace",
                "fonts": {
                    "headline": ["Helvetica Neue-Light", "SF Pro Display-Light", "Arial"],
                    "subheadline": ["Helvetica Neue-Light", "SF Pro Text-Light", "Arial"],
                    "body": ["Helvetica Neue-Light", "SF Pro Text-Light", "Arial"],
                    "cta": ["Helvetica Neue", "SF Pro Text", "Arial"],
                    "brand": ["Helvetica Neue-Light", "SF Pro Display-Light", "Arial"],
                },
                "text_treatments": {
                    "headline": "minimal_elegant",
                    "subheadline": "simple",
                    "body": "simple",
                    "cta": "simple",
                    "brand": "simple"
                },
                "text_placement": "centered",
                "text_proportions": {
                    "headline_size": 0.08,
                    "subheadline_size": 0.035,
                    "body_size": 0.03,
                    "cta_size": 0.035,
                    "brand_size": 0.045
                },
                "layout_spacing": {
                    "headline_to_subheadline": 0.03,
                    "subheadline_to_body": 0.025,
                    "body_to_cta": 0.04
                },
                "cta_style": "minimal_line",
                "background_style": "none",
                "color_strategy": "monochromatic"
            },
            
            "dramatic": {
                "description": "High-contrast, cinematic typography with overlay effects",
                "fonts": {
                    "headline": ["Gotham-Black", "Montserrat-Black", "Arial-Black"],
                    "subheadline": ["Gotham-Book", "Montserrat", "Arial"],
                    "body": ["Gotham-Light", "Montserrat-Light", "Arial"],
                    "cta": ["Gotham-Bold", "Montserrat-Bold", "Arial-Bold"],
                    "brand": ["Gotham-Black", "Montserrat-Black", "Arial-Black"],
                },
                "text_treatments": {
                    "headline": "premium_gradient",
                    "subheadline": "subtle_glow",
                    "body": "simple",
                    "cta": "simple",
                    "brand": "simple"
                },
                "text_placement": "text_overlay",
                "text_proportions": {
                    "headline_size": 0.085,
                    "subheadline_size": 0.04,
                    "body_size": 0.032,
                    "cta_size": 0.038,
                    "brand_size": 0.05
                },
                "layout_spacing": {
                    "headline_to_subheadline": 0.025,
                    "subheadline_to_body": 0.02,
                    "body_to_cta": 0.035
                },
                "cta_style": "gradient",
                "background_style": "gradient",
                "color_strategy": "dramatic"
            }
        }
    
    def _load_industry_standards(self) -> Dict[str, Dict[str, Any]]:
        """
        Load typography standards for different industries.
        
        Returns:
            Dictionary of industry standards
        """
        return {
            "technology": {
                "style_base": "modern",
                "fonts": {
                    "headline": ["SF Pro Display-Bold", "Helvetica Neue-Bold", "Arial-Bold"],
                    "subheadline": ["SF Pro Text", "Helvetica Neue", "Arial"],
                    "body": ["SF Pro Text-Light", "Helvetica Neue-Light", "Arial"],
                    "cta": ["SF Pro Display-Semibold", "Helvetica Neue-Bold", "Arial-Bold"],
                    "brand": ["SF Pro Display-Bold", "Helvetica Neue-Bold", "Arial-Bold"],
                },
                "text_treatments": {
                    "headline": "clean_gradient",
                    "subheadline": "simple",
                    "body": "simple",
                    "cta": "simple",
                    "brand": "simple"
                },
                "colors": {
                    "primary": [(41, 128, 185, 255), (52, 152, 219, 255)],  # Blue tones
                    "accent": [(46, 204, 113, 255), (26, 188, 156, 255)],  # Green/teal accents
                    "text": [(255, 255, 255, 255), (52, 73, 94, 255)]  # White and dark blue
                }
            },
            
            "fashion": {
                "style_base": "minimalist",
                "fonts": {
                    "headline": ["Didot-Light", "Futura-Light", "Times New Roman-Light"],
                    "subheadline": ["Futura-Light", "Didot", "Helvetica Neue-Light"],
                    "body": ["Futura-Light", "Helvetica Neue-Light", "Arial-Light"],
                    "cta": ["Futura-Medium", "Helvetica Neue", "Arial"],
                    "brand": ["Didot", "Futura-Light", "Helvetica Neue-Light"],
                },
                "text_treatments": {
                    "headline": "minimal_elegant",
                    "subheadline": "simple",
                    "body": "simple",
                    "cta": "simple",
                    "brand": "simple"
                },
                "text_placement": "bottom_left",
                "colors": {
                    "primary": [(0, 0, 0, 255), (25, 25, 25, 255)],  # Black/near black
                    "accent": [(255, 255, 255, 255), (200, 200, 200, 255)],  # White/light gray
                    "text": [(255, 255, 255, 255), (0, 0, 0, 255)]  # White and black
                }
            },
            
            "luxury": {
                "style_base": "luxury",
                "fonts": {
                    "headline": ["Didot-Bold", "Baskerville-Bold", "Times New Roman-Bold"],
                    "subheadline": ["Didot", "Baskerville", "Times New Roman"],
                    "body": ["Didot-Light", "Baskerville", "Times New Roman"],
                    "cta": ["Didot-Bold", "Baskerville-Bold", "Times New Roman-Bold"],
                    "brand": ["Didot-Bold", "Baskerville-Bold", "Times New Roman-Bold"],
                },
                "text_treatments": {
                    "headline": "elegant_serif",
                    "subheadline": "simple",
                    "body": "simple",
                    "cta": "simple",
                    "brand": "luxury_metallic"
                },
                "text_placement": "bottom_centered",
                "colors": {
                    "primary": [(0, 0, 0, 255), (20, 20, 20, 255)],  # Black
                    "accent": [(212, 175, 55, 255), (207, 181, 59, 255)],  # Gold
                    "text": [(255, 255, 255, 255), (212, 175, 55, 255)]  # White and gold
                }
            },
            
            "food": {
                "style_base": "bold",
                "fonts": {
                    "headline": ["Gotham-Bold", "Montserrat-Bold", "Arial-Bold"],
                    "subheadline": ["Gotham-Book", "Montserrat", "Arial"],
                    "body": ["Gotham-Light", "Montserrat-Light", "Arial"],
                    "cta": ["Gotham-Bold", "Montserrat-Bold", "Arial-Bold"],
                    "brand": ["Gotham-Bold", "Montserrat-Bold", "Arial-Bold"],
                },
                "text_treatments": {
                    "headline": "vibrant_overlay",
                    "subheadline": "simple",
                    "body": "simple",
                    "cta": "simple",
                    "brand": "simple"
                },
                "text_placement": "bottom_centered",
                "colors": {
                    "primary": [(211, 84, 0, 255), (230, 126, 34, 255)],  # Orange tones
                    "accent": [(46, 204, 113, 255), (39, 174, 96, 255)],  # Green accents
                    "text": [(255, 255, 255, 255), (236, 240, 241, 255)]  # White and light gray
                }
            },
            
            "beauty": {
                "style_base": "minimalist",
                "fonts": {
                    "headline": ["Helvetica Neue-Light", "Didot-Light", "Gotham-Light"],
                    "subheadline": ["Helvetica Neue-Light", "Didot", "Gotham-Light"],
                    "body": ["Helvetica Neue-Light", "Gotham-Light", "Arial-Light"],
                    "cta": ["Helvetica Neue", "Gotham-Book", "Arial"],
                    "brand": ["Helvetica Neue-Light", "Didot", "Gotham-Light"],
                },
                "text_treatments": {
                    "headline": "subtle_glow",
                    "subheadline": "simple",
                    "body": "simple",
                    "cta": "simple",
                    "brand": "simple"
                },
                "text_placement": "centered",
                "colors": {
                    "primary": [(155, 89, 182, 255), (142, 68, 173, 255)],  # Purple tones
                    "accent": [(241, 196, 15, 255), (243, 156, 18, 255)],  # Gold/yellow accents
                    "text": [(255, 255, 255, 255), (52, 73, 94, 255)]  # White and dark blue
                }
            }
        }
    
    def _load_brand_style_guides(self) -> Dict[str, Dict[str, Any]]:
        """
        Load brand-specific style guides for typography.
        
        Returns:
            Dictionary of brand style guides
        """
        return {
            "apple": {
                "description": "Clean, minimal typography in Apple's distinctive style",
                "fonts": {
                    "headline": ["SF Pro Display-Light", "Helvetica Neue-Light", "Arial-Light"],
                    "subheadline": ["SF Pro Text", "Helvetica Neue", "Arial"],
                    "body": ["SF Pro Text-Light", "Helvetica Neue-Light", "Arial"],
                    "cta": ["SF Pro Text", "Helvetica Neue", "Arial"],
                    "brand": ["SF Pro Display-Medium", "Helvetica Neue-Medium", "Arial-Bold"],
                },
                "text_treatments": {
                    "headline": "minimal_elegant",
                    "subheadline": "simple",
                    "body": "simple",
                    "cta": "simple",
                    "brand": "simple"
                },
                "text_placement": "centered",
                "text_proportions": {
                    "headline_size": 0.08,
                    "subheadline_size": 0.035,
                    "body_size": 0.025,
                    "cta_size": 0.03,
                    "brand_size": 0.04
                },
                "cta_style": "minimal_line",
                "color_overrides": {
                    "text_color": (255, 255, 255, 255),
                    "accent_color": (0, 122, 255, 255)
                },
                "layout_spacing": {
                    "headline_to_subheadline": 0.02,
                    "subheadline_to_body": 0.02,
                    "body_to_cta": 0.04
                }
            },
            
            "nike": {
                "description": "Bold, dynamic typography with Nike's iconic style",
                "fonts": {
                    "headline": ["Futura-Bold", "Helvetica Neue-Bold", "Arial-Black"],
                    "subheadline": ["Futura-Medium", "Helvetica Neue", "Arial"],
                    "body": ["Futura-Medium", "Helvetica Neue", "Arial"],
                    "cta": ["Futura-Bold", "Helvetica Neue-Bold", "Arial-Bold"],
                    "brand": ["Futura-Bold", "Helvetica Neue-Bold", "Arial-Black"],
                },
                "text_treatments": {
                    "headline": "nike_bold",
                    "subheadline": "simple",
                    "body": "simple",
                    "cta": "simple",
                    "brand": "simple"
                },
                "text_placement": "bottom_left",
                "text_proportions": {
                    "headline_size": 0.09,
                    "subheadline_size": 0.04,
                    "body_size": 0.035,
                    "cta_size": 0.04,
                    "brand_size": 0.045
                },
                "cta_style": "minimal_line",
                "color_overrides": {
                    "text_color": (255, 255, 255, 255),
                    "accent_color": (255, 255, 255, 255)
                },
                "text_transform": {
                    "headline": "uppercase",
                    "cta": "uppercase"
                },
                "layout_spacing": {
                    "headline_to_subheadline": 0.015,
                    "subheadline_to_body": 0.015,
                    "body_to_cta": 0.03
                }
            },
            
            "coca-cola": {
                "description": "Classic, bold typography with Coca-Cola's iconic style",
                "fonts": {
                    "headline": ["TCCC-UnityHeadline", "Gotham-Bold", "Arial-Bold"],
                    "subheadline": ["TCCC-UnityText", "Gotham-Book", "Arial"],
                    "body": ["TCCC-UnityText", "Gotham-Book", "Arial"],
                    "cta": ["TCCC-UnityHeadline", "Gotham-Bold", "Arial-Bold"],
                    "brand": ["TCCC-UnityHeadline", "Gotham-Bold", "Arial-Black"],
                },
                "text_treatments": {
                    "headline": "dynamic_bold",
                    "subheadline": "simple",
                    "body": "simple",
                    "cta": "simple",
                    "brand": "simple"
                },
                "text_placement": "centered",
                "text_proportions": {
                    "headline_size": 0.08,
                    "subheadline_size": 0.035,
                    "body_size": 0.03,
                    "cta_size": 0.04,
                    "brand_size": 0.045
                },
                "cta_style": "rounded",
                "color_overrides": {
                    "text_color": (255, 255, 255, 255),
                    "accent_color": (237, 28, 36, 255)  # Coca-Cola red
                },
                "layout_spacing": {
                    "headline_to_subheadline": 0.02,
                    "subheadline_to_body": 0.02,
                    "body_to_cta": 0.03
                }
            },
            
            "louis vuitton": {
                "description": "Elegant, sophisticated typography with luxury feel",
                "fonts": {
                    "headline": ["Futura-Light", "Didot-Light", "Times New Roman-Light"],
                    "subheadline": ["Futura-Light", "Didot", "Times New Roman"],
                    "body": ["Futura-Light", "Didot-Light", "Times New Roman"],
                    "cta": ["Futura-Medium", "Didot", "Times New Roman"],
                    "brand": ["Futura-Medium", "Didot-Bold", "Times New Roman-Bold"],
                },
                "text_treatments": {
                    "headline": "luxury_metallic",
                    "subheadline": "simple",
                    "body": "simple",
                    "cta": "simple",
                    "brand": "simple"
                },
                "text_placement": "bottom_centered",
                "text_proportions": {
                    "headline_size": 0.07,
                    "subheadline_size": 0.035,
                    "body_size": 0.03,
                    "cta_size": 0.035,
                    "brand_size": 0.05
                },
                "cta_style": "minimal_line",
                "color_overrides": {
                    "text_color": (255, 255, 255, 255),
                    "accent_color": (212, 175, 55, 255)  # Gold
                },
                "text_transform": {
                    "headline": "uppercase",
                    "brand": "uppercase"
                },
                "letter_spacing": {
                    "headline": 0.15,
                    "brand": 0.15
                },
                "layout_spacing": {
                    "headline_to_subheadline": 0.025,
                    "subheadline_to_body": 0.02,
                    "body_to_cta": 0.04
                }
            }
        }
    
    def get_typography_style(self,
                           style_name: Optional[str] = None,
                           brand_name: Optional[str] = None,
                           industry: Optional[str] = None,
                           brand_level: Optional[str] = None,
                           style_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get typography style based on brand, industry and level.
        
        Args:
            style_name: Optional style preset name
            brand_name: Optional brand name for brand-specific styling
            industry: Optional industry for industry-specific styling
            brand_level: Optional brand positioning
            style_overrides: Optional style override properties
            
        Returns:
            Typography style dictionary
        """
        # Start with a base style
        base_style = None
        
        # Check if we have a specific style name
        if style_name and style_name in self.style_presets:
            base_style = self.style_presets[style_name].copy()
        
        # Check for brand-specific style
        elif brand_name:
            brand_key = self._find_matching_brand(brand_name)
            if brand_key:
                base_style = self.brand_style_guides[brand_key].copy()
        
        # Check for industry-specific style
        elif industry:
            industry_key = self._find_matching_industry(industry)
            if industry_key:
                # Get industry base
                industry_standards = self.industry_standards[industry_key]
                
                # Get referenced style base
                style_base = industry_standards.get('style_base', 'modern')
                if style_base in self.style_presets:
                    base_style = self.style_presets[style_base].copy()
                    
                    # Override with industry specifics
                    for key, value in industry_standards.items():
                        if key != 'style_base':
                            if isinstance(value, dict) and key in base_style and isinstance(base_style[key], dict):
                                # Merge dictionaries for nested objects
                                base_style[key].update(value)
                            else:
                                # Direct override
                                base_style[key] = value
        
        # If still no style, use appropriate default based on brand level
        if not base_style:
            if brand_level:
                brand_level_lower = brand_level.lower()
                if 'luxury' in brand_level_lower or 'premium' in brand_level_lower:
                    base_style = self.style_presets['luxury'].copy()
                elif 'bold' in brand_level_lower or 'dramatic' in brand_level_lower:
                    base_style = self.style_presets['bold'].copy()
                elif 'minimal' in brand_level_lower or 'clean' in brand_level_lower:
                    base_style = self.style_presets['minimalist'].copy()
                else:
                    base_style = self.style_presets['modern'].copy()
            else:
                # Default to modern
                base_style = self.style_presets['modern'].copy()
        
        # Apply any style overrides
        if style_overrides:
            for key, value in style_overrides.items():
                if isinstance(value, dict) and key in base_style and isinstance(base_style[key], dict):
                    # Merge dictionaries for nested objects
                    base_style[key].update(value)
                else:
                    # Direct override
                    base_style[key] = value
        
        return base_style
    
    def _find_matching_brand(self, brand_name: str) -> Optional[str]:
        """
        Find a matching brand in the style guides.
        
        Args:
            brand_name: Brand name to match
            
        Returns:
            Matched brand key or None if not found
        """
        if not brand_name:
            return None
            
        brand_lower = brand_name.lower()
        
        # Direct match
        if brand_lower in self.brand_style_guides:
            return brand_lower
        
        # Partial match
        for brand_key in self.brand_style_guides.keys():
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
            "adidas": "adidas",  # Hypothetical entry
            "samsung": "samsung",  # Hypothetical entry
            "galaxy": "samsung",  # Hypothetical entry
            "coca cola": "coca-cola",
            "coke": "coca-cola",
            "lv": "louis vuitton"
        }
        
        for alias, brand_key in brand_aliases.items():
            if alias in brand_lower and brand_key in self.brand_style_guides:
                return brand_key
                
        return None
    
    def _find_matching_industry(self, industry: str) -> Optional[str]:
        """
        Find a matching industry in the standards database.
        
        Args:
            industry: Industry to match
            
        Returns:
            Matched industry key or None if not found
        """
        if not industry:
            return None
            
        industry_lower = industry.lower()
        
        # Direct match
        if industry_lower in self.industry_standards:
            return industry_lower
        
        # Partial match
        for industry_key in self.industry_standards.keys():
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
            "perfume": "beauty"
        }
        
        for category, industry_key in industry_categories.items():
            if category in industry_lower and industry_key in self.industry_standards:
                return industry_key
        
        return None
    
    def generate_color_scheme(self,
                            image: Image.Image,
                            typography_style: Dict[str, Any],
                            brand_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a color scheme for typography based on the image and style.
        
        Args:
            image: Image to extract colors from
            typography_style: Typography style dictionary
            brand_name: Optional brand name for brand colors
            
        Returns:
            Color scheme dictionary
        """
        # Extract dominant colors from image
        dominant_colors = self._extract_dominant_colors(image)
        
        # Calculate image brightness
        brightness = self._calculate_image_brightness(image)
        
        # Determine text color based on brightness
        if brightness > 0.5:
            text_color = (30, 30, 30, 255)  # Dark text for light images
        else:
            text_color = (255, 255, 255, 255)  # Light text for dark images
        
        # Get color strategy from style
        color_strategy = typography_style.get('color_strategy', 'brand_colors')
        
        # Check for brand-specific colors
        brand_colors = self._get_brand_colors(brand_name)
        
        # Color scheme to return
        color_scheme = {
            "text_color": text_color,
            "headline_color": text_color,
            "subheadline_color": text_color,
            "body_color": text_color,
            "cta_color": text_color,
            "brand_color": text_color,
            "accent_color": None,
            "button_color": None,
            "background_color": None
        }
        
        # Apply color strategy
        if color_strategy == 'brand_colors' and brand_colors:
            # Use brand colors
            color_scheme["accent_color"] = brand_colors.get("primary", (41, 128, 185, 230))
            color_scheme["button_color"] = brand_colors.get("primary", (41, 128, 185, 230))
            
            # Ensure adequate contrast for text
            if brightness > 0.5:
                # Light image - see if brand color works for text
                brand_text = brand_colors.get("dark_text", text_color)
                color_scheme["text_color"] = brand_text
                color_scheme["headline_color"] = brand_text
                color_scheme["subheadline_color"] = brand_text
                color_scheme["body_color"] = brand_text
                color_scheme["cta_color"] = (255, 255, 255, 255)  # White CTA text
                color_scheme["brand_color"] = brand_text
            else:
                # Dark image - use light brand text
                brand_text = brand_colors.get("light_text", text_color)
                color_scheme["text_color"] = brand_text
                color_scheme["headline_color"] = brand_text
                color_scheme["subheadline_color"] = brand_text
                color_scheme["body_color"] = brand_text
                color_scheme["cta_color"] = (255, 255, 255, 255)  # White CTA text
                color_scheme["brand_color"] = brand_text
                
        elif color_strategy == 'image_derived':
            # Use colors derived from the image
            if dominant_colors:
                dominant = dominant_colors[0]
                color_scheme["accent_color"] = (*dominant, 230)
                color_scheme["button_color"] = (*dominant, 230)
                
                # Check if the dominant color has enough contrast with text
                luminance = (0.299 * dominant[0] + 0.587 * dominant[1] + 0.114 * dominant[2]) / 255
                if abs(luminance - (brightness > 0.5)) < 0.3:
                    # Not enough contrast, use complementary color
                    complementary = self._get_complementary_color(dominant)
                    color_scheme["accent_color"] = (*complementary, 230)
                    color_scheme["button_color"] = (*complementary, 230)
                    
        elif color_strategy == 'monochromatic':
            # Use monochromatic scheme based on brightness
            if brightness > 0.5:
                # Light image - use dark accent
                color_scheme["accent_color"] = (30, 30, 30, 230)
                color_scheme["button_color"] = (30, 30, 30, 230)
            else:
                # Dark image - use light accent
                color_scheme["accent_color"] = (245, 245, 245, 230)
                color_scheme["button_color"] = (245, 245, 245, 230)
                
        elif color_strategy == 'dramatic':
            # High contrast, dramatic colors
            if brightness > 0.5:
                # Light image - use bold, dark colors
                color_scheme["accent_color"] = (48, 63, 159, 230)  # Deep blue
                color_scheme["button_color"] = (48, 63, 159, 230)
                color_scheme["background_color"] = (0, 0, 0, 160)  # Semi-transparent black
            else:
                # Dark image - use vibrant accent
                color_scheme["accent_color"] = (255, 87, 34, 230)  # Deep orange
                color_scheme["button_color"] = (255, 87, 34, 230)
                color_scheme["background_color"] = (0, 0, 0, 180)  # More opaque black
                
        elif color_strategy == 'contrasting':
            # Use contrasting color to dominant
            if dominant_colors:
                dominant = dominant_colors[0]
                complementary = self._get_complementary_color(dominant)
                color_scheme["accent_color"] = (*complementary, 230)
                color_scheme["button_color"] = (*complementary, 230)
                
                # Use dominant as background if it has enough contrast with text
                luminance = (0.299 * dominant[0] + 0.587 * dominant[1] + 0.114 * dominant[2]) / 255
                if abs(luminance - (brightness > 0.5)) > 0.4:
                    color_scheme["background_color"] = (*dominant, 120)  # Semi-transparent
        
        # Apply any color overrides from the style
        color_overrides = typography_style.get('color_overrides', {})
        for key, value in color_overrides.items():
            if key in color_scheme:
                color_scheme[key] = value
            
        return color_scheme
    
    def _extract_dominant_colors(self, image: Image.Image, num_colors: int = 5) -> List[Tuple[int, int, int]]:
        """
        Extract dominant colors from an image.
        
        Args:
            image: PIL Image object
            num_colors: Number of colors to extract
            
        Returns:
            List of RGB tuples representing dominant colors
        """
        # Resize image for faster processing
        img_small = image.resize((100, 100), Image.Resampling.LANCZOS)
        
        # Convert to RGB if needed
        if img_small.mode != 'RGB':
            img_small = img_small.convert('RGB')
        
        # Get colors
        pixels = [tuple(p) for p in np.array(img_small).reshape(-1, 3)]
        
        # Count occurrences of each color
        color_counts = {}
        for pixel in pixels:
            if pixel in color_counts:
                color_counts[pixel] += 1
            else:
                color_counts[pixel] = 1
        
        # Sort by frequency
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Return top colors
        return [color for color, count in sorted_colors[:num_colors]]
    
    def _calculate_image_brightness(self, image: Image.Image) -> float:
        """
        Calculate the overall brightness of an image.
        
        Args:
            image: PIL Image object
            
        Returns:
            Float value between 0 (dark) and 1 (bright)
        """
        # Convert to grayscale for brightness calculation
        gray = image.convert('L')
        
        # Calculate average brightness normalized to 0-1
        histogram = gray.histogram()
        pixels = sum(histogram)
        brightness = sum(i * pixels for i, pixels in enumerate(histogram)) / (255 * sum(histogram))
        
        return brightness
    
    def _get_complementary_color(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        Get complementary color.
        
        Args:
            color: RGB color tuple
            
        Returns:
            Complementary RGB color tuple
        """
        r, g, b = color
        return (255 - r, 255 - g, 255 - b)
    
    def _get_brand_colors(self, brand_name: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Get brand-specific colors.
        
        Args:
            brand_name: Brand name
            
        Returns:
            Dictionary with brand colors or None if not found
        """
        if not brand_name:
            return None
            
        brand_lower = brand_name.lower()
        
        # Common brand colors
        brand_colors = {
            "apple": {
                "primary": (0, 122, 255, 255),  # Apple blue
                "secondary": (255, 59, 48, 255),  # Apple red
                "light_text": (255, 255, 255, 255),
                "dark_text": (0, 0, 0, 255)
            },
            "nike": {
                "primary": (0, 0, 0, 255),  # Nike black
                "secondary": (255, 255, 255, 255),  # White
                "light_text": (255, 255, 255, 255),
                "dark_text": (0, 0, 0, 255)
            },
            "coca-cola": {
                "primary": (237, 28, 36, 255),  # Coca-Cola red
                "secondary": (255, 255, 255, 255),  # White
                "light_text": (255, 255, 255, 255),
                "dark_text": (0, 0, 0, 255)
            },
            "facebook": {
                "primary": (66, 103, 178, 255),  # Facebook blue
                "secondary": (255, 255, 255, 255),  # White
                "light_text": (255, 255, 255, 255),
                "dark_text": (0, 0, 0, 255)
            },
            "amazon": {
                "primary": (255, 153, 0, 255),  # Amazon orange
                "secondary": (0, 0, 0, 255),  # Black
                "light_text": (255, 255, 255, 255),
                "dark_text": (0, 0, 0, 255)
            },
            "google": {
                "primary": (66, 133, 244, 255),  # Google blue
                "secondary": (234, 67, 53, 255),  # Google red
                "tertiary": (251, 188, 5, 255),  # Google yellow
                "quaternary": (52, 168, 83, 255),  # Google green
                "light_text": (255, 255, 255, 255),
                "dark_text": (0, 0, 0, 255)
            },
            "microsoft": {
                "primary": (241, 80, 37, 255),  # Microsoft red
                "secondary": (0, 164, 239, 255),  # Microsoft blue
                "tertiary": (255, 185, 0, 255),  # Microsoft yellow
                "quaternary": (127, 186, 0, 255),  # Microsoft green
                "light_text": (255, 255, 255, 255),
                "dark_text": (0, 0, 0, 255)
            },
            "starbucks": {
                "primary": (0, 122, 74, 255),  # Starbucks green
                "secondary": (0, 0, 0, 255),  # Black
                "light_text": (255, 255, 255, 255),
                "dark_text": (0, 0, 0, 255)
            },
            "mcdonalds": {
                "primary": (255, 199, 44, 255),  # McDonald's yellow
                "secondary": (227, 31, 38, 255),  # McDonald's red
                "light_text": (255, 255, 255, 255),
                "dark_text": (0, 0, 0, 255)
            },
            "adidas": {
                "primary": (0, 0, 0, 255),  # Adidas black
                "secondary": (255, 255, 255, 255),  # White
                "light_text": (255, 255, 255, 255),
                "dark_text": (0, 0, 0, 255)
            },
            "pepsi": {
                "primary": (0, 85, 184, 255),  # Pepsi blue
                "secondary": (230, 9, 23, 255),  # Pepsi red
                "light_text": (255, 255, 255, 255),
                "dark_text": (0, 0, 0, 255)
            },
            "louis vuitton": {
                "primary": (157, 122, 74, 255),  # LV brown
                "secondary": (4, 9, 40, 255),  # Navy blue
                "light_text": (255, 255, 255, 255),
                "dark_text": (0, 0, 0, 255)
            }
        }
        
        # Check for direct match
        if brand_lower in brand_colors:
            return brand_colors[brand_lower]
        
        # Check for partial matches
        for brand, colors in brand_colors.items():
            if brand in brand_lower or brand_lower in brand:
                return colors
                
        # Brand aliases
        brand_aliases = {
            "iphone": "apple",
            "macbook": "apple",
            "ipad": "apple",
            "imac": "apple",
            "airpods": "apple",
            "just do it": "nike",
            "coke": "coca-cola",
            "fb": "facebook",
            "galaxy": "samsung",
            "pixel": "google",
            "surface": "microsoft",
            "lv": "louis vuitton"
        }
        
        for alias, brand in brand_aliases.items():
            if alias in brand_lower and brand in brand_colors:
                return brand_colors[brand]
        
        return None
    
    def get_available_styles(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available style presets.
        
        Returns:
            Dictionary of style presets
        """
        return self.style_presets 
