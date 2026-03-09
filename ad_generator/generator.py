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
Respond with a JSON object with EXACTLY these keys:
{{
  "headline": "impactful headline, max 8 words",
  "subheadline": "supporting message, 10-15 words",
  "body_text": "2-3 sentences on key benefits and emotional connection",
  "call_to_action": "motivating CTA, 3-5 words",
  "image_description": "detailed product photography direction",
  "layout": {{
    "style": "left_column | bottom_banner | centered | top_bottom | split_horizontal | bold_statement | diagonal | floating_cards",
    "text_color": "#FFFFFF",
    "accent_color": "#HEX",
    "overlay_type": "gradient_top_bottom | gradient_left | vignette_bottom | frosted_strip | shadow_only | solid_bar",
    "overlay_opacity": 0.7,
    "headline_position": "top_center | top_left | center | bottom_left",
    "headline_size": "large | xlarge | medium",
    "cta_style": "pill_button | square_button | text_underline | block_inverted",
    "cta_color": "#FFFFFF",
    "show_body_text": true,
    "mood": "dark_luxury | bright_clean | bold_contrast | soft_elegant | urban_gritty"
  }}
}}
Choose the layout style, colors, and overlay that best fit the brand personality and industry.
A luxury watch should look completely different from a streetwear sneaker ad."""

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

            result = json.loads(response.choices[0].message.content)
            validated = self._validate_ad_copy(result, product, brand_analysis)
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

    def create_ad(self, prompt: str, product_image_path: str = None,
                  tone: str = None, visual_style: str = None) -> Dict[str, Any]:
        """
        Two-model pipeline:
          1. Fine-tuned model → creative brief (tone, visual_style, technique, draft headline)
          2. GPT-4o          → full copy + layout JSON
          3. DALL-E 3        → layout-aware product image
          4. TypographySystem→ dynamic text overlay
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

        # --- Step 2: full copy + layout from GPT-4o ---
        ad_copy = self.generate_ad_copy(
            brand_info['product'],
            brand_analysis,
            creative_brief=creative_brief,
            tone=tone,
            visual_style=visual_style,
        )

        layout = ad_copy.get('layout', {})

        # --- Step 3: DALL-E image (layout-aware, text-free) ---
        if product_image_path:
            if not os.path.exists(product_image_path):
                raise FileNotFoundError(f"Product image not found: {product_image_path}")
            image_result = self.image_generator.create_ad_with_user_product(
                product_image_path=product_image_path,
                product=brand_info['product'],
                brand_name=brand_info['brand'],
                headline=ad_copy['headline'],
                subheadline=ad_copy.get('subheadline'),
                call_to_action=ad_copy.get('call_to_action'),
                industry=brand_analysis.get('industry'),
                brand_level=brand_analysis.get('brand_level'),
            )
        else:
            self.logger.info("Generating ad image from scratch (layout-aware)")
            image_result = self.image_generator.create_studio_ad(
                product=brand_info['product'],
                brand_name=brand_info['brand'],
                headline=ad_copy['headline'],
                subheadline=ad_copy.get('subheadline'),
                call_to_action=ad_copy.get('call_to_action'),
                industry=brand_analysis.get('industry'),
                brand_level=brand_analysis.get('brand_level'),
                image_description=ad_copy.get('image_description'),
                layout_hint=layout,
            )

        # --- Step 4: dynamic typography overlay ---
        final_path = image_result.get('final_path')
        if final_path and os.path.exists(final_path):
            try:
                from PIL import Image as PILImage
                from .typography import TypographySystem
                typo          = TypographySystem()
                img           = PILImage.open(final_path)
                img_with_text = typo.apply_typography(img, ad_copy, layout=layout)
                img_with_text.save(final_path)
                self.logger.info(
                    f"Typography overlay applied — style={layout.get('style')}, "
                    f"overlay={layout.get('overlay_type')}, cta={layout.get('cta_style')}"
                )
            except Exception as exc:
                self.logger.warning(f"Typography overlay failed (raw DALL-E image kept): {exc}")

        # --- Merge result ---
        result = {
            **ad_copy,
            **brand_analysis,
            **image_result,
            'product':         brand_info['product'],
            'brand_name':      brand_info['brand'],
            'layout':          layout,
            'tone':            creative_brief.get('tone') or brand_analysis.get('tone', ''),
            'visual_style':    creative_brief.get('visual_style') or brand_analysis.get('visual_direction', ''),
            'conceptual_technique': creative_brief.get('conceptual_technique', ''),
            'emotion':         creative_brief.get('emotion', ''),
            'generation_time': datetime.now().isoformat(),
        }

        self.logger.info("Ad generation completed successfully")
        return result
    
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