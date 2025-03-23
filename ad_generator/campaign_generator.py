'''campaign generator'''
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO
import random
import glob
from .image_maker import RunwayImageGenerator


class AdCampaignGenerator:
    """Generate winning ad campaigns using insights from top campaigns."""
    
    def __init__(self):
        """Initialize the campaign generator with necessary clients."""
        # Setup logging
        self.setup_logging()
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Initialize Runway credentials
        self.runway_api_key = os.getenv('RUNWAY_API_KEY')
        
        # Initialize image generator
        self.image_generator = RunwayImageGenerator(api_key=self.runway_api_key)
        
        # Load training materials if available
        self.load_training_materials()
    
    def setup_logging(self):
        """Configure logging for the ad campaign generator."""
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/ad_campaign_generation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_training_materials(self):
        """Load training materials if available."""
        self.training_materials = None
        self.prompt_enhancement = None
        
        # Check for processed data directory
        if not os.path.exists('data/processed'):
            self.logger.warning("No processed data directory found. Using base models without training enhancements.")
            return
        
        # Load latest training materials
        training_files = glob.glob('data/processed/ad_training_materials_*.json')
        if training_files:
            latest_training = sorted(training_files)[-1]
            try:
                with open(latest_training, 'r', encoding='utf-8') as f:
                    self.training_materials = json.load(f)
                self.logger.info(f"Loaded training materials from {latest_training}")
            except Exception as e:
                self.logger.error(f"Error loading training materials: {str(e)}")
        
        # Load latest prompt enhancement
        enhancement_files = glob.glob('data/processed/prompt_enhancement_*.json')
        if enhancement_files:
            latest_enhancement = sorted(enhancement_files)[-1]
            try:
                with open(latest_enhancement, 'r', encoding='utf-8') as f:
                    self.prompt_enhancement = json.load(f)
                self.logger.info(f"Loaded prompt enhancement from {latest_enhancement}")
            except Exception as e:
                self.logger.error(f"Error loading prompt enhancement: {str(e)}")
    
    def enhance_product_analysis(self, product: str, industry: str, brand_name: str = None) -> Dict:
        """
        Enhance product analysis with training materials.
        
        Args:
            product: Product name
            industry: Industry category
            brand_name: Brand name (optional)
            
        Returns:
            Enhanced product analysis
        """
        try:
            # Prepare system prompt
            system_content = "You are an expert marketing strategist specializing in high-performing ad campaigns."
            
            # Add training insights if available
            if self.training_materials:
                trend_data = self.training_materials.get('trend_analysis', {})
                system_content += f"\n\nYou've analyzed thousands of successful ad campaigns and identified these trends:\n{json.dumps(trend_data, indent=2)}"
            
            # Check for industry-specific patterns
            industry_patterns = {}
            if self.training_materials and 'industry_patterns' in self.training_materials:
                # Find closest matching industry
                for ind_key, ind_data in self.training_materials['industry_patterns'].items():
                    if ind_key.replace('_', ' ') in industry.lower() or industry.lower() in ind_key.replace('_', ' '):
                        industry_patterns = ind_data
                        break
            
            if industry_patterns:
                system_content += f"\n\nFor the {industry} industry specifically, you've observed these patterns:\n{json.dumps(industry_patterns, indent=2)}"
            
            # Create prompt enhancements
            prompt_enhancements = ""
            if self.prompt_enhancement:
                for section, content in self.prompt_enhancement.items():
                    if isinstance(content, dict) and section != "industry_specific":
                        prompt_enhancements += f"\n\n{section.replace('_', ' ').title()}:\n{json.dumps(content, indent=2)}"
                
                # Add industry-specific guidance if available
                if "industry_specific" in self.prompt_enhancement:
                    for ind_key, ind_data in self.prompt_enhancement["industry_specific"].items():
                        if ind_key.replace('_', ' ') in industry.lower() or industry.lower() in ind_key.replace('_', ' '):
                            prompt_enhancements += f"\n\nIndustry-Specific Guidance for {industry}:\n{json.dumps(ind_data, indent=2)}"
                            break
            
            # Add brand specific prompt if provided
            brand_content = ""
            if brand_name:
                brand_content = f"This is for the brand: {brand_name}. Ensure the analysis considers the brand's positioning."
            
            # Generate enhanced analysis
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": system_content
                    },
                    {
                        "role": "user", 
                        "content": f"""Analyze {product} in the {industry} industry for ad campaign creation.
                        {brand_content}
                        
                        Provide a comprehensive analysis including:
                        1. Target audience demographics and psychographics
                        2. Key value propositions and USPs
                        3. Emotional triggers that would resonate with the audience
                        4. Brand tone and style recommendations
                        5. Visual direction recommendations
                        6. Suggested messaging themes
                        7. Competitive landscape insights
                        8. Brand positioning strategy
                        9. Color scheme suggestions that work well with this type of product
                        
                        {prompt_enhancements}
                        
                        Format as a detailed JSON object.
                        """
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            self.logger.info(f"Enhanced product analysis for {product}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in product analysis: {str(e)}")
            raise
    
    def generate_winning_ad_copy(self, product: str, industry: str, brand_name: str, analysis: Dict) -> Dict:
        """
        Generate winning ad copy using training insights.
        
        Args:
            product: Product name
            industry: Industry category
            brand_name: Brand name
            analysis: Product analysis
            
        Returns:
            Generated ad copy
        """
        try:
            # Select a style template if available
            style_template = {}
            if self.training_materials and 'style_templates' in self.training_materials:
                templates = self.training_materials['style_templates']
                if isinstance(templates, list) and templates:
                    # Either randomly select a template or choose based on product/industry
                    style_template = random.choice(templates)
                elif isinstance(templates, dict) and 'styles' in templates:
                    style_template = random.choice(templates['styles'])
            
            # Prepare system prompt
            system_content = f"You are an expert copywriter specializing in high-conversion {industry} advertisements."
            
            if style_template:
                system_content += f"\n\nYou write in the following style:\n{json.dumps(style_template, indent=2)}"
            
            # Generate optimized ad copy
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": system_content
                    },
                    {
                        "role": "user", 
                        "content": f"""Create a professional, industry-standard advertisement for {product} for the brand {brand_name} based on this analysis:
                        
                        {json.dumps(analysis, indent=2)}
                        
                        Generate an ad that follows industry best practices with:
                        1. Headline: A powerful, attention-grabbing headline (5-8 words max)
                        2. Subheadline: A compelling supporting message (10-15 words max)
                        3. Body text: Brief but impactful description (2-3 short sentences)
                        4. Call to action: Clear and concise action prompt
                        5. Tagline: A memorable brand tagline (if appropriate)
                        6. Image description: Detailed visual scene for the ad (be specific about composition, elements, mood, colors)
                        7. Text placement: Specify where text elements should be positioned on the image
                        8. Typography: Recommend font style (elegant, bold, minimal, etc.)
                        9. Color scheme: Suggested text colors that work with the image
                        
                        IMPORTANT: The ad must look like a professional advertisement with text overlaid on the image.
                        Format as a comprehensive JSON object with these exact fields.
                        """
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            ad_copy = json.loads(response.choices[0].message.content)
            
            # Add the brand name if not already included
            ad_copy['brand_name'] = brand_name
            
            # Ensure all required fields exist
            required_fields = ['headline', 'subheadline', 'body_text', 'call_to_action', 'image_description']
            for field in required_fields:
                if field not in ad_copy:
                    ad_copy[field] = ""
            
            # Ensure image_description is a string
            if not isinstance(ad_copy['image_description'], str):
                if isinstance(ad_copy['image_description'], dict):
                    # Convert to string if it's a dict
                    image_desc_parts = []
                    for key, value in ad_copy['image_description'].items():
                        if isinstance(value, list):
                            value = " ".join(value)
                        image_desc_parts.append(f"{key}: {value}")
                    ad_copy['image_description'] = " ".join(image_desc_parts)
                else:
                    ad_copy['image_description'] = str(ad_copy['image_description'])
            
            self.logger.info(f"Winning ad copy generated for {product}")
            return ad_copy
        
        except Exception as e:
            self.logger.error(f"Error generating ad copy: {str(e)}")
            raise
    
    def generate_ad_image_with_text(self, ad_copy: Dict, product: str, industry: str, brand_name: str) -> str:
        """
        Generate a complete ad image with text overlay.
        
        Args:
            ad_copy: Generated ad copy
            product: Product name
            industry: Industry category
            brand_name: Brand name
            
        Returns:
            Path to generated image with text overlay
        """
        try:
            # First generate the base image
            image_description = ad_copy.get('image_description', f'Professional advertisement for {product}')
            
            # Enhance with brand and product context
            enhanced_description = f"{image_description}. This is for {brand_name} {product} in the {industry} industry."
            
            # Generate base image
            self.logger.info(f"Generating base image with description: {enhanced_description[:100]}...")
            base_image_path = self.image_generator.generate_ad_image(enhanced_description)
            self.logger.info(f"Base image generated at: {base_image_path}")
            
            # Extract text elements for overlay
            headline = ad_copy.get('headline', '')
            subheadline = ad_copy.get('subheadline', '')
            call_to_action = ad_copy.get('call_to_action', '')
            
            # Determine font style based on ad copy or industry
            font_style = ad_copy.get('typography', 'bold')
            if not font_style or font_style == "":
                # Default based on industry
                if 'luxury' in industry.lower() or 'premium' in industry.lower():
                    font_style = 'elegant'
                elif 'tech' in industry.lower() or 'digital' in industry.lower():
                    font_style = 'modern'
                else:
                    font_style = 'bold'
            
            # Determine text placement
            text_placement = ad_copy.get('text_placement', 'centered')
            if not text_placement or text_placement == "":
                text_placement = 'centered'
            
            # Add text overlay to image
            final_image_path = self.image_generator.add_text_overlay(
                base_image_path,
                headline=headline,
                subheadline=subheadline,
                call_to_action=call_to_action,
                brand_name=brand_name,
                font_style=font_style,
                text_placement=text_placement
            )
            
            self.logger.info(f"Final ad image with text created at: {final_image_path}")
            return final_image_path
            
        except Exception as e:
            self.logger.error(f"Error creating ad image with text: {str(e)}")
            # Return the base image if text overlay fails
            return base_image_path if 'base_image_path' in locals() else self._generate_fallback_image(product)
    
    def _generate_fallback_image(self, prompt: Union[str, Dict]) -> str:
        """
        Generate fallback image using DALL-E if Runway fails.
        
        Args:
            prompt: Image description (string or dict)
            
        Returns:
            Path to generated image
        """
        try:
            self.logger.info("Falling back to DALL-E for image generation")
            
            # Ensure prompt is a string
            if not isinstance(prompt, str):
                if isinstance(prompt, dict):
                    # Convert dict to string
                    prompt_parts = []
                    for key, value in prompt.items():
                        if isinstance(value, list):
                            value = " ".join(value)
                        prompt_parts.append(f"{key}: {value}")
                    prompt = " ".join(prompt_parts)
                else:
                    prompt = str(prompt)
            
            # Add any needed cleanup or formatting to the prompt
            prompt = prompt.replace('\n', ' ').strip()
            
            # Limit prompt length if needed
            if len(prompt) > 1000:
                prompt = prompt[:997] + "..."
                
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=f"Create a professional advertisement image: {prompt}. Make it look like a magazine ad without any text.",
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            
            # Download image
            image_response = requests.get(image_url)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"output/images/dalle_ad_{timestamp}.png"
            
            os.makedirs("output/images", exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(image_response.content)
                
            self.logger.info(f"DALL-E fallback image generated: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"DALL-E fallback image generation failed: {str(e)}")
            # Return path to a placeholder image if available
            placeholder_path = "output/images/placeholder_ad.png"
            if os.path.exists(placeholder_path):
                return placeholder_path
            
            # If no placeholder, create a simple one
            from .image_maker import create_placeholder_image
            return create_placeholder_image()
    
    def generate_winning_ad_campaign(self, product: str, industry: str, brand_name: str = None) -> Dict:
        """
        Generate a complete, high-performing ad campaign.
        
        Args:
            product: Product to create ad for
            industry: Industry of the product
            brand_name: Brand name (optional)
            
        Returns:
            Complete ad campaign details
        """
        try:
            # Use product name as brand if not provided
            if not brand_name:
                brand_words = product.split()
                brand_name = brand_words[0].upper() if brand_words else "BRAND"
            
            # Enhanced product analysis
            analysis = self.enhance_product_analysis(product, industry, brand_name)
            
            # Generate winning ad copy
            ad_copy = self.generate_winning_ad_copy(product, industry, brand_name, analysis)
            
            # Generate image with text overlay
            image_path = self.generate_ad_image_with_text(ad_copy, product, industry, brand_name)
            
            # Compile campaign details
            campaign = {
                "product": product,
                "industry": industry,
                "brand_name": brand_name,
                "ad_copy": ad_copy,
                "campaign_analysis": analysis,
                "image_path": image_path,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Winning ad campaign generated for {brand_name} {product}")
            return campaign
            
        except Exception as e:
            self.logger.error(f"Error generating ad campaign: {str(e)}")
            raise

# Example usage if run directly
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    generator = AdCampaignGenerator()
    
    # Generate a sample campaign
    campaign = generator.generate_winning_ad_campaign(
        "luxury watch",
        "Fashion Accessories",
        "ROLEX"
    )
    
    print(json.dumps(campaign, indent=2))