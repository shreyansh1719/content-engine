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
    
    def generate_ad_copy(self, prompt: str, brand_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate professional ad copy based on brand analysis using GPT-4o.
        """
        if not self.openai_client:
            self.logger.warning("OpenAI client not available. Using default ad copy.")
            return self._generate_default_ad_copy(prompt, brand_analysis)
    
        try:
            # Create comprehensive copy prompt with expert guidance
            copy_prompt = f"""Create premium advertising copy for: {prompt}

            MARKETING BRIEF:
            Industry: {brand_analysis['industry']}
            Brand Level: {brand_analysis['brand_level']}
            Brand Voice: {brand_analysis['tone']}
            Target Audience: {brand_analysis['target_market']}
            Key Benefits: {', '.join(brand_analysis['key_benefits'])}
            Product Highlight: {brand_analysis['product_highlight']}
            Visual Direction: {brand_analysis['visual_direction']}
        
            Create the following elements with perfect integration and brand alignment:
            1. Headline: An impactful, memorable headline (max 6-8 words) that immediately captures attention
            2. Subheadline: Supporting message (10-15 words) that expands on the headline promise
            3. Body Text: Concise main copy (2-3 sentences) focusing on key benefits and emotional connection
            4. Call to Action: Clear, motivating CTA (3-5 words) that drives specific action
            5. Image Description: Detailed creative direction for the product photography
        
            Your copy should reflect specific product characteristics and unique selling points.
            For spirits or luxury products, emphasize craftsmanship, premium ingredients, and sensory experience.
            """

            # Get response from OpenAI with high creativity
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"You are a world-class copywriter specializing in {brand_analysis['industry']} advertising for {brand_analysis['brand_level']} brands. Your copy consistently outperforms industry benchmarks by 35% and has won multiple industry awards."},
                    {"role": "user", "content": copy_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.8
            )

            # Extract JSON directly
            result = json.loads(response.choices[0].message.content)
        
            # Validate and enhance ad copy
            validated_result = self._validate_ad_copy(result, prompt, brand_analysis)
        
            self.logger.info(f"Ad copy generation completed with headline: {validated_result['headline']}")
            return validated_result
        
        except Exception as e:
            self.logger.error(f"Ad copy generation error: {str(e)}")
            self.logger.error(traceback.format_exc())
            # Return default ad copy
            return self._generate_default_ad_copy(prompt, brand_analysis)
    
    def _validate_ad_copy(self, result: Dict[str, Any], prompt: str, brand_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance ad copy results."""
        # Ensure all required fields exist
        required_fields = {
            'headline': f"EXPERIENCE {prompt.upper()}",
            'subheadline': f"Discover the quality and innovation of our premium {prompt}.",
            'body_text': f"Our {prompt} offers unmatched performance and style. Experience the difference today.",
            'call_to_action': "SHOP NOW",
            'image_description': f"Professional product photography of {prompt} with perfect lighting and composition."
        }
        
        # Check and fix each field
        for field, default_value in required_fields.items():
            if field not in result or not result[field]:
                result[field] = default_value
        
        # Enhance headline if needed
        if len(result['headline'].split()) > 8:
            # Truncate to 8 words
            words = result['headline'].split()[:8]
            result['headline'] = ' '.join(words)
        
        # Ensure headline is impactful - capitalize if brand level is luxury or premium
        if brand_analysis['brand_level'].lower() in ['luxury', 'premium'] and not result['headline'].isupper():
            # Check if headline is in title case
            if not all(word[0].isupper() for word in result['headline'].split() if word):
                result['headline'] = result['headline'].title()
        
        # Ensure call-to-action is clear and action-oriented
        common_ctas = ["SHOP NOW", "LEARN MORE", "DISCOVER", "EXPERIENCE", "GET STARTED"]
        if len(result['call_to_action'].split()) > 5 or len(result['call_to_action']) < 3:
            result['call_to_action'] = common_ctas[0]
        
        # Enhance image description if too short
        if len(result['image_description'].split()) < 10:
            result['image_description'] += f" Professional studio lighting with dramatic shadows highlighting the product's key features. {brand_analysis['visual_direction']}"
        
        return result
    
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
                    {"role": "system", "content": "You are a precise entity extraction specialist focused on accurate identification of products and brands."},
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

    def create_ad(self, prompt: str, product_image_path: str = None) -> Dict[str, Any]:
        """
        Create a complete ad with image and copy using GPT-4o and DALL-E.

        Args:
            prompt: Description of the product to advertise
            product_image_path: Optional path to product image

        Returns:
            Dictionary with ad details
        """
        self.logger.info(f"Starting ad generation for: {prompt}")

        # Dev mode: return mock data immediately when no API key is present
        if DEV_MODE or not self.openai_client:
            self.logger.warning("DEV MODE active — returning mock ad (no OPENAI_API_KEY set)")
            return self._generate_mock_ad(prompt)

        # Extract brand and product information
        brand_info = self.extract_brand_info(prompt)
    
        # Analyze brand for industry-specific insights
        brand_analysis = self.analyze_brand(brand_info)
    
        # Generate ad copy based on brand analysis
        ad_copy = self.generate_ad_copy(prompt, brand_analysis)
    
        # Process user-provided product image if available
        if product_image_path:
            self.logger.info(f"Processing user product image: {product_image_path}")
        
            # Validate path before processing
            if not os.path.exists(product_image_path):
                self.logger.error(f"Product image not found: {product_image_path}")
                raise FileNotFoundError(f"Product image not found: {product_image_path}")
            
            # Generate ad with user product image
            image_result = self.image_generator.create_ad_with_user_product(
                product_image_path=product_image_path,
                product=brand_info['product'],
                brand_name=brand_info['brand'],
                headline=ad_copy['headline'],
                subheadline=ad_copy.get('subheadline'),
                call_to_action=ad_copy.get('call_to_action'),
                industry=brand_analysis.get('industry'),
                brand_level=brand_analysis.get('brand_level')
            )
        else:
            # Generate complete ad image from scratch
            self.logger.info("Generating ad image from scratch")
        
            # Use the image generator to create the ad
            image_result = self.image_generator.create_studio_ad(
                product=brand_info['product'],
                brand_name=brand_info['brand'],
                headline=ad_copy['headline'],
                subheadline=ad_copy.get('subheadline'),
                call_to_action=ad_copy.get('call_to_action'),
                industry=brand_analysis.get('industry'),
                brand_level=brand_analysis.get('brand_level'),
                image_description=ad_copy.get('image_description')
            )
        
        # Merge all information into result
        result = {
            **ad_copy,
            **brand_analysis,
            **image_result,
            'product': brand_info['product'],
            'brand_name': brand_info['brand'],
            'generation_time': datetime.now().isoformat()
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