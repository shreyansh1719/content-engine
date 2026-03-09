"""
Professional Ad Generator with GPT-4o Integration
Creates integrated ad campaigns with direct OpenAI image handling
"""
import os
import json
import logging
import re
import traceback
from typing import Dict, Optional, List, Any, Union
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .image_maker import ModernStudioImageGenerator

# Dev mode: enabled automatically when OPENAI_API_KEY is absent
DEV_MODE = not bool(os.getenv('OPENAI_API_KEY', '').strip())

class AdGenerator:
    """Generate complete ad campaigns with GPT-4o-driven visuals and content."""
    
    def __init__(self, openai_api_key=None):
        """Initialize generator with API key and setup components."""
        # Setup API key
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        # Setup detailed logging
        self.setup_logging()
        
        # Initialize OpenAI client with proper error handling
        if OpenAI:
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                self.logger.info("OpenAI client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.openai_client = None
        else:
            self.logger.warning("OpenAI package not installed. Some features may not work.")
            self.openai_client = None
        
        # Initialize modernized image generator
        self.image_generator = ModernStudioImageGenerator(self.openai_api_key)
        
        # Setup output directories
        os.makedirs("output/images", exist_ok=True)
        os.makedirs("output/data", exist_ok=True)
        
        # Fine-tuned model ID (creative brief step)
        self.fine_tuned_model_id = os.getenv(
            'FINE_TUNED_MODEL_ID',
            'ft:gpt-3.5-turbo-0125:shreyansh::BLDyTfqs'
        )

        # Layout variety tracking — avoids repeating same layout in one session
        self._used_layouts: List[str] = []

        # Design approach tracking — avoids repeating same HTML/CSS layout in one session
        self._used_styles: List[str] = []

        # HTML typography renderer (lazy-initialized on first real-pipeline call)
        self._html_renderer = None

        # Cache for generated ads to improve performance
        self.ad_cache = {}
    
    def setup_logging(self):
        """Set up detailed logging configuration with rotation."""
        from logging.handlers import RotatingFileHandler
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_format)
        self.logger = logging.getLogger("AdGenerator")

        # Rotating file handler: max 5 MB, keep 3 backups
        try:
            os.makedirs("logs", exist_ok=True)
            file_handler = RotatingFileHandler(
                "logs/adcraft.log",
                maxBytes=5 * 1024 * 1024,
                backupCount=3,
            )
            file_handler.setFormatter(logging.Formatter(log_format))
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not set up log file: {e}")
    
    def analyze_brand(self, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze brand and determine appropriate strategy using GPT-4o.
        
        Args:
            brand_info: Dictionary with brand and product information
            
        Returns:
            Brand analysis dictionary
        """
        if not self.openai_client:
            self.logger.warning("OpenAI client not available. Using default brand analysis.")
            return self._generate_default_brand_analysis(brand_info)
        
        try:
            # Extract product and brand name from brand_info
            product = brand_info['product']
            brand_name = brand_info['brand']
            
            # Create comprehensive analysis prompt with expert guidance
            analysis_prompt = f"""Analyze this brand/product request and create a comprehensive strategic brief for {brand_name} {product}:
            
            Identify key elements including:
            - Industry vertical and specific category
            - Brand positioning level (luxury, premium, mid-range, mass-market)
            - Brand voice and tone characteristics
            - Primary target audience demographics and psychographics
            - Top 3-5 key competitive advantages or product benefits
            - Main direct competitors in this space
            - Most effective advertising approach for this product/category
            - Visual direction that aligns with brand positioning
            - Color strategy aligned with product psychology
            - Typography style recommendations with specific reasoning
            - The single most important product feature or aspect to highlight
            
            Respond in JSON format with:
            {{
                "industry": "specific industry category",
                "brand_level": "luxury/premium/mid-range/mass-market",
                "tone": "brand voice and style descriptors",
                "target_market": "detailed audience description",
                "key_benefits": ["benefit 1", "benefit 2", "benefit 3"],
                "competitors": ["competitor 1", "competitor 2"],
                "ad_style": "recommended advertising approach",
                "visual_direction": "detailed art direction guidelines",
                "color_scheme": "specific color strategy recommendations",
                "typography_style": "font style with rationale",
                "product_highlight": "specific feature or aspect to emphasize"
            }}

            Use professional marketing terminology and current industry best practices.
            """

            # Get response from OpenAI with increased temperature for creativity
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a senior brand strategist and market analyst with 15+ years of experience developing campaigns for premium brands. Your specialty is translating product requests into comprehensive marketing briefs."},
                    {"role": "user", "content": analysis_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )

            # Extract JSON directly
            result = json.loads(response.choices[0].message.content)
            
            # Validate and enhance response
            validated_result = self._validate_brand_analysis(result, product)
            
            # Log successful analysis
            self.logger.info(f"Brand analysis completed for industry: {validated_result['industry']}, level: {validated_result['brand_level']}")
            
            return validated_result
            
        except Exception as e:
            self.logger.error(f"Brand analysis error: {str(e)}")
            self.logger.error(traceback.format_exc())
            # Return default analysis
            return self._generate_default_brand_analysis(brand_info)
    
    def _validate_brand_analysis(self, result: Dict[str, Any], product: str) -> Dict[str, Any]:
        """Validate and enhance brand analysis results."""
        # Ensure all required fields exist with valid values
        required_fields = {
            'industry': "General", 
            'brand_level': "Premium", 
            'tone': "Professional and sophisticated", 
            'target_market': "Discerning consumers seeking quality",
            'ad_style': "Modern and professional", 
            'visual_direction': "Clean and sophisticated", 
            'color_scheme': "Brand-appropriate colors with complementary accents", 
            'typography_style': "Modern and professional", 
            'product_highlight': "Quality and craftsmanship"
        }
        
        # Check and fix each field
        for field, default_value in required_fields.items():
            if field not in result or not result[field]:
                result[field] = default_value
        
        # Ensure list fields are properly formatted
        list_fields = ['key_benefits', 'competitors']
        for field in list_fields:
            if field not in result or not isinstance(result[field], list):
                if field == 'key_benefits':
                    result[field] = ["Quality", "Innovation", "Performance", "Value"]
                else:
                    result[field] = []
            elif field in result and isinstance(result[field], list) and len(result[field]) == 0:
                if field == 'key_benefits':
                    result[field] = ["Quality", "Innovation", "Performance", "Value"]
        
        return result
    
    def _generate_default_brand_analysis(self, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate default brand analysis when API fails."""
        # Extract product and brand from brand_info
        product = brand_info['product']
        brand_name = brand_info['brand']
        
        # Extract potential industry from product
        industry = "General"
        brand_level = "Premium"
        
        industry_keywords = {
            "technology": ["phone", "tech", "digital", "smart", "computer", "laptop", "gadget", "electronic"],
            "fashion": ["clothing", "apparel", "fashion", "wear", "dress", "shoe", "accessory"],
            "beauty": ["beauty", "cosmetic", "makeup", "skin", "cream", "perfume", "fragrance"],
            "luxury": ["luxury", "premium", "exclusive", "high-end", "designer"],
            "food_beverage": ["food", "drink", "beverage", "restaurant", "coffee", "wine", "spirit"]
        }
        
        # Check for industry keywords in product
        product_lower = product.lower()
        for ind, keywords in industry_keywords.items():
            if any(keyword in product_lower for keyword in keywords):
                industry = ind
                break
        
        # Check for brand level indicators
        if any(term in product_lower for term in ["luxury", "premium", "high-end", "exclusive"]):
            brand_level = "Luxury"
        elif any(term in product_lower for term in ["quality", "premium", "professional"]):
            brand_level = "Premium"
        elif any(term in product_lower for term in ["affordable", "value", "budget"]):
            brand_level = "Mass-market"
        
        return {
            "industry": industry.capitalize(),
            "brand_level": brand_level,
            "tone": "Professional and sophisticated",
            "target_market": "Discerning consumers seeking quality",
            "key_benefits": ["Quality", "Innovation", "Performance", "Value"],
            "competitors": [],
            "ad_style": "Modern and professional",
            "visual_direction": "Clean and sophisticated",
            "color_scheme": "Brand-appropriate colors with complementary accents",
            "typography_style": "Modern and professional",
            "product_highlight": "Quality and craftsmanship"
        }
    
    def generate_ad_copy(self, product: str, brand_analysis: Dict[str, Any],
                         creative_brief: Dict[str, Any] = None,
                         tone: str = None, visual_style: str = None) -> Dict[str, Any]:
        """
        Generate full ad copy + layout JSON using GPT-4o.
        Optionally incorporates a creative brief from the fine-tuned model.
        """
        if not self.openai_client:
            self.logger.warning("OpenAI client not available. Using default ad copy.")
            return self._generate_default_ad_copy(product, brand_analysis)

        try:
            # Build creative brief context string
            brief_ctx = ""
            if creative_brief:
                brief_ctx = (
                    f"\nCREATIVE BRIEF (from brand specialist):\n"
                    f"  Draft headline: {creative_brief.get('headline', '')}\n"
                    f"  Tone signal: {creative_brief.get('tone', '')}\n"
                    f"  Visual style: {creative_brief.get('visual_style', '')}\n"
                    f"  Technique: {creative_brief.get('conceptual_technique', '')}\n"
                    f"  Emotion: {creative_brief.get('emotion', '')}\n"
                )

            tone_str   = tone         or brand_analysis.get('tone', 'professional')
            visual_str = visual_style or brand_analysis.get('visual_direction', 'modern')

            avoid_str = (
                f"\nDo NOT use these layout styles (already used this session): "
                f"{', '.join(self._used_layouts)}"
                if self._used_layouts else ""
            )

            copy_prompt = f"""Create premium advertising copy and visual layout for: {product}

MARKETING BRIEF:
Industry: {brand_analysis['industry']}
Brand Level: {brand_analysis['brand_level']}
Brand Voice: {tone_str}
Target Audience: {brand_analysis['target_market']}
Key Benefits: {', '.join(brand_analysis['key_benefits'])}
Product Highlight: {brand_analysis['product_highlight']}
Visual Direction: {visual_str}
{brief_ctx}
You MUST select a layout combination that fits this product's category. Use ALL options across different products — do not default to the same layout.

LAYOUT STYLES:
- "top_bottom": Headline top, CTA bottom. Best for: products centered in frame.
- "left_column": All text left-aligned in left 40%. Best for: lifestyle/fashion.
- "bottom_banner": Text in bottom 30% only. Best for: hero product shots.
- "centered": Text centered vertically. Best for: minimal/clean products.
- "bold_statement": Massive headline fills top 40%, no body text. Best for: brand statements.
- "split_horizontal": Text on right side panel. Best for: editorial/magazine feel.

OVERLAY TYPES:
- "gradient_top_bottom": Classic gradient top and bottom.
- "gradient_left": Dark fade from left. Pair with left_column.
- "vignette_bottom": Heavy bottom darkening. Pair with bottom_banner.
- "frosted_strip": Behind-text-only blur strip. Pair with split_horizontal.
- "shadow_only": No overlay — rely on text shadows. For clean/bright images.
- "solid_bar": Opaque colored bar. For bold/graphic style.

CTA STYLES:
- "pill_button": Rounded pill with fill. Classic.
- "square_button": Sharp borders, no fill. Premium/editorial.
- "text_underline": Text + underline + arrow. Most minimal/premium.
- "block_inverted": Wide colored bar. Bold/graphic.

CATEGORY RULES (follow these):
- luxury/premium → left_column or bold_statement + shadow_only or gradient_left + text_underline or square_button
- streetwear/urban → bold_statement or bottom_banner + solid_bar or vignette_bottom + block_inverted or pill_button
- food/beverage/plant-based → centered or bottom_banner + gradient_top_bottom or frosted_strip + pill_button
- tech/electronics → split_horizontal or top_bottom + frosted_strip or shadow_only + square_button or pill_button
- fashion/beauty → left_column + gradient_left + text_underline
- automotive → bold_statement + vignette_bottom + block_inverted
{avoid_str}
Respond with a JSON object with EXACTLY these keys:
{{
  "headline": "impactful headline, max 8 words",
  "subheadline": "supporting message, 10-15 words",
  "body_text": "2-3 sentences on key benefits and emotional connection",
  "call_to_action": "motivating CTA, 3-5 words",
  "image_description": "detailed product photography direction",
  "layout": {{
    "style": "top_bottom | left_column | bottom_banner | centered | bold_statement | split_horizontal",
    "text_color": "#FFFFFF",
    "accent_color": "#HEX",
    "overlay_type": "gradient_top_bottom | gradient_left | vignette_bottom | frosted_strip | shadow_only | solid_bar",
    "overlay_opacity": 0.65,
    "headline_position": "top_center | top_left | center | bottom_left",
    "headline_size": "large | xlarge | medium",
    "cta_style": "pill_button | square_button | text_underline | block_inverted",
    "cta_color": "#FFFFFF",
    "show_body_text": true,
    "mood": "dark_luxury | bright_clean | bold_contrast | soft_elegant | urban_gritty"
  }}
}}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"You are a world-class advertising copywriter AND art director "
                            f"specializing in {brand_analysis['industry']} for {brand_analysis['brand_level']} brands. "
                            f"You create compelling copy AND design the complete visual layout for every ad. "
                            f"Be creative and varied — never repeat the same layout for different products. "
                            f"Respond in JSON format."
                        )
                    },
                    {"role": "user", "content": copy_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.8
            )

            result    = json.loads(response.choices[0].message.content)
            validated = self._validate_ad_copy(result, product, brand_analysis)
            chosen    = validated.get('layout', {}).get('style', '')
            if chosen and chosen not in self._used_layouts:
                self._used_layouts.append(chosen)
            self.logger.info(f"Ad copy generation completed with headline: {validated['headline']}")
            return validated

        except Exception as e:
            self.logger.error(f"Ad copy generation error: {str(e)}")
            self.logger.error(traceback.format_exc())
            return self._generate_default_ad_copy(product, brand_analysis)
    
    def _validate_ad_copy(self, result: Dict[str, Any], product: str, brand_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ad copy — normalise alternate key names, fill defaults, validate layout."""
        # --- Normalise alternate JSON key names GPT-4o sometimes uses ---
        alt_keys = {
            'subheadline':     ['sub_headline', 'subheading', 'sub', 'subtitle'],
            'body_text':       ['body', 'copy', 'main_copy', 'description', 'text'],
            'call_to_action':  ['cta', 'cta_text', 'action', 'button_text'],
            'image_description': ['image', 'visual', 'photo_description', 'image_direction'],
        }
        for canonical, alts in alt_keys.items():
            if not result.get(canonical):
                for alt in alts:
                    if result.get(alt):
                        result[canonical] = result[alt]
                        break

        # --- Defaults ---
        defaults = {
            'headline':          f"Experience {product}",
            'subheadline':       f"Discover the quality and craftsmanship of {product}.",
            'body_text':         f"Crafted for those who demand excellence. {product} delivers unmatched performance and style.",
            'call_to_action':    "SHOP NOW",
            'image_description': f"Professional studio photography of {product} with dramatic lighting and perfect composition.",
        }
        for field, default in defaults.items():
            if not result.get(field):
                result[field] = default

        # CTA sanity check (no truncation of headline — trust GPT-4o)
        if len(result['call_to_action'].split()) > 6:
            result['call_to_action'] = "SHOP NOW"

        # --- Layout ---
        layout = result.get('layout')
        if isinstance(layout, dict):
            result['layout'] = self._validate_layout(layout)
        else:
            result['layout'] = self._validate_layout({})

        return result

    _VALID_STYLES        = {'left_column','bottom_banner','centered','top_bottom',
                            'split_horizontal','bold_statement','diagonal','floating_cards'}
    _VALID_OVERLAYS      = {'gradient_top_bottom','gradient_left','vignette_bottom',
                            'frosted_strip','shadow_only','solid_bar'}
    _VALID_HEADLINE_POS  = {'top_center','top_left','center','bottom_left'}
    _VALID_HEADLINE_SIZE = {'large','xlarge','medium'}
    _VALID_CTA_STYLES    = {'pill_button','square_button','text_underline','block_inverted'}

    def _validate_layout(self, layout: Dict[str, Any]) -> Dict[str, Any]:
        """Fill defaults and clamp values for the layout dict."""
        layout.setdefault('style',            'top_bottom')
        layout.setdefault('text_color',       '#FFFFFF')
        layout.setdefault('accent_color',     '#FFFFFF')
        layout.setdefault('overlay_type',     'gradient_top_bottom')
        layout.setdefault('overlay_opacity',  0.7)
        layout.setdefault('headline_position','top_center')
        layout.setdefault('headline_size',    'large')
        layout.setdefault('cta_style',        'pill_button')
        layout.setdefault('cta_color',        '#FFFFFF')
        layout.setdefault('show_body_text',   True)
        layout.setdefault('mood',             'bold_contrast')

        if layout['style']            not in self._VALID_STYLES:        layout['style']            = 'top_bottom'
        if layout['overlay_type']     not in self._VALID_OVERLAYS:     layout['overlay_type']     = 'gradient_top_bottom'
        if layout['headline_position']not in self._VALID_HEADLINE_POS: layout['headline_position']= 'top_center'
        if layout['headline_size']    not in self._VALID_HEADLINE_SIZE: layout['headline_size']    = 'large'
        if layout['cta_style']        not in self._VALID_CTA_STYLES:    layout['cta_style']        = 'pill_button'

        try:
            layout['overlay_opacity'] = max(0.2, min(1.0, float(layout['overlay_opacity'])))
        except (TypeError, ValueError):
            layout['overlay_opacity'] = 0.7

        return layout
    
    def _generate_default_ad_copy(self, prompt: str, brand_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate default ad copy when API fails."""
        # Check for spirit/beverage products
        product_lower = prompt.lower()
        is_spirit = any(term in product_lower for term in ["gin", "vodka", "whiskey", "rum", "brandy", "tequila", "spirit", "liquor"])
    
        # Check brand level for appropriate style
        brand_level = brand_analysis.get('brand_level', '').lower()
    
        if is_spirit and 'luxury' in brand_level:
            return {
                "headline": f"EXPERIENCE THE ESSENCE",
                "subheadline": f"Discover the exquisite craftsmanship and artistry behind {prompt}.",
                "body_text": f"Meticulously crafted with select botanicals and premium ingredients. {prompt} represents the perfect balance of tradition and innovation in every sip.",
                "call_to_action": "TASTE THE DIFFERENCE",
                "image_description": f"Dramatic studio lighting on {prompt} bottle showcasing the iconic shape and label details. Elegant glassware with perfect pour and fresh garnishes on a polished marble surface. Cool blue ambient lighting with subtle reflections and minimal bar setting backdrop."
            }
        elif 'luxury' in brand_level:
            return {
                "headline": f"EXPERIENCE {prompt.upper()}",
                "subheadline": f"Discover unparalleled craftsmanship and sophistication with our premium {prompt}.",
                "body_text": f"Meticulously crafted for those who demand nothing but excellence. The {prompt} represents the pinnacle of luxury and performance.",
                "call_to_action": "DISCOVER NOW",
                "image_description": f"Dramatic studio lighting on {prompt} against dark background with subtle luxury material elements. Perfect reflections and premium environment with negative space for typography."
            }
        elif 'premium' in brand_level:
            return {
                "headline": f"Elevate Your Experience",
                "subheadline": f"Discover why discerning customers choose our exceptional {prompt}.",
                "body_text": f"Our {prompt} combines innovative design with superior performance. Experience quality that exceeds expectations.",
                "call_to_action": "EXPLORE NOW",
                "image_description": f"Professional product photography of {prompt} with premium lighting and subtle reflections. Clean environment with sophisticated styling and perfect composition."
            }
        else:
            return {
                "headline": f"Introducing the {prompt}",
                "subheadline": f"Quality and innovation at a price you'll love.",
                "body_text": f"Our {prompt} delivers the features you need with the reliability you expect. Perfect for everyday use.",
                "call_to_action": "SHOP NOW",
                "image_description": f"Bright, clean product photography of {prompt} with clear details. Simple background with product as hero and space for typography."
            }
    
    # ── Two-model pipeline — Step 1 ───────────────────────────────────────────

    def generate_creative_brief(self, brand_info: Dict[str, Any],
                                 brand_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call the fine-tuned model to produce a creative brief:
        tone, visual_style, conceptual_technique, draft headline, emotion.
        Falls back to defaults if the model is unavailable.
        """
        if DEV_MODE or not self.openai_client:
            return self._default_creative_brief(brand_analysis)

        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert advertising creative director. Given a brand and product, "
                        "generate a complete ad creative brief including copy and visual direction. "
                        "Respond only in JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Create an ad for:\n"
                        f"Brand: {brand_info['brand']}\n"
                        f"Product type: {brand_info['product']}\n"
                        f"Tone: {brand_analysis.get('tone', 'professional')}\n"
                        f"Visual style: {brand_analysis.get('visual_direction', 'modern')}\n"
                        f"Conceptual technique: {brand_analysis.get('ad_style', 'product showcase')}\n"
                        f"Format: image"
                    ),
                },
            ]
            response = self.openai_client.chat.completions.create(
                model=self.fine_tuned_model_id,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.75,
            )
            brief = json.loads(response.choices[0].message.content)
            self.logger.info(
                f"Creative brief: tone={brief.get('tone')}, "
                f"visual_style={brief.get('visual_style')}, "
                f"technique={brief.get('conceptual_technique')}"
            )
            return brief

        except Exception as exc:
            self.logger.warning(f"Fine-tuned model failed ({exc}), using default brief")
            return self._default_creative_brief(brand_analysis)

    def _default_creative_brief(self, brand_analysis: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "headline":             "",
            "caption":              "",
            "tone":                 brand_analysis.get('tone', 'professional'),
            "visual_style":         brand_analysis.get('visual_direction', 'modern minimal'),
            "conceptual_technique": brand_analysis.get('ad_style', 'product showcase'),
            "call_to_action":       "SHOP NOW",
            "emotion":              "confidence",
        }

    def extract_brand_product(self, prompt: str) -> Dict[str, Any]:
        """
        Extract brand name and product from prompt using GPT-4o.
        
        Args:
            prompt: User's input prompt
            
        Returns:
            Dictionary with brand_name and product
        """
        if not self.openai_client:
            self.logger.warning("OpenAI client not available. Using simple brand/product extraction.")
            return self._simple_brand_product_extraction(prompt)
        
        try:
            # Create extraction prompt with comprehensive examples
            extraction_prompt = f"""Extract the exact product/service and brand name from this request: "{prompt}"
            
            If a brand isn't explicitly mentioned, make an educated guess based on context or categorize properly.
            
            Examples:
            - "iPhone 15 Pro" → product="iPhone 15 Pro", brand_name="APPLE"
            - "luxury sneakers" → product="luxury sneakers", brand_name="LUXURY"
            - "Nike running shoes" → product="running shoes", brand_name="NIKE"
            - "Blue silk tie" → product="blue silk tie", brand_name="FASHION"
            - "Perfume for men" → product="perfume for men", brand_name="FRAGRANCE"
            - "Galaxy S22 Ultra" → product="Galaxy S22 Ultra", brand_name="SAMSUNG"
            
            For established products, identify the correct brand. For generic products, use an appropriate category name as the brand.
            """

            # Get response from OpenAI with low temperature for consistency
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a precise entity extraction specialist focused on accurate identification of products and brands. Respond in JSON format."},
                    {"role": "user", "content": extraction_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            # Extract JSON directly
            result = json.loads(response.choices[0].message.content)
            
            # Validate and enhance extraction
            validated_result = self._validate_brand_product(result, prompt)
            
            self.logger.info(f"Extracted brand: {validated_result['brand_name']}, product: {validated_result['product']}")
            return validated_result
            
        except Exception as e:
            self.logger.error(f"Brand/product extraction error: {str(e)}")
            # Return simple extraction
            return self._simple_brand_product_extraction(prompt)
    
    def _validate_brand_product(self, result: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Validate and enhance brand/product extraction."""
        # Ensure required fields exist
        if 'product' not in result or not result['product']:
            result['product'] = prompt
        
        if 'brand_name' not in result or not result['brand_name']:
            # Extract first word as brand if not specified
            words = prompt.split()
            brand = words[0].upper() if words else "BRAND"
            result['brand_name'] = brand
        else:
            # Ensure brand_name is uppercase
            result['brand_name'] = result['brand_name'].upper()
        
        return result
    
    def extract_brand_info(self, prompt: str) -> Dict[str, Any]:
        """
        Extract brand information from prompt.
        
        Args:
            prompt: User's product/brand prompt
            
        Returns:
            Brand information dictionary
        """
        brand_product = self.extract_brand_product(prompt)
        return {
            'product': brand_product['product'],
            'brand': brand_product['brand_name']
        }

    def _simple_brand_product_extraction(self, prompt: str) -> Dict[str, Any]:
        """Extract brand and product using simple rules."""
        words = prompt.split()
        
        if not words:
            return {
                "product": prompt,
                "brand_name": "BRAND"
            }
        
        # Common brand names to recognize
        known_brands = {
            "iphone": "APPLE",
            "macbook": "APPLE",
            "ipad": "APPLE",
            "airpods": "APPLE",
            "galaxy": "SAMSUNG",
            "nike": "NIKE",
            "adidas": "ADIDAS",
            "rolex": "ROLEX",
            "gucci": "GUCCI",
            "bmw": "BMW",
            "mercedes": "MERCEDES",
            "coca": "COCA-COLA",
            "pepsi": "PEPSI"
        }
        
        # Check if any known brand is in the prompt
        prompt_lower = prompt.lower()
        for brand_keyword, brand_name in known_brands.items():
            if brand_keyword in prompt_lower:
                # Remove brand from product
                product = prompt
                return {
                    "product": product,
                    "brand_name": brand_name
                }
        
        # Default behavior - use first word as brand
        brand = words[0].upper()
        
        return {
            "product": prompt,
            "brand_name": brand
        }
    
    def _generate_mock_ad(self, prompt: str) -> Dict[str, Any]:
        """Return realistic mock ad data for dev/testing when no API key is set."""
        from PIL import Image, ImageDraw, ImageFont

        words = prompt.split()
        brand = words[0].upper() if words else "BRAND"
        product = " ".join(words[:4]) if len(words) >= 4 else prompt

        # Build gradient background
        width, height = 1024, 1024
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        for y in range(height):
            r = int(20 + (40 * y / height))
            g = int(30 + (60 * y / height))
            b = int(80 + (100 * y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Ad copy dict for typography system
        ad_copy = {
            'headline': f"Discover {brand}",
            'subheadline': f"Experience the quality and innovation of {product}.",
            'body_text': (
                f"Our {product} delivers unmatched performance and style. "
                f"Built for those who demand the best."
            ),
            'call_to_action': "SHOP NOW",
        }

        # Apply full typography overlay (same as live pipeline)
        try:
            from .typography import TypographySystem
            typo = TypographySystem()
            img = typo.apply_typography(img, ad_copy)
        except Exception as exc:
            self.logger.warning(
                "Typography overlay failed in mock mode: %s — falling back to plain text", exc
            )
            draw = ImageDraw.Draw(img)
            try:
                font_large = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 60)
                font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 36)
            except Exception:
                font_large = font_small = ImageFont.load_default()
            draw.text((width // 2, height // 2 - 80), f"[MOCK] {brand}",
                      fill=(255, 255, 255), font=font_large, anchor="mm")
            draw.text((width // 2, height // 2 + 20), product[:50],
                      fill=(180, 200, 255), font=font_small, anchor="mm")
            draw.text((width // 2, height // 2 + 80), "DEV MODE — No API Key",
                      fill=(120, 140, 180), font=font_small, anchor="mm")

        os.makedirs("output/images/final", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        mock_path = f"output/images/final/mock_{timestamp}.png"
        img.save(mock_path)

        return {
            'product': product,
            'brand_name': brand,
            **ad_copy,
            'industry': "General",
            'brand_level': "Premium",
            'tone': "Professional",
            'image_path': mock_path,
            'final_path': mock_path,
            'dev_mode': True,
            'generation_time': datetime.now().isoformat(),
        }

    # ── HTML/CSS pipeline methods ─────────────────────────────────────────────

    def _expand_brief_to_full_ad(self, creative_brief: Dict[str, Any],
                                  brand_info: Dict[str, Any],
                                  brand_analysis: Dict[str, Any],
                                  tone: str = None,
                                  visual_style: str = None) -> Dict[str, Any]:
        """GPT-4o creates ad copy + production-ready HTML/CSS overlay."""
        product = brand_info.get('product', '')
        brand = brand_info.get('brand', '')

        brief_tone = tone or creative_brief.get('tone', brand_analysis.get('tone', 'Premium'))
        brief_visual = visual_style or creative_brief.get('visual_style', brand_analysis.get('visual_direction', 'Modern'))
        technique = creative_brief.get('conceptual_technique', brand_analysis.get('ad_style', ''))
        emotion = creative_brief.get('emotion', 'aspiration')
        typography_style = brand_analysis.get('typography_style', '')
        color_scheme = brand_analysis.get('color_scheme', '')

        avoid = ""
        if self._used_styles:
            avoid = f"\nDo NOT reuse these approaches (already used this session): {', '.join(self._used_styles[-3:])}"

        prompt_text = f"""You are a world-class advertising art director who creates production-ready ad typography.

CREATIVE BRIEF:
- Brand: {brand}
- Product: {product}
- Tone: {brief_tone}
- Visual style: {brief_visual}
- Technique: {technique}
- Emotion to evoke: {emotion}
- Typography direction: {typography_style}
- Color direction: {color_scheme}
{avoid}

Create compelling ad copy AND a production-quality HTML/CSS overlay.

The overlay will be rendered at exactly 1024×1024 pixels and composited onto a product photograph. The HTML background MUST be fully transparent — only text and decorative elements should be visible.

Respond ONLY with JSON:
{{
  "headline": "powerful 3-8 word headline in title case or ALL CAPS depending on brand voice",
  "subheadline": "engaging 8-15 word subheadline",
  "body_text": "1-2 sentence body (can be empty string if cleaner without it)",
  "call_to_action": "2-4 word CTA",
  "design_approach": "brief 5-word description of the layout approach you chose",
  "overlay_html": "COMPLETE HTML DOCUMENT AS A STRING (see rules below)"
}}

RULES FOR overlay_html — YOU MUST FOLLOW ALL OF THESE:

1. STRUCTURE: Must be a complete document: <!DOCTYPE html><html><head><style>CSS HERE</style></head><body>CONTENT</body></html>

2. TRANSPARENT BACKGROUND:
   html, body {{ margin: 0; padding: 0; width: 1024px; height: 1024px; overflow: hidden; background: transparent; }}

3. FONTS: Import 1-2 Google Fonts that match the brand personality using a <style> @import inside <head>:
   Font choices by tone:
   - Luxury/Premium: Playfair Display, Cormorant Garamond, Cinzel
   - Bold/Urban/Street: Oswald, Anton, Bebas Neue
   - Clean/Tech/Minimal: Inter, Outfit, Space Grotesk, DM Sans
   - Playful/Friendly: Poppins, Quicksand, Nunito
   - Editorial/Fashion: Libre Baskerville, EB Garamond, Lora

4. TEXT SHADOWS: Every text element must have text-shadow for readability over photographs:
   text-shadow: 0 2px 8px rgba(0,0,0,0.7), 0 0 30px rgba(0,0,0,0.4);

5. LAYOUT: Use CSS flexbox or absolute positioning. Keep product zone (roughly center 30-70% height) clear of text. Group text in deliberate zones.

6. VARIETY: Mix these approaches — each brand gets a unique treatment:
   - Left-aligned editorial (text on left, product on right)
   - Bottom-heavy (all text in lower 35%)
   - Top headline with bottom CTA (classic)
   - Centered dramatic (large centered headline)
   - Magazine-style (horizontal band)
   - Bold statement (oversized headline, minimal other text)

7. SCRIM/OVERLAY: Add a subtle gradient or semi-transparent area ONLY behind text zones:
   - Linear gradient: background: linear-gradient(to bottom, rgba(0,0,0,0.6) 0%, transparent 30%);
   - Backdrop blur: backdrop-filter: blur(8px); background: rgba(0,0,0,0.3);
   - Or just strong text-shadow with no overlay for clean images

8. CTA BUTTON STYLES — match brand personality:
   - Pill: border-radius: 50px; padding: 14px 40px; background: accent-color;
   - Square/ghost: border: 2px solid white; padding: 12px 36px; background: transparent;
   - Underline CTA: text-decoration: underline; text-underline-offset: 6px; (with → arrow)
   - Block bar: width: 70%; padding: 16px; background: accent-color; text-align: center;

9. COLORS: Do NOT default to white text every time. Choose colors matching brand personality (luxury = gold/cream, tech = blue/white, food = warm/green). Use accent color for CTA.

10. SIZE HIERARCHY:
    - Headline: 52-80px (shorter headline = bigger font; if >5 words use ≤60px to avoid wrapping)
    - Subheadline: 20-28px
    - Body: 16-18px (omit if cleaner)
    - CTA: 18-24px bold
    - Add letter-spacing: 0.05em to 0.15em for uppercase headlines

11. DO NOT include any <img> tags, JavaScript, or external resources besides Google Fonts.

12. The HTML must look like a real ad when overlaid on a product photo — professional agency quality."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior advertising art director who writes flawless, production-ready HTML/CSS. "
                        "Your typography overlays look like they came from a top creative agency. "
                        "You never repeat the same layout — every brand gets a unique visual treatment. "
                        "Respond ONLY with valid JSON."
                    )
                },
                {"role": "user", "content": prompt_text}
            ],
            response_format={"type": "json_object"},
            temperature=0.95
        )

        ad_data = json.loads(response.choices[0].message.content)

        # Normalise alternate key names
        if "body" in ad_data and "body_text" not in ad_data:
            ad_data["body_text"] = ad_data.pop("body")
        if "cta" in ad_data and "call_to_action" not in ad_data:
            ad_data["call_to_action"] = ad_data.pop("cta")

        overlay_html = ad_data.get("overlay_html", "")
        if not overlay_html or "<html" not in overlay_html.lower():
            raise ValueError(
                f"GPT-4o did not return valid overlay_html. Got: {overlay_html[:200]}"
            )

        approach = ad_data.get("design_approach", "")
        if approach:
            self._used_styles.append(approach)

        # Carry creative brief metadata forward
        ad_data["tone"] = brief_tone
        ad_data["visual_style"] = brief_visual
        ad_data["conceptual_technique"] = technique
        ad_data["emotion"] = emotion

        return ad_data

    def _generate_dalle_image(self, ad_data: Dict[str, Any],
                               creative_brief: Dict[str, Any],
                               brand_info: Dict[str, Any]) -> Image.Image:
        """Generate a text-free DALL-E 3 product image guided by creative brief."""
        import requests as _req
        from io import BytesIO
        from PIL import Image as PILImage

        product = brand_info.get('product', '')
        brand = brand_info.get('brand', '')
        visual_style = creative_brief.get('visual_style', 'professional photography')
        technique = creative_brief.get('conceptual_technique', '')
        color_scheme = ad_data.get('color_scheme', creative_brief.get('color_scheme', ''))

        dalle_prompt = f"""Create a premium advertisement photograph for {brand} {product}.

VISUAL DIRECTION:
{visual_style}

COLOR DIRECTION:
{color_scheme}

CONCEPTUAL APPROACH:
{technique}

TECHNICAL REQUIREMENTS:
- Professional studio-quality lighting
- Shot on medium format camera with shallow depth of field
- Product is the clear hero — prominently featured and recognizable
- Clean composition with intentional negative space for text overlay
- Leave the top 20% and bottom 25% slightly less busy (text will be added there)
- Color grading should match the brand personality
- Premium post-production quality

CRITICAL — DO NOT INCLUDE ANY TEXT:
- No text, words, letters, numbers, or typography of any kind
- No brand names, logos, or watermarks
- No signs, labels, or printed text visible in the scene
- The image must be completely free of any written content

Style: {visual_style}. Make it look like a real campaign photo from {brand}'s actual advertising."""

        response = self.openai_client.images.generate(
            model="dall-e-3",
            prompt=dalle_prompt,
            size="1024x1024",
            quality="hd",
            n=1
        )

        image_url = response.data[0].url
        img_data = _req.get(image_url, timeout=30)
        img = PILImage.open(BytesIO(img_data.content)).convert("RGB")
        self.logger.info(f"DALL-E 3 image generated: {img.size}")
        return img

    def create_ad(self, prompt: str, product_image_path: str = None,
                  tone: str = None, visual_style: str = None) -> Dict[str, Any]:
        """
        HTML/CSS pipeline:
          1. Fine-tuned model → creative brief (tone, visual_style, technique, draft headline)
          2. GPT-4o          → ad copy + complete HTML/CSS overlay document
          3. DALL-E 3        → text-free product image (improved prompts)
          4. Playwright      → renders HTML/CSS overlay to transparent 1024x1024 PNG
          5. Pillow          → composites overlay onto DALL-E image
        """
        self.logger.info(f"Starting ad generation for: {prompt}")

        if DEV_MODE or not self.openai_client:
            self.logger.warning("DEV MODE active — returning mock ad (no OPENAI_API_KEY set)")
            return self._generate_mock_ad(prompt)

        # --- Step 0: extract brand/product ---
        brand_info     = self.extract_brand_info(prompt)
        brand_analysis = self.analyze_brand(brand_info)

        # --- Step 1: creative brief from fine-tuned model ---
        creative_brief = self.generate_creative_brief(brand_info, brand_analysis)

        # --- Step 2: ad copy + HTML/CSS overlay from GPT-4o ---
        ad_data = self._expand_brief_to_full_ad(
            creative_brief, brand_info, brand_analysis,
            tone=tone, visual_style=visual_style
        )
        overlay_html = ad_data.pop("overlay_html")

        # --- Step 3: DALL-E 3 text-free product image ---
        if product_image_path:
            if not os.path.exists(product_image_path):
                raise FileNotFoundError(f"Product image not found: {product_image_path}")
            from PIL import Image as PILImage
            base_image = PILImage.open(product_image_path).convert("RGB")
            base_image = base_image.resize((1024, 1024), PILImage.LANCZOS)
        else:
            self.logger.info("Generating DALL-E 3 product image (text-free, HD)")
            base_image = self._generate_dalle_image(ad_data, creative_brief, brand_info)

        # --- Step 4: render HTML/CSS overlay with Playwright ---
        if self._html_renderer is None:
            from .typography.html_renderer import HTMLTypographyRenderer
            self._html_renderer = HTMLTypographyRenderer()

        self.logger.info("Rendering HTML/CSS typography overlay via Playwright")
        overlay_image = self._html_renderer.render_overlay(overlay_html, width=1024, height=1024)

        # --- Step 5: composite overlay onto base image ---
        final_image = self._html_renderer.composite_overlay(base_image, overlay_image)

        # --- Save final image ---
        os.makedirs("output/images/final", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_path = f"output/images/final/final_ad_{timestamp}.png"
        final_image.save(final_path, "PNG")
        self.logger.info(
            f"Final ad saved: {final_path}  design={ad_data.get('design_approach')}"
        )

        # --- Merge result ---
        result = {
            **ad_data,
            **brand_analysis,
            'product':              brand_info['product'],
            'brand_name':           brand_info['brand'],
            'final_path':           final_path,
            'image_path':           final_path,
            'tone':                 ad_data.get('tone') or brand_analysis.get('tone', ''),
            'visual_style':         ad_data.get('visual_style') or brand_analysis.get('visual_direction', ''),
            'conceptual_technique': ad_data.get('conceptual_technique', ''),
            'emotion':              ad_data.get('emotion', ''),
            'generation_time':      datetime.now().isoformat(),
        }

        self.logger.info("Ad generation completed successfully")
        self._save_ad_metadata(result, final_path)
        return result
    
    def _save_ad_metadata(self, result: Dict[str, Any], image_path: str) -> None:
        """Save a JSON sidecar file next to the generated image."""
        if not image_path:
            return
        try:
            meta_path = image_path.replace('.png', '_metadata.json').replace('.jpg', '_metadata.json')
            safe = {k: v for k, v in result.items() if k != 'image'}
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(safe, f, indent=2, default=str)
            self.logger.info(f"Metadata saved to {meta_path}")
        except Exception as exc:
            self.logger.warning(f"Metadata save failed: {exc}")

    def _create_fallback_ad(self, prompt: str) -> Dict[str, Any]:
        """Create a fallback ad when the regular process fails."""
        try:
            # Extract basic info
            words = prompt.split()
            brand = words[0].upper() if words else "BRAND"
            
            # Create placeholder image
            placeholder_path = self.image_generator._create_fallback_image(prompt, brand)
            
            return {
                'product': prompt,
                'brand_name': brand,
                'headline': f"EXPERIENCE {prompt.upper()}",
                'subheadline': f"Discover the quality and innovation of our premium {prompt}.",
                'body_text': f"Our {prompt} offers unmatched performance and style. Experience the difference today.",
                'call_to_action': "SHOP NOW",
                'image_path': placeholder_path,
                'final_path': placeholder_path,
                'brand_analysis': {
                    "industry": "General",
                    "brand_level": "Premium",
                    "tone": "Professional",
                    "target_market": "General consumers",
                    "key_benefits": ["Quality", "Value", "Innovation"],
                    "competitors": [],
                    "ad_style": "Modern",
                    "visual_direction": "Clean and professional",
                    "color_scheme": "Blue and white",
                    "typography_style": "Modern sans-serif",
                    "product_highlight": "Overall quality"
                },
                'generation_time': datetime.now().isoformat(),
                'error': "Failed to generate ad properly, using fallback."
            }
        except Exception as e:
            self.logger.error(f"Fallback ad creation error: {str(e)}")
            return {
                'product': prompt,
                'headline': "DEFAULT HEADLINE",
                'subheadline': "Default subheadline",
                'body_text': "Default body text",
                'call_to_action': "SHOP NOW",
                'image_path': "",
                'generation_time': datetime.now().isoformat(),
                'error': "Complete generation failure."
            }