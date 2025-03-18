"""
Ad metrics analysis system for identifying high-performing patterns
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
import random
from datetime import datetime

class AdMetricsAnalyzer:
    """
    Analyze ad metrics to determine high-performing patterns and styles.
    Can be extended to use real data from Facebook Marketplace scraper.
    """
    
    def __init__(self, data_dir: str = 'data/processed'):
        """
        Initialize with data directory.
        
        Args:
            data_dir: Directory with saved ad metrics
        """
        self.data_dir = data_dir
        self.setup_logging()
        
        # Load any existing metrics data
        self.metrics_data = self._load_metrics_data()
        
        # Pre-defined patterns based on industry research
        self.default_patterns = self._load_default_patterns()
    
    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _load_metrics_data(self) -> Dict[str, Any]:
        """
        Load metrics data from saved files.
        
        Returns:
            Dictionary of metrics data
        """
        metrics_data = {}
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Look for metrics data files
            metrics_files = [f for f in os.listdir(self.data_dir) if f.endswith('.json') and 'metrics' in f]
            
            if metrics_files:
                # Use the most recent file
                latest_file = max(metrics_files, key=lambda f: os.path.getmtime(os.path.join(self.data_dir, f)))
                
                # Load data
                with open(os.path.join(self.data_dir, latest_file), 'r', encoding='utf-8') as f:
                    metrics_data = json.load(f)
                
                self.logger.info(f"Loaded metrics data from {latest_file}")
            else:
                self.logger.info("No metrics data files found, using default patterns")
        except Exception as e:
            self.logger.warning(f"Error loading metrics data: {str(e)}")
        
        return metrics_data
    
    def _load_default_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Load default patterns based on industry research.
        
        Returns:
            Dictionary of default patterns by industry
        """
        return {
            "Technology": {
                "headline_patterns": [
                    "INNOVATION [VERB]",
                    "EXPERIENCE THE [ADJECTIVE]",
                    "THE FUTURE OF [NOUN]",
                    "[PRODUCT] REIMAGINED"
                ],
                "subheadline_patterns": [
                    "Discover the next generation of [product] technology",
                    "Experience [feature] like never before",
                    "[Feature] that adapts to your lifestyle"
                ],
                "cta_patterns": [
                    "UPGRADE NOW",
                    "EXPERIENCE [PRODUCT]",
                    "DISCOVER MORE",
                    "SHOP TODAY"
                ],
                "copy_patterns": "Use short, impactful headlines with technology-focused terminology. Emphasize innovation, performance, and cutting-edge features. Subheadlines should explain a key benefit. CTAs should be direct and suggest an immediate upgrade or discovery.",
                "visual_patterns": "Product-centered with clean backgrounds. Focus on product details with subtle highlights on key features. Use cool color tones (blue, teal, silver).",
                "text_placement": "centered",
                "typography": "modern sans-serif"
            },
            "Fashion": {
                "headline_patterns": [
                    "DEFINE YOUR [NOUN]",
                    "ELEVATE YOUR [NOUN]",
                    "[ADJECTIVE] STYLE",
                    "THE [ADJECTIVE] COLLECTION"
                ],
                "subheadline_patterns": [
                    "Designed for those who demand excellence",
                    "Crafted with attention to every detail",
                    "Where comfort meets unparalleled style"
                ],
                "cta_patterns": [
                    "SHOP THE COLLECTION",
                    "EXPLORE NOW",
                    "FIND YOUR STYLE",
                    "DISCOVER MORE"
                ],
                "copy_patterns": "Use aspirational, lifestyle-focused headlines that evoke emotion. Emphasize exclusivity, craftsmanship, and style. Subheadlines should connect to identity and self-expression. CTAs should invite exploration.",
                "visual_patterns": "Lifestyle imagery with models in aspirational settings. Focus on product in context with attention to styling details.",
                "text_placement": "left or bottom",
                "typography": "elegant serif or minimal sans-serif"
            },
            "Beauty": {
                "headline_patterns": [
                    "REVEAL YOUR [NOUN]",
                    "TRANSFORM YOUR [NOUN]",
                    "[ADJECTIVE] RESULTS",
                    "THE SECRET TO [NOUN]"
                ],
                "subheadline_patterns": [
                    "Clinically proven to deliver visible results",
                    "The advanced formula your skin deserves",
                    "Discover what [product] can do for you"
                ],
                "cta_patterns": [
                    "TRANSFORM NOW",
                    "REVEAL YOUR [NOUN]",
                    "TRY IT TODAY",
                    "SHOP NOW"
                ],
                "copy_patterns": "Use transformative, results-focused headlines that promise benefits. Emphasize scientific innovation, visible improvements, and confidence. Subheadlines should mention clinical validation or premium ingredients. CTAs should suggest personal transformation.",
                "visual_patterns": "Clean, bright imagery with before/after suggestion. Focus on product with ingredient visualization or results demonstration.",
                "text_placement": "right or bottom",
                "typography": "elegant sans-serif"
            },
            "Automotive": {
                "headline_patterns": [
                    "ENGINEERED FOR [NOUN]",
                    "DOMINATE THE [NOUN]",
                    "PERFORMANCE [VERB]",
                    "THE [ADJECTIVE] DRIVE"
                ],
                "subheadline_patterns": [
                    "Experience power and precision like never before",
                    "Where luxury meets uncompromising performance",
                    "Redefining what's possible on the road"
                ],
                "cta_patterns": [
                    "BOOK A TEST DRIVE",
                    "EXPLORE FEATURES",
                    "CONFIGURE YOURS",
                    "LEARN MORE"
                ],
                "copy_patterns": "Use powerful, performance-focused headlines that convey engineering excellence. Emphasize power, innovation, and driving experience. Subheadlines should highlight luxury and technical achievements. CTAs should invite interaction with the product.",
                "visual_patterns": "Dynamic vehicle imagery with dramatic lighting. Focus on distinctive angles that highlight design elements. Use dark backgrounds with high contrast.",
                "text_placement": "bottom with logo at top",
                "typography": "modern technical sans-serif"
            },
            "Luxury": {
                "headline_patterns": [
                    "CRAFTED FOR [NOUN]",
                    "THE ART OF [NOUN]",
                    "[ADJECTIVE] EXCELLENCE",
                    "TIMELESS [NOUN]"
                ],
                "subheadline_patterns": [
                    "A legacy of craftsmanship and uncompromising quality",
                    "Experience the difference that excellence makes",
                    "For those who appreciate the exceptional"
                ],
                "cta_patterns": [
                    "DISCOVER THE COLLECTION",
                    "EXPERIENCE [PRODUCT]",
                    "BOOK A CONSULTATION",
                    "LEARN MORE"
                ],
                "copy_patterns": "Use sophisticated, understated headlines that suggest exclusivity. Emphasize heritage, craftsmanship, and timeless quality. Subheadlines should connect to legacy and exceptional standards. CTAs should be elegant invitations rather than direct commands.",
                "visual_patterns": "Minimalist, elegant imagery with perfect lighting. Focus on exceptional details and craftsmanship. Use dark or neutral backgrounds with subtle lighting.",
                "text_placement": "centered or bottom with logo at top",
                "typography": "elegant serif"
            }
        }
    
    def get_recommendations_for_industry(self, industry: str, brand_level: str = None) -> Dict[str, Any]:
        """
        Get recommendations for a specific industry and brand level.
        
        Args:
            industry: Industry category
            brand_level: Brand level (luxury, premium, etc.)
            
        Returns:
            Dictionary of recommendations
        """
        # Normalize industry
        industry_lower = industry.lower()
        
        # Match to closest default industry
        matched_industry = None
        if 'tech' in industry_lower or 'phone' in industry_lower or 'electronics' in industry_lower:
            matched_industry = "Technology"
        elif 'fashion' in industry_lower or 'cloth' in industry_lower or 'apparel' in industry_lower or 'shoe' in industry_lower:
            matched_industry = "Fashion"
        elif 'beauty' in industry_lower or 'cosmetic' in industry_lower or 'skin' in industry_lower:
            matched_industry = "Beauty"
        elif 'auto' in industry_lower or 'car' in industry_lower or 'vehicle' in industry_lower:
            matched_industry = "Automotive"
        elif 'luxury' in industry_lower or 'premium' in industry_lower or 'jewelry' in industry_lower or 'watch' in industry_lower:
            matched_industry = "Luxury"
        
        # If we have real metrics data for this industry, use it
        if self.metrics_data and industry in self.metrics_data:
            industry_metrics = self.metrics_data[industry]
            
            # Filter by brand level if available
            if brand_level and 'brand_levels' in industry_metrics and brand_level in industry_metrics['brand_levels']:
                return industry_metrics['brand_levels'][brand_level]
            
            # Otherwise return general industry metrics
            return industry_metrics
        
        # If we don't have real metrics, use default patterns
        elif matched_industry and matched_industry in self.default_patterns:
            recommendations = self.default_patterns[matched_industry]
            
            # Customize based on brand level
            if brand_level:
                brand_level_lower = brand_level.lower()
                
                if 'luxury' in brand_level_lower or 'premium' in brand_level_lower:
                    # Enhance for luxury/premium
                    recommendations['typography'] = 'elegant serif'
                    recommendations['text_placement'] = 'centered'
                
                elif 'budget' in brand_level_lower or 'mass' in brand_level_lower:
                    # Adjust for mass market
                    recommendations['typography'] = 'bold sans-serif'
                    recommendations['copy_patterns'] = recommendations['copy_patterns'].replace('exclusivity', 'value').replace('craftsmanship', 'quality')
            
            return recommendations
        
        # If no specific match, use generic recommendations
        return {
            "headline_patterns": [
                "DISCOVER [PRODUCT]",
                "EXPERIENCE [ADJECTIVE] [NOUN]",
                "INTRODUCING [PRODUCT]",
                "THE [ADJECTIVE] CHOICE"
            ],
            "subheadline_patterns": [
                "Quality and performance you can trust",
                "Designed with you in mind",
                "Experience the difference"
            ],
            "cta_patterns": [
                "LEARN MORE",
                "SHOP NOW",
                "DISCOVER TODAY",
                "FIND OUT MORE"
            ],
            "copy_patterns": "Use clear, benefit-focused headlines. Emphasize quality, value, and user benefits. Subheadlines should explain a key advantage. CTAs should be direct and action-oriented.",
            "visual_patterns": "Clean product photography with professional lighting. Focus on product with context appropriate to use case.",
            "text_placement": "centered",
            "typography": "modern sans-serif"
        }
    
    def get_headline_suggestion(self, industry: str, product: str, brand_name: str = None) -> str:
        """
        Get headline suggestion based on high-performing patterns.
        
        Args:
            industry: Industry category
            product: Product name/description
            brand_name: Brand name
            
        Returns:
            Suggested headline
        """
        # Get recommendations for this industry
        recommendations = self.get_recommendations_for_industry(industry)
        
        # Get headline patterns
        headline_patterns = recommendations.get('headline_patterns', [
            "DISCOVER [PRODUCT]",
            "EXPERIENCE THE [ADJECTIVE]",
            "INTRODUCING [PRODUCT]",
            "THE [ADJECTIVE] CHOICE"
        ])
        
        # List of powerful adjectives
        adjectives = [
            "ULTIMATE", "EXCEPTIONAL", "PREMIUM", "ADVANCED", "INNOVATIVE",
            "POWERFUL", "EXCLUSIVE", "SUPERIOR", "ESSENTIAL", "REVOLUTIONARY"
        ]
        
        # List of powerful nouns related to benefits
        nouns = [
            "PERFORMANCE", "QUALITY", "EXPERIENCE", "INNOVATION", "EXCELLENCE",
            "STYLE", "COMFORT", "FUTURE", "LUXURY", "PRECISION"
        ]
        
        # List of powerful verbs
        verbs = [
            "REDEFINED", "REIMAGINED", "ELEVATED", "UNLEASHED", "TRANSFORMED",
            "PERFECTED", "EVOLVED", "MASTERED", "ENGINEERED", "CRAFTED"
        ]
        
        # Select random pattern
        pattern = random.choice(headline_patterns)
        
        # Replace placeholders
        headline = pattern.replace("[PRODUCT]", product.upper())
        headline = headline.replace("[ADJECTIVE]", random.choice(adjectives))
        headline = headline.replace("[NOUN]", random.choice(nouns))
        headline = headline.replace("[VERB]", random.choice(verbs))
        
        # Include brand if provided and not already in headline
        if brand_name and brand_name.upper() not in headline:
            if random.random() < 0.3:  # 30% chance to prepend brand
                headline = f"{brand_name.upper()} {headline}"
        
        return headline
    
    def get_cta_suggestion(self, industry: str) -> str:
        """
        Get CTA suggestion based on high-performing patterns.
        
        Args:
            industry: Industry category
            
        Returns:
            Suggested CTA
        """
        # Get recommendations for this industry
        recommendations = self.get_recommendations_for_industry(industry)
        
        # Get CTA patterns
        cta_patterns = recommendations.get('cta_patterns', [
            "LEARN MORE",
            "SHOP NOW",
            "DISCOVER TODAY",
            "FIND OUT MORE"
        ])
        
        # Select random pattern
        return random.choice(cta_patterns)
    
    def analyze_marketplace_data(self, data_file: str) -> Dict[str, Any]:
        """
        Analyze Facebook Marketplace data to extract high-performing patterns.
        
        Args:
            data_file: Path to marketplace data file
            
        Returns:
            Dictionary of analyzed metrics
        """
        try:
            # Load data file
            with open(data_file, 'r', encoding='utf-8') as f:
                if data_file.endswith('.json'):
                    data = json.load(f)
                else:
                    # Handle CSV or other formats
                    self.logger.warning("Unsupported file format")
                    return {}
            
            # Process data to extract patterns
            # This would be a comprehensive analysis of ad elements and performance
            # For now, we'll return a placeholder
            
            results = {
                "analyzed_date": datetime.now().isoformat(),
                "source_file": data_file,
                "total_ads": len(data),
                "industries": {},
                "global_patterns": {
                    "headline_avg_length": 5.2,  # Words
                    "high_engagement_factors": [
                        "Clear product visualization",
                        "Professional lighting",
                        "Minimal text overlay",
                        "Consistent brand elements"
                    ]
                }
            }
            
            # Save results
            self._save_analysis_results(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing marketplace data: {str(e)}")
            return {}
    
    def _save_analysis_results(self, results: Dict[str, Any]) -> None:
        """
        Save analysis results to file.
        
        Args:
            results: Analysis results
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ad_metrics_{timestamp}.json"
            
            # Save to file
            with open(os.path.join(self.data_dir, filename), 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            
            self.logger.info(f"Saved analysis results to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving analysis results: {str(e)}")
    
    def process_marketplace_scraper_data(self, market_data_folder: str) -> Dict[str, Any]:
        """
        Process data collected from Facebook Marketplace scraper.
        
        Args:
            market_data_folder: Folder containing marketplace scraped data
            
        Returns:
            Processed metrics data
        """
        try:
            # Find all JSON files in the folder
            json_files = [f for f in os.listdir(market_data_folder) if f.endswith('.json')]
            
            if not json_files:
                self.logger.warning(f"No JSON files found in {market_data_folder}")
                return {}
            
            combined_data = []
            
            # Process each file
            for json_file in json_files:
                file_path = os.path.join(market_data_folder, json_file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    if isinstance(data, list):
                        combined_data.extend(data)
                    elif isinstance(data, dict):
                        # Handle dictionary format
                        if 'ads' in data and isinstance(data['ads'], list):
                            combined_data.extend(data['ads'])
                        else:
                            combined_data.append(data)
                            
                except Exception as e:
                    self.logger.error(f"Error processing {json_file}: {str(e)}")
            
            # Now analyze the combined data
            if not combined_data:
                return {}
            
            # Extract patterns and metrics
            metrics = {
                "analyzed_date": datetime.now().isoformat(),
                "total_ads": len(combined_data),
                "industries": {},
                "global_patterns": {
                    "text_length": {},
                    "image_features": {},
                    "pricing_strategies": {},
                    "high_engagement_factors": []
                }
            }
            
            # Calculate various metrics
            # This would be a comprehensive analysis based on the actual structure of your scraped data
            # The implementation depends on the specific structure of your Facebook Marketplace scraper output
            
            # Save the metrics
            self._save_analysis_results(metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error processing marketplace data: {str(e)}")
            return {}