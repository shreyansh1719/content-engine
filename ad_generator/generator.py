"""
Professional Ad Generator with industry-standard quality
Studio-quality ad generation with proper typography and composition
"""
import os
import json
import logging
import re
import traceback
from typing import Dict, Optional, List, Any
from datetime import datetime
from openai import OpenAI

from .image_maker import StudioImageGenerator, create_placeholder_image
from .analytics import AdMetricsAnalyzer
from .social_media import search_social_media_ads

class AdGenerator:
    """Generate complete ad campaigns with studio-quality images and typography."""
    
    def __init__(self, openai_api_key=None):
        """Initialize generator with API keys."""
        # Setup API key
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        # Initialize image generator
        self.image_generator = StudioImageGenerator(self.openai_api_key)
        
        # Initialize metrics analyzer
        self.metrics_analyzer = AdMetricsAnalyzer()
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def analyze_brand(self, prompt: str) -> Dict:
        """
        Analyze brand and determine appropriate strategy.
        
        Args:
            prompt: User's product/brand prompt
            
        Returns:
            Brand analysis dictionary
        """
        try:
            # Create analysis prompt
            analysis_prompt = f"""Analyze this brand/product request: "{prompt}"
            
            Create a comprehensive JSON response with:
            {{
                "industry": "specific industry category",
                "brand_level": "luxury/premium/mass-market/etc",
                "tone": "brand voice and style",
                "target_market": "detailed audience description",
                "key_benefits": ["main selling points"],
                "competitors": ["similar brands"],
                "ad_style": "recommended advertising approach",
                "visual_direction": "art direction guidelines",
                "color_scheme": "brand-appropriate colors",
                "typography_style": "appropriate font style (modern, classic, bold, elegant, etc.)",
                "product_highlight": "specific feature or aspect to emphasize"
            }}

            Use industry standards and professional marketing terminology.
            """

            # Get response from OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert brand strategist and market analyst with experience developing campaigns for Fortune 500 companies."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.7
            )

            # Extract and parse JSON
            result = self._extract_json(response.choices[0].message.content)
            
            # Ensure all required fields exist
            required_fields = ['industry', 'brand_level', 'tone', 'target_market', 
                              'key_benefits', 'competitors', 'ad_style', 
                              'visual_direction', 'color_scheme', 'typography_style',
                              'product_highlight']
            
            for field in required_fields:
                if field not in result:
                    if field in ['key_benefits', 'competitors']:
                        result[field] = []
                    else:
                        result[field] = "Not specified"
            
            # Log successful analysis
            self.logger.info(f"Brand analysis completed for industry: {result['industry']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Brand analysis error: {str(e)}")
            # Return default analysis
            return {
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
            }
    
    def generate_ad_copy(self, prompt: str, brand_analysis: Dict, social_insights: Dict) -> Dict:
        """
        Generate ad copy based on brand analysis and social media insights.
        
        Args:
            prompt: User's product/brand prompt
            brand_analysis: Brand analysis dictionary
            social_insights: Social media insights
            
        Returns:
            Ad copy dictionary
        """
        try:
            # Add insights from ad metrics analyzer
            metrics_recommendations = self.metrics_analyzer.get_recommendations_for_industry(
                brand_analysis['industry'], 
                brand_analysis['brand_level']
            )
            
            # Create copy prompt with comprehensive inputs
            copy_prompt = f"""Create professional ad copy for: {prompt}

            Brand Context:
            Industry: {brand_analysis['industry']}
            Brand Level: {brand_analysis['brand_level']}
            Tone: {brand_analysis['tone']}
            Target: {brand_analysis['target_market']}
            Key Benefits: {', '.join(brand_analysis['key_benefits'])}
            
            Social Media Insights:
            Recommended Format: {social_insights.get('recommended_format', 'Product-focused')}
            Key Elements: {', '.join(social_insights.get('key_elements', ['quality', 'features']))}
            {"Trending Keywords: " + ', '.join(social_insights.get('trending_keywords', [])) if 'trending_keywords' in social_insights else ""}
            
            High-Performing Ad Patterns:
            {metrics_recommendations.get('copy_patterns', 'Use concise, benefit-focused headlines')}
            
            Generate JSON with:
            {{
                "headline": "attention-grabbing headline (max 6-8 words)",
                "subheadline": "supporting message (10-15 words, elaborates on headline)",
                "body_text": "main ad copy (2-3 short sentences, focused on benefits)",
                "call_to_action": "clear CTA (3-5 words, action-oriented)",
                "image_description": "detailed scene description for product photography"
            }}
            
            IMPORTANT GUIDELINES:
            - The headline must be short, impactful, and memorable
            - Focus on benefits, not just features
            - Use powerful, evocative language
            - Write text that fits elegantly in an ad layout (consider space)
            - The image description should focus on studio-quality product photography
            """

            # Get response from OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are an award-winning copywriter specializing in {brand_analysis['industry']} advertising for {brand_analysis['brand_level']} brands."},
                    {"role": "user", "content": copy_prompt}
                ],
                temperature=0.7
            )

            # Extract and parse JSON
            result = self._extract_json(response.choices[0].message.content)
            
            # Ensure all required fields exist
            required_fields = ['headline', 'subheadline', 'body_text', 'call_to_action', 'image_description']
            for field in required_fields:
                if field not in result:
                    result[field] = f"Default {field} for {prompt}"
            
            # Ensure headline is short and impactful
            if len(result['headline'].split()) > 8:
                # Truncate to 8 words
                words = result['headline'].split()[:8]
                result['headline'] = ' '.join(words)
            
            self.logger.info("Ad copy generation completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Ad copy generation error: {str(e)}")
            # Return default ad copy
            return {
                "headline": f"EXPERIENCE {prompt.upper()}",
                "subheadline": f"Discover the quality and innovation of our premium {prompt}.",
                "body_text": f"Our {prompt} offers unmatched performance and style. Experience the difference today.",
                "call_to_action": "SHOP NOW",
                "image_description": f"Professional product photography of {prompt} with clean background and perfect lighting."
            }
    
    def extract_brand_product(self, prompt: str) -> Dict:
        """
        Extract brand name and product from prompt.
        
        Args:
            prompt: User's input prompt
            
        Returns:
            Dictionary with brand_name and product
        """
        try:
            # Create extraction prompt
            extraction_prompt = f"""Extract the product/service and brand name from this request: "{prompt}"
            
            If a brand isn't explicitly mentioned, make an educated guess or extract the first word.
            Format your response as JSON with:
            {{
                "product": "the main product or service",
                "brand_name": "the brand name (in ALL CAPS)"
            }}

            Examples:
            - For "iPhone 15", extract product="iPhone 15", brand_name="APPLE"
            - For "luxury sneakers", extract product="luxury sneakers", brand_name="FASHION"
            - For "Nike running shoes", extract product="running shoes", brand_name="NIKE"
            """

            # Get response from OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You extract product and brand information."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.5
            )

            # Extract and parse JSON
            result = self._extract_json(response.choices[0].message.content)
            
            # Ensure brand_name is uppercase
            if 'brand_name' in result:
                result['brand_name'] = result['brand_name'].upper()
            else:
                # Extract first word as brand if not specified
                first_word = prompt.split()[0] if prompt else "BRAND"
                result['brand_name'] = first_word.upper()
            
            # Ensure product exists
            if 'product' not in result:
                result['product'] = prompt
            
            return result
            
        except Exception as e:
            self.logger.error(f"Brand/product extraction error: {str(e)}")
            # Return default extraction
            words = prompt.split()
            brand = words[0].upper() if words else "BRAND"
            return {
                "product": prompt,
                "brand_name": brand
            }
    
    def create_ad(self, prompt: str) -> Dict:
        """
        Create a complete ad with brand analysis, copy, and studio-quality image.
        
        Args:
            prompt: User's product/brand prompt
            
        Returns:
            Complete ad dictionary
        """
        try:
            # Step 1: Extract brand and product information
            self.logger.info(f"Extracting brand and product from: {prompt}")
            extraction = self.extract_brand_product(prompt)
            product = extraction['product']
            brand_name = extraction['brand_name']
            
            # Step 2: Analyze brand
            self.logger.info(f"Analyzing brand: {brand_name}")
            brand_analysis = self.analyze_brand(prompt)
            
            # Step 3: Get social media insights
            self.logger.info(f"Getting social media insights for: {product}")
            social_media_insights = search_social_media_ads(product, brand_name, brand_analysis['industry'])
            
            # Step 4: Generate ad copy
            self.logger.info("Generating ad copy")
            ad_copy = self.generate_ad_copy(prompt, brand_analysis, social_media_insights)
            
            # Step 5: Generate studio-quality image
            self.logger.info("Generating ad image")
            
            # Create image with professional typography
            image_result = self.image_generator.create_studio_ad(
                product=product,
                brand_name=brand_name,
                headline=ad_copy['headline'],
                subheadline=ad_copy['subheadline'],
                call_to_action=ad_copy['call_to_action'],
                industry=brand_analysis['industry'],
                brand_level=brand_analysis['brand_level'],
                typography_style=brand_analysis['typography_style'],
                color_scheme=brand_analysis['color_scheme'],
                image_description=ad_copy['image_description'],
                visual_focus=social_media_insights.get('visual_focus', 'product details'),
                text_placement=social_media_insights.get('text_placement', 'centered')
            )
            
            # Step 6: Compile results
            ad_data = {
                'product': product,
                'brand_name': brand_name,
                'headline': ad_copy['headline'],
                'subheadline': ad_copy['subheadline'],
                'body_text': ad_copy['body_text'],
                'call_to_action': ad_copy['call_to_action'],
                'image_path': image_result['final_path'],
                'base_image_path': image_result.get('base_path', ''),
                'brand_analysis': brand_analysis,
                'social_media_insights': social_media_insights,
                'generation_time': datetime.now().isoformat()
            }
            
            self.logger.info(f"Ad generation completed successfully: {ad_data['image_path']}")
            return ad_data
            
        except Exception as e:
            self.logger.error(f"Error creating ad: {str(e)}")
            self.logger.error(traceback.format_exc())
            
            # Create a fallback ad with basic image
            try:
                placeholder_path = create_placeholder_image(prompt, prompt.split()[0].upper() if prompt.split() else "BRAND")
                
                return {
                    'product': prompt,
                    'brand_name': prompt.split()[0].upper() if prompt.split() else "BRAND",
                    'headline': f"EXPERIENCE {prompt.upper()}",
                    'subheadline': f"Discover the quality and innovation of our premium {prompt}.",
                    'body_text': f"Our {prompt} offers unmatched performance and style. Experience the difference today.",
                    'call_to_action': "SHOP NOW",
                    'image_path': placeholder_path,
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
                    'social_media_insights': {
                        "recommended_format": "Product-focused with clean background",
                        "text_placement": "centered",
                        "text_style": "minimal",
                        "key_elements": ["product close-up", "brand elements", "quality suggestion"],
                        "visual_focus": "product details",
                        "color_scheme": "blue gradient"
                    },
                    'generation_time': datetime.now().isoformat(),
                    'error': str(e)
                }
            except Exception as fallback_error:
                self.logger.error(f"Fallback ad creation error: {str(fallback_error)}")
                return {
                    'product': prompt,
                    'headline': "DEFAULT HEADLINE",
                    'subheadline': "Default subheadline",
                    'body_text': "Default body text",
                    'call_to_action': "SHOP NOW",
                    'image_path': "",
                    'generation_time': datetime.now().isoformat(),
                    'error': str(e)
                }
    
    def _extract_json(self, text: str) -> Dict:
        """
        Extract JSON object from text.
        
        Args:
            text: Text containing JSON
            
        Returns:
            Parsed JSON as dictionary
        """
        try:
            # Try to parse the entire content as JSON
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON using regex
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
            
            # If regex extraction fails, try line-by-line parsing
            try:
                # Look for key-value pairs in the format "key": "value"
                result = {}
                lines = text.split('\n')
                
                for line in lines:
                    # Match "key": "value" or "key": ["item1", "item2"]
                    key_value_match = re.search(r'"([^"]+)"\s*:\s*("([^"]*)"|\[.*\])', line)
                    if key_value_match:
                        key = key_value_match.group(1)
                        value = key_value_match.group(2)
                        
                        # If it's a list, parse it
                        if value.startswith('['):
                            try:
                                value = json.loads(value)
                            except:
                                value = [item.strip('" ') for item in value.strip('[]').split(',')]
                        else:
                            # Otherwise, remove quotes
                            value = value.strip('"')
                        
                        result[key] = value
                
                return result
            except:
                # Return empty dict if all parsing fails
                return {}