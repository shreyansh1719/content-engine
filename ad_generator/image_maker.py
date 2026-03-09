"""
Simplified Studio-quality image generator utilizing GPT-4o and DALL-E
Creates high-end ad images with direct image input handling
"""
import os
import logging
import json
import base64
import traceback
from typing import Dict, Optional, Union, Tuple, List, Any
from datetime import datetime
from io import BytesIO
import requests
from PIL import Image

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class ModernStudioImageGenerator:
    """Generate studio-quality ad images with GPT-4o-driven typography and composition."""
    
    def __init__(self, openai_api_key=None):
        """Initialize generator with API key and setup components."""
        # Setup API key
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        # Setup detailed logging
        self.setup_logging()
        
        # Initialize OpenAI client
        try:
            from openai import OpenAI
            if self.openai_api_key:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                self.logger.info("OpenAI client initialized successfully")
            else:
                self.logger.warning("No OPENAI_API_KEY set — image generation will use fallback/mock mode")
                self.openai_client = None
        except ImportError:
            self.logger.error("OpenAI package not installed. Please install with: pip install openai")
            self.openai_client = None
        except Exception as e:
            self.logger.warning(f"OpenAI client init failed: {e} — using fallback/mock mode")
            self.openai_client = None
        
        # Setup output directories
        os.makedirs("output/images/base", exist_ok=True)
        os.makedirs("output/images/final", exist_ok=True)
        
        # Cache for generated images to improve performance
        self.image_cache = {}
    
    def setup_logging(self):
        """Set up detailed logging configuration with rotation."""
        from logging.handlers import RotatingFileHandler
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_format)
        self.logger = logging.getLogger("ModernStudioImageGenerator")

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
    
    def generate_product_image(self, product: str, brand_name: str = None, industry: str = None, 
                            image_description: str = None, brand_level: str = "premium") -> str:
        """
        Generate studio-quality product image using GPT-4o for creative direction and DALL-E for execution.
        
        Args:
            product: Product name/description
            brand_name: Brand name (optional)
            industry: Industry category (optional)
            image_description: Specific image description (optional)
            brand_level: Brand positioning level (optional)
            
        Returns:
            Path to generated image
        """
        if not self.openai_client:
            self.logger.error("OpenAI client not available. Cannot generate image.")
            return self._create_fallback_image(product, brand_name)
        
        try:
            # Generate cache key
            cache_key = f"{product}_{brand_name}_{industry}_{brand_level}"
            
            # Check cache first
            if cache_key in self.image_cache:
                self.logger.info(f"Using cached image for {cache_key}")
                return self.image_cache[cache_key]
            
            # 1. Use GPT-4o to generate creative direction for the image
            self.logger.info(f"Generating creative direction for {product}")
            creative_direction = self._generate_creative_direction(
                product, brand_name, industry, image_description, brand_level
            )
            
            # 2. Use DALL-E to generate the image based on the creative direction
            self.logger.info(f"Generating image for {product} with DALL-E")
            image_prompt = creative_direction.get("image_prompt", f"Professional advertisement photograph of {product}")
            
            # Request image from DALL-E
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
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
            
            # Cache the result
            self.image_cache[cache_key] = raw_filepath
            
            return raw_filepath
            
        except Exception as e:
            self.logger.error(f"Error generating product image: {str(e)}")
            self.logger.error(traceback.format_exc())
            return self._create_fallback_image(product, brand_name)
    
    def _generate_creative_direction(self, product: str, brand_name: str = None, 
                                  industry: str = None, image_description: str = None,
                                  brand_level: str = "premium") -> Dict[str, Any]:
        """
        Use GPT-4o to generate creative direction for the advertisement.
        
        Args:
            product: Product name/description
            brand_name: Brand name
            industry: Industry category
            image_description: Specific image description
            brand_level: Brand positioning level
            
        Returns:
            Dictionary with creative direction details
        """
        try:
            # Create prompt for GPT-4o
            product_info = f"{brand_name} {product}" if brand_name else product
            industry_info = f" in the {industry} industry" if industry else ""
            brand_level_info = f" at a {brand_level} level" if brand_level else ""
            
            prompt = f"""Generate creative direction for a professional advertisement for {product_info}{industry_info}{brand_level_info}.

The creative direction should include:
1. A detailed image prompt for DALL-E 3 to generate a studio-quality product image
2. Typography recommendations for headline, subheadline, and call-to-action
3. Color scheme recommendations
4. Layout recommendations
5. Any special visual elements or effects

{f"Additional description: {image_description}" if image_description else ""}

Please format your response as a JSON object with the following keys:
- image_prompt: A detailed prompt for DALL-E 3 (should be comprehensive and specific)
- typography: Object with font recommendations and styling for each text element
- color_scheme: Recommended colors for the ad
- layout: Recommended layout for the ad elements
- special_elements: Any special visual elements to include
"""
            
            # Get creative direction from GPT-4o
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a world-class art director and advertising creative with 20+ years of experience creating award-winning campaigns for premium brands. You excel at developing detailed creative direction for commercial photography and advertisement design."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            # Parse and return the creative direction
            creative_direction = json.loads(response.choices[0].message.content)
            return creative_direction
            
        except Exception as e:
            self.logger.error(f"Error generating creative direction: {str(e)}")
            
            # Create default creative direction
            return {
                "image_prompt": self._create_default_image_prompt(product, brand_name, industry, brand_level),
                "typography": {
                    "headline": {"font": "Arial Bold", "style": "clean, modern"},
                    "subheadline": {"font": "Arial", "style": "simple, elegant"},
                    "cta": {"font": "Arial Bold", "style": "attention-grabbing"}
                },
                "color_scheme": {"primary": "#000000", "secondary": "#FFFFFF", "accent": "#0066CC"},
                "layout": "centered product with text at top and bottom",
                "special_elements": "subtle shadow beneath product"
            }
    
    def _create_default_image_prompt(self, product: str, brand_name: str = None,
                                  industry: str = None, brand_level: str = "premium") -> str:
        """Create a default image prompt when GPT-4o fails."""
        product_info = f"{brand_name} {product}" if brand_name else product
        
        return f"""Professional advertisement photograph of {product_info} with studio lighting against a clean background. 
        The product should be the main focus, centered with perfect lighting that highlights its key features. 
        Use {brand_level} styling and commercial-quality photography techniques with professional color grading. 
        The composition should allow space for headline at the top and supporting text at the bottom."""
    
    def _generate_ad_content(self, product: str, brand_name: str = None,
                          industry: str = None, brand_level: str = "premium") -> Dict[str, Any]:
        """
        Use GPT-4o to generate complete ad content including headline, subheadline, call-to-action, and image description.
        
        Args:
            product: Product name/description
            brand_name: Brand name
            industry: Industry category
            brand_level: Brand positioning level
            
        Returns:
            Dictionary with ad content details
        """
        try:
            if not self.openai_client:
                raise Exception("OpenAI client not available")
            
            # Create prompt for GPT-4o
            product_info = f"{brand_name} {product}" if brand_name else product
            industry_info = f" in the {industry} industry" if industry else ""
            brand_level_info = f" at a {brand_level} level" if brand_level else ""
            
            prompt = f"""Generate complete advertisement content for {product_info}{industry_info}{brand_level_info}.

Please provide:
1. A compelling headline (5-8 words)
2. A supporting subheadline (10-15 words)
3. A call-to-action (3-5 words)
4. A detailed image description for generating the advertisement visual

Format your response as a JSON object with the following keys:
- headline: The main headline
- subheadline: The supporting subheadline
- call_to_action: The call-to-action
- image_description: Detailed description for the advertisement visual
"""
            
            # Get ad content from GPT-4o
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a world-class advertising copywriter with expertise in creating compelling advertisement content for premium brands."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            # Parse and return the ad content
            ad_content = json.loads(response.choices[0].message.content)
            return ad_content
            
        except Exception as e:
            self.logger.error(f"Error generating ad content: {str(e)}")
            
            # Create default ad content
            return {
                "headline": f"Experience {product}",
                "subheadline": f"Discover the quality and innovation of our premium {product}.",
                "call_to_action": "Shop Now",
                "image_description": f"Professional product photography of {product} with perfect lighting and composition."
            }
    
    def create_ad_with_user_product(self, product_image_path: str, product: str, 
                                 brand_name: str = None, headline: str = None,
                                 subheadline: str = None, call_to_action: str = None, 
                                 industry: str = None, brand_level: str = "premium") -> Dict[str, str]:
        """
        Create a complete ad using a user-provided product image by sending directly to DALL-E.
        
        Args:
            product_image_path: Path to user product image
            product: Product name/description
            brand_name: Brand name
            headline: Ad headline
            subheadline: Ad subheadline
            call_to_action: Call to action text
            industry: Industry category
            brand_level: Brand positioning level
            
        Returns:
            Dictionary with paths to generated images
        """
        if not self.openai_client:
            self.logger.error("OpenAI client not available. Cannot process user image.")
            return self._create_fallback_ad(product, brand_name)
        
        try:
            self.logger.info(f"Creating ad with user product image: {product_image_path}")
            
            # Generate ad content if not provided
            if not headline:
                ad_content = self._generate_ad_content(product, brand_name, industry, brand_level)
                headline = ad_content.get("headline", f"Experience {product}")
                subheadline = ad_content.get("subheadline")
                call_to_action = ad_content.get("call_to_action", "Shop Now")
            
            # Read and encode the image file
            with open(product_image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Get creative direction for the ad style
            creative_direction = self._generate_creative_direction(
                product, brand_name, industry, None, brand_level
            )
            
            # Build a comprehensive prompt for DALL-E
            prompt = f"""Create a professional advertisement using this product image.

PRODUCT INFORMATION:
- Product: {product}
- Brand: {brand_name or ""}
- Industry: {industry or "General"}
- Brand Level: {brand_level or "Premium"}

TEXT ELEMENTS:
- Headline: {headline}
- Subheadline: {subheadline or ""}
- Call to Action: {call_to_action or ""}

CREATIVE DIRECTION:
{creative_direction.get('image_prompt', 'Create a professional advertisement with studio lighting and perfect composition.')}

INSTRUCTIONS:
1. Use the provided product image as the main element
2. Remove the background if needed and place the product on an appropriate, professional background
3. Maintain the product's original appearance and details
4. Integrate the text elements using professional typography that matches the brand level
5. Ensure the composition is balanced with perfect lighting and professional advertisement quality
6. Add any necessary shadows, reflections, or studio effects to enhance the product
7. Create the final ad with a layout appropriate for {industry or "this type of product"}

The final image should look like a professional advertisement created by a top-tier design agency.
"""
            
            # Generate the ad using DALL-E
            self.logger.info("Sending product image to DALL-E for ad generation")
            
            # Save the image to a temporary file in PNG format if it's not already
            temp_image_path = self._convert_to_png(product_image_path)
            
            # Open the image file
            with open(temp_image_path, "rb") as image_file:
                # Generate the ad
                response = self.openai_client.images.edit(
                    image=image_file,
                    prompt=prompt,
                    size="1024x1024",
                    quality="hd",
                    n=1
                )
            
            # Clean up temporary file if needed
            if temp_image_path != product_image_path and os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            
            # Get the result URL
            image_url = response.data[0].url
            
            # Download image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Save the final image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_filepath = f"output/images/final/final_ad_{timestamp}.png"
            
            with open(final_filepath, 'wb') as f:
                f.write(image_response.content)
            
            self.logger.info(f"Final ad with user product saved to: {final_filepath}")
            
            return {
                'original_product_path': product_image_path,
                'final_path': final_filepath,
                'headline': headline,
                'subheadline': subheadline,
                'call_to_action': call_to_action
            }
            
        except Exception as e:
            self.logger.error(f"Error creating ad with user product: {str(e)}")
            self.logger.error(traceback.format_exc())
            
            # Try alternative approach with GPT-4 Vision
            try:
                self.logger.info("Attempting alternative approach with GPT-4 Vision")
                return self._create_ad_with_gpt4_vision(
                    product_image_path, product, brand_name, headline, 
                    subheadline, call_to_action, industry, brand_level
                )
            except Exception as vision_error:
                self.logger.error(f"GPT-4 Vision approach failed: {str(vision_error)}")
                
                # Final fallback - create ad without user product image
                self.logger.info("Falling back to creating ad without user product image")
                return self.create_studio_ad(
                    product, brand_name, headline, subheadline, call_to_action, industry, brand_level
                )
    
    def _convert_to_png(self, image_path: str) -> str:
        """
        Convert image to PNG format if needed for DALL-E.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Path to PNG image (either the original if already PNG or a new temp file)
        """
        # Check if already PNG
        if image_path.lower().endswith('.png'):
            return image_path
        
        try:
            # Open the image
            img = Image.open(image_path)
            
            # Create temp file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_path = f"output/images/temp_{timestamp}.png"
            
            # Save as PNG
            img.save(temp_path, format="PNG")
            self.logger.info(f"Converted image to PNG: {temp_path}")
            
            return temp_path
        except Exception as e:
            self.logger.error(f"Error converting image to PNG: {str(e)}")
            # Return original path if conversion fails
            return image_path
    
    def _create_ad_with_gpt4_vision(self, product_image_path: str, product: str, 
                                brand_name: str = None, headline: str = None,
                                subheadline: str = None, call_to_action: str = None, 
                                industry: str = None, brand_level: str = "premium") -> Dict[str, str]:
        """
        Alternative approach using GPT-4 Vision to get creative direction and DALL-E to generate the ad.
        
        Args:
            product_image_path: Path to user product image
            product: Product name/description
            brand_name: Brand name
            headline: Ad headline
            subheadline: Ad subheadline
            call_to_action: Call to action text
            industry: Industry category
            brand_level: Brand positioning level
            
        Returns:
            Dictionary with paths to generated images
        """
        # Encode image to base64
        with open(product_image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Create prompt for GPT-4 Vision
        vision_prompt = f"""Analyze this product image and create detailed directions for an advertisement.

Product: {product}
Brand: {brand_name or ""}
Industry: {industry or "General"}
Brand Level: {brand_level or "Premium"}

Please provide:
1. An analysis of the product's key visual features
2. Recommendations for background style and color
3. Lighting and composition recommendations
4. Color palette recommendations that complement the product
5. A detailed prompt for DALL-E to create a professional advertisement featuring this product
"""
        
        # Call GPT-4 Vision
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": vision_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        # Extract creative direction from response
        vision_analysis = response.choices[0].message.content
        
        # Extract DALL-E prompt if available
        dalle_prompt = self._extract_dalle_prompt_from_vision(vision_analysis)
        
        # Combine with ad text
        ad_text = f"""
Headline: {headline or f"Experience {product}"}
{f"Subheadline: {subheadline}" if subheadline else ""}
{f"Call to Action: {call_to_action}" if call_to_action else ""}
"""
        
        # Create complete prompt for DALL-E
        complete_prompt = f"""Create a professional advertisement based on this creative direction:

{dalle_prompt}

Please integrate the following text with professional typography:
{ad_text}

The final result should be a studio-quality advertisement with perfect integration of product and text.
"""
        
        # Generate image with DALL-E
        response = self.openai_client.images.generate(
            model="dall-e-3",
            prompt=complete_prompt,
            size="1024x1024",
            quality="hd",
            n=1
        )
        
        # Get the result URL
        image_url = response.data[0].url
        
        # Download image
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        
        # Save the final image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_filepath = f"output/images/final/final_vision_ad_{timestamp}.png"
        
        with open(final_filepath, 'wb') as f:
            f.write(image_response.content)
        
        self.logger.info(f"Final ad with GPT-4 Vision approach saved to: {final_filepath}")
        
        return {
            'original_product_path': product_image_path,
            'final_path': final_filepath,
            'headline': headline,
            'subheadline': subheadline,
            'call_to_action': call_to_action,
            'method': 'gpt4_vision'
        }
    
    def _extract_dalle_prompt_from_vision(self, vision_analysis: str) -> str:
        """
        Extract DALL-E prompt from GPT-4 Vision analysis.
        
        Args:
            vision_analysis: The text analysis from GPT-4 Vision
            
        Returns:
            Extracted DALL-E prompt or default prompt
        """
        # Look for a section that might contain a DALL-E prompt
        prompt_indicators = [
            "DALL-E PROMPT:", 
            "DALL-E:", 
            "Here's a prompt for DALL-E:", 
            "Prompt for DALL-E:", 
            "ADVERTISEMENT PROMPT:"
        ]
        
        for indicator in prompt_indicators:
            if indicator in vision_analysis:
                # Extract the text after the indicator
                parts = vision_analysis.split(indicator, 1)
                if len(parts) > 1:
                    # Find the end of the prompt (next section or end of text)
                    prompt_text = parts[1].strip()
                    
                    # Look for end markers
                    end_markers = ["---", "###", "NOTE:", "ADDITIONAL", "This prompt"]
                    for marker in end_markers:
                        if marker in prompt_text:
                            prompt_text = prompt_text.split(marker, 1)[0].strip()
                    
                    return prompt_text
        
        # If no specific prompt section is found, return the entire analysis
        # This works because DALL-E can process the entire analysis as a prompt
        return vision_analysis
    
    def create_studio_ad(self, product: str, brand_name: str = None, headline: str = None,
                       subheadline: str = None, call_to_action: str = None, industry: str = None,
                       brand_level: str = None, image_description: str = None,
                       layout_hint: Dict = None) -> Dict[str, str]:
        """
        Create complete studio-quality ad with integrated typography.
        
        Args:
            product: Product name/description
            brand_name: Brand name
            headline: Ad headline
            subheadline: Ad subheadline
            call_to_action: Call to action text
            industry: Industry category
            brand_level: Brand positioning level
            image_description: Specific image description
            
        Returns:
            Dictionary with paths to generated images
        """
        try:
            self.logger.info(f"Creating studio ad for {product}")
            
            # Generate ad content if not provided
            if not headline:
                ad_content = self._generate_ad_content(product, brand_name, industry, brand_level)
                headline = ad_content.get("headline", f"Experience {product}")
                subheadline = ad_content.get("subheadline")
                call_to_action = ad_content.get("call_to_action", "Shop Now")
                image_description = ad_content.get("image_description") or image_description
            
            # Create a clean product-only DALL-E prompt (no text — TypographySystem handles text)
            complete_prompt = self._create_complete_ad_prompt(
                product, brand_name, industry=industry, brand_level=brand_level,
                image_description=image_description, layout_hint=layout_hint,
            )
            
            # Generate image with DALL-E
            self.logger.info("Generating complete ad with DALL-E")
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=complete_prompt,
                size="1024x1024",
                quality="hd",
                n=1
            )
            
            # Get the result URL
            image_url = response.data[0].url
            
            # Download image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Save the final image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_filepath = f"output/images/final/final_ad_{timestamp}.png"
            
            with open(final_filepath, 'wb') as f:
                f.write(image_response.content)
            
            self.logger.info(f"Complete studio ad saved to: {final_filepath}")
            
            return {
                'final_path': final_filepath,
                'headline': headline,
                'subheadline': subheadline,
                'call_to_action': call_to_action
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create studio ad: {str(e)}")
            self.logger.error(traceback.format_exc())
            
            # Create fallback ad
            fallback_path = self._create_fallback_image(product, brand_name)
            
            return {
                'final_path': fallback_path,
                'headline': headline or f"Experience {product}",
                'subheadline': subheadline or f"Discover the quality of {product}",
                'call_to_action': call_to_action or "Shop Now",
                'error': str(e)
            }
    
    def _create_complete_ad_prompt(self, product: str, brand_name: str = None,
                                industry: str = None, brand_level: str = "premium",
                                image_description: str = None,
                                layout_hint: Dict = None) -> str:
        """
        Build a clean DALL-E prompt focused on product photography only.
        Text rendering is handled entirely by TypographySystem — DALL-E must NOT
        add any text, logos, or typography to the image.
        layout_hint tells DALL-E where to leave compositional space for overlay zones.
        """
        creative_direction = self._generate_creative_direction(
            product, brand_name, industry, image_description, brand_level
        )

        base_prompt = creative_direction.get(
            "image_prompt",
            f"Professional advertisement photograph of {product} with studio lighting and perfect composition",
        )

        # Positioning hint — leaves space for the correct text overlay zones
        layout_hint = layout_hint or {}
        style       = layout_hint.get('style', '')
        headline_pos= layout_hint.get('headline_position', 'top_center')
        overlay     = layout_hint.get('overlay_type', '')

        if style == 'left_column' or overlay == 'gradient_left':
            positioning = (
                "Position the main product on the right two-thirds of the frame. "
                "The left side should be darker and visually clean, fading naturally toward the edge."
            )
        elif style == 'split_horizontal':
            positioning = (
                "Place the product on the left half of the image. "
                "The right half should be clean and uncluttered."
            )
        elif style == 'bottom_banner':
            positioning = (
                "Center the product in the upper 60% of the frame. "
                "The bottom 35% should transition to a darker, simpler background."
            )
        elif style == 'bold_statement':
            positioning = (
                "High-contrast, dramatic composition. "
                "Leave visual breathing room across the center of the image."
            )
        elif style == 'centered':
            positioning = (
                "Center-weighted product with clear open space above and below."
            )
        elif headline_pos == 'bottom_left':
            positioning = (
                "Product prominent in the upper-right area. "
                "Lower-left quadrant should be darker and cleaner."
            )
        else:
            positioning = (
                "Leave the top 30% and bottom 30% of the frame relatively clean and darker "
                "to provide contrast zones for text overlay."
            )

        complete_prompt = (
            f"{base_prompt}\n\n"
            f"{positioning}\n\n"
            f"Color scheme: {creative_direction.get('color_scheme', 'professional and brand-appropriate')}\n\n"
            f"IMPORTANT: Do NOT include any text, words, logos, typography, or written elements "
            f"anywhere in the image. This is a pure product photography base for a {brand_level} "
            f"brand in the {industry or 'general'} industry. Text will be added separately."
        )

        return complete_prompt
    
    def _create_fallback_image(self, product: str, brand_name: str = None) -> str:
        """Create a fallback image when generation fails."""
        try:
            # Default text if none provided
            product_text = product.upper() if product else "PRODUCT"
            brand_text = brand_name.upper() if brand_name else "BRAND"
            
            # Create a gradient background
            width, height = 1024, 1024
            img = Image.new('RGB', (width, height), color=(20, 30, 50))
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            placeholder_path = f"output/images/final/placeholder_{timestamp}.png"
            img.save(placeholder_path)
            
            return placeholder_path
        except:
            # Absolute last resort
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            placeholder_path = f"output/images/final/minimal_placeholder_{timestamp}.png"
            
            # Create an empty file if everything else fails
            with open(placeholder_path, 'w') as f:
                f.write('')
            
            return placeholder_path
    
    def _create_fallback_ad(self, product: str, brand_name: str = None) -> Dict[str, str]:
        """Create a fallback ad when all methods fail."""
        fallback_path = self._create_fallback_image(product, brand_name)
        
        return {
            'original_product_path': '',
            'final_path': fallback_path,
            'headline': f"Experience {product}",
            'subheadline': f"Discover the quality of {product}",
            'call_to_action': "Shop Now",
            'error': "Failed to generate ad with user product image"
        }