"""
Typography Style Manager - Handles style selection and management for different industries/brands
"""
import os
import logging
from typing import Dict, Any, Optional, List, Tuple
from PIL import ImageFont

from .base import TypographyBase, DEFAULT_PREMIUM_FONTS, load_font

class TypographyStyleManager(TypographyBase):
    """Manages typography styles for different industries and brands."""
    
    def __init__(self):
        """Initialize typography style manager."""
        super().__init__()
        
        # Premium font mappings by style with fallbacks
        self.font_styles = DEFAULT_PREMIUM_FONTS
        
        # Industry-specific style templates
        self.industry_templates = self._setup_industry_templates()
        
        # Brand-specific style templates for major brands
        self.brand_templates = self._setup_brand_templates()
    
    def _setup_industry_templates(self) -> Dict[str, Dict[str, Any]]:
        """Setup industry-specific typography templates."""
        return {
            'technology': {
                'style': 'modern',
                'text_treatments': {
                    'headline': 'clean_gradient',
                    'subheadline': 'simple',
                    'body': 'simple',
                    'cta': 'rounded_button'
                },
                'text_placement': 'centered',
                'color_scheme': {
                    'headline': {'text': (255, 255, 255, 255), 'shadow': (0, 0, 0, 100), 'gradient': [(70, 130, 180, 255), (30, 144, 255, 255)]},
                    'subheadline': {'text': (255, 255, 255, 230), 'shadow': (0, 0, 0, 80)},
                    'body': {'text': (255, 255, 255, 200), 'shadow': (0, 0, 0, 60)},
                    'cta': {'text': (255, 255, 255, 255), 'button': (0, 122, 255, 230), 'hover': (0, 144, 255, 230)}
                },
                'text_proportions': {
                    'headline_size': 0.075,  # Relative to image height
                    'subheadline_size': 0.035,
                    'body_size': 0.025,
                    'cta_size': 0.035
                },
                'spacing': {
                    'headline_padding': 0.03,  # Relative to image height
                    'subheadline_padding': 0.02,
                    'body_padding': 0.03,
                    'cta_padding': 0.04
                },
                'letterSpacing': {
                    'headline': 0.5,  # Relative to font size
                    'subheadline': 0.2,
                    'body': 0,
                    'cta': 0.3
                }
            },
            'luxury': {
                'style': 'elegant',
                'text_treatments': {
                    'headline': 'elegant_serif',
                    'subheadline': 'subtle_bg',
                    'body': 'simple',
                    'cta': 'minimal_line'
                },
                'text_placement': 'bottom_right',
                'color_scheme': {
                    'headline': {'text': (255, 255, 255, 255), 'shadow': (0, 0, 0, 100)},
                    'subheadline': {'text': (255, 255, 255, 230), 'shadow': (0, 0, 0, 80), 'bg': (0, 0, 0, 100)},
                    'body': {'text': (255, 255, 255, 200), 'shadow': (0, 0, 0, 60)},
                    'cta': {'text': (255, 215, 0, 255), 'button': (0, 0, 0, 0), 'border': (255, 215, 0, 180)}
                },
                'text_proportions': {
                    'headline_size': 0.065,
                    'subheadline_size': 0.030,
                    'body_size': 0.025,
                    'cta_size': 0.030
                },
                'spacing': {
                    'headline_padding': 0.02,
                    'subheadline_padding': 0.01,
                    'body_padding': 0.03,
                    'cta_padding': 0.05
                },
                'letterSpacing': {
                    'headline': 0.3,
                    'subheadline': 0.1,
                    'body': 0,
                    'cta': 0.5
                }
            },
            'fashion': {
                'style': 'fashion',
                'text_treatments': {
                    'headline': 'thin_elegant',
                    'subheadline': 'simple',
                    'body': 'subtle_serif',
                    'cta': 'minimal_line'
                },
                'text_placement': 'centered',
                'color_scheme': {
                    'headline': {'text': (255, 255, 255, 255), 'shadow': (0, 0, 0, 40)},
                    'subheadline': {'text': (255, 255, 255, 230)},
                    'body': {'text': (255, 255, 255, 200)},
                    'cta': {'text': (255, 255, 255, 255), 'button': (0, 0, 0, 0), 'border': (255, 255, 255, 180)}
                },
                'text_proportions': {
                    'headline_size': 0.085,
                    'subheadline_size': 0.030,
                    'body_size': 0.022,
                    'cta_size': 0.028
                },
                'spacing': {
                    'headline_padding': 0.04,
                    'subheadline_padding': 0.02,
                    'body_padding': 0.04,
                    'cta_padding': 0.06
                },
                'letterSpacing': {
                    'headline': 1.0,
                    'subheadline': 0.5,
                    'body': 0.1,
                    'cta': 0.8
                }
            },
            'automotive': {
                'style': 'automotive',
                'text_treatments': {
                    'headline': 'dynamic_bold',
                    'subheadline': 'simple',
                    'body': 'simple',
                    'cta': 'elegant_button'
                },
                'text_placement': 'bottom_left',
                'color_scheme': {
                    'headline': {'text': (255, 255, 255, 255), 'shadow': (0, 0, 0, 120), 'gradient': [(200, 200, 200, 255), (255, 255, 255, 255)]},
                    'subheadline': {'text': (200, 200, 200, 240), 'shadow': (0, 0, 0, 100)},
                    'body': {'text': (180, 180, 180, 220), 'shadow': (0, 0, 0, 80)},
                    'cta': {'text': (255, 255, 255, 255), 'button': (180, 30, 30, 220), 'hover': (200, 40, 40, 220)}
                },
                'text_proportions': {
                    'headline_size': 0.070,
                    'subheadline_size': 0.032,
                    'body_size': 0.022,
                    'cta_size': 0.030
                },
                'spacing': {
                    'headline_padding': 0.02,
                    'subheadline_padding': 0.015,
                    'body_padding': 0.02,
                    'cta_padding': 0.04
                },
                'letterSpacing': {
                    'headline': 0.2,
                    'subheadline': 0.1,
                    'body': 0,
                    'cta': 0.3
                }
            }
        }
    
    def _setup_brand_templates(self) -> Dict[str, Dict[str, Any]]:
        """Setup brand-specific typography templates."""
        return {
            'apple': {
                'style': 'modern',
                'primary_font': 'SF Pro Display',
                'text_treatments': {
                    'headline': 'apple_minimalist',
                    'subheadline': 'simple',
                    'body': 'simple',
                    'cta': 'minimal_apple_button'
                },
                'text_placement': 'centered',
                'color_scheme': {
                    'headline': {'text': (255, 255, 255, 255)},
                    'subheadline': {'text': (255, 255, 255, 220)},
                    'body': {'text': (255, 255, 255, 200)},
                    'cta': {'text': (255, 255, 255, 255), 'button': (0, 122, 255, 230)}
                },
                'text_proportions': {
                    'headline_size': 0.070,
                    'subheadline_size': 0.032,
                    'body_size': 0.022,
                    'cta_size': 0.030
                },
                'spacing': {
                    'headline_padding': 0.02,
                    'subheadline_padding': 0.015,
                    'body_padding': 0.025,
                    'cta_padding': 0.04
                },
                'letterSpacing': {
                    'headline': 0.03,
                    'subheadline': 0.01,
                    'body': 0,
                    'cta': 0
                }
            },
            'samsung': {
                'style': 'modern',
                'primary_font': 'Samsung Sans',
                'text_treatments': {
                    'headline': 'samsung_bold',
                    'subheadline': 'simple',
                    'body': 'simple',
                    'cta': 'rounded_button'
                },
                'text_placement': 'bottom_left',
                'color_scheme': {
                    'headline': {'text': (255, 255, 255, 255), 'shadow': (0, 0, 0, 80)},
                    'subheadline': {'text': (200, 200, 200, 240)},
                    'body': {'text': (180, 180, 180, 220)},
                    'cta': {'text': (255, 255, 255, 255), 'button': (41, 128, 185, 230)}
                },
                'text_proportions': {
                    'headline_size': 0.075,
                    'subheadline_size': 0.035,
                    'body_size': 0.025,
                    'cta_size': 0.032
                },
                'spacing': {
                    'headline_padding': 0.025,
                    'subheadline_padding': 0.015,
                    'body_padding': 0.025,
                    'cta_padding': 0.035
                },
                'letterSpacing': {
                    'headline': 0.05,
                    'subheadline': 0.02,
                    'body': 0,
                    'cta': 0.02
                }
            },
            'nike': {
                'style': 'athletic',
                'primary_font': 'Futura-Bold',
                'text_treatments': {
                    'headline': 'nike_bold',
                    'subheadline': 'simple',
                    'body': 'simple',
                    'cta': 'minimal_line'
                },
                'text_placement': 'dynamic',
                'color_scheme': {
                    'headline': {'text': (255, 255, 255, 255), 'shadow': (0, 0, 0, 100)},
                    'subheadline': {'text': (255, 255, 255, 230)},
                    'body': {'text': (255, 255, 255, 200)},
                    'cta': {'text': (255, 255, 255, 255), 'button': (0, 0, 0, 0), 'border': (255, 255, 255, 180)}
                },
                'text_proportions': {
                    'headline_size': 0.090,
                    'subheadline_size': 0.035,
                    'body_size': 0.025,
                    'cta_size': 0.032
                },
                'spacing': {
                    'headline_padding': 0.03,
                    'subheadline_padding': 0.02,
                    'body_padding': 0.03,
                    'cta_padding': 0.05
                },
                'letterSpacing': {
                    'headline': 0.05,
                    'subheadline': 0.02,
                    'body': 0,
                    'cta': 0.5
                }
            }
        }
    
    def get_font(self, style: str, element: str, size: int, brand: str = None) -> Optional[ImageFont.FreeTypeFont]:
        """
        Get professional font based on typography style and element.
        
        Args:
            style: Typography style ('modern', 'luxury', 'minimal', etc.)
            element: Element type ('headline', 'subheadline', 'body', 'cta')
            size: Font size
            brand: Optional brand name for brand-specific fonts
            
        Returns:
            Font object
        """
        # Check for brand-specific font first
        if brand and brand.lower() in self.brand_templates:
            brand_data = self.brand_templates[brand.lower()]
            primary_font = brand_data.get('primary_font')
            
            if primary_font:
                # Adjust font weight based on element
                if element == 'headline':
                    font_name = f"{primary_font}-Bold"
                elif element == 'cta':
                    font_name = f"{primary_font}-Semibold"
                elif element == 'subheadline':
                    font_name = primary_font
                else:
                    font_name = f"{primary_font}-Light" if 'Light' not in primary_font else primary_font
                
                # Try to load the brand font
                font = load_font(font_name, size, self.font_directories)
                if font:
                    return font
        
        # Get style-specific fonts
        style_lower = style.lower()
        
        # Find the closest matching style
        if style_lower in self.font_styles:
            style_key = style_lower
        elif 'modern' in style_lower or 'sans' in style_lower:
            style_key = 'modern'
        elif 'luxury' in style_lower or 'premium' in style_lower or 'high-end' in style_lower:
            style_key = 'luxury'
        elif 'minimal' in style_lower or 'clean' in style_lower or 'simple' in style_lower:
            style_key = 'minimal'
        elif 'bold' in style_lower or 'strong' in style_lower or 'powerful' in style_lower:
            style_key = 'bold'
        elif 'elegant' in style_lower or 'sophisticated' in style_lower or 'classic' in style_lower:
            style_key = 'elegant'
        elif 'technical' in style_lower or 'digital' in style_lower or 'tech' in style_lower:
            style_key = 'technical'
        elif 'athletic' in style_lower or 'sport' in style_lower:
            style_key = 'athletic'
        elif 'fashion' in style_lower or 'style' in style_lower:
            style_key = 'fashion'
        elif 'auto' in style_lower or 'car' in style_lower:
            style_key = 'automotive'
        else:
            # Default to modern
            style_key = 'modern'
        
        # Get font list for this style and element
        font_list = self.font_styles.get(style_key, {}).get(element, ['Arial-Bold', 'Helvetica-Bold'])
        
        # Try each font in the list
        for font_name in font_list:
            font = load_font(font_name, size, self.font_directories)
            if font:
                return font
        
        # Last resort: default font
        try:
            return ImageFont.load_default()
        except:
            return None
    
    def get_text_treatment(self, treatment_name: str) -> Dict:
        """
        Get parameters for a specific text treatment.
        
        Args:
            treatment_name: Name of the text treatment
            
        Returns:
            Dictionary with treatment parameters
        """
        treatments = {
            'simple': {
                'shadow_offset': 1,
                'shadow_color': (0, 0, 0, 180),
                'gradient': False,
                'outline': False,
                'bg': False
            },
            'clean_gradient': {
                'shadow_offset': 1,
                'shadow_color': (0, 0, 0, 120),
                'gradient': True,
                'gradient_direction': 'vertical',
                'outline': False,
                'bg': False
            },
            'subtle_bg': {
                'shadow_offset': 0,
                'shadow_color': (0, 0, 0, 0),
                'gradient': False,
                'outline': False,
                'bg': True,
                'bg_padding': 10,
                'bg_color': (0, 0, 0, 120),
                'bg_radius': 5
            },
            'elegant_serif': {
                'shadow_offset': 1,
                'shadow_color': (0, 0, 0, 100),
                'gradient': False,
                'outline': True,
                'outline_size': 1,
                'outline_color': (255, 255, 255, 50),
                'bg': False
            },
            'thin_elegant': {
                'shadow_offset': 1,
                'shadow_color': (0, 0, 0, 80),
                'gradient': False,
                'outline': False,
                'letter_spacing': 0.8,
                'bg': False
            },
            'dynamic_bold': {
                'shadow_offset': 2,
                'shadow_color': (0, 0, 0, 150),
                'gradient': True,
                'gradient_direction': 'diagonal',
                'outline': True,
                'outline_size': 1,
                'outline_color': (255, 255, 255, 80),
                'bg': False
            },
            'athletic_bold': {
                'shadow_offset': 0,
                'shadow_color': (0, 0, 0, 0),
                'gradient': False,
                'outline': True,
                'outline_size': 2,
                'outline_color': (0, 0, 0, 200),
                'bg': False,
                'skew': 5  # Slight rightward slant
            },
            'nike_bold': {
                'shadow_offset': 0,
                'shadow_color': (0, 0, 0, 0),
                'gradient': False,
                'outline': True,
                'outline_size': 1,
                'outline_color': (0, 0, 0, 200),
                'condensed': True,
                'letter_spacing': -0.05,
                'transform': 'uppercase',
                'bg': False
            },
            'delicious_gradient': {
                'shadow_offset': 1,
                'shadow_color': (0, 0, 0, 150),
                'gradient': True,
                'gradient_direction': 'horizontal',
                'outline': False,
                'bg': False,
                'glow': True,
                'glow_color': (255, 200, 100, 100),
                'glow_size': 10
            },
            'apple_minimalist': {
                'shadow_offset': 0,
                'shadow_color': (0, 0, 0, 0),
                'gradient': False,
                'outline': False,
                'bg': False,
                'weight': 'thin',
                'letter_spacing': 0.05
            },
            'samsung_bold': {
                'shadow_offset': 1,
                'shadow_color': (0, 0, 0, 80),
                'gradient': False,
                'outline': False,
                'bg': False,
                'weight': 'bold',
                'letter_spacing': 0.02
            },
            'bmw_elegant': {
                'shadow_offset': 1,
                'shadow_color': (0, 0, 0, 60),
                'gradient': False,
                'outline': False,
                'bg': False,
                'letter_spacing': 0.1,
                'transform': 'uppercase'
            },
            'luxury_serif': {
                'shadow_offset': 1,
                'shadow_color': (0, 0, 0, 60),
                'gradient': False,
                'outline': False,
                'bg': False,
                'letter_spacing': 0.2,
                'transform': 'uppercase'
            },
            'subtle_serif': {
                'shadow_offset': 0,
                'shadow_color': (0, 0, 0, 0),
                'gradient': False,
                'outline': False,
                'bg': False,
                'letter_spacing': 0.05,
                'spacing': 1.2  # Line spacing factor
            }
        }
        
        return treatments.get(treatment_name, treatments['simple'])
    
    def get_template_for_industry(self, industry: str) -> Dict:
        """
        Get template for a specific industry.
        
        Args:
            industry: Industry name
            
        Returns:
            Typography template for the industry
        """
        industry_lower = industry.lower()
        
        # Try to find an exact match
        for ind_key, template in self.industry_templates.items():
            if ind_key.lower() == industry_lower:
                return template
        
        # Try to find a partial match
        for ind_key, template in self.industry_templates.items():
            if ind_key.lower() in industry_lower or industry_lower in ind_key.lower():
                return template
        
        # Map common industries to templates
        industry_map = {
            'tech': 'technology',
            'software': 'technology',
            'electronics': 'technology',
            'computer': 'technology',
            'phone': 'technology',
            'digital': 'technology',
            
            'fashion': 'fashion',
            'clothing': 'fashion',
            'apparel': 'fashion',
            'style': 'fashion',
            
            'luxury': 'luxury',
            'premium': 'luxury',
            'high-end': 'luxury',
            'jewelry': 'luxury',
            'watch': 'luxury',
            
            'auto': 'automotive',
            'car': 'automotive',
            'vehicle': 'automotive',
            'transport': 'automotive'
        }
        
        for term, mapped_industry in industry_map.items():
            if term in industry_lower:
                return self.industry_templates.get(mapped_industry, self.industry_templates['technology'])
        
        # Default to technology template
        return self.industry_templates['technology']
    
    def get_template_for_brand(self, brand_name: str) -> Optional[Dict]:
        """
        Get template for a specific brand.
        
        Args:
            brand_name: Brand name
            
        Returns:
            Typography template for the brand or None if not found
        """
        brand_lower = brand_name.lower()
        
        # Try to find an exact match
        if brand_lower in self.brand_templates:
            return self.brand_templates[brand_lower]
        
        # Try common brand variations
        brand_variations = {
            'apple': ['apple', 'iphone', 'ipad', 'macbook', 'imac'],
            'samsung': ['samsung', 'galaxy'],
            'nike': ['nike', 'just do it', 'nikeid'],
            'bmw': ['bmw', 'bayerische motoren werke'],
            'rolex': ['rolex', 'oyster', 'daytona', 'submariner']
        }
        
        for key, variations in brand_variations.items():
            if brand_lower in variations:
                return self.brand_templates[key]
        
        return None