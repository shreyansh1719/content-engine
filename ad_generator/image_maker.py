"""
Studio-quality image generator with professional typography
Creates high-end ad images with proper composition and text treatment
"""
import os
import logging
import json
import time
import base64
import re
import traceback
from typing import Dict, Optional, Union, Tuple, List, Any
from datetime import datetime
from io import BytesIO
import requests
import numpy as np
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageColor, ImageOps

# Import typography modules - these should be imported but not referenced directly
try:
    from .typography import (
        TypographyStyleManager, 
        TextEffectsEngine, 
        ColorSchemeGenerator, 
        ImageAnalyzer, 
        TextPlacementEngine,
        FontManager
    )
except ImportError:
    # Create fallback classes if imports fail
    class FallbackClass:
        def __init__(self, *args, **kwargs):
            pass
        def __getattr__(self, name):
            def method(*args, **kwargs):
                return None
            return method
    
    TypographyStyleManager = TextEffectsEngine = ColorSchemeGenerator = ImageAnalyzer = TextPlacementEngine = FontManager = FallbackClass

class StudioImageGenerator:
    """Generate studio-quality ad images with professional typography."""
    
    def __init__(self, openai_api_key=None):
        """Initialize with OpenAI API key."""
        # Setup API key
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
    
        # Setup logging with more detailed formatting
        self.setup_logging()
    
        # Initialize typography components with proper error handling
        try:
            self.typography_manager = TypographyStyleManager()
            self.text_effects = TextEffectsEngine()
            self.color_scheme_generator = ColorSchemeGenerator()
            self.image_analyzer = ImageAnalyzer()
            self.text_placement = TextPlacementEngine()
            self.font_manager = FontManager()
        except Exception as e:
            self.logger.error(f"Failed to initialize typography components: {str(e)}")
            # Create fallback instances
            self.typography_manager = FallbackClass()
            self.text_effects = FallbackClass()
            self.color_scheme_generator = FallbackClass()
            self.image_analyzer = FallbackClass()
            self.text_placement = FallbackClass()
            self.font_manager = FallbackClass()
    
        # Define ad styles and industry templates
        self.ad_styles = self._setup_ad_styles()
        self.industry_templates = self._setup_industry_templates()
        self.brand_level_templates = self._setup_brand_level_templates()
        self.product_specific_templates = self._setup_product_specific_templates()
        
        # Setup composition templates
        self.composition_templates = self._setup_composition_templates()
        
        # Cache for generated images to avoid regeneration
        self.image_cache = {}
        
        # Setup output directories
        os.makedirs("output/images", exist_ok=True)
        os.makedirs("output/images/base", exist_ok=True)
        os.makedirs("output/images/enhanced", exist_ok=True)
        os.makedirs("output/images/final", exist_ok=True)

    def setup_logging(self):
        """Set up detailed logging configuration."""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_format)
        self.logger = logging.getLogger("StudioImageGenerator")
        
        # Add file handler for persistent logs
        try:
            os.makedirs("logs", exist_ok=True)
            file_handler = logging.FileHandler(f"logs/image_generator_{datetime.now().strftime('%Y%m%d')}.log")
            file_handler.setFormatter(logging.Formatter(log_format))
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not set up log file: {e}")
    
    def _setup_ad_styles(self) -> Dict[str, Dict[str, Any]]:
        """Setup professional ad styles based on industry standards."""
        return {
            "minimal": {
                "description": "Clean, minimalist design with ample white space",
                "prompt_elements": [
                    "minimalist product photography against clean background",
                    "ample negative space for typography",
                    "subtle shadows and reflections",
                    "monochromatic color palette with single accent color"
                ],
                "typography": {
                    "style": "minimal",
                    "headline_weight": "light",
                    "headline_size_factor": 0.08,
                    "subheadline_size_factor": 0.035,
                    "preferred_placement": "centered",
                    "text_effects": ["subtle_shadow"],
                    "allowed_colors": ["monochrome", "brand_color"]
                },
                "composition": "centered"
            },
            "dramatic": {
                "description": "High-contrast dramatic imagery with bold typography",
                "prompt_elements": [
                    "dramatic lighting with strong directional light source",
                    "high contrast shadows and highlights",
                    "cinematic color grading with deep blacks",
                    "dramatic camera angle showcasing product"
                ],
                "typography": {
                    "style": "bold",
                    "headline_weight": "bold",
                    "headline_size_factor": 0.09,
                    "subheadline_size_factor": 0.04,
                    "preferred_placement": "dynamic",
                    "text_effects": ["gradient", "shadow"],
                    "allowed_colors": ["high_contrast", "complementary"]
                },
                "composition": "dynamic"
            },
            "lifestyle": {
                "description": "Product in aspirational use context with lifestyle elements",
                "prompt_elements": [
                    "product in aspirational real-world context",
                    "lifestyle setting that appeals to target demographic",
                    "golden hour lighting with warm tones",
                    "shallow depth of field with bokeh elements"
                ],
                "typography": {
                    "style": "modern",
                    "headline_weight": "medium",
                    "headline_size_factor": 0.07,
                    "subheadline_size_factor": 0.035,
                    "preferred_placement": "bottom_left",
                    "text_effects": ["subtle_background", "shadow"],
                    "allowed_colors": ["environment_matched", "brand_color"]
                },
                "composition": "rule_of_thirds"
            },
            "luxury": {
                "description": "Elegant, premium imagery with sophisticated typography",
                "prompt_elements": [
                    "premium luxury product photography with perfect lighting",
                    "sophisticated materials like marble, gold, or black surfaces",
                    "elegant reflections and precise highlights",
                    "negative space with dramatic shadows"
                ],
                "typography": {
                    "style": "elegant",
                    "headline_weight": "light",
                    "headline_size_factor": 0.065,
                    "subheadline_size_factor": 0.03,
                    "preferred_placement": "centered",
                    "text_effects": ["elegant_serif", "subtle_glow"],
                    "allowed_colors": ["gold", "monochrome", "premium"]
                },
                "composition": "symmetrical"
            },
            "technical": {
                "description": "Technical product showcase with detailed features",
                "prompt_elements": [
                    "technical product photography with feature highlight",
                    "precision lighting to showcase details and materials",
                    "subtle grid elements or technical patterns",
                    "clean environment with slight technical context"
                ],
                "typography": {
                    "style": "technical",
                    "headline_weight": "medium",
                    "headline_size_factor": 0.075,
                    "subheadline_size_factor": 0.035,
                    "preferred_placement": "left_aligned",
                    "text_effects": ["gradient", "technical_lines"],
                    "allowed_colors": ["tech_blue", "brand_color"]
                },
                "composition": "technical"
            }
        }
    
    def _setup_industry_templates(self) -> Dict[str, Dict[str, Any]]:
        """Setup industry-specific templates for image generation."""
        return {
            "technology": {
                "preferred_styles": ["technical", "minimal", "dramatic"],
                "lighting": "crisp key lighting with blue accent light",
                "background": "gradient or minimalist environment",
                "composition_elements": [
                    "product at hero angle (3/4 view)",
                    "clean reflective surface beneath product",
                    "technical details clearly visible",
                    "screen content visible and vibrant (if applicable)"
                ],
                "color_palette": ["tech_blue", "sleek_gray", "deep_black", "clean_white"],
                "environment_cues": [
                    "modern minimal environment",
                    "subtle tech grid patterns",
                    "clean desk or workspace elements"
                ],
                "typography_zones": [
                    "clear top third zone for headline",
                    "bottom third for subheadline and CTA"
                ],
                "text_integration": [
                    "text integrates with UI elements if showing screen",
                    "can overlap with product if using subtle effects"
                ],
                "inspiration_brands": ["Apple", "Samsung", "Google"]
            },
            "fashion": {
                "preferred_styles": ["lifestyle", "dramatic", "luxury"],
                "lighting": "soft diffused main light with dramatic rim lighting",
                "background": "studio environment or contextual lifestyle setting",
                "composition_elements": [
                    "product as clear hero element",
                    "elegant styling and arrangement",
                    "material texture clearly visible",
                    "aspirational positioning"
                ],
                "color_palette": ["fashion_neutral", "rich_accent", "editorial_black", "textured_white"],
                "environment_cues": [
                    "high-end studio environment",
                    "elegant materials like marble or fabric",
                    "subtle fashion environment elements"
                ],
                "typography_zones": [
                    "balanced negative space for typography",
                    "clear zone contrasting with product"
                ],
                "text_integration": [
                    "typography follows product contours",
                    "text can interact with shadows or reflections"
                ],
                "inspiration_brands": ["Gucci", "Chanel", "Prada"]
            },
            "beauty": {
                "preferred_styles": ["minimal", "luxury", "lifestyle"],
                "lighting": "soft flattering light with subtle glow effects",
                "background": "clean gradient or soft-focus environment",
                "composition_elements": [
                    "product with perfect reflection",
                    "ingredient elements or texture displays",
                    "soft organic shapes or patterns",
                    "visual texture cues for product effect"
                ],
                "color_palette": ["soft_neutral", "skin_tone", "product_color", "subtle_accent"],
                "environment_cues": [
                    "clean spa-like environment",
                    "natural elements like water or botanicals",
                    "gentle texture elements suggesting product effect"
                ],
                "typography_zones": [
                    "clean top area for brand and headline",
                    "balanced side space for supporting text"
                ],
                "text_integration": [
                    "text interacts with light effects",
                    "typography can follow organic product elements"
                ],
                "inspiration_brands": ["Estée Lauder", "La Mer", "Glossier"]
            },
            "spirits_beverages": {
                "preferred_styles": ["luxury", "dramatic", "lifestyle"],
                "lighting": "dramatic low-key lighting with accent highlights",
                "background": "upscale bar environment or dark luxury setting",
                "composition_elements": [
                    "bottle as hero with perfect label visibility",
                    "crystal-clear glassware with proper drink presentation",
                    "premium surfaces like marble, wood, or glass",
                    "atmospheric elements like subtle smoke or condensation"
                ],
                "color_palette": ["deep_black", "rich_amber", "jewel_tones", "brand_signature_color"],
                "environment_cues": [
                    "upscale bar or lounge setting",
                    "premium material textures",
                    "subtle bokeh and reflections"
                ],
                "typography_zones": [
                    "clear top area for headline",
                    "bottom third for brand and tagline"
                ],
                "text_integration": [
                    "typography integrates with lighting effects",
                    "text can interact with reflective surfaces"
                ],
                "inspiration_brands": ["Bombay Sapphire", "Grey Goose", "Johnnie Walker"],
                "product_presentation": {
                    "bottle_focus": "central focus on bottle with pristine label detail",
                    "glassware": "appropriate premium glassware for the spirit type",
                    "garnishes": "fresh, artfully arranged botanical elements",
                    "pour_effects": "perfect liquid clarity with dynamic motion elements",
                    "ice": "crystal clear ice with perfect shape and placement"
                }
            },
            "luxury": {
                "preferred_styles": ["luxury", "dramatic", "minimal"],
                "lighting": "dramatic directional lighting with precise highlights",
                "background": "dark elegant background or premium environment",
                "composition_elements": [
                    "perfectly centered hero product",
                    "precise reflections and shadows",
                    "luxury material cues (marble, leather, metal)",
                    "perfect symmetry or golden ratio composition"
                ],
                "color_palette": ["deep_black", "gold_accent", "luxury_tone", "rich_neutral"],
                "environment_cues": [
                    "museum-quality display elements",
                    "subtle luxury material textures",
                    "elegant architectural elements"
                ],
                "typography_zones": [
                    "balanced breathing space around product",
                    "clear zones for elegant type placement"
                ],
                "text_integration": [
                    "typography integrates with luxury materials",
                    "text can have subtle metallic or material effects"
                ],
                "inspiration_brands": ["Rolex", "Louis Vuitton", "Cartier"]
            },
            "food_beverage": {
                "preferred_styles": ["lifestyle", "dramatic", "minimal"],
                "lighting": "warm directional lighting with backlighting effects",
                "background": "complementary environment with depth",
                "composition_elements": [
                    "hero product with perfect styling",
                    "appetizing details clearly visible",
                    "dynamic elements (steam, pour, splash)",
                    "complementary ingredient styling"
                ],
                "color_palette": ["food_natural", "rich_complement", "warm_accent", "deep_contrast"],
                "environment_cues": [
                    "natural material elements (wood, stone)",
                    "contextual dining or preparation cues",
                    "ingredient stories or origin elements"
                ],
                "typography_zones": [
                    "avoiding overlap with key food elements",
                    "clear zone that doesn't distract from appetite appeal"
                ],
                "text_integration": [
                    "typography can integrate with surfaces or materials",
                    "text may have texture elements matching environment"
                ],
                "inspiration_brands": ["Coca-Cola", "Grey Goose", "Godiva"]
            }
        }
    
    def _setup_brand_level_templates(self) -> Dict[str, Dict[str, Any]]:
        """Setup templates based on brand positioning level."""
        return {
            "luxury": {
                "preferred_styles": ["luxury", "dramatic", "minimal"],
                "prompt_elements": [
                    "ultra-premium product presentation",
                    "museum-quality lighting with perfect highlights",
                    "luxury material cues and environment",
                    "immaculate styling and composition"
                ],
                "typography": {
                    "preferred_styles": ["elegant", "luxury", "minimal"],
                    "headline_treatment": "elegant_serif",
                    "preferred_colors": ["monochrome", "gold"],
                    "letter_spacing": "expanded",
                    "text_effects": ["subtle_glow", "elegant_shadow"]
                }
            },
            "premium": {
                "preferred_styles": ["dramatic", "minimal", "technical"],
                "prompt_elements": [
                    "high-end product presentation",
                    "professional studio lighting with deliberate shadows",
                    "premium environment with quality materials",
                    "sophisticated styling with attention to detail"
                ],
                "typography": {
                    "preferred_styles": ["modern", "minimal", "elegant"],
                    "headline_treatment": "clean_gradient",
                    "preferred_colors": ["brand_color", "monochrome"],
                    "letter_spacing": "balanced",
                    "text_effects": ["gradient", "subtle_shadow"]
                }
            },
            "mid_range": {
                "preferred_styles": ["lifestyle", "technical", "dramatic"],
                "prompt_elements": [
                    "quality product presentation in context",
                    "balanced lighting with good dimension",
                    "appealing environment with practical context",
                    "relatable styling with commercial appeal"
                ],
                "typography": {
                    "preferred_styles": ["modern", "bold", "technical"],
                    "headline_treatment": "shadow",
                    "preferred_colors": ["vibrant", "brand_color"],
                    "letter_spacing": "normal",
                    "text_effects": ["shadow", "simple"]
                }
            },
            "mass_market": {
                "preferred_styles": ["lifestyle", "dramatic"],
                "prompt_elements": [
                    "clear product presentation with mass appeal",
                    "bright, accessible lighting",
                    "straightforward environment with universal appeal",
                    "simple, direct styling"
                ],
                "typography": {
                    "preferred_styles": ["bold", "modern"],
                    "headline_treatment": "simple",
                    "preferred_colors": ["high_contrast", "primary"],
                    "letter_spacing": "tight",
                    "text_effects": ["outline", "shadow"]
                }
            }
        }
    
    def _setup_product_specific_templates(self) -> Dict[str, Dict[str, Any]]:
        """Setup templates for specific product categories with detailed styling."""
        return {
            "smartphone": {
                "composition": {
                    "primary_angle": "3/4 view showing both screen and profile",
                    "secondary_angles": ["front view with screen", "side profile for thinness"],
                    "placement": "centered on reflective surface or floating"
                },
                "details": {
                    "screen": "vibrant, color-rich screen content without glare",
                    "materials": "highlight premium materials (glass, metal, ceramic)",
                    "cameras": "precise detail on camera lenses and array",
                    "edges": "clean edges with perfect light reflection"
                },
                "lighting": {
                    "style": "dramatic key lighting with rim light for edges",
                    "highlights": "subtle highlights on screen edges and buttons",
                    "environment": "tech-focused with blue/cool tones"
                },
                "background": {
                    "style": "gradient or minimal with subtle tech elements",
                    "colors": "brand-appropriate with complementary tones",
                    "depth": "subtle depth cues without distraction"
                }
            },
            "spirits": {
                "composition": {
                    "primary_angle": "straight-on or slight angle showing full bottle and label",
                    "secondary_elements": ["premium glassware", "ice", "garnish", "pour"],
                    "placement": "bottle as hero on reflective surface with proper glassware"
                },
                "details": {
                    "bottle": "pristine label with perfect alignment and sharp details",
                    "glassware": "crystal-clear appropriate glassware with perfect liquid level",
                    "liquid": "perfect clarity with appropriate color and reflections",
                    "garnishes": "fresh, artfully arranged botanical elements",
                    "ice": "crystal clear ice with perfect shape and placement"
                },
                "lighting": {
                    "style": "dramatic backlighting with accent lights on bottle",
                    "highlights": "precise highlights on glass edges and liquid",
                    "environment": "upscale with brand-appropriate color temperature"
                },
                "background": {
                    "style": "upscale bar or lounge setting with soft focus",
                    "materials": "premium surfaces (marble, wood, glass)",
                    "elements": "subtle bar elements without distraction"
                },
                "specialized": {
                    "gin": {
                        "glassware": "copa de balón or highball glass",
                        "garnishes": "juniper berries, citrus peel, cucumber",
                        "color": "crystal clear with slight blue tones",
                        "environment": "cool-toned with blue ambient lighting"
                    },
                    "whiskey": {
                        "glassware": "rocks glass or Glencairn",
                        "garnishes": "minimal or none, perhaps orange peel",
                        "color": "rich amber with warm highlights",
                        "environment": "warm-toned with amber/wood elements"
                    },
                    "vodka": {
                        "glassware": "martini glass or highball",
                        "garnishes": "lemon twist, olives, or minimal",
                        "color": "crystal clear with icy elements",
                        "environment": "cool tones with white/silver accents"
                    },
                    "rum": {
                        "glassware": "tiki mug or rocks glass",
                        "garnishes": "tropical fruits, mint, cinnamon",
                        "color": "golden to dark amber",
                        "environment": "warm with tropical or nautical elements"
                    }
                }
            },
            "luxury_watch": {
                "composition": {
                    "primary_angle": "10:10 position with logo/face clearly visible",
                    "secondary_angles": ["bracelet detail", "side profile for thickness"],
                    "placement": "centered on premium surface or wrist"
                },
                "details": {
                    "dial": "crystal-clear view of dial details and complications",
                    "hands": "perfect position showing craftsmanship",
                    "bezel": "highlight engraving and materials",
                    "bracelet": "perfect link arrangement showing craftsmanship"
                },
                "lighting": {
                    "style": "dramatic lighting with precise reflections",
                    "highlights": "subtle highlights on crystal and metal parts",
                    "environment": "premium with brand-appropriate mood"
                },
                "background": {
                    "style": "minimal luxury with subtle texture",
                    "colors": "deep blacks, blues, or brand colors",
                    "elements": "subtle luxury cues without distraction"
                }
            },
            "perfume": {
                "composition": {
                    "primary_angle": "straight-on or slight angle showing bottle shape",
                    "secondary_elements": ["cap detail", "atomizer", "packaging"],
                    "placement": "centered on reflective surface or floating"
                },
                "details": {
                    "bottle": "perfect refraction and transparency with liquid visible",
                    "label": "crisp detail on label and embossing",
                    "cap": "highlight luxury materials and detail",
                    "atmosphere": "subtle scent visualization elements"
                },
                "lighting": {
                    "style": "soft diffused with dramatic accents",
                    "highlights": "glass edge highlights and liquid refraction",
                    "environment": "elegant with brand-appropriate mood"
                },
                "background": {
                    "style": "soft gradient or atmospheric elements",
                    "colors": "brand-appropriate with complementary tones",
                    "elements": "subtle note ingredients or mood cues"
                }
            },
            "sneakers": {
                "composition": {
                    "primary_angle": "3/4 view showing profile and sole",
                    "secondary_angles": ["top-down", "heel detail", "material close-up"],
                    "placement": "floating or on minimal surface"
                },
                "details": {
                    "materials": "highlight texture, stitching, and premium materials",
                    "sole": "clear tread pattern and construction",
                    "branding": "crisp logo and branded elements",
                    "laces": "perfect arrangement showing style"
                },
                "lighting": {
                    "style": "clean studio lighting with defined shadows",
                    "highlights": "material texture highlights",
                    "environment": "energetic with brand-appropriate mood"
                },
                "background": {
                    "style": "minimal or lifestyle context depending on brand",
                    "colors": "complementary to shoe colorway",
                    "elements": "subtle movement or sport cues"
                }
            }
        }
    
    def _setup_composition_templates(self) -> Dict[str, Dict[str, Any]]:
        """Setup composition templates for different ad styles."""
        return {
            "centered": {
                "description": "Product perfectly centered with balanced negative space",
                "text_zones": {
                    "headline": {"y_range": [0.1, 0.25], "preferred_alignment": "center"},
                    "subheadline": {"y_range": [0.28, 0.35], "preferred_alignment": "center"},
                    "body": {"y_range": [0.7, 0.8], "preferred_alignment": "center"},
                    "cta": {"y_range": [0.82, 0.9], "preferred_alignment": "center"}
                },
                "prompt_cues": [
                    "perfectly centered product with balanced negative space",
                    "symmetrical lighting and reflections",
                    "clear space at top and bottom for typography"
                ]
            },
            "rule_of_thirds": {
                "description": "Product placed on rule of thirds with dynamic balance",
                "text_zones": {
                    "headline": {"y_range": [0.1, 0.3], "x_align": "opposite_product", "preferred_alignment": "dynamic"},
                    "subheadline": {"y_range": [0.35, 0.45], "x_align": "with_headline", "preferred_alignment": "dynamic"},
                    "body": {"y_range": [0.75, 0.85], "preferred_alignment": "dynamic"},
                    "cta": {"y_range": [0.85, 0.95], "preferred_alignment": "dynamic"}
                },
                "prompt_cues": [
                    "product positioned on rule of thirds grid intersection",
                    "asymmetrical balanced composition",
                    "clear negative space opposite to product for typography"
                ]
            },
            "dynamic": {
                "description": "Dramatic composition with strong directional elements",
                "text_zones": {
                    "headline": {"y_range": [0.15, 0.35], "x_align": "dynamic", "preferred_alignment": "impact"},
                    "subheadline": {"y_range": [0.4, 0.5], "x_align": "with_headline", "preferred_alignment": "impact"},
                    "body": {"y_range": [0.65, 0.75], "preferred_alignment": "clean"},
                    "cta": {"y_range": [0.8, 0.9], "preferred_alignment": "clean"}
                },
                "prompt_cues": [
                    "dramatic product angle with dynamic energy",
                    "strong directional lighting creating movement",
                    "composition with clear foreground, midground, background",
                    "intentional negative space for impactful typography"
                ]
            },
            "symmetrical": {
                "description": "Perfect symmetry with balanced elements",
                "text_zones": {
                    "headline": {"y_range": [0.05, 0.15], "preferred_alignment": "center"},
                    "subheadline": {"y_range": [0.18, 0.25], "preferred_alignment": "center"},
                    "body": {"y_range": [0.85, 0.9], "preferred_alignment": "center"},
                    "cta": {"y_range": [0.92, 0.98], "preferred_alignment": "center"}
                },
                "prompt_cues": [
                    "perfect bilateral symmetry with centered product",
                    "mirrored lighting and reflections",
                    "formal, balanced composition with clear hierarchy",
                    "elegant negative space at top and bottom for typography"
                ]
            },
            "technical": {
                "description": "Technical composition with feature focus",
                "text_zones": {
                    "headline": {"y_range": [0.1, 0.2], "x_align": "left", "preferred_alignment": "left"},
                    "subheadline": {"y_range": [0.23, 0.3], "x_align": "left", "preferred_alignment": "left"},
                    "body": {"y_range": [0.7, 0.8], "x_align": "left", "preferred_alignment": "left"},
                    "cta": {"y_range": [0.85, 0.92], "x_align": "left", "preferred_alignment": "left"}
                },
                "prompt_cues": [
                    "technical product view showing key features",
                    "precision lighting highlighting details",
                    "diagrammatic composition with clear hierarchy",
                    "structured negative space for technical typography"
                ]
            }
        }
    
    def _map_industry_to_template(self, industry: str) -> Dict[str, Any]:
        """Map industry to appropriate template."""
        if not industry:
            return self.industry_templates.get("technology", {})
            
        industry_lower = industry.lower()
        
        # Map to main industry templates
        if any(tech in industry_lower for tech in ["tech", "computer", "phone", "electronic", "digital"]):
            return self.industry_templates.get("technology", {})
        elif any(fashion in industry_lower for fashion in ["fashion", "apparel", "clothing", "shoe", "wear"]):
            return self.industry_templates.get("fashion", {})
        elif any(beauty in industry_lower for beauty in ["beauty", "cosmetic", "skin", "makeup"]):
            return self.industry_templates.get("beauty", {})
        elif any(spirits in industry_lower for spirits in ["spirit", "alcohol", "liquor", "gin", "whiskey", "vodka", "rum"]):
            return self.industry_templates.get("spirits_beverages", {})
        elif any(luxury in industry_lower for luxury in ["luxury", "premium", "watch", "jewelry"]):
            return self.industry_templates.get("luxury", {})
        elif any(food in industry_lower for food in ["food", "beverage", "drink", "restaurant"]):
            return self.industry_templates.get("food_beverage", {})
        
        # Default to technology if no match
        return self.industry_templates.get("technology", {})
    
    def _map_brand_level(self, brand_level: str) -> Dict[str, Any]:
        """Map brand level to appropriate template."""
        if not brand_level:
            return self.brand_level_templates.get("premium", {})
            
        level_lower = brand_level.lower()
        
        if "luxury" in level_lower or "high-end" in level_lower:
            return self.brand_level_templates.get("luxury", {})
        elif "premium" in level_lower:
            return self.brand_level_templates.get("premium", {})
        elif "mid" in level_lower or "middle" in level_lower:
            return self.brand_level_templates.get("mid_range", {})
        elif "mass" in level_lower or "budget" in level_lower:
            return self.brand_level_templates.get("mass_market", {})
        
        # Default to premium
        return self.brand_level_templates.get("premium", {})
    
    def _identify_product_type(self, product: str, industry: str) -> str:
        """Identify specific product type for detailed styling."""
        product_lower = product.lower()
        industry_lower = industry.lower() if industry else ""
        
        # Check for smartphone
        if any(term in product_lower for term in ["phone", "iphone", "galaxy", "pixel", "smartphone"]):
            return "smartphone"
        
        # Check for spirits/beverages
        if any(term in product_lower for term in ["gin", "vodka", "whiskey", "rum", "brandy", "tequila"]) or \
           any(term in industry_lower for term in ["spirit", "alcohol", "liquor", "beverage"]):
            
            # Identify specific spirit type
            if "gin" in product_lower:
                return "spirits.gin"
            elif "whiskey" in product_lower or "whisky" in product_lower or "bourbon" in product_lower:
                return "spirits.whiskey"
            elif "vodka" in product_lower:
                return "spirits.vodka"
            elif "rum" in product_lower:
                return "spirits.rum"
            else:
                return "spirits"
        
        # Check for luxury watch
        if "watch" in product_lower or "timepiece" in product_lower:
            return "luxury_watch"
        
        # Check for perfume
        if any(term in product_lower for term in ["perfume", "fragrance", "cologne", "scent"]):
            return "perfume"
        
        # Check for sneakers
        if any(term in product_lower for term in ["sneaker", "shoe", "footwear", "trainer"]):
            return "sneakers"
        
        # Default to generic
        return "generic"
    
    def _get_product_template(self, product_type: str) -> Dict[str, Any]:
        """Get product-specific template for detailed styling."""
        if not product_type or product_type == "generic":
            return {}
            
        # Handle sub-types (e.g., spirits.gin)
        if "." in product_type:
            main_type, sub_type = product_type.split(".", 1)
            template = self.product_specific_templates.get(main_type, {})
            
            # Add specialized sub-type details if available
            if "specialized" in template and sub_type in template["specialized"]:
                # Create a deep copy of template
                result = {k: v for k, v in template.items() if k != "specialized"}
                
                # Add specialized details
                specialized = template["specialized"][sub_type]
                for key, value in specialized.items():
                    if key in result:
                        if isinstance(result[key], dict) and isinstance(value, dict):
                            # Merge dictionaries
                            result[key].update(value)
                        else:
                            # Replace value
                            result[key] = value
                    else:
                        # Add new key
                        result[key] = value
                
                return result
            
            return template
        else:
            return self.product_specific_templates.get(product_type, {})
    
    def _select_best_ad_style(self, industry: str, brand_level: str, product_type: str) -> str:
        """Select the most appropriate ad style based on industry, brand level and product."""
        industry_template = self._map_industry_to_template(industry)
        brand_template = self._map_brand_level(brand_level)
        
        # Get preferred styles from industry and brand templates
        industry_styles = industry_template.get("preferred_styles", [])
        brand_styles = brand_template.get("preferred_styles", [])
        
        # Find common preferred styles
        common_styles = [style for style in industry_styles if style in brand_styles]
        
        # Use common style if available, otherwise use first industry style
        if common_styles:
            return common_styles[0]
        elif industry_styles:
            return industry_styles[0]
        else:
            # Product-specific style selection based on product type
            if product_type == "smartphone":
                return "technical"
            elif product_type.startswith("spirits"):
                return "luxury"
            elif product_type == "luxury_watch":
                return "luxury"
            elif product_type == "perfume":
                return "minimal"
            elif product_type == "sneakers":
                return "lifestyle"
            
            # Default to minimal
            return "minimal"
    
    def _select_composition_template(self, ad_style: str, product_type: str) -> Dict[str, Any]:
        """Select appropriate composition template based on ad style and product."""
        style_composition = self.ad_styles.get(ad_style, {}).get("composition", "centered")
        return self.composition_templates.get(style_composition, self.composition_templates["centered"])
    
    def generate_product_image(self, product: str, brand_name: str = None, industry: str = None, 
                             image_description: str = None, visual_focus: str = None,
                             brand_level: str = "premium", text_placement: str = "dynamic",
                             with_typography_zones: bool = True) -> str:
        """
        Generate studio-quality product image with typography zones.
        
        Args:
            product: Product name/description
            brand_name: Brand name (optional)
            industry: Industry category (optional)
            image_description: Specific image description (optional)
            visual_focus: Specific aspect to focus on (optional)
            brand_level: Brand positioning level (optional)
            text_placement: Text placement style (optional)
            with_typography_zones: Whether to include text zones in prompt (optional)
            
        Returns:
            Path to generated image
        """
        try:
            # Check if we can import OpenAI
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_api_key)
            except ImportError:
                self.logger.error("OpenAI package not installed. Please install with: pip install openai")
                return self._create_fallback_image(product, brand_name)
            
            # Identify product type for specific styling
            product_type = self._identify_product_type(product, industry)
            product_template = self._get_product_template(product_type)
            
            # Select best ad style
            ad_style = self._select_best_ad_style(industry, brand_level, product_type)
            self.logger.info(f"Selected ad style: {ad_style} for {product} (product type: {product_type})")
            
            # Get templates
            industry_template = self._map_industry_to_template(industry)
            brand_template = self._map_brand_level(brand_level)
            style_template = self.ad_styles.get(ad_style, {})
            composition_template = self._select_composition_template(ad_style, product_type)
            
            # Create optimized prompt for studio-quality product photography
            prompt = self._craft_studio_photography_prompt(
                product=product,
                brand_name=brand_name,
                industry_template=industry_template,
                brand_template=brand_template,
                style_template=style_template,
                composition_template=composition_template,
                product_template=product_template,
                image_description=image_description,
                visual_focus=visual_focus,
                with_typography_zones=with_typography_zones,
                text_placement=text_placement,
                product_type=product_type
            )
            
            # Generate a unique cache key
            cache_key = f"{product}_{brand_name}_{industry}_{brand_level}_{ad_style}"
            
            # Check cache first
            if cache_key in self.image_cache:
                self.logger.info(f"Using cached image for {cache_key}")
                return self.image_cache[cache_key]
            
            self.logger.info(f"Generating studio-quality ad image for {product}")
            self.logger.debug(f"Using prompt: {prompt[:500]}...")
            
            # Generate image with DALL-E 3
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="hd",
                n=1
            )
            
            image_url = response.data[0].url
            
            # Download image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Save the raw image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_filepath = f"output/images/base/studio_base_{timestamp}.png"
            
            with open(raw_filepath, 'wb') as f:
                f.write(image_response.content)
            
            self.logger.info(f"Raw image saved to: {raw_filepath}")
            
            # Apply professional image enhancements
            enhanced_path = self._enhance_image_quality(raw_filepath, ad_style, product_type)
            
            # Cache the result
            self.image_cache[cache_key] = enhanced_path
            
            return enhanced_path
            
        except Exception as e:
            self.logger.error(f"Error generating product image: {str(e)}")
            self.logger.error(traceback.format_exc())
            return self._create_fallback_image(product, brand_name)
    
    def _craft_studio_photography_prompt(self, product: str, brand_name: str,
                                       industry_template: Dict[str, Any],
                                       brand_template: Dict[str, Any],
                                       style_template: Dict[str, Any],
                                       composition_template: Dict[str, Any],
                                       product_template: Dict[str, Any] = None,
                                       image_description: str = None,
                                       visual_focus: str = None,
                                       with_typography_zones: bool = True,
                                       text_placement: str = "dynamic",
                                       product_type: str = "generic") -> str:
        """
        Create optimized DALL-E prompt for professional ad photography.
        
        Args:
            product: Product name/description
            brand_name: Brand name
            industry_template: Industry-specific template
            brand_template: Brand level template
            style_template: Ad style template
            composition_template: Composition template
            product_template: Product-specific template
            image_description: Custom image description
            visual_focus: Element to focus on
            with_typography_zones: Whether to include text zones in prompt
            text_placement: Text placement style
            product_type: Specific product type
            
        Returns:
            Optimized DALL-E prompt
        """
        # Build main description
        if image_description:
            main_description = image_description
        else:
            # Combine brand name with product if available
            product_info = f"{brand_name} {product}" if brand_name else product
            
            # Get lighting and background from industry template
            lighting = industry_template.get("lighting", "professional studio lighting")
            background = industry_template.get("background", "clean studio background")
            
            # Get style prompt elements
            style_elements = style_template.get("prompt_elements", ["professional product photography"])
            style_element = random.choice(style_elements) if style_elements else "professional product photography"
            
            # Create main description
            main_description = f"Professional advertisement photograph of {product_info} with {lighting} against {background}. {style_element}."
        
        # Get composition cues
        composition_cues = composition_template.get("prompt_cues", [])
        composition_cue = random.choice(composition_cues) if composition_cues else "balanced composition"
        
        # Build visual style section
        color_palette = industry_template.get("color_palette", ["brand colors"])
        palette_description = ", ".join(random.sample(color_palette, min(2, len(color_palette))))
        
        environment_cues = industry_template.get("environment_cues", [])
        environment_cue = random.choice(environment_cues) if environment_cues else "professional environment"
        
        visual_style = f"""
        VISUAL STYLE:
        - {composition_cue}
        - Color palette: {palette_description}
        - {environment_cue}
        - {visual_focus if visual_focus else "Focus on product as hero"}
        """
        
        # Build product-specific styling section
        product_styling = ""
        if product_template:
            # Get composition details
            if "composition" in product_template:
                comp = product_template["composition"]
                product_styling += f"""
                PRODUCT COMPOSITION:
                - Primary view: {comp.get('primary_angle', 'optimal angle showing key features')}
                """
                
                if "secondary_angles" in comp and comp["secondary_angles"]:
                    angles = ", ".join(comp["secondary_angles"][:2])
                    product_styling += f"- Secondary elements: {angles}\n"
                
                if "placement" in comp:
                    product_styling += f"- Placement: {comp['placement']}\n"
            
            # Get detail focus
            if "details" in product_template:
                details = product_template["details"]
                detail_points = []
                
                for key, value in details.items():
                    detail_points.append(f"- {key.capitalize()}: {value}")
                
                if detail_points:
                    product_styling += """
                    DETAIL FOCUS:
                    """ + "\n".join(detail_points) + "\n"
            
            # Get lighting details
            if "lighting" in product_template:
                lighting = product_template["lighting"]
                lighting_points = []
                
                for key, value in lighting.items():
                    lighting_points.append(f"- {key.capitalize()}: {value}")
                
                if lighting_points:
                    product_styling += """
                    LIGHTING SPECIFICS:
                    """ + "\n".join(lighting_points) + "\n"
        
        # Special handling for spirits
        if product_type.startswith("spirits"):
            # Extract spirit type
            spirit_type = product_type.split(".", 1)[1] if "." in product_type else "generic"
            
            # Add specialized spirit styling
            if spirit_type == "gin":
                product_styling += f"""
                GIN-SPECIFIC STYLING:
                - Bottle: Showcase the iconic blue {brand_name} bottle with crystal clear glass and perfect label detail
                - Glassware: Use a copa de balón or highball glass with crystal clear glass
                - Drink: Classic gin and tonic with clear liquid, perfectly formed ice cubes, and a fresh slice of lime or lemon
                - Garnishes: Include fresh juniper berries, coriander seeds, and citrus peel arranged artfully around the bottle
                - Surface: Place on polished marble surface with subtle reflections
                - Lighting: Cool blue ambient lighting that complements the bottle color
                - Background: Luxurious bar environment with soft bokeh effects and minimal distractions
                """
            elif spirit_type == "whiskey":
                product_styling += """
                WHISKEY-SPECIFIC STYLING:
                - Bottle: Showcase the bottle with perfect label clarity and amber liquid visibility
                - Glassware: Use a rocks glass or Glencairn with crystal clarity
                - Pour: Show perfect pour with rich amber color and light refraction
                - Garnishes: Minimal or subtle orange peel if appropriate
                - Surface: Rich wood or leather surface with subtle grain
                - Lighting: Warm amber lighting that complements the liquid color
                - Background: Classic bar or library setting with warm tones
                """
            elif spirit_type == "vodka":
                product_styling += """
                VODKA-SPECIFIC STYLING:
                - Bottle: Showcase the bottle with perfect clarity and frosted elements if present
                - Glassware: Use a martini glass or chilled shot glass with frost effect
                - Liquid: Crystal clear with perfect light refraction
                - Garnishes: Minimal, perhaps lemon twist or olives
                - Surface: Icy or metallic surface with condensation elements
                - Lighting: Cool blue/white lighting with crystalline highlights
                - Background: Modern, clean setting with cool tones
                """
        
        # Build typography zones section if requested
        typography_section = ""
        if with_typography_zones:
            # Get text zones from composition template
            text_zones = composition_template.get("text_zones", {})
            
            # Get typography zones from industry template
            industry_typography_zones = industry_template.get("typography_zones", [])
            
            # Get text integration guidance
            text_integration = industry_template.get("text_integration", [])
            integration_guidance = random.choice(text_integration) if text_integration else "text integrates harmoniously with image"
            
            typography_section = f"""
            TYPOGRAPHY ZONES:
            - {industry_typography_zones[0] if industry_typography_zones else "Clear space at top for headline"}
            - {industry_typography_zones[1] if len(industry_typography_zones) > 1 else "Space at bottom for supporting text"}
            - {integration_guidance}
            - Composition allows for {text_placement} text placement
            """
        
        # Build photography directives
        composition_elements = industry_template.get("composition_elements", [])
        composition_element = random.choice(composition_elements) if composition_elements else "clear product focus"
        
        photography_directives = f"""
        PHOTOGRAPHY DIRECTIVES:
        - {composition_element}
        - Frame with professional advertisement composition
        - Create depth and dimension with strategic lighting
        - Ensure product details are crystal clear and perfectly lit
        - Use premium color grading with perfect white balance
        """
        
        # Build reference and quality guidance
        inspiration_brands = industry_template.get("inspiration_brands", [])
        inspiration_reference = f"similar to premium {', '.join(inspiration_brands)} advertisements" if inspiration_brands else "magazine-quality advertisement"
        
        reference_guidance = f"""
        REFERENCE & QUALITY GUIDANCE:
        - Create advertisement-quality photography {inspiration_reference}
        - Ensure hyper-realistic photographic quality, not illustrative
        - Composition should allow for typography as specified
        - 8K resolution, photo-realistic commercial advertising photography
        - This should look like it belongs in a high-end advertisement or editorial
        """
        
        # Combine all sections into final prompt
        complete_prompt = f"""
        {main_description}
        
        {visual_style}
        
        {product_styling}
        
        {typography_section}
        
        {photography_directives}
        
        {reference_guidance}
        
        VERY IMPORTANT: The image must leave appropriate space for text placement that will be added later.
        The final image should be indistinguishable from professional commercial photography.
        """
        
        return complete_prompt.strip()
    
    def _enhance_image_quality(self, image_path: str, ad_style: str = None, product_type: str = None) -> str:
        """
        Apply professional image enhancements based on ad style and product type.
        
        Args:
            image_path: Path to the image
            ad_style: Ad style for style-specific enhancements
            product_type: Product type for specialized enhancements
            
        Returns:
            Path to enhanced image
        """
        try:
            # Open the image
            img = Image.open(image_path)
            
            # Apply style-specific enhancements
            if ad_style == "dramatic":
                # Dramatic style - higher contrast, deeper blacks
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.2)
                
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(0.95)
                
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(1.15)
                
                # Custom shadow deepening
                img = self._deepen_shadows(img, amount=0.2)
                
            elif ad_style == "minimal":
                # Minimal style - cleaner, brighter look
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.05)
                
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.08)
                
                # Slightly desaturate for minimal aesthetic
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(0.95)
                
            elif ad_style == "luxury":
                # Luxury style - rich colors, deep shadows
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.15)
                
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(1.1)
                
                # Custom shadow deepening
                img = self._deepen_shadows(img, amount=0.2)
                
                # Add subtle vignette for premium feel
                img = self._add_subtle_vignette(img)
                
            elif ad_style == "lifestyle":
                # Lifestyle style - warmer, more vibrant
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.1)
                
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.05)
                
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(1.2)
                
                # Add warmth
                img = self._add_warmth(img, amount=0.15)
                
            # Product-specific enhancements
            if product_type:
                if product_type.startswith("spirits"):
                    # Enhance reflections and glass clarity
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(1.3)
                    
                    # Enhance highlights for glass and liquid
                    img = self._enhance_highlights(img, 1.15)
                    
                    # Special handling for gin - enhance blue tones
                    if "gin" in product_type:
                        img = self._enhance_color_tone(img, "blue", amount=0.15)
                    
                    # Special handling for whiskey - enhance amber tones
                    elif "whiskey" in product_type:
                        img = self._enhance_color_tone(img, "amber", amount=0.2)
                
                elif product_type == "luxury_watch":
                    # Enhance details and metal highlights
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(1.4)
                    
                    # Enhance contrast for detailed elements
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(1.15)
                    
                    # Enhance reflections on metal and crystal
                    img = self._enhance_highlights(img, 1.2)
            
            # Common final enhancements
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.3)
            
            # Save enhanced image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            enhanced_path = f"output/images/enhanced/enhanced_{timestamp}.png"
            img.save(enhanced_path, "PNG", quality=100)
            
            self.logger.info(f"Enhanced image saved to: {enhanced_path}")
            return enhanced_path
        
        except Exception as e:
            self.logger.warning(f"Image enhancement failed: {str(e)}")
            return image_path  # Return original if enhancement fails
    
    def _deepen_shadows(self, img: Image.Image, amount: float = 0.2) -> Image.Image:
        """Deepen shadows in image for luxury look."""
        # Convert to numpy array for processing
        img_array = np.array(img.convert('RGB'))
        
        # Create a shadow mask (darker areas)
        luminance = 0.299 * img_array[:,:,0] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,2]
        shadow_mask = (luminance < 128).astype(np.float32) * amount
        
        # Apply shadow darkening
        for i in range(3):
            img_array[:,:,i] = img_array[:,:,i] * (1 - shadow_mask)
        
        # Convert back to PIL Image
        return Image.fromarray(img_array.astype(np.uint8))
    
    def _add_warmth(self, img: Image.Image, amount: float = 0.1) -> Image.Image:
        """Add warmth to image for lifestyle appeal."""
        # Split into RGB channels
        r, g, b = img.convert('RGB').split()
        
        # Increase red channel, slightly decrease blue
        r_data = np.array(r)
        b_data = np.array(b)
        
        r_data = np.clip(r_data * (1 + amount), 0, 255).astype(np.uint8)
        b_data = np.clip(b_data * (1 - amount/2), 0, 255).astype(np.uint8)
        
        # Merge channels back
        r_adjusted = Image.fromarray(r_data)
        b_adjusted = Image.fromarray(b_data)
        
        return Image.merge('RGB', (r_adjusted, g, b_adjusted))
    
    def _enhance_highlights(self, img: Image.Image, amount: float = 1.2) -> Image.Image:
        """Enhance highlights for reflective surfaces and glass."""
        # Convert to numpy array for processing
        img_array = np.array(img.convert('RGB')).astype(np.float32)
        
        # Create a highlight mask (brighter areas)
        luminance = 0.299 * img_array[:,:,0] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,2]
        highlight_mask = (luminance > 180).astype(np.float32) * (amount - 1.0)
        
        # Apply highlight enhancement
        for i in range(3):
            img_array[:,:,i] = img_array[:,:,i] * (1.0 + highlight_mask)
        
        # Clip values to valid range
        img_array = np.clip(img_array, 0, 255)
        
        # Convert back to PIL Image
        return Image.fromarray(img_array.astype(np.uint8))
    
    def _enhance_color_tone(self, img: Image.Image, tone: str, amount: float = 0.15) -> Image.Image:
        """Enhance specific color tone in the image."""
        # Split into RGB channels
        r, g, b = img.convert('RGB').split()
        
        # Convert to numpy arrays
        r_data = np.array(r).astype(np.float32)
        g_data = np.array(g).astype(np.float32)
        b_data = np.array(b).astype(np.float32)
        
        if tone == "blue":
            # Enhance blue tones
            b_data = np.clip(b_data * (1 + amount), 0, 255)
            
            # Slight adjustment to other channels for balance
            r_data = np.clip(r_data * (1 - amount/3), 0, 255)
            
        elif tone == "amber":
            # Enhance amber (red and green, less blue)
            r_data = np.clip(r_data * (1 + amount), 0, 255)
            g_data = np.clip(g_data * (1 + amount/2), 0, 255)
            b_data = np.clip(b_data * (1 - amount/3), 0, 255)
            
        elif tone == "cool":
            # Enhance cool tones (more blue, less red)
            b_data = np.clip(b_data * (1 + amount), 0, 255)
            r_data = np.clip(r_data * (1 - amount/2), 0, 255)
            
        # Convert back to 8-bit
        r_adjusted = Image.fromarray(r_data.astype(np.uint8))
        g_adjusted = Image.fromarray(g_data.astype(np.uint8))
        b_adjusted = Image.fromarray(b_data.astype(np.uint8))
        
        # Merge channels back
        return Image.merge('RGB', (r_adjusted, g_adjusted, b_adjusted))
    
    def _add_subtle_vignette(self, img: Image.Image, amount: float = 0.3) -> Image.Image:
        """Add subtle vignette effect for premium look."""
        # Create a radial gradient mask
        width, height = img.size
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 2
        
        mask = Image.new('L', img.size, 255)
        draw = ImageDraw.Draw(mask)
        
        # Create gradient
        for r in range(radius, int(radius * 1.5)):
            # Calculate opacity based on distance from radius
            opacity = int(255 * (1.0 - amount * (r - radius) / (radius * 0.5)))
            opacity = max(0, min(255, opacity))
            
            # Draw circle with calculated opacity
            draw.ellipse((center_x - r, center_y - r, center_x + r, center_y + r), fill=opacity)
        
        # Apply mask
        return Image.composite(img, Image.new('RGB', img.size, (0, 0, 0)), mask)
    
    def apply_integrated_typography(self, image_path: str, headline: str, subheadline: str = None,
                                  call_to_action: str = None, brand_name: str = None,
                                  industry: str = None, brand_level: str = "premium",
                                  text_placement: str = "dynamic", color_scheme: str = None) -> str:
        """
        Apply advanced typography that integrates with the image.
        
        Args:
            image_path: Path to base image
            headline: Main headline text
            subheadline: Subheadline text (optional)
            call_to_action: Call to action text (optional)
            brand_name: Brand name (optional)
            industry: Industry category (optional)
            brand_level: Brand positioning level (optional)
            text_placement: Text placement style (optional)
            color_scheme: Color scheme to use (optional)
        
        Returns:
            Path to final image with integrated typography
        """
        try:
            # Check if image exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            # Open original image
            original_image = Image.open(image_path).convert('RGBA')
            width, height = original_image.size
            
            # Identify product type for typography styling
            product_type = self._identify_product_type(headline, industry)
            
            # Select ad style based on industry and brand level
            ad_style = self._select_best_ad_style(industry, brand_level, product_type)
            style_template = self.ad_styles.get(ad_style, {})
            industry_template = self._map_industry_to_template(industry)
            brand_template = self._map_brand_level(brand_level)
            composition_template = self._select_composition_template(ad_style, product_type)
            
            # Analyze image for optimal text placement
            brightness_map = self.image_analyzer.analyze_brightness_map(original_image)
            composition_analysis = self._analyze_image_composition(original_image)
            
            # Extract dominant colors for color scheme
            dominant_colors = self.color_scheme_generator.extract_dominant_colors(original_image)
            
            # Generate color scheme
            if not color_scheme:
                # Use industry-specific color preferences
                color_palette = industry_template.get("color_palette", [])
                if color_palette and "brand_color" in color_palette:
                    # Use first dominant color as brand color
                    if dominant_colors:
                        brand_color = dominant_colors[0]
                    else:
                        brand_color = (41, 128, 185)  # Default blue
                    
                    color_scheme = f"brand color #{brand_color[0]:02x}{brand_color[1]:02x}{brand_color[2]:02x}"
            
            # Get typography style from brand template
            typography_styles = brand_template.get("typography", {}).get("preferred_styles", ["modern"])
            typography_style = typography_styles[0] if typography_styles else "modern"
            
            # Get text treatment preferences
            text_effects = brand_template.get("typography", {}).get("text_effects", ["shadow"])
            headline_treatment = brand_template.get("typography", {}).get("headline_treatment", "shadow")
            
            # Calculate optimal font sizes based on image dimensions and brand level
            headline_size_factor = style_template.get("typography", {}).get("headline_size_factor", 0.075)
            subheadline_size_factor = style_template.get("typography", {}).get("subheadline_size_factor", 0.035)
            
            headline_size = int(height * headline_size_factor)
            subheadline_size = int(height * subheadline_size_factor)
            cta_size = int(height * 0.035)
            brand_size = int(height * 0.045)
            
            # Get preferred font weights
            headline_weight = style_template.get("typography", {}).get("headline_weight", "bold")
            
            # Load fonts
            try:
                headline_font = self.font_manager.get_font(typography_style, "headline", headline_size, brand_name)
                subheadline_font = self.font_manager.get_font(typography_style, "subheadline", subheadline_size, brand_name)
                cta_font = self.font_manager.get_font(typography_style, "cta", cta_size, brand_name)
                brand_font = self.font_manager.get_font(typography_style, "headline", brand_size, brand_name)
            except Exception as e:
                self.logger.error(f"Error loading fonts: {str(e)}")
                # Fallback to system fonts
                headline_font = ImageFont.truetype("arial.ttf", headline_size) if os.path.exists("arial.ttf") else ImageFont.load_default()
                subheadline_font = ImageFont.truetype("arial.ttf", subheadline_size) if os.path.exists("arial.ttf") else ImageFont.load_default()
                cta_font = ImageFont.truetype("arial.ttf", cta_size) if os.path.exists("arial.ttf") else ImageFont.load_default()
                brand_font = ImageFont.truetype("arial.ttf", brand_size) if os.path.exists("arial.ttf") else ImageFont.load_default()
            
            # Set up text elements
            text_elements = {
                'headline': headline or "",
                'subheadline': subheadline or "",
                'call_to_action': call_to_action or "",
                'brand_name': brand_name or ""
            }
            
            # Determine optimal text positions based on composition and brightness
            text_positions = self._determine_optimal_text_positions(
                width, height, 
                text_elements,
                composition_analysis, 
                brightness_map, 
                composition_template,
                text_placement
            )
            
            # Determine optimal text colors based on image and brand
            text_colors = self._determine_optimal_text_colors(
                dominant_colors, 
                brightness_map, 
                color_scheme
            )
            
            # Create transparent overlay for text
            text_overlay = Image.new('RGBA', original_image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(text_overlay)
            
            # Apply brand name if provided
            if brand_name and brand_name in text_elements:
                brand_text = text_elements['brand_name']
                brand_position = text_positions.get('brand_name', (width // 2, height // 10))
                brand_effect = 'minimal_elegant'
                
                # Apply brand name with subtle effect
                self._apply_text_with_effect(
                    draw, text_overlay, 
                    brand_text, 
                    brand_position, 
                    brand_font, 
                    text_colors['brand_name'], 
                    brand_effect, 
                    brightness_map,
                    original_image
                )
            
            # Apply headline with premium effect
            if headline and headline in text_elements:
                headline_text = text_elements['headline']
                headline_position = text_positions.get('headline', (width // 2, height // 4))
                
                # Apply headline with integrated effect
                self._apply_text_with_effect(
                    draw, text_overlay, 
                    headline_text, 
                    headline_position, 
                    headline_font, 
                    text_colors['headline'], 
                    headline_treatment, 
                    brightness_map,
                    original_image
                )
            
            # Apply subheadline if provided
            if subheadline and subheadline in text_elements:
                subheadline_text = text_elements['subheadline']
                subheadline_position = text_positions.get('subheadline', (width // 2, height // 3))
                subheadline_effect = text_effects[0] if text_effects else 'subtle_shadow'
                
                # Apply subheadline with subtle effect
                self._apply_text_with_effect(
                    draw, text_overlay, 
                    subheadline_text, 
                    subheadline_position, 
                    subheadline_font, 
                    text_colors['subheadline'], 
                    subheadline_effect, 
                    brightness_map,
                    original_image
                )
            
            # Apply call-to-action with button if provided
            if call_to_action and call_to_action in text_elements:
                cta_text = text_elements['call_to_action']
                cta_position = text_positions.get('call_to_action', (width // 2, height * 4 // 5))
                
                # Determine button style based on brand level
                if brand_level and "luxury" in brand_level.lower():
                    button_style = "minimal_line"
                elif brand_level and "premium" in brand_level.lower():
                    button_style = "rounded"
                else:
                    button_style = "pill"
                
                # Apply CTA button
                self._apply_cta_button(
                    draw, text_overlay,
                    cta_text, 
                    cta_position, 
                    cta_font, 
                    text_colors['call_to_action'], 
                    text_colors['cta_button'],
                    button_style,
                    brightness_map
                )
            
            # Composite the text overlay with original image
            # Use soft light blending mode for better integration
            final_image = self._blend_text_with_image(original_image, text_overlay)
            
            # Save the final image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_path = f"output/images/final/final_ad_{timestamp}.png"
            final_image.convert('RGB').save(final_path, 'PNG', quality=100)
            
            self.logger.info(f"Final image with integrated typography saved: {final_path}")
            return final_path
            
        except Exception as e:
            self.logger.error(f"Typography application error: {str(e)}")
            self.logger.error(traceback.format_exc())
            return image_path  # Return original if typography fails
    
    def _analyze_image_composition(self, image: Image.Image) -> Dict[str, Any]:
        """
        Analyze image composition to determine optimal text placement.
        
        Args:
            image: PIL Image
            
        Returns:
            Dictionary with composition analysis
        """
        try:
            # Convert to grayscale for analysis
            gray = image.convert('L')
            width, height = gray.size
            
            # Analyze edges to find subject position
            edges = gray.filter(ImageFilter.FIND_EDGES)
            edge_data = np.array(edges)
            
            # Find strongest edge regions
            threshold = np.percentile(edge_data, 75)
            strong_edges = edge_data > threshold
            
            # Find subject position (approximate center of strong edges)
            y_indices, x_indices = np.where(strong_edges)
            
            if len(y_indices) > 0 and len(x_indices) > 0:
                subject_x = int(np.mean(x_indices))
                subject_y = int(np.mean(y_indices))
                
                # Normalize to 0-1 range
                subject_x_norm = subject_x / width
                subject_y_norm = subject_y / height
            else:
                # Default to center if no strong edges
                subject_x_norm = 0.5
                subject_y_norm = 0.5
            
            # Analyze image thirds (rule of thirds)
            third_w = width // 3
            third_h = height // 3
            
            # Check which third contains most edge content
            thirds = {}
            for row in range(3):
                for col in range(3):
                    region = edge_data[row*third_h:(row+1)*third_h, col*third_w:(col+1)*third_w]
                    thirds[f"{row}_{col}"] = np.sum(region)
            
            # Find third with most content
            strongest_third = max(thirds.items(), key=lambda x: x[1])
            
            # Determine subject position in terms of thirds
            subject_third_row = int(subject_y_norm * 3)
            subject_third_col = int(subject_x_norm * 3)
            
            return {
                "subject_position": {"x": subject_x_norm, "y": subject_y_norm},
                "subject_third": {"row": subject_third_row, "col": subject_third_col},
                "strongest_third": strongest_third[0],
                "has_clear_subject": np.max(thirds.values()) > np.mean(list(thirds.values())) * 2
            }
            
        except Exception as e:
            self.logger.warning(f"Image composition analysis failed: {str(e)}")
            # Return default analysis
            return {
                "subject_position": {"x": 0.5, "y": 0.5},
                "subject_third": {"row": 1, "col": 1},
                "strongest_third": "1_1",
                "has_clear_subject": False
            }
    
    def _determine_optimal_text_positions(self, width: int, height: int, 
                                        text_elements: Dict[str, str],
                                        composition: Dict[str, Any], 
                                        brightness_map: Dict[str, float],
                                        composition_template: Dict[str, Any],
                                        text_placement: str) -> Dict[str, Tuple[int, int]]:
        """
        Determine optimal positions for text elements based on image analysis.
        
        Args:
            width: Image width
            height: Image height
            text_elements: Dictionary of text elements
            composition: Composition analysis dictionary
            brightness_map: Brightness map dictionary
            composition_template: Composition template
            text_placement: Text placement style
            
        Returns:
            Dictionary with optimal positions for each text element
        """
        # Positions dictionary
        positions = {}
        
        # Get text zones from composition template
        text_zones = composition_template.get("text_zones", {})
        
        # If text_placement is dynamic and we have composition data, use it
        if text_placement == "dynamic" and composition.get("has_clear_subject", False):
            # Get subject position
            subject_x = composition["subject_position"]["x"]
            subject_y = composition["subject_position"]["y"]
            
            # Place text in opposite area to subject
            # If subject is in left third, place text in right third
            x_placement = width * 0.8 if subject_x < 0.5 else width * 0.2
            
            # If subject is in top half, place text in bottom
            if subject_y < 0.4:
                # Text in bottom area
                headline_y = height * 0.75
                subheadline_y = height * 0.82
                cta_y = height * 0.9
                brand_y = height * 0.68
            elif subject_y > 0.6:
                # Text in top area
                headline_y = height * 0.25
                subheadline_y = height * 0.32
                cta_y = height * 0.45
                brand_y = height * 0.15
            else:
                # Subject in middle, check brightness
                if brightness_map.get("top_center", 0.5) < brightness_map.get("bottom_center", 0.5):
                    # Top is darker, place text there for contrast
                    headline_y = height * 0.25
                    subheadline_y = height * 0.32
                    cta_y = height * 0.45
                    brand_y = height * 0.15
                else:
                    # Bottom is darker or equal, place text there
                    headline_y = height * 0.75
                    subheadline_y = height * 0.82
                    cta_y = height * 0.9
                    brand_y = height * 0.68
            
            # Set positions with appropriate alignment
            positions['headline'] = (int(x_placement), int(headline_y))
            positions['subheadline'] = (int(x_placement), int(subheadline_y))
            positions['call_to_action'] = (int(x_placement), int(cta_y))
            positions['brand_name'] = (int(x_placement), int(brand_y))
            
        else:
            # Use composition template zones
            for element, element_text in text_elements.items():
                if not element_text:
                    continue
                
                # Get zone for this element
                zone = text_zones.get(element.replace('_name', ''), {})
                
                # Get y-range from zone
                y_range = zone.get('y_range', [0.5, 0.6])
                y_position = height * random.uniform(y_range[0], y_range[1])
                
                # Get x-alignment from zone or use centered
                x_align = zone.get('x_align', 'center')
                preferred_alignment = zone.get('preferred_alignment', 'center')
                
                # Calculate x-position
                if x_align == 'left':
                    x_position = width * 0.1
                elif x_align == 'right':
                    x_position = width * 0.9
                elif x_align == 'opposite_product' and composition.get("subject_position"):
                    # Place opposite to subject
                    subject_x = composition["subject_position"]["x"]
                    x_position = width * 0.8 if subject_x < 0.5 else width * 0.2
                elif x_align == 'with_headline' and 'headline' in positions:
                    # Place aligned with headline
                    x_position = positions['headline'][0]
                elif x_align == 'dynamic':
                    # Use darker area for better contrast
                    left_brightness = brightness_map.get('middle_left', 0.5)
                    right_brightness = brightness_map.get('middle_right', 0.5)
                    x_position = width * 0.8 if left_brightness < right_brightness else width * 0.2
                else:
                    # Default to center
                    x_position = width * 0.5
                
                # Add position to dictionary
                positions[element] = (int(x_position), int(y_position))
        
        return positions
    
    def _determine_optimal_text_colors(self, dominant_colors: List[Tuple[int, int, int]],
                                      brightness_map: Dict[str, float],
                                      color_scheme: str = None) -> Dict[str, Tuple[int, int, int, int]]:
        """
        Determine optimal text and accent colors based on image and scheme.
        
        Args:
            dominant_colors: List of dominant colors from image
            brightness_map: Brightness map dictionary
            color_scheme: Color scheme specification
            
        Returns:
            Dictionary with colors for different text elements
        """
        # Default colors
        default_light_text = (255, 255, 255, 255)  # White
        default_dark_text = (10, 10, 10, 255)      # Near black
        default_accent = (41, 128, 185, 255)       # Blue accent
        
        # Determine base text color based on image brightness
        overall_brightness = brightness_map.get('overall', 0.5)
        base_text_color = default_dark_text if overall_brightness > 0.6 else default_light_text
        
        # Process color scheme if specified
        if color_scheme:
            scheme_lower = color_scheme.lower()
            
            # Extract hex color if present
            hex_match = re.search(r'#(?:[0-9a-fA-F]{3}){1,2}', scheme_lower)
            
            if hex_match:
                # Use specified hex color as accent
                hex_color = hex_match.group(0)
                try:
                    rgb = ImageColor.getrgb(hex_color)
                    accent_color = rgb + (255,)  # Add alpha
                except:
                    accent_color = default_accent
            elif "gold" in scheme_lower:
                accent_color = (212, 175, 55, 255)  # Gold
            elif "silver" in scheme_lower:
                accent_color = (192, 192, 192, 255)  # Silver
            elif "black" in scheme_lower:
                accent_color = (10, 10, 10, 255)  # Black
            elif "white" in scheme_lower:
                accent_color = (240, 240, 240, 255)  # White
            elif "blue" in scheme_lower:
                accent_color = (41, 128, 185, 255)  # Blue
            elif "red" in scheme_lower:
                accent_color = (192, 57, 43, 255)  # Red
            elif "green" in scheme_lower:
                accent_color = (39, 174, 96, 255)  # Green
            elif "purple" in scheme_lower:
                accent_color = (142, 68, 173, 255)  # Purple
            elif "amber" in scheme_lower or "gold" in scheme_lower:
                accent_color = (255, 191, 0, 255)  # Amber
            elif "cool" in scheme_lower:
                accent_color = (64, 138, 210, 255)  # Cool blue
            elif dominant_colors:
                # Use first dominant color
                accent_color = dominant_colors[0] + (255,)  # Add alpha
            else:
                accent_color = default_accent
        elif dominant_colors:
            # If no scheme specified but we have dominant colors
            # Use first dominant color with good contrast as accent
            for color in dominant_colors:
                # Check contrast with text color
                color_brightness = (color[0] * 299 + color[1] * 587 + color[2] * 114) / 1000
                text_brightness = (base_text_color[0] * 299 + base_text_color[1] * 587 + base_text_color[2] * 114) / 1000
                
                # If good contrast with text color, use as accent
                if abs(color_brightness - text_brightness) > 125:
                    accent_color = color + (255,)  # Add alpha
                    break
            else:
                # No good contrast, use default
                accent_color = default_accent
        else:
            accent_color = default_accent
        
        # Derive CTA button color from accent with appropriate contrast
        cta_button_color = self._ensure_contrast_with_text(accent_color, base_text_color)
        
        # Create results dictionary
        return {
            'headline': base_text_color,
            'subheadline': base_text_color,
            'call_to_action': self._ensure_contrast_with_background(base_text_color, cta_button_color),
            'brand_name': accent_color,
            'cta_button': cta_button_color,
            'accent': accent_color
        }
    
    def _ensure_contrast_with_text(self, bg_color: Tuple[int, int, int, int], 
                                 text_color: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """Ensure background color has good contrast with text."""
        bg_brightness = (bg_color[0] * 299 + bg_color[1] * 587 + bg_color[2] * 114) / 1000
        text_brightness = (text_color[0] * 299 + text_color[1] * 587 + text_color[2] * 114) / 1000
        
        # If contrast is too low, adjust bg_color
        if abs(bg_brightness - text_brightness) < 125:
            # Darken or lighten the background
            if text_brightness > 128:
                # Text is light, make bg darker
                return (max(0, bg_color[0] - 100), max(0, bg_color[1] - 100), max(0, bg_color[2] - 100), bg_color[3])
            else:
                # Text is dark, make bg lighter
                return (min(255, bg_color[0] + 100), min(255, bg_color[1] + 100), min(255, bg_color[2] + 100), bg_color[3])
        
        return bg_color
    
    def _ensure_contrast_with_background(self, text_color: Tuple[int, int, int, int], 
                                       bg_color: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """Ensure text color has good contrast with background."""
        bg_brightness = (bg_color[0] * 299 + bg_color[1] * 587 + bg_color[2] * 114) / 1000
        text_brightness = (text_color[0] * 299 + text_color[1] * 587 + text_color[2] * 114) / 1000
        
        # If contrast is too low, adjust text_color
        if abs(bg_brightness - text_brightness) < 125:
            # Darken or lighten the text
            if bg_brightness > 128:
                # Bg is light, make text darker
                return (max(0, text_color[0] - 150), max(0, text_color[1] - 150), max(0, text_color[2] - 150), text_color[3])
            else:
                # Bg is dark, make text lighter
                return (min(255, text_color[0] + 150), min(255, text_color[1] + 150), min(255, text_color[2] + 150), text_color[3])
        
        return text_color
    
    def _apply_text_with_effect(self, draw: ImageDraw, overlay: Image.Image, text: str, 
                              position: Tuple[int, int], font, color: Tuple[int, int, int, int],
                              effect: str, brightness_map: Dict[str, float],
                              original_image: Image.Image) -> None:
        """
        Apply text with professional effect that integrates with the image.
        
        Args:
            draw: ImageDraw object
            overlay: Text overlay image
            text: Text to add
            position: Position (x, y)
            font: Font to use
            color: Text color
            effect: Effect type
            brightness_map: Brightness map dictionary
            original_image: Original image for reference
        """
        x, y = position
        
        # Get text dimensions
        try:
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            # Fallback for older PIL
            try:
                text_width, text_height = font.getsize(text)
            except:
                # Rough estimate
                text_width = len(text) * font.size // 2
                text_height = font.size
        
        # Center align text by default
        x = x - text_width // 2
        
        # Apply text effect based on type
        if effect == 'elegant_serif':
            self._apply_elegant_serif_effect(draw, overlay, text, (x, y), font, color, original_image)
        elif effect == 'clean_gradient':
            self._apply_clean_gradient_effect(draw, overlay, text, (x, y), font, color, original_image)
        elif effect == 'subtle_shadow':
            self._apply_subtle_shadow_effect(draw, overlay, text, (x, y), font, color, brightness_map)
        elif effect == 'subtle_background':
            self._apply_subtle_background_effect(draw, overlay, text, (x, y), font, color, text_width, text_height, brightness_map)
        elif effect == 'gradient':
            self._apply_gradient_effect(draw, overlay, text, (x, y), font, color, original_image)
        elif effect == 'subtle_glow':
            self._apply_subtle_glow_effect(draw, overlay, text, (x, y), font, color, original_image)
        elif effect == 'minimal_elegant':
            self._apply_minimal_elegant_effect(draw, overlay, text, (x, y), font, color, brightness_map)
        elif effect == 'shadow':
            self._apply_shadow_effect(draw, overlay, text, (x, y), font, color, brightness_map)
        else:
            # Default simple text
            draw.text((x, y), text, font=font, fill=color)
    
    def _apply_elegant_serif_effect(self, draw, overlay, text, position, font, color, original_image):
        """Apply elegant serif effect with refined typography."""
        x, y = position
        
        # Create a separate layer for the text effect
        text_layer = Image.new('RGBA', overlay.size, (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        
        # Apply subtle shadow
        shadow_offset = 2
        shadow_color = (0, 0, 0, 80)
        text_draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
        
        # Apply main text
        text_draw.text((x, y), text, font=font, fill=color)
        
        # Apply very subtle glow
        glow_layer = text_layer.copy()
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(1))
        
        # Compose layers
        text_layer = Image.alpha_composite(glow_layer, text_layer)
        
        # Integrate with original image by applying subtle blend mode
        x_offset, y_offset = 0, 0
        overlay_region = overlay.crop((x_offset, y_offset, x_offset + overlay.width, y_offset + overlay.height))
        result = Image.alpha_composite(overlay_region, text_layer)
        overlay.paste(result, (x_offset, y_offset))
    
    def _apply_clean_gradient_effect(self, draw, overlay, text, position, font, color, original_image):
        """Apply clean gradient effect with modern typography."""
        x, y = position
        width, height = overlay.size
        
        # Get text dimensions
        try:
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            # Fallback for older PIL
            try:
                text_width, text_height = font.getsize(text)
            except:
                text_width = len(text) * font.size // 2
                text_height = font.size
        
        # Create a separate layer for the text effect
        text_layer = Image.new('RGBA', overlay.size, (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        
        # Extract color components
        r, g, b, a = color
        
        # Create gradient from top to bottom
        for i in range(text_height):
            # Calculate gradient alpha from top to bottom
            ratio = i / text_height
            alpha = int(a * (1.0 - ratio * 0.3))  # Slight fade to 70% at bottom
            
            # Create text mask for this line
            mask = Image.new('L', (text_width, text_height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.text((0, 0), text, font=font, fill=255)
            
            # Draw this line with proper alpha
            line_color = (r, g, b, alpha)
            text_draw.text((x, y + i), text, font=font, fill=line_color)
        
        # Apply subtle shadow
        shadow_layer = Image.new('RGBA', overlay.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_layer)
        shadow_draw.text((x+1, y+1), text, font=font, fill=(0, 0, 0, 80))
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(1))
        
        # Composite layers
        result = Image.alpha_composite(overlay, shadow_layer)
        result = Image.alpha_composite(result, text_layer)
        
        overlay.paste(result, (0, 0))

    def _apply_subtle_shadow_effect(self, draw, overlay, text, position, font, color, brightness_map):
        """Apply subtle shadow effect for clean, professional typography."""
        x, y = position
        
        # Adjust shadow opacity based on image brightness
        shadow_opacity = int(120 * (1.0 - brightness_map.get('overall', 0.5)))
        shadow_color = (0, 0, 0, shadow_opacity)
        
        # Shadow offset based on text size
        shadow_offset = max(1, font.size // 30)
        
        # Create a separate layer for the shadow
        shadow_layer = Image.new('RGBA', overlay.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_layer)
        
        # Draw shadow
        shadow_draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
        
        # Apply Gaussian blur to shadow
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(1))
        
        # Composite shadow with overlay
        overlay.paste(Image.alpha_composite(overlay, shadow_layer), (0, 0))
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=color)
    
    def _apply_subtle_glow_effect(self, draw, overlay, text, position, font, color, original_image):
        """Apply subtle glow effect that enhances text without overwhelming."""
        x, y = position
        
        # Create a separate layer for the text effect
        text_layer = Image.new('RGBA', overlay.size, (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        
        # Draw text
        text_draw.text((x, y), text, font=font, fill=color)
        
        # Extract color components
        r, g, b, a = color
        
        # Create glow color (slightly brighter)
        glow_color = (min(255, r + 40), min(255, g + 40), min(255, b + 40), 100)
        
        # Create glow mask
        glow_mask = Image.new('RGBA', overlay.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_mask)
        glow_draw.text((x, y), text, font=font, fill=glow_color)
        
        # Apply blur to glow
        glow_mask = glow_mask.filter(ImageFilter.GaussianBlur(2))
        
        # Composite glow and text
        result = Image.alpha_composite(glow_mask, text_layer)
        
        # Integrate with overlay
        overlay.paste(Image.alpha_composite(overlay, result), (0, 0))
    
    def _apply_cta_button(self, draw, overlay, text, position, font, text_color, button_color, button_style, brightness_map):
        """
        Apply professional CTA button with style matching the image.
        """
        x, y = position
        width, height = overlay.size
        
        # Get text dimensions
        try:
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            # Fallback for older PIL
            try:
                text_width, text_height = font.getsize(text)
            except:
                text_width = len(text) * font.size // 2
                text_height = font.size
        
        # Create button layer
        button_layer = Image.new('RGBA', overlay.size, (0, 0, 0, 0))
        button_draw = ImageDraw.Draw(button_layer)
        
        # Calculate button dimensions with proper padding
        padding_x = int(text_width * 0.4)
        padding_y = int(text_height * 0.5)
        
        button_width = text_width + padding_x * 2
        button_height = text_height + padding_y * 2
        
        # Center the button horizontally
        button_x = x - button_width // 2
        button_y = y - button_height // 2
        
        # Define button coordinates
        button_coords = [
            button_x,
            button_y,
            button_x + button_width,
            button_y + button_height
        ]
        
        # Apply button style
        if button_style == "minimal_line":
            # Elegant border-only button
            line_width = max(1, int(text_height * 0.05))
            button_draw.rounded_rectangle(
                button_coords,
                radius=int(button_height * 0.2),
                outline=button_color,
                width=line_width
            )
            
            # Draw text
            text_x = button_x + (button_width - text_width) // 2
            text_y = button_y + (button_height - text_height) // 2
            button_draw.text((text_x, text_y), text, font=font, fill=text_color)
            
        elif button_style == "pill":
            # Pill-shaped button (fully rounded)
            radius = button_height // 2
            
            # Draw button with shadow
            shadow_color = (0, 0, 0, 80)
            button_draw.rounded_rectangle(
                [c + 2 for c in button_coords],
                radius=radius,
                fill=shadow_color
            )
            
            # Draw main button
            button_draw.rounded_rectangle(
                button_coords,
                radius=radius,
                fill=button_color
            )
            
            # Add highlight for 3D effect
            highlight_height = button_height // 2
            highlight_color = (255, 255, 255, 40)
            button_draw.rounded_rectangle(
                [
                    button_x + 2,
                    button_y + 2,
                    button_x + button_width - 2,
                    button_y + highlight_height
                ],
                radius=radius - 2,
                fill=highlight_color
            )
            
            # Draw text
            text_x = button_x + (button_width - text_width) // 2
            text_y = button_y + (button_height - text_height) // 2
            
            # Draw text shadow
            button_draw.text((text_x + 1, text_y + 1), text, font=font, fill=(0, 0, 0, 100))
            
            # Draw text
            button_draw.text((text_x, text_y), text, font=font, fill=text_color)
        
        else:  # "rounded" or default
            # Professional rounded button
            radius = int(button_height * 0.25)
            
            # Draw shadow for depth
            shadow_color = (0, 0, 0, 80)
            button_draw.rounded_rectangle(
                [c + 2 for c in button_coords],
                radius=radius,
                fill=shadow_color
            )
            
            # Draw main button
            button_draw.rounded_rectangle(
                button_coords,
                radius=radius,
                fill=button_color
            )
            
            # Add highlight for 3D effect
            highlight_height = int(button_height * 0.4)
            highlight_color = (255, 255, 255, 60)
            button_draw.rounded_rectangle(
                [
                    button_x + 2, 
                    button_y + 2, 
                    button_x + button_width - 2, 
                    button_y + highlight_height
                ],
                radius=radius - 2,
                fill=highlight_color
            )
            
            # Draw text with slight shadow for depth
            text_x = button_x + (button_width - text_width) // 2
            text_y = button_y + (button_height - text_height) // 2
            
            # Draw shadow
            button_draw.text((text_x + 1, text_y + 1), text, font=font, fill=(0, 0, 0, 100))
            
            # Draw text
            button_draw.text((text_x, text_y), text, font=font, fill=text_color)
        
        # Composite button with overlay
        overlay.paste(Image.alpha_composite(overlay, button_layer), (0, 0))
    
    def _blend_text_with_image(self, image: Image.Image, text_overlay: Image.Image) -> Image.Image:
        """
        Blend text overlay with image using advanced blending techniques.
        """
        # Create a copy of the image to work with
        result = image.copy()
        
        # Simple alpha composite as fallback
        try:
            # First try standard alpha composite
            result = Image.alpha_composite(result.convert('RGBA'), text_overlay)
        except Exception as e:
            self.logger.warning(f"Standard alpha composite failed: {str(e)}")
            # Manual composite as fallback
            result.paste(text_overlay, (0, 0), text_overlay)
        
        return result
    
    def create_studio_ad(self, product: str, brand_name: str = None, headline: str = None,
                       subheadline: str = None, call_to_action: str = None, industry: str = None,
                       brand_level: str = None, typography_style: str = None,
                       color_scheme: str = None, image_description: str = None,
                       visual_focus: str = None, text_placement: str = "dynamic") -> Dict[str, str]:
        """
        Create complete studio-quality ad with integrated typography.
        """
        try:
            self.logger.info(f"Creating studio ad for {product} with brand {brand_name}")
            
            # Step 1: Generate studio-quality product image with typography zones
            base_image_path = self.generate_product_image(
                product=product,
                brand_name=brand_name,
                industry=industry,
                image_description=image_description,
                visual_focus=visual_focus,
                brand_level=brand_level,
                text_placement=text_placement,
                with_typography_zones=True
            )
            
            # Step 2: Apply integrated typography
            final_image_path = self.apply_integrated_typography(
                image_path=base_image_path,
                headline=headline,
                subheadline=subheadline,
                call_to_action=call_to_action,
                brand_name=brand_name,
                industry=industry,
                brand_level=brand_level,
                text_placement=text_placement,
                color_scheme=color_scheme
            )
            
            self.logger.info(f"Successfully created studio ad: {final_image_path}")
            return {
                'base_path': base_image_path,
                'final_path': final_image_path
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create studio ad: {str(e)}")
            self.logger.error(traceback.format_exc())
            
            return self._create_fallback_ad(product, brand_name, headline, subheadline, call_to_action)
    
    def _create_fallback_image(self, product: str, brand_name: str = None) -> str:
        """Create a fallback image when generation fails."""
        try:
            # Default text if none provided
            product_text = product.upper() if product else "PRODUCT"
            brand_text = brand_name.upper() if brand_name else "BRAND"
            
            # Create a gradient background
            width, height = 1024, 1024
            img = Image.new('RGB', (width, height), color=(20, 30, 50))
            draw = ImageDraw.Draw(img)
            
            # Draw gradient background
            for y in range(height):
                # Create a deep blue to deep purple gradient
                r = int(20 + (50 - 20) * y / height)
                g = int(30 + (40 - 30) * y / height)
                b = int(50 + (100 - 50) * y / height)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
            
            # Try to use a system font
            try:
                # Search for common fonts
                font_paths = [
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                    '/Library/Fonts/Arial Bold.ttf',
                    'C:\\Windows\\Fonts\\arialbd.ttf',
                    '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
                ]
                
                headline_font = None
                for path in font_paths:
                    if os.path.exists(path):
                        headline_font = ImageFont.truetype(path, 60)
                        subheadline_font = ImageFont.truetype(path, 30)
                        break
                
                if not headline_font:
                    # Fallback to default
                    headline_font = ImageFont.load_default()
                    subheadline_font = ImageFont.load_default()
            except:
                # Fallback to default font if all else fails
                headline_font = ImageFont.load_default()
                subheadline_font = ImageFont.load_default()
            
            # Add a product placeholder shape
            draw.rectangle([width/4, height/4, width*3/4, height*3/4], 
                          fill=(255, 255, 255, 30), outline=(255, 255, 255))
            
            # Add brand name at top
            draw.text((width/2, height/8), brand_text, fill=(255, 255, 255), anchor="mm", font=headline_font)
            
            # Add product at center
            draw.text((width/2, height/2), product_text, fill=(255, 255, 255), anchor="mm", font=headline_font)
            
            # Add placeholder text
            draw.text((width/2, height*7/8), "Professional Ad Placeholder", fill=(200, 200, 200), anchor="mm", font=subheadline_font)
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            placeholder_path = f"output/images/placeholder_{timestamp}.png"
            img.save(placeholder_path)
            
            return placeholder_path
        except:
            # Absolute last resort
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            placeholder_path = f"output/images/minimal_placeholder_{timestamp}.png"
            
            try:
                img = Image.new('RGB', (1024, 1024), color=(0, 0, 0))
                draw = ImageDraw.Draw(img)
                draw.text((512, 512), "Ad Placeholder", fill=(255, 255, 255))
                img.save(placeholder_path)
            except:
                # Create an empty file if everything else fails
                with open(placeholder_path, 'w') as f:
                    f.write('')
            
            return placeholder_path
    
    def _create_fallback_ad(self, product: str, brand_name: str, 
                          headline: str = None, subheadline: str = None, 
                          call_to_action: str = None) -> Dict[str, str]:
        """Create a fallback ad when the regular process fails."""
        placeholder_path = self._create_fallback_image(product, brand_name)
        
        return {
            'base_path': placeholder_path,
            'final_path': placeholder_path
        }
    

