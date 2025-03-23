"""
Data formatter for preparing data for LLM training
"""
import os
import json
import logging
import random
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Tuple
from collections import defaultdict

class DataFormatter:
    """
    Format processed data for training LLMs on ad generation.
    
    Features:
    - Converts scraped data into training examples
    - Supports multiple formats for different LLM types
    - Creates balanced datasets from available sources
    - Includes prompt templates for different ad formats
    - Generates cross-platform training data
    """
    
    def __init__(
        self,
        input_dir: str = 'data',
        output_dir: str = 'data/training',
        log_level: int = logging.INFO
    ):
        """
        Initialize data formatter.
        
        Args:
            input_dir: Directory containing data files
            output_dir: Directory to save formatted training data
            log_level: Logging level
        """
        # Setup logging
        self.logger = logging.getLogger('DataFormatter')
        self.logger.setLevel(log_level)
        
        if not self.logger.handlers:
            # Create handlers
            console_handler = logging.StreamHandler()
            file_handler = logging.FileHandler(
                os.path.join(output_dir, 'data_formatter.log'),
                encoding='utf-8'
            )
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Set formatters
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            # Add handlers
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
        
        # Directories
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Directory paths for different data types
        self.raw_dir = os.path.join(input_dir, 'raw')
        self.processed_dir = os.path.join(input_dir, 'processed')
        self.insights_dir = os.path.join(input_dir, 'insights')
        
        # Create subdirectories if they don't exist
        for subdir in [self.raw_dir, self.processed_dir, self.insights_dir]:
            if not os.path.exists(subdir):
                os.makedirs(subdir, exist_ok=True)
        
        # Prompt templates for different models
        self.prompt_templates = {
            'gpt': {
                'facebook': "Create a Facebook ad for {brand} {product} that highlights {feature}. Use {format} format with a {tone} tone.",
                'instagram': "Design an Instagram ad for {brand} {product} that showcases {feature}. Use {format} format with a {tone} tone.",
                'general': "Create a social media ad for {brand} {product} that emphasizes {feature}. Use {format} format with a {tone} tone."
            },
            'llama': {
                'facebook': "<|system|>You are an expert ad copywriter. Create a Facebook ad with the provided details.</|system|>\n<|user|>Product: {brand} {product}\nFeature to highlight: {feature}\nFormat: {format}\nTone: {tone}\nTarget audience: {audience}</|user|>\n<|assistant|>",
                'instagram': "<|system|>You are an expert ad copywriter. Create an Instagram ad with the provided details.</|system|>\n<|user|>Product: {brand} {product}\nFeature to highlight: {feature}\nFormat: {format}\nTone: {tone}\nTarget audience: {audience}</|user|>\n<|assistant|>",
                'general': "<|system|>You are an expert ad copywriter. Create a social media ad with the provided details.</|system|>\n<|user|>Product: {brand} {product}\nFeature to highlight: {feature}\nFormat: {format}\nTone: {tone}\nTarget audience: {audience}</|user|>\n<|assistant|>"
            },
            'custom': {
                'facebook': "Create Facebook Ad:\nProduct: {brand} {product}\nHighlight: {feature}\nFormat: {format}\nTone: {tone}",
                'instagram': "Create Instagram Ad:\nProduct: {brand} {product}\nHighlight: {feature}\nFormat: {format}\nTone: {tone}",
                'general': "Create Social Media Ad:\nProduct: {brand} {product}\nHighlight: {feature}\nFormat: {format}\nTone: {tone}"
            }
        }
    
    def format_all_sources(self, model_type: str = 'gpt') -> List[Dict[str, Any]]:
        """
        Format data from all available sources for training.
        
        Args:
            model_type: Model type ('gpt', 'llama', 'custom')
            
        Returns:
            List of formatted training examples
        """
        all_examples = []
        
        try:
            # Process Facebook ads data
            facebook_examples = self._format_facebook_data(model_type)
            all_examples.extend(facebook_examples)
            self.logger.info(f"Formatted {len(facebook_examples)} examples from Facebook ads")
            
            # Process Reddit data
            reddit_examples = self._format_reddit_data(model_type)
            all_examples.extend(reddit_examples)
            self.logger.info(f"Formatted {len(reddit_examples)} examples from Reddit data")
            
            # Process AdSpy data
            adspy_examples = self._format_adspy_data(model_type)
            all_examples.extend(adspy_examples)
            self.logger.info(f"Formatted {len(adspy_examples)} examples from AdSpy data")
            
            # Process insights data
            insights_examples = self._format_insights_data(model_type)
            all_examples.extend(insights_examples)
            self.logger.info(f"Formatted {len(insights_examples)} examples from insights data")
            
            # Save all examples
            if all_examples:
                self._save_training_examples(all_examples, model_type)
            
            return all_examples
            
        except Exception as e:
            self.logger.error(f"Error formatting training data: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []
    
    def _format_facebook_data(self, model_type: str = 'gpt') -> List[Dict[str, Any]]:
        """
        Format Facebook ads data for training.
        
        Args:
            model_type: Model type ('gpt', 'llama', 'custom')
            
        Returns:
            List of formatted training examples
        """
        examples = []
        
        try:
            # Look for Facebook ads files
            fb_files = []
            
            # Check if raw directory exists
            if os.path.exists(self.raw_dir):
                # Check raw directory
                for file in os.listdir(self.raw_dir):
                    if file.startswith('fb_ads_') and file.endswith('.json'):
                        fb_files.append(os.path.join(self.raw_dir, file))
            
            # Check if processed directory exists
            if os.path.exists(self.processed_dir):
                # Check processed directory
                for file in os.listdir(self.processed_dir):
                    if file.startswith('fb_ads_') and file.endswith('.json'):
                        fb_files.append(os.path.join(self.processed_dir, file))
                    elif file.startswith('facebook_') and file.endswith('.json'):
                        fb_files.append(os.path.join(self.processed_dir, file))
            
            # Process each file
            for filepath in fb_files:
                try:
                    file_examples = self._process_facebook_file(filepath, model_type)
                    examples.extend(file_examples)
                    self.logger.info(f"Extracted {len(file_examples)} examples from {filepath}")
                except Exception as e:
                    self.logger.error(f"Error processing file {filepath}: {str(e)}")
                    
            # Process merged ads files that might contain Facebook ads
            if os.path.exists(self.processed_dir):
                merged_files = [f for f in os.listdir(self.processed_dir) 
                            if f.startswith('merged_ads_') and f.endswith('.json')]
                
                for filepath in merged_files:
                    try:
                        file_examples = self._process_merged_file(
                            os.path.join(self.processed_dir, filepath), 
                            platform='facebook',
                            model_type=model_type
                        )
                        examples.extend(file_examples)
                        self.logger.info(f"Extracted {len(file_examples)} Facebook examples from {filepath}")
                    except Exception as e:
                        self.logger.error(f"Error processing merged file {filepath}: {str(e)}")
                    
            return examples
            
        except Exception as e:
            self.logger.error(f"Error formatting Facebook data: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []
    
    def _process_facebook_file(self, filepath: str, model_type: str) -> List[Dict[str, Any]]:
        """
        Process a Facebook ads data file.
        
        Args:
            filepath: Path to Facebook ads JSON file
            model_type: Model type ('gpt', 'llama', 'custom')
            
        Returns:
            List of formatted training examples
        """
        examples = []
        
        try:
            # Load the JSON data
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract ads from the data
            ads = []
            if 'ads' in data:
                ads = data['ads']
            elif 'items' in data:
                # Handle different data structure
                ads = [item for item in data['items'] if item.get('source', '').lower() == 'facebook']
            
            # Process each ad
            for ad in ads:
                # Extract required fields
                advertiser = ad.get('page_name', '') or ad.get('advertiser_name', '')
                if not advertiser:
                    continue
                
                # Extract product/keyword from either search keyword or ad text
                product = ad.get('search_keyword', '')
                if not product and 'metadata' in ad:
                    product = ad.get('metadata', {}).get('search_keyword', '')
                
                # If no product specified, try to extract from ad content
                if not product:
                    ad_text = ad.get('ad_text', '') or ad.get('text', '')
                    headline = ad.get('headline', '')
                    if headline and len(headline.split()) <= 5:
                        product = headline
                    elif ad_text:
                        # Try to extract a likely product name (first few words after the brand name)
                        if advertiser in ad_text:
                            text_after_brand = ad_text.split(advertiser, 1)[1].strip()
                            words = text_after_brand.split()
                            product = ' '.join(words[:min(3, len(words))])
                
                # Skip if we can't determine a product
                if not product:
                    product = "product"
                
                # Extract ad format
                ad_format = ad.get('ad_format', '') or ad.get('media_type', '')
                if not ad_format:
                    if ad.get('video_urls', []):
                        ad_format = 'video'
                    elif ad.get('image_urls', []) and len(ad.get('image_urls', [])) > 1:
                        ad_format = 'carousel'
                    elif ad.get('image_urls', []):
                        ad_format = 'image'
                    else:
                        ad_format = 'text'
                
                # Extract tone based on content (simple heuristic)
                ad_text = ad.get('ad_text', '') or ad.get('text', '')
                tone = self._determine_tone(ad_text)
                
                # Extract potential feature/benefit to highlight
                feature = self._extract_feature_from_text(ad_text, product)
                
                # Format the example based on model type
                template = self.prompt_templates[model_type]['facebook']
                prompt = template.format(
                    brand=advertiser,
                    product=product,
                    feature=feature,
                    format=ad_format,
                    tone=tone,
                    audience="general"  # Default audience
                )
                
                # Construct output (response)
                output = {
                    "headline": ad.get('headline', '') or ad.get('title', ''),
                    "body_text": ad_text,
                    "cta": ad.get('cta_text', '') or ad.get('cta', ''),
                    "format": ad_format,
                    "media_urls": ad.get('image_urls', []) + ad.get('video_urls', [])
                }
                
                # Create the example
                example = {
                    "input": prompt,
                    "output": output
                }
                
                examples.append(example)
            
            return examples
            
        except Exception as e:
            self.logger.error(f"Error processing Facebook file {filepath}: {str(e)}")
            return []
    
    def _format_reddit_data(self, model_type: str = 'gpt') -> List[Dict[str, Any]]:
        """
        Format Reddit data for training.
        
        Args:
            model_type: Model type ('gpt', 'llama', 'custom')
            
        Returns:
            List of formatted training examples
        """
        examples = []
        
        try:
            # Look for Reddit data files
            reddit_files = []
            
            # Check if raw directory exists
            if os.path.exists(self.raw_dir):
                # Check raw directory
                for file in os.listdir(self.raw_dir):
                    if file.startswith('reddit_') and file.endswith('.json'):
                        reddit_files.append(os.path.join(self.raw_dir, file))
            
            # Check if processed directory exists
            if os.path.exists(self.processed_dir):
                # Check processed directory
                for file in os.listdir(self.processed_dir):
                    if file.startswith('reddit_') and file.endswith('.json'):
                        reddit_files.append(os.path.join(self.processed_dir, file))
                    elif file.startswith('merged_reddit_') and file.endswith('.json'):
                        reddit_files.append(os.path.join(self.processed_dir, file))
            
            # Process each file
            for filepath in reddit_files:
                try:
                    file_examples = self._process_reddit_file(filepath, model_type)
                    examples.extend(file_examples)
                    self.logger.info(f"Extracted {len(file_examples)} examples from {filepath}")
                except Exception as e:
                    self.logger.error(f"Error processing file {filepath}: {str(e)}")
                
            return examples
            
        except Exception as e:
            self.logger.error(f"Error formatting Reddit data: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []
    
    def _process_reddit_file(self, filepath: str, model_type: str) -> List[Dict[str, Any]]:
        """
        Process a Reddit data file.
        
        Args:
            filepath: Path to Reddit JSON file
            model_type: Model type ('gpt', 'llama', 'custom')
            
        Returns:
            List of formatted training examples
        """
        examples = []
        
        try:
            # Load the JSON data
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract posts from the data
            posts = []
            if 'posts' in data:
                posts = data['posts']
            elif 'items' in data:
                # Handle different data structure
                posts = [item for item in data['items'] if item.get('source', '').lower() == 'reddit']
            elif 'post' in data and isinstance(data['post'], dict):
                # Single post with comments
                posts = [data['post']]
            
            # Process each post with sufficient engagement
            for post in posts:
                # Skip posts with low engagement
                engagement = post.get('engagement', {})
                score = engagement.get('score', 0) if isinstance(engagement, dict) else 0
                
                if isinstance(engagement, dict):
                    upvote_ratio = engagement.get('upvote_ratio', 0)
                    comments = engagement.get('comments', 0)
                else:
                    upvote_ratio = post.get('upvote_ratio', 0)
                    comments = post.get('num_comments', 0)
                
                # Skip low engagement posts
                if score < 10 and comments < 5:
                    continue
                
                # Extract required fields
                subreddit = post.get('subreddit', '')
                title = post.get('title', '')
                text = post.get('text', '') or post.get('selftext', '')
                
                # Skip if no title or subreddit
                if not title or not subreddit:
                    continue
                
                # Determine post topic/subject
                topic = post.get('query', '')
                if not topic and 'metadata' in post:
                    topic = post.get('metadata', {}).get('query', '')
                
                # If no topic specified, use the title
                if not topic:
                    topic = title
                
                # Extract brand if present
                brand = post.get('advertiser_name', '')
                
                # Determine audience
                audience = f"r/{subreddit} subscribers"
                
                # Determine post format
                post_format = "text"
                if post.get('image_urls', []):
                    post_format = "image"
                elif post.get('video_urls', []):
                    post_format = "video"
                
                # Determine tone
                tone = "informative"
                if 'sentiment_label' in post:
                    sentiment = post['sentiment_label']
                    if sentiment == 'positive':
                        tone = "positive"
                    elif sentiment == 'negative':
                        tone = "concerned"
                else:
                    tone = self._determine_tone(text or title)
                
                # Extract feature/highlight
                feature = self._extract_feature_from_text(text or title, topic)
                
                # Format the example based on model type
                template = self.prompt_templates[model_type]['general']
                
                # Create prompt with available information
                prompt_data = {
                    'brand': brand or 'Brand',
                    'product': topic,
                    'feature': feature,
                    'format': post_format,
                    'tone': tone,
                    'audience': audience
                }
                
                prompt = template.format(**prompt_data)
                
                # Construct output
                output = {
                    "headline": title,
                    "body_text": text,
                    "format": post_format,
                    "engagement_metrics": {
                        "score": score,
                        "comments": comments,
                        "upvote_ratio": upvote_ratio
                    },
                    "subreddit": subreddit
                }
                
                # Create the example
                example = {
                    "input": prompt,
                    "output": output
                }
                
                examples.append(example)
            
            return examples
            
        except Exception as e:
            self.logger.error(f"Error processing Reddit file {filepath}: {str(e)}")
            return []
    
    def _format_adspy_data(self, model_type: str = 'gpt') -> List[Dict[str, Any]]:
        """
        Format AdSpy data for training.
        
        Args:
            model_type: Model type ('gpt', 'llama', 'custom')
            
        Returns:
            List of formatted training examples
        """
        examples = []
        
        try:
            # Look for AdSpy data files
            adspy_files = []
            
            # Check if raw directory exists
            if os.path.exists(self.raw_dir):
                # Check raw directory
                for file in os.listdir(self.raw_dir):
                    if file.startswith('adspy_') and file.endswith('.json'):
                        adspy_files.append(os.path.join(self.raw_dir, file))
            
            # Check if processed directory exists
            if os.path.exists(self.processed_dir):
                # Check processed directory
                for file in os.listdir(self.processed_dir):
                    if file.startswith('adspy_') and file.endswith('.json'):
                        adspy_files.append(os.path.join(self.processed_dir, file))
            
            # Process each file
            for filepath in adspy_files:
                try:
                    file_examples = self._process_adspy_file(filepath, model_type)
                    examples.extend(file_examples)
                    self.logger.info(f"Extracted {len(file_examples)} examples from {filepath}")
                except Exception as e:
                    self.logger.error(f"Error processing file {filepath}: {str(e)}")
                
            # Process merged ads files that might contain AdSpy data
            if os.path.exists(self.processed_dir):
                merged_files = [f for f in os.listdir(self.processed_dir) 
                            if f.startswith('merged_ads_') and f.endswith('.json')]
                
                for filepath in merged_files:
                    try:
                        file_examples = self._process_merged_file(
                            os.path.join(self.processed_dir, filepath), 
                            platform='adspy',
                            model_type=model_type
                        )
                        examples.extend(file_examples)
                        self.logger.info(f"Extracted {len(file_examples)} AdSpy examples from {filepath}")
                    except Exception as e:
                        self.logger.error(f"Error processing merged file {filepath}: {str(e)}")
                
            return examples
            
        except Exception as e:
            self.logger.error(f"Error formatting AdSpy data: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []
    
    def _process_adspy_file(self, filepath: str, model_type: str) -> List[Dict[str, Any]]:
        """
        Process an AdSpy data file.
        
        Args:
            filepath: Path to AdSpy JSON file
            model_type: Model type ('gpt', 'llama', 'custom')
            
        Returns:
            List of formatted training examples
        """
        examples = []
        
        try:
            # Load the JSON data
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract ads from the data
            ads = []
            if 'ads' in data:
                ads = data['ads']
            elif 'items' in data:
                # Handle different data structure
                ads = [item for item in data['items'] if item.get('source', '').lower() == 'adspy']
            
            # Process each ad
            for ad in ads:
                # Extract required fields
                advertiser = ad.get('advertiser_name', '')
                if not advertiser:
                    continue
                
                # Determine platform
                platform = ad.get('platform', '').lower()
                if platform not in ['facebook', 'instagram']:
                    platform = 'general'
                
                # Extract product/keyword from either search keyword or ad text
                product = ad.get('search_keyword', '')
                if not product and 'metadata' in ad:
                    product = ad.get('metadata', {}).get('search_keyword', '')
                
                # If no product specified, try to extract from ad content
                if not product:
                    ad_text = ad.get('ad_text', '') or ad.get('text', '')
                    headline = ad.get('headline', '')
                    if headline and len(headline.split()) <= 5:
                        product = headline
                    elif ad_text:
                        # Try to extract a likely product name (first few words after the brand name)
                        if advertiser in ad_text:
                            text_after_brand = ad_text.split(advertiser, 1)[1].strip()
                            words = text_after_brand.split()
                            product = ' '.join(words[:min(3, len(words))])
                
                # Skip if we can't determine a product
                if not product:
                    product = "product"
                
                # Extract ad format
                ad_format = ad.get('media_type', '')
                if not ad_format:
                    if ad.get('video_urls', []):
                        ad_format = 'video'
                    elif ad.get('image_urls', []) and len(ad.get('image_urls', [])) > 1:
                        ad_format = 'carousel'
                    elif ad.get('image_urls', []):
                        ad_format = 'image'
                    else:
                        ad_format = 'text'
                
                # Extract ad text and determine tone
                ad_text = ad.get('ad_text', '') or ad.get('text', '')
                tone = self._determine_tone(ad_text)
                
                # Extract potential feature/benefit to highlight
                feature = self._extract_feature_from_text(ad_text, product)
                
                # Extract targeting information
                targeting = ad.get('targeting', {})
                audience = "general"
                if targeting:
                    audience_parts = []
                    if 'gender' in targeting:
                        audience_parts.append(targeting['gender'])
                    if 'age' in targeting:
                        audience_parts.append(targeting['age'])
                    if 'location' in targeting:
                        audience_parts.append(f"in {targeting['location']}")
                    
                    if audience_parts:
                        audience = " ".join(audience_parts)
                
                # Format the example based on model type and platform
                template = self.prompt_templates[model_type].get(platform, self.prompt_templates[model_type]['general'])
                prompt = template.format(
                    brand=advertiser,
                    product=product,
                    feature=feature,
                    format=ad_format,
                    tone=tone,
                    audience=audience
                )
                
                # Construct output (response)
                output = {
                    "headline": ad.get('headline', ''),
                    "body_text": ad_text,
                    "cta": ad.get('cta', ''),
                    "format": ad_format,
                    "platform": platform,
                    "media_urls": ad.get('image_urls', []) + ad.get('video_urls', []),
                    "landing_page": ad.get('landing_page', ''),
                    "targeting": targeting
                }
                
                # Create the example
                example = {
                    "input": prompt,
                    "output": output
                }
                
                examples.append(example)
            
            return examples
            
        except Exception as e:
            self.logger.error(f"Error processing AdSpy file {filepath}: {str(e)}")
            return []
    
    def _process_merged_file(
        self, 
        filepath: str, 
        platform: str,
        model_type: str
    ) -> List[Dict[str, Any]]:
        """
        Process a merged data file for a specific platform.
        
        Args:
            filepath: Path to merged JSON file
            platform: Platform to filter for ('facebook', 'adspy')
            model_type: Model type ('gpt', 'llama', 'custom')
            
        Returns:
            List of formatted training examples
        """
        if platform == 'facebook':
            return self._process_facebook_file(filepath, model_type)
        elif platform == 'adspy':
            return self._process_adspy_file(filepath, model_type)
        else:
            self.logger.warning(f"Unsupported platform: {platform}")
            return []
    
    def _format_insights_data(self, model_type: str = 'gpt') -> List[Dict[str, Any]]:
        """
        Format insights data for training.
        
        Args:
            model_type: Model type ('gpt', 'llama', 'custom')
            
        Returns:
            List of formatted training examples
        """
        examples = []
        
        try:
            # Check if insights directory exists
            if not os.path.exists(self.insights_dir):
                self.logger.warning(f"Insights directory not found: {self.insights_dir}")
                return examples
            
            # Look for insights files
            insights_files = [f for f in os.listdir(self.insights_dir) 
                             if f.endswith('_insights.json') or f.endswith('_insights_20') or '_insights_' in f]
            
            # Process each file
            for file in insights_files:
                try:
                    filepath = os.path.join(self.insights_dir, file)
                    file_examples = self._process_insights_file(filepath, model_type)
                    examples.extend(file_examples)
                    self.logger.info(f"Extracted {len(file_examples)} examples from {filepath}")
                except Exception as e:
                    self.logger.error(f"Error processing file {filepath}: {str(e)}")
            
            return examples
            
        except Exception as e:
            self.logger.error(f"Error formatting insights data: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []
    
    def _process_insights_file(self, filepath: str, model_type: str) -> List[Dict[str, Any]]:
        """
        Process an insights data file.
        
        Args:
            filepath: Path to insights JSON file
            model_type: Model type ('gpt', 'llama', 'custom')
            
        Returns:
            List of formatted training examples
        """
        examples = []
        
        try:
            # Load the JSON data
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract insights type
            insights_type = data.get('type', '')
            
            # Handle different insights formats
            if insights_type == 'keyword_insights':
                examples.extend(self._format_keyword_insights(data, model_type))
            elif insights_type == 'brand_insights':
                examples.extend(self._format_brand_insights(data, model_type))
            elif insights_type == 'comprehensive_insights' or insights_type == 'minimal_insights':
                examples.extend(self._format_comprehensive_insights(data, model_type))
            elif 'insights' in data:
                # Multiple insights in a single file
                for insight in data['insights']:
                    if insight.get('type') == 'keyword_insights':
                        examples.extend(self._format_keyword_insights(insight, model_type))
                    elif insight.get('type') == 'brand_insights':
                        examples.extend(self._format_brand_insights(insight, model_type))
                    elif insight.get('type') == 'comprehensive_insights' or insight.get('type') == 'minimal_insights':
                        examples.extend(self._format_comprehensive_insights(insight, model_type))
            
            return examples
            
        except Exception as e:
            self.logger.error(f"Error processing insights file {filepath}: {str(e)}")
            return []
    
    def _format_keyword_insights(self, insights: Dict[str, Any], model_type: str) -> List[Dict[str, Any]]:
        """
        Format keyword insights into training examples.
        
        Args:
            insights: Keyword insights dictionary
            model_type: Model type ('gpt', 'llama', 'custom')
            
        Returns:
            List of formatted training examples
        """
        examples = []
        
        try:
            # Extract keyword
            keyword = insights.get('keyword', '')
            if not keyword:
                return []
            
            # Extract recommendations
            recommendations = insights.get('recommendations', {})
            if not recommendations:
                return []
            
            # Extract content insights
            content_insights = insights.get('content_insights', {})
            
            # Extract format insights
            format_insights = insights.get('format_insights', {})
            
            # Get recommended formats
            recommended_format = recommendations.get('recommended_format', 'image')
            
            # Get headline suggestions
            headline_suggestions = recommendations.get('headline_suggestions', [])
            
            # Get copy suggestions
            copy_suggestions = recommendations.get('copy_suggestions', [])
            
            # Get recommended tone
            tone = recommendations.get('recommended_tone', 'informative')
            
            # Create examples using headline and copy suggestions
            if headline_suggestions and copy_suggestions:
                # Generate examples for different platforms
                for platform in ['facebook', 'instagram', 'general']:
                    # Get template for this platform
                    template = self.prompt_templates[model_type].get(platform, self.prompt_templates[model_type]['general'])
                    
                    # Generate prompt
                    prompt = template.format(
                        brand='Brand',  # Generic brand for keyword insights
                        product=keyword,
                        feature=random.choice(recommendations.get('content_elements', ['key features'])),
                        format=recommended_format,
                        tone=tone,
                        audience="people interested in " + keyword
                    )
                    
                    # Use a headline and copy suggestion
                    headline = random.choice(headline_suggestions)
                    body_text = random.choice(copy_suggestions)
                    cta = recommendations.get('recommended_cta', 'Learn More')
                    
                    # Construct output
                    output = {
                        "headline": headline,
                        "body_text": body_text,
                        "cta": cta,
                        "format": recommended_format,
                        "platform": platform
                    }
                    
                    # Create the example
                    example = {
                        "input": prompt,
                        "output": output
                    }
                    
                    examples.append(example)
            
            return examples
            
        except Exception as e:
            self.logger.error(f"Error formatting keyword insights: {str(e)}")
            return []
    
    def _format_brand_insights(self, insights: Dict[str, Any], model_type: str) -> List[Dict[str, Any]]:
        """
        Format brand insights into training examples.
        
        Args:
            insights: Brand insights dictionary
            model_type: Model type ('gpt', 'llama', 'custom')
            
        Returns:
            List of formatted training examples
        """
        examples = []
        
        try:
            # Extract brand
            brand = insights.get('brand', '')
            if not brand:
                return []
            
            # Extract recommendations
            recommendations = insights.get('recommendations', {})
            if not recommendations:
                return []
            
            # Extract brand perception
            brand_perception = insights.get('brand_perception', {})
            
            # Extract content insights
            content_insights = insights.get('content_insights', {})
            
            # Extract format insights
            format_insights = insights.get('format_insights', {})
            
            # Get recommended format
            recommended_format = recommendations.get('recommended_format', 'image')
            
            # Get headline suggestions
            headline_suggestions = recommendations.get('headline_suggestions', [])
            
            # Get copy suggestions
            copy_suggestions = recommendations.get('copy_suggestions', [])
            
            # Get recommended tone
            tone = recommendations.get('recommended_tone', 'informative')
            
            # Extract brand attributes to use as features
            attributes = []
            if brand_perception and 'attributes' in brand_perception:
                attributes = [attr['attribute'] for attr in brand_perception.get('attributes', [])]
            
            # Use a default if no attributes found
            if not attributes:
                attributes = ['quality', 'innovation', 'performance']
            
            # Create examples using headline and copy suggestions
            if headline_suggestions and copy_suggestions:
                # Generate examples for different platforms
                for platform in ['facebook', 'instagram', 'general']:
                    # Get template for this platform
                    template = self.prompt_templates[model_type].get(platform, self.prompt_templates[model_type]['general'])
                    
                    # Generate prompt
                    prompt = template.format(
                        brand=brand,
                        product='product',  # Generic product for brand insights
                        feature=random.choice(attributes),
                        format=recommended_format,
                        tone=tone,
                        audience="general audience"
                    )
                    
                    # Use a headline and copy suggestion
                    headline = random.choice(headline_suggestions)
                    body_text = random.choice(copy_suggestions)
                    cta = recommendations.get('recommended_cta', 'Learn More')
                    
                    # Construct output
                    output = {
                        "headline": headline,
                        "body_text": body_text,
                        "cta": cta,
                        "format": recommended_format,
                        "platform": platform
                    }
                    
                    # Create the example
                    example = {
                        "input": prompt,
                        "output": output
                    }
                    
                    examples.append(example)
            
            return examples
            
        except Exception as e:
            self.logger.error(f"Error formatting brand insights: {str(e)}")
            return []
    
    def _format_comprehensive_insights(self, insights: Dict[str, Any], model_type: str) -> List[Dict[str, Any]]:
        """
        Format comprehensive insights into training examples.
        
        Args:
            insights: Comprehensive insights dictionary
            model_type: Model type ('gpt', 'llama', 'custom')
            
        Returns:
            List of formatted training examples
        """
        examples = []
        
        try:
            # Extract brand and product
            brand = insights.get('brand', '')
            product = insights.get('product', '')
            
            if not brand or not product:
                return []
            
            # Extract recommendations
            recommendations = insights.get('recommendations', {})
            if not recommendations:
                return []
            
            # Extract industry insights
            industry_insights = insights.get('industry_insights', {})
            industry = insights.get('industry', 'general')
            
            # Get recommended formats
            recommended_format = recommendations.get('recommended_format', 'image')
            
            # Consider industry-specific format suggestion
            if industry_insights and 'format_suggestion' in industry_insights:
                if random.random() < 0.5:  # 50% chance to use industry-specific format
                    format_suggestion = industry_insights['format_suggestion']
                    if 'video' in format_suggestion.lower():
                        recommended_format = 'video'
                    elif 'carousel' in format_suggestion.lower():
                        recommended_format = 'carousel'
            
            # Get headline suggestions
            headline_suggestions = recommendations.get('headline_suggestions', [])
            
            # Get copy suggestions
            copy_suggestions = recommendations.get('copy_suggestions', [])
            
            # Get recommended tone
            tone = recommendations.get('recommended_tone', 'informative')
            
            # Get content elements to use as features
            content_elements = recommendations.get('content_elements', [])
            
            # Get industry-specific recommendations
            industry_recommendations = []
            if industry_insights and 'specific_recommendations' in industry_insights:
                industry_recommendations = industry_insights['specific_recommendations']
            
            # Combine content elements with industry recommendations
            features = content_elements + industry_recommendations
            
            # Use default if no features found
            if not features:
                features = [f'{product} features', f'{brand} quality', 'customer benefits']
            
            # Create examples using headline and copy suggestions
            if headline_suggestions and copy_suggestions:
                # Generate examples for different platforms
                for platform in ['facebook', 'instagram', 'general']:
                    # Get template for this platform
                    template = self.prompt_templates[model_type].get(platform, self.prompt_templates[model_type]['general'])
                    
                    # Generate prompt
                    prompt = template.format(
                        brand=brand,
                        product=product,
                        feature=random.choice(features),
                        format=recommended_format,
                        tone=tone,
                        audience=f"people interested in {industry} products"
                    )
                    
                    # Use a headline and copy suggestion
                    headline = random.choice(headline_suggestions)
                    body_text = random.choice(copy_suggestions)
                    cta = recommendations.get('recommended_cta', 'Learn More')
                    
                    # Construct output
                    output = {
                        "headline": headline,
                        "body_text": body_text,
                        "cta": cta,
                        "format": recommended_format,
                        "platform": platform,
                        "industry": industry
                    }
                    
                    # Create the example
                    example = {
                        "input": prompt,
                        "output": output
                    }
                    
                    examples.append(example)
            
            return examples
            
        except Exception as e:
            self.logger.error(f"Error formatting comprehensive insights: {str(e)}")
            return []
    
    def _determine_tone(self, text: str) -> str:
        """
        Determine tone from text content using simple heuristics.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Tone label
        """
        if not text:
            return "informative"
            
        text = text.lower()
        
        # Check for positive tone indicators
        positive_indicators = [
            'amazing', 'awesome', 'best', 'exciting', 'love', 'perfect',
            'beautiful', 'incredible', 'happy', 'thrilled', 'enjoy'
        ]
        
        # Check for promotional tone indicators
        promotional_indicators = [
            'sale', 'discount', 'limited', 'offer', 'save', 'special',
            'exclusive', 'free', 'hurry', 'now', 'today', 'deal'
        ]
        
        # Check for informative tone indicators
        informative_indicators = [
            'how', 'why', 'what', 'when', 'learn', 'discover', 'guide',
            'tips', 'know', 'understand', 'information', 'features'
        ]
        
        # Check for persuasive tone indicators
        persuasive_indicators = [
            'you need', 'should', 'must', 'don\'t miss', 'essential',
            'proven', 'guaranteed', 'trust', 'believe', 'experts'
        ]
        
        # Count indicators for each tone
        positive_count = sum(1 for word in positive_indicators if word in text)
        promotional_count = sum(1 for word in promotional_indicators if word in text)
        informative_count = sum(1 for word in informative_indicators if word in text)
        persuasive_count = sum(1 for word in persuasive_indicators if word in text)
        
        # Determine dominant tone
        counts = {
            'positive': positive_count,
            'promotional': promotional_count,
            'informative': informative_count,
            'persuasive': persuasive_count
        }
        
        # Default to informative if counts are tied or all zero
        max_count = max(counts.values())
        if max_count == 0:
            return "informative"
            
        # Find tone with maximum count
        dominant_tones = [tone for tone, count in counts.items() if count == max_count]
        return random.choice(dominant_tones)
    
    def _extract_feature_from_text(self, text: str, product: str) -> str:
        """
        Extract a potential feature/benefit to highlight from text.
        
        Args:
            text: Text content to analyze
            product: Product name
            
        Returns:
            Feature/benefit to highlight
        """
        if not text:
            return f"{product} benefits"
            
        # Look for common benefit indicators
        benefit_indicators = [
            'benefit', 'advantage', 'feature', 'improve', 'better',
            'save', 'enhance', 'increase', 'reduce', 'boost',
            'easy', 'powerful', 'efficient', 'effective', 'innovative'
        ]
        
        # Check for sentences containing these indicators
        for indicator in benefit_indicators:
            # Find sentences containing the indicator
            if indicator in text.lower():
                # Simple sentence extraction (very basic)
                sentences = text.replace('!', '.').replace('?', '.').split('.')
                for sentence in sentences:
                    if indicator in sentence.lower():
                        # Return a simplified version of the sentence
                        words = sentence.strip().split()
                        if len(words) > 10:
                            # Truncate long sentences
                            return ' '.join(words[:10])
                        return sentence.strip()
        
        # If no benefit found, return a generic feature
        return f"{product} quality and features"
    
    def _save_training_examples(self, examples: List[Dict[str, Any]], model_type: str) -> None:
        """
        Save training examples to output files.
        
        Args:
            examples: List of training examples
            model_type: Model type ('gpt', 'llama', 'custom')
        """
        try:
            # Create timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save all examples to a single file
            all_examples_path = os.path.join(
                self.output_dir,
                f"{model_type}_training_examples_{timestamp}.json"
            )
            
            with open(all_examples_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "model_type": model_type,
                        "example_count": len(examples),
                        "timestamp": datetime.now().isoformat()
                    },
                    "examples": examples
                }, f, indent=2)
            
            self.logger.info(f"Saved {len(examples)} training examples to {all_examples_path}")
            
            # Save training and validation split (80/20)
            random.shuffle(examples)
            split_idx = int(len(examples) * 0.8)
            
            training_examples = examples[:split_idx]
            validation_examples = examples[split_idx:]
            
            # Save training set
            train_path = os.path.join(
                self.output_dir,
                f"{model_type}_training_set_{timestamp}.json"
            )
            
            with open(train_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "model_type": model_type,
                        "example_count": len(training_examples),
                        "set_type": "training",
                        "timestamp": datetime.now().isoformat()
                    },
                    "examples": training_examples
                }, f, indent=2)
            
            self.logger.info(f"Saved {len(training_examples)} training examples to {train_path}")
            
            # Save validation set
            val_path = os.path.join(
                self.output_dir,
                f"{model_type}_validation_set_{timestamp}.json"
            )
            
            with open(val_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "model_type": model_type,
                        "example_count": len(validation_examples),
                        "set_type": "validation",
                        "timestamp": datetime.now().isoformat()
                    },
                    "examples": validation_examples
                }, f, indent=2)
            
            self.logger.info(f"Saved {len(validation_examples)} validation examples to {val_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving training examples: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())


if __name__ == "__main__":
    # Example usage
    formatter = DataFormatter(
        input_dir='data',
        output_dir='data/training'
    )
    
    # Format data for different model types
    gpt_examples = formatter.format_all_sources(model_type='gpt')
    print(f"Generated {len(gpt_examples)} training examples for GPT model")
    
    llama_examples = formatter.format_all_sources(model_type='llama')
    print(f"Generated {len(llama_examples)} training examples for Llama model")