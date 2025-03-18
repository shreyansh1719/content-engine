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
from typing import Dict, Optional, Union, Tuple, List, Any
import requests
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageColor
import traceback
import numpy as np
import random

class StudioImageGenerator:
    """Generate studio-quality ad images with professional typography."""
    
    def __init__(self, openai_api_key=None):
        """Initialize with OpenAI API key."""
        # Setup API key
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        # Setup logging
        self.setup_logging()
        
        # Default font directories to search in different operating systems
        self.font_directories = [
            '',  # Current directory
            '/usr/share/fonts/truetype/',
            '/usr/share/fonts/',
            '/Library/Fonts/',
            'C:\\Windows\\Fonts\\',
            os.path.join(os.path.expanduser('~'), 'Library/Fonts'),
            os.path.join(os.path.expanduser('~'), '.fonts')
        ]
        
        # Premium font mappings by style
        self.premium_fonts = self._setup_premium_fonts()
    
    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _setup_premium_fonts(self) -> Dict[str, Dict[str, List[str]]]:
        """Setup premium font mappings for different typography styles."""
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
    
    def _get_font(self, style: str, element: str, size: int) -> Optional[ImageFont.FreeTypeFont]:
        """
        Get professional font based on typography style and element.
        
        Args:
            style: Typography style ('modern', 'luxury', 'minimal', etc.)
            element: Element type ('headline', 'subheadline', 'body', 'cta')
            size: Font size
            
        Returns:
            Font object
        """
        # Map style to closest available
        style_lower = style.lower()
        if 'modern' in style_lower or 'sans' in style_lower:
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
        else:
            # Default to modern
            style_key = 'modern'
        
        # Get font list for this style and element
        font_list = self.premium_fonts.get(style_key, {}).get(element, ['Arial-Bold', 'Helvetica-Bold'])
        
        # Try each font in the list
        for font_name in font_list:
            # Try with various extensions
            for ext in ['', '.ttf', '.otf', '.TTF', '.OTF']:
                for directory in self.font_directories:
                    try:
                        font_path = os.path.join(directory, f"{font_name}{ext}")
                        if os.path.exists(font_path):
                            return ImageFont.truetype(font_path, size)
                    except (OSError, IOError):
                        continue
        
        # Fallback to a generic approach
        generic_fonts = {
            'headline': ['Arial-Bold', 'Helvetica-Bold', 'OpenSans-Bold', 'Verdana-Bold'],
            'subheadline': ['Arial', 'Helvetica', 'OpenSans', 'Verdana'],
            'body': ['Arial', 'Helvetica', 'OpenSans', 'Verdana'],
            'cta': ['Arial-Bold', 'Helvetica-Bold', 'OpenSans-Bold', 'Verdana-Bold']
        }
        
        # Try generic fonts
        for font_name in generic_fonts.get(element, ['Arial']):
            for ext in ['', '.ttf', '.otf', '.TTF', '.OTF']:
                for directory in self.font_directories:
                    try:
                        font_path = os.path.join(directory, f"{font_name}{ext}")
                        if os.path.exists(font_path):
                            return ImageFont.truetype(font_path, size)
                    except (OSError, IOError):
                        continue
        
        # Last resort: default font
        try:
            return ImageFont.load_default()
        except:
            self.logger.warning(f"Could not load any fonts for {style} {element}")
            return None
    
    def generate_product_image(self, product: str, brand_name: str = None, industry: str = None, 
                             image_description: str = None, visual_focus: str = None) -> str:
        """
        Generate studio-quality product image using DALL-E.
        
        Args:
            product: Product name or description
            brand_name: Brand name (optional)
            industry: Industry category (optional)
            image_description: Specific image description (optional)
            visual_focus: Specific aspect to focus on (optional)
            
        Returns:
            Path to generated image
        """
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            # Create an optimized prompt for studio-quality product photography
            prompt = self._craft_studio_photography_prompt(
                product, brand_name, industry, image_description, visual_focus
            )
            
            self.logger.info(f"Generating studio-quality image for {product}")
            self.logger.info(f"Using optimized prompt: {prompt[:100]}...")
            
            # Generate image with DALL-E 3
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="hd",
                n=1
            )
            
            image_url = response.data[0].url
            
            # Download and save
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Save the image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"output/images/studio_base_{timestamp}.png"
            
            os.makedirs("output/images", exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(image_response.content)
            
            self.logger.info(f"Studio-quality image saved to: {filepath}")
            
            # Apply basic image enhancements
            enhanced_path = self._enhance_image_quality(filepath)
            
            return enhanced_path
            
        except Exception as e:
            self.logger.error(f"Error generating product image: {str(e)}")
            self.logger.error(traceback.format_exc())
            # Return a placeholder image
            return create_placeholder_image(product, brand_name)
    
    def _craft_studio_photography_prompt(self, product: str, brand_name: str = None, 
                                       industry: str = None, image_description: str = None,
                                       visual_focus: str = None) -> str:
        """
        Create optimized prompt for studio-quality product photography.
        
        Args:
            product: Product name/description
            brand_name: Brand name
            industry: Industry category
            image_description: Specific image description
            visual_focus: Specific aspect to focus on
            
        Returns:
            Optimized prompt for DALL-E
        """
        # Start with base product info
        product_info = f"{brand_name + ' ' if brand_name else ''}{product}"
        
        # Include specific image description if provided
        description = image_description or f"Professional product photography of {product_info}"
        
        # Determine visual focus
        focus = visual_focus or "product details and features"
        
        # Industry-specific directives
        industry_directives = self._get_industry_photography_directives(industry, product)
        
        # Craft the complete prompt
        prompt = f"""
        Create a professional, studio-quality advertisement photograph of {product_info}.
        
        {description}
        
        {industry_directives}
        
        KEY REQUIREMENTS:
        - Focus on {focus}
        - Use dramatic, professional studio lighting
        - Include subtle reflections and shadows
        - Product must be clearly visible and occupy 60-70% of frame
        - Use a high-end, minimalist background that complements the product
        - Leave appropriate space for text at the top and bottom
        - No text, logos, or watermarks in the image
        - 8K resolution, photorealistic commercial product photography
        - The image should look like it belongs in a premium magazine advertisement or billboard
        
        Important: Create a composition that allows for headline text at the top and smaller text at the bottom.
        """
        
        return prompt.strip()
    
    def _get_industry_photography_directives(self, industry: str, product: str) -> str:
        """
        Get industry-specific photography directives.
        
        Args:
            industry: Industry category
            product: Product name/description
            
        Returns:
            Industry-specific photography directions
        """
        product_lower = product.lower()
        
        # Technology products
        if any(term in product_lower for term in ["phone", "smartphone", "iphone"]) or \
           (industry and any(term in industry.lower() for term in ["tech", "electronics", "smartphone"])):
            return """
            PHOTOGRAPHY DIRECTIVES:
            - Show the device at a 3/4 angle that highlights both the screen and profile
            - Use dramatic lighting that accentuates the sleek design
            - Include subtle reflections on surfaces
            - Display a vibrant, visually appealing screen
            - Position against a dark or gradient background with professional studio lighting
            - Ensure all product details are crisp and clear
            """
        
        # Luxury watches
        elif any(term in product_lower for term in ["watch", "timepiece"]) or \
             (industry and any(term in industry.lower() for term in ["watches", "jewelry", "luxury"])):
            return """
            PHOTOGRAPHY DIRECTIVES:
            - Show the watch at the classic 10:10 position to frame the logo
            - Use macro photography techniques to highlight fine details
            - Employ dramatic lighting with precise highlights on metal elements
            - Create subtle shadows to convey depth and dimension
            - Position against a dark, elegant background
            - Use studio lighting that accentuates metallic finish and watch face details
            """
        
        # Perfumes/Fragrances
        elif any(term in product_lower for term in ["perfume", "fragrance", "cologne"]) or \
             (industry and any(term in industry.lower() for term in ["fragrance", "beauty", "cosmetics"])):
            return """
            PHOTOGRAPHY DIRECTIVES:
            - Showcase the bottle with dramatic lighting that highlights its contours
            - Create delicate reflections on glass/crystal surfaces
            - Use soft diffused lighting to create an atmosphere of luxury and sophistication
            - Position against a dark gradient background
            - Add subtle environmental elements that suggest the fragrance profile (floral, woody, etc.)
            - Include minimal water droplets or mist for sensory appeal
            """
        
        # Shoes/Footwear
        elif any(term in product_lower for term in ["shoe", "sneaker", "footwear"]) or \
             (industry and any(term in industry.lower() for term in ["footwear", "athletic", "fashion"])):
            return """
            PHOTOGRAPHY DIRECTIVES:
            - Position the footwear at a dynamic 45-degree angle
            - Light to highlight textures and materials
            - Show subtle shadows beneath for grounding
            - Capture both profile and top-down perspective elements
            - Use dramatic studio lighting with careful highlights on key design elements
            - Position against a simple, complementary background that doesn't distract
            """
        
        # Skincare/Beauty
        elif any(term in product_lower for term in ["cream", "serum", "moisturizer", "skincare"]) or \
             (industry and any(term in industry.lower() for term in ["skincare", "beauty", "cosmetics"])):
            return """
            PHOTOGRAPHY DIRECTIVES:
            - Position product with lid/cap slightly open to suggest use
            - Create soft, diffused lighting for a clean, clinical feel
            - Add subtle cream/product texture elements
            - Include droplets or application suggestion for lotions/liquids
            - Use a light, bright background that suggests purity and cleanliness
            - Incorporate subtle elements suggesting natural ingredients where appropriate
            """
        
        # Default directives for other products
        return """
        PHOTOGRAPHY DIRECTIVES:
        - Position the product as the clear focal point
        - Use professional studio lighting with controlled highlights and shadows
        - Create a composition with visual balance and clear focus
        - Ensure the product's key features are prominently displayed
        - Use a clean, professional background that complements the product
        """
    
    def _enhance_image_quality(self, image_path: str) -> str:
        """
        Apply professional image enhancements.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Path to enhanced image
        """
        try:
            # Open the image
            img = Image.open(image_path)
            
            # Apply a series of enhancements
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)  # Slightly increase contrast
            
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.05)  # Slightly increase brightness
            
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.1)  # Increase color vibrance
            
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.2)  # Increase sharpness
            
            # Save enhanced image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            enhanced_path = f"output/images/enhanced_{timestamp}.png"
            img.save(enhanced_path, "PNG", quality=100)
            
            self.logger.info(f"Enhanced image saved to: {enhanced_path}")
            return enhanced_path
        
        except Exception as e:
            self.logger.warning(f"Image enhancement failed: {str(e)}")
            return image_path  # Return original if enhancement fails
    
    def apply_professional_typography(self, image_path: str, headline: str, subheadline: str = None,
                                   call_to_action: str = None, brand_name: str = None,
                                   typography_style: str = "modern", text_placement: str = "centered",
                                   color_scheme: str = None) -> str:
        """
        Apply professional typography with industry-standard design principles.
        
        Args:
            image_path: Path to base image
            headline: Main headline text
            subheadline: Subheadline text (optional)
            call_to_action: Call to action text (optional)
            brand_name: Brand name (optional)
            typography_style: Typography style
            text_placement: Text placement style
            color_scheme: Color scheme to use
            
        Returns:
            Path to final image with typography
        """
        try:
            # Check if image exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            # Open and prepare image
            original_image = Image.open(image_path).convert('RGBA')
            width, height = original_image.size
            
            # Create transparent overlay for text
            text_overlay = Image.new('RGBA', original_image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(text_overlay)
            
            # Analyze image to determine optimal text treatment
            brightness_map = self._analyze_image_brightness_map(original_image)
            dominant_colors = self._extract_dominant_colors(original_image)
            
            # Calculate optimal font sizes based on image dimensions
            headline_size = int(height * 0.075)  # Professional ads use smaller, more elegant type
            subheadline_size = int(height * 0.035)
            cta_size = int(height * 0.045)
            brand_size = int(height * 0.055)
            
            # Load professional fonts based on typography style
            headline_font = self._get_font(typography_style, "headline", headline_size)
            subheadline_font = self._get_font(typography_style, "subheadline", subheadline_size)
            cta_font = self._get_font(typography_style, "cta", cta_size)
            brand_font = self._get_font(typography_style, "headline", brand_size)
            
            # Use rule of thirds for text positioning based on text_placement
            positions = self._calculate_professional_text_positions(
                width, height, text_placement, brightness_map
            )
            
            # Get color scheme for text and accents
            text_color, accent_color, overlay_bg = self._determine_professional_colors(
                dominant_colors, brightness_map, color_scheme
            )
            
            # Add brand name
            if brand_name:
                brand_text = brand_name.upper()
                brand_dims = self._get_text_dimensions(brand_text, brand_font)
                brand_pos = positions['brand_pos']
                
                self._add_text_with_treatment(
                    draw,
                    brand_text,
                    brand_pos,
                    brand_font,
                    text_color,
                    brightness_map,
                    treatment="subtle_bg"
                )
            
            # Add headline with professional treatment
            if headline:
                headline_text = headline.upper() if len(headline.split()) <= 4 else headline
                headline_dims = self._get_text_dimensions(headline_text, headline_font)
                headline_pos = positions['headline_pos']
                
                self._add_text_with_treatment(
                    draw,
                    headline_text,
                    headline_pos,
                    headline_font,
                    text_color,
                    brightness_map,
                    treatment="gradient"
                )
            
            # Add subheadline
            if subheadline:
                subheadline_dims = self._get_text_dimensions(subheadline, subheadline_font)
                subheadline_pos = positions['subheadline_pos']
                
                self._add_text_with_treatment(
                    draw,
                    subheadline,
                    subheadline_pos,
                    subheadline_font,
                    text_color,
                    brightness_map,
                    treatment="subtle_bg"
                )
            
            # Add call-to-action with button
            if call_to_action:
                cta_text = call_to_action.upper()
                cta_dims = self._get_text_dimensions(cta_text, cta_font)
                cta_pos = positions['cta_pos']
                
                # Create elegant button for CTA
                self._add_cta_button(
                    draw, 
                    cta_text, 
                    cta_pos, 
                    cta_font, 
                    accent_color
                )
            
            # Apply subtle overall adjustments for cohesion
            text_overlay = text_overlay.filter(ImageFilter.GaussianBlur(radius=0.3))
            
            # Composite the text overlay with the original image
            final_image = Image.alpha_composite(original_image, text_overlay)
            
            # Save and return
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_path = f"output/images/final_ad_{timestamp}.png"
            final_image.convert('RGB').save(final_path, 'PNG', quality=100)
            
            self.logger.info(f"Final image with professional typography saved: {final_path}")
            return final_path
            
        except Exception as e:
            self.logger.error(f"Typography application error: {str(e)}")
            self.logger.error(traceback.format_exc())
            return image_path  # Return original image if typography fails
    
    def _analyze_image_brightness_map(self, image: Image.Image) -> Dict[str, float]:
        """
        Analyze image to create a brightness map for optimal text placement.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with brightness values for different regions
        """
        # Convert to grayscale
        gray = image.convert('L')
        width, height = gray.size
        
        # Divide the image into a 3x3 grid (Rule of Thirds)
        cell_width = width // 3
        cell_height = height // 3
        
        brightness_map = {}
        
        # Analyze each cell
        for row in range(3):
            for col in range(3):
                # Define cell boundaries
                left = col * cell_width
                upper = row * cell_height
                right = left + cell_width
                lower = upper + cell_height
                
                # Crop and calculate brightness
                cell = gray.crop((left, upper, right, lower))
                brightness = sum(list(cell.getdata())) / (cell_width * cell_height * 255)
                
                # Store in map
                position = f"{['top', 'middle', 'bottom'][row]}_{['left', 'center', 'right'][col]}"
                brightness_map[position] = brightness
        
        # Calculate overall brightness
        brightness_map['overall'] = sum(list(gray.getdata())) / (width * height * 255)
        
        return brightness_map
    
    def _extract_dominant_colors(self, image: Image.Image, num_colors: int = 5) -> List[Tuple[int, int, int]]:
        """
        Extract dominant colors from image for color scheme coordination.
        
        Args:
            image: PIL Image object
            num_colors: Number of dominant colors to extract
            
        Returns:
            List of RGB color tuples
        """
        # Resize image for faster processing
        img_small = image.resize((100, 100), Image.Resampling.LANCZOS)
        
        # Convert to RGB if needed
        if img_small.mode != 'RGB':
            img_small = img_small.convert('RGB')
        
        # Get colors
        pixels = list(img_small.getdata())
        
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
    
    def _calculate_professional_text_positions(
        self, width: int, height: int, placement: str, brightness_map: Dict[str, float]
    ) -> Dict[str, Tuple[int, int]]:
        """
        Calculate professional text positions using the rule of thirds.
        
        Args:
            width: Image width
            height: Image height
            placement: Text placement style
            brightness_map: Image brightness map
            
        Returns:
            Dictionary with text element positions
        """
        # Use rule of thirds
        third_w = width // 3
        third_h = height // 3
        
        # Default positions (centered)
        positions = {
            'brand_pos': (width // 2, third_h // 2),            # Top center
            'headline_pos': (width // 2, third_h),              # First third line
            'subheadline_pos': (width // 2, third_h + third_h // 2),  # Between first and second third
            'cta_pos': (width // 2, height - third_h)           # Bottom third
        }
        
        # Adjust based on placement preference and brightness
        if placement.lower() == 'top_heavy':
            # More emphasis on top elements
            positions['headline_pos'] = (width // 2, third_h // 2)
            positions['subheadline_pos'] = (width // 2, third_h)
            positions['brand_pos'] = (width // 2, third_h // 4)
            
        elif placement.lower() == 'bottom_heavy':
            # More emphasis on bottom elements
            positions['headline_pos'] = (width // 2, height - third_h - third_h // 2)
            positions['subheadline_pos'] = (width // 2, height - third_h)
            positions['cta_pos'] = (width // 2, height - third_h // 2)
            
        elif placement.lower() == 'left':
            # Left-aligned text (typical in many print ads)
            margin = int(width * 0.1)
            positions['brand_pos'] = (margin, third_h // 2)
            positions['headline_pos'] = (margin, third_h)
            positions['subheadline_pos'] = (margin, third_h + third_h // 2)
            positions['cta_pos'] = (margin, height - third_h)
            
        elif placement.lower() == 'right':
            # Right-aligned text
            margin = int(width * 0.9)
            positions['brand_pos'] = (margin, third_h // 2)
            positions['headline_pos'] = (margin, third_h)
            positions['subheadline_pos'] = (margin, third_h + third_h // 2)
            positions['cta_pos'] = (margin, height - third_h)
        
        # Further adjust based on image brightness
        # Find darkest third for text placement (for light text)
        if brightness_map['overall'] > 0.5:
            # For bright images, find darkest areas for text
            darkest = min(brightness_map.items(), key=lambda x: x[1] if x[0] != 'overall' else 1.0)
            brightest = max(brightness_map.items(), key=lambda x: x[1] if x[0] != 'overall' else 0.0)
            
            # Adjust headline position if very bright image
            if brightness_map['overall'] > 0.7:
                # Very bright image, add more contrast with positioning
                if 'top' in darkest[0]:
                    positions['headline_pos'] = (positions['headline_pos'][0], third_h // 2)
                elif 'bottom' in darkest[0]:
                    positions['headline_pos'] = (positions['headline_pos'][0], height - third_h - third_h // 2)
        
        return positions
    
    def _determine_professional_colors(
        self, dominant_colors: List[Tuple[int, int, int]], 
        brightness_map: Dict[str, float],
        color_scheme: str = None
    ) -> Tuple[Tuple[int, int, int, int], Tuple[int, int, int, int], Tuple[int, int, int, int]]:
        """
        Determine professional color scheme for text and accents.
        
        Args:
            dominant_colors: List of dominant image colors
            brightness_map: Image brightness map
            color_scheme: User-specified color scheme
            
        Returns:
            Tuple of (text_color, accent_color, overlay_bg)
        """
        # Default colors
        default_text = (255, 255, 255, 255)  # White text
        default_dark_text = (30, 30, 30, 255)  # Near black text
        default_accent = (41, 128, 185, 230)  # Professional blue
        default_overlay = (0, 0, 0, 160)  # Semi-transparent black
        
        # Determine text color based on image brightness
        if brightness_map['overall'] > 0.5:
            text_color = default_dark_text
            overlay_bg = (255, 255, 255, 160)  # Semi-transparent white
        else:
            text_color = default_text
            overlay_bg = default_overlay
        
        # Handle specific color schemes
        if color_scheme:
            try:
                # Parse color scheme for accent color
                if 'blue' in color_scheme.lower():
                    accent_color = (41, 128, 185, 230)  # Professional blue
                elif 'red' in color_scheme.lower():
                    accent_color = (192, 57, 43, 230)  # Professional red
                elif 'green' in color_scheme.lower():
                    accent_color = (39, 174, 96, 230)  # Professional green
                elif 'gold' in color_scheme.lower() or 'yellow' in color_scheme.lower():
                    accent_color = (241, 196, 15, 230)  # Gold
                elif 'purple' in color_scheme.lower():
                    accent_color = (142, 68, 173, 230)  # Purple
                elif 'black' in color_scheme.lower():
                    accent_color = (30, 30, 30, 230)  # Black
                elif 'white' in color_scheme.lower():
                    accent_color = (240, 240, 240, 230)  # White
                else:
                    # Try to parse an explicit color
                    try:
                        # Try to extract a color from the color_scheme string
                        color_match = re.search(r'#(?:[0-9a-fA-F]{3}){1,2}', color_scheme)
                        if color_match:
                            hex_color = color_match.group(0)
                            rgb = ImageColor.getrgb(hex_color)
                            accent_color = (rgb[0], rgb[1], rgb[2], 230)
                        else:
                            # Use the first dominant color as accent
                            if dominant_colors:
                                first_color = dominant_colors[0]
                                accent_color = (first_color[0], first_color[1], first_color[2], 230)
                            else:
                                accent_color = default_accent
                    except:
                        accent_color = default_accent
            except:
                accent_color = default_accent
        else:
            # No specific scheme, use dominant color if it has enough contrast
            if dominant_colors:
                first_color = dominant_colors[0]
                # Check if dominant color has enough contrast with text
                brightness = (first_color[0] * 299 + first_color[1] * 587 + first_color[2] * 114) / 1000
                if abs(brightness - (text_color[0] * 299 + text_color[1] * 587 + text_color[2] * 114) / 1000) > 100:
                    accent_color = (first_color[0], first_color[1], first_color[2], 230)
                else:
                    # Not enough contrast, use default
                    accent_color = default_accent
            else:
                accent_color = default_accent
        
        return text_color, accent_color, overlay_bg
    
    def _get_text_dimensions(self, text: str, font) -> Tuple[int, int]:
        """Get dimensions of text with given font."""
        try:
            # Try getbbox method first (Pillow >= 8.0.0)
            bbox = font.getbbox(text)
            if bbox:
                return bbox[2] - bbox[0], bbox[3] - bbox[1]
        except (AttributeError, TypeError):
            try:
                # Try older PIL method
                return font.getsize(text)
            except:
                # Estimate based on character count
                size = getattr(font, 'size', 12)
                return int(len(text) * size * 0.6), int(size * 1.2)
    
    def _add_text_with_treatment(self, draw, text, position, font, text_color, 
                               brightness_map, treatment="gradient"):
        """
        Add text with professional treatment techniques.
        
        Args:
            draw: ImageDraw object
            text: Text to draw
            position: Text position (x, y)
            font: Font to use
            text_color: Text color
            brightness_map: Image brightness map
            treatment: Text treatment style
        """
        x, y = position
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Center text horizontally (unless positioning logic changes)
        x = x - text_width // 2
        
        if treatment == "gradient":
            # Create gradient text treatment (subtly feathered edges)
            for offset in range(2):
                # Add subtle shadow offsets
                shadow_color = (0, 0, 0, 100 - offset * 40)
                draw.text((x + offset, y + offset), text, font=font, fill=shadow_color)
            
            # Draw main text
            draw.text((x, y), text, font=font, fill=text_color)
            
        elif treatment == "subtle_bg":
            # Create subtle background that doesn't overpower
            bg_padding = 10
            bg_color = (0, 0, 0, 120) if brightness_map['overall'] > 0.5 else (255, 255, 255, 100)
            
            # Draw semi-transparent background
            draw.rectangle(
                [
                    (x - bg_padding, y - bg_padding // 2),
                    (x + text_width + bg_padding, y + text_height + bg_padding // 2)
                ],
                fill=bg_color
            )
            
            # Draw text
            draw.text((x, y), text, font=font, fill=text_color)
            
        elif treatment == "simple":
            # Just draw the text
            draw.text((x, y), text, font=font, fill=text_color)
        
        else:
            # Default - add subtle shadow for contrast
            shadow_offset = 1
            shadow_color = (0, 0, 0, 180)
            
            # Draw shadow
            draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
            
            # Draw main text
            draw.text((x, y), text, font=font, fill=text_color)
    
    def _add_cta_button(self, draw, text, position, font, accent_color):
        """
        Add professional CTA button.
        
        Args:
            draw: ImageDraw object
            text: CTA text
            position: Button center position
            font: Font to use
            accent_color: Button color
        """
        x, y = position
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Button dimensions
        padding_x = 20
        padding_y = 12
        button_width = text_width + (padding_x * 2)
        button_height = text_height + (padding_y * 2)
        
        # Center the button
        button_left = x - button_width // 2
        button_top = y - button_height // 2
        
        # Define button coordinates
        button_coords = [
            (button_left, button_top),
            (button_left + button_width, button_top + button_height)
        ]
        
        # Draw button
        self._draw_rounded_rectangle(
            draw,
            button_coords,
            accent_color,
            radius=int(button_height * 0.2)
        )
        
        # Add subtle highlight and shadow effects for depth
        highlight_color = (255, 255, 255, 80)
        shadow_color = (0, 0, 0, 60)
        
        # Highlight at top
        highlight_coords = [
            (button_left, button_top),
            (button_left + button_width, button_top + int(button_height * 0.3))
        ]
        self._draw_rounded_rectangle(
            draw,
            highlight_coords,
            highlight_color,
            radius=int(button_height * 0.2),
            corners=['top-left', 'top-right']
        )
        
        # Draw text centered in button
        text_x = button_left + (button_width - text_width) // 2
        text_y = button_top + (button_height - text_height) // 2
        
        # Draw text with slight shadow for depth
        shadow_offset = 1
        draw.text(
            (text_x + shadow_offset, text_y + shadow_offset),
            text,
            font=font,
            fill=(0, 0, 0, 100)
        )
        draw.text(
            (text_x, text_y),
            text,
            font=font,
            fill=(255, 255, 255, 255)
        )
    
    def _draw_rounded_rectangle(self, draw, coords, color, radius=10, corners=None):
        """
        Draw a rounded rectangle.
        
        Args:
            draw: ImageDraw object
            coords: Rectangle coordinates [(x1, y1), (x2, y2)]
            color: Fill color
            radius: Corner radius
            corners: List of corners to round ['top-left', 'top-right', 'bottom-left', 'bottom-right']
                    If None, all corners are rounded
        """
        x1, y1 = coords[0]
        x2, y2 = coords[1]
        
        # If no specific corners, round all
        if corners is None:
            corners = ['top-left', 'top-right', 'bottom-left', 'bottom-right']
        
        # Draw rectangle
        draw.rectangle([(x1, y1), (x2, y2)], fill=color)
        
        # Draw rounded corners by overlaying circles
        if 'top-left' in corners:
            draw.ellipse([(x1, y1), (x1 + radius * 2, y1 + radius * 2)], fill=color)
        if 'top-right' in corners:
            draw.ellipse([(x2 - radius * 2, y1), (x2, y1 + radius * 2)], fill=color)
        if 'bottom-left' in corners:
            draw.ellipse([(x1, y2 - radius * 2), (x1 + radius * 2, y2)], fill=color)
        if 'bottom-right' in corners:
            draw.ellipse([(x2 - radius * 2, y2 - radius * 2), (x2, y2)], fill=color)
    
    def create_studio_ad(self, product: str, brand_name: str = None, headline: str = None,
                       subheadline: str = None, call_to_action: str = None, industry: str = None,
                       brand_level: str = None, typography_style: str = None,
                       color_scheme: str = None, image_description: str = None,
                       visual_focus: str = None, text_placement: str = "centered") -> Dict[str, str]:
        """
        Create complete studio-quality ad with professional typography.
        
        Args:
            product: Product name/description
            brand_name: Brand name
            headline: Main headline text
            subheadline: Subheadline text
            call_to_action: Call to action text
            industry: Industry category
            brand_level: Brand level (luxury, premium, etc.)
            typography_style: Typography style
            color_scheme: Color scheme
            image_description: Custom image description
            visual_focus: Visual focus for image
            text_placement: Text placement style
            
        Returns:
            Dictionary with paths to generated images
        """
        try:
            # Generate studio-quality product image
            self.logger.info(f"Generating studio ad for {product}")
            base_image_path = self.generate_product_image(
                product=product,
                brand_name=brand_name,
                industry=industry,
                image_description=image_description,
                visual_focus=visual_focus
            )
            
            # Determine optimal typography style if not specified
            if not typography_style:
                if brand_level and "luxury" in brand_level.lower():
                    typography_style = "luxury"
                elif brand_level and "premium" in brand_level.lower():
                    typography_style = "elegant"
                elif industry and "tech" in industry.lower():
                    typography_style = "modern"
                else:
                    typography_style = "modern"
            
            # Apply professional typography
            self.logger.info(f"Applying professional typography with {typography_style} style")
            final_image_path = self.apply_professional_typography(
                image_path=base_image_path,
                headline=headline or f"{brand_name} {product}",
                subheadline=subheadline,
                call_to_action=call_to_action,
                brand_name=brand_name,
                typography_style=typography_style,
                text_placement=text_placement,
                color_scheme=color_scheme
            )
            
            return {
                'base_path': base_image_path,
                'final_path': final_image_path
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create studio ad: {str(e)}")
            self.logger.error(traceback.format_exc())
            
            # Create placeholder as fallback
            placeholder_path = create_placeholder_image(product, brand_name)
            return {
                'base_path': placeholder_path,
                'final_path': placeholder_path
            }


def create_placeholder_image(product: str = None, brand_name: str = None) -> str:
    """Create a placeholder image when generation fails."""
    try:
        # Default text if none provided
        headline = product.upper() if product else "PRODUCT"
        brand = brand_name.upper() if brand_name else "BRAND"
        
        # Create a gradient background
        width, height = 1024, 1024
        img = Image.new('RGB', (width, height), color=(53, 59, 72))
        draw = ImageDraw.Draw(img)
        
        # Draw gradient background
        for y in range(height):
            r = int(53 + (150 - 53) * y / height)
            g = int(59 + (180 - 59) * y / height)
            b = int(72 + (220 - 72) * y / height)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Try to load fonts
        try:
            # Search for fonts in standard locations
            font_dirs = [
                '',
                '/usr/share/fonts/truetype/',
                '/Library/Fonts/',
                'C:\\Windows\\Fonts\\',
            ]
            
            font = None
            for dir in font_dirs:
                for font_name in ['Arial.ttf', 'Helvetica.ttf', 'DejaVuSans.ttf']:
                    try:
                        font_path = os.path.join(dir, font_name)
                        if os.path.exists(font_path):
                            large_font = ImageFont.truetype(font_path, 60)
                            medium_font = ImageFont.truetype(font_path, 40)
                            break
                    except:
                        continue
                if font:
                    break
            
            if not font:
                large_font = medium_font = ImageFont.load_default()
                
        except:
            # Use default font if all else fails
            large_font = medium_font = ImageFont.load_default()
        
        # Add a product placeholder shape
        draw.rectangle([width/4, height/4, width*3/4, height*3/4], 
                      fill=(255, 255, 255, 30), outline=(255, 255, 255))
        
        # Add brand name at top
        draw.text((width/2, height/8), brand, fill=(255, 255, 255), anchor="mm", font=large_font)
        
        # Add headline at bottom
        draw.text((width/2, height*7/8), headline, fill=(255, 255, 255), anchor="mm", font=large_font)
        
        # Add subheadline
        draw.text((width/2, height*7/8 + 70), "Professional Ad", fill=(200, 200, 200), anchor="mm", font=medium_font)
        
        # Save image
        os.makedirs("output/images", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        placeholder_path = f"output/images/placeholder_{timestamp}.png"
        img.save(placeholder_path)
        
        return placeholder_path
    except:
        # Last resort - create a basic black image with text
        try:
            img = Image.new('RGB', (1024, 1024), color=(0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.text((512, 512), "Ad Placeholder", fill=(255, 255, 255))
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            minimal_path = f"output/images/minimal_placeholder_{timestamp}.png"
            img.save(minimal_path)
            return minimal_path
        except:
            return ""