import os
import json
import logging
import traceback
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv

# Import various data sources
from adspy_scraper import AdSpyScraper
from ad_generator.social_media import search_social_media_ads

class ComprehensiveDataCollector:
    """
    Advanced data collection system for ad generation
    Integrates multiple data sources and provides robust processing
    """
    def __init__(self, 
                 output_dir: str = 'data', 
                 log_level: int = logging.INFO):
        """
        Initialize the comprehensive data collector
        
        Args:
            output_dir: Base directory for storing collected data
            log_level: Logging verbosity level
        """
        # Setup logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(os.path.join(output_dir, 'data_collection.log'), encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Load environment variables
        load_dotenv()
        
        # Setup output directories
        self.output_dir = output_dir
        self._setup_directories()
    
    def _setup_directories(self):
        """
        Create necessary directories for data collection
        """
        directories = [
            os.path.join(self.output_dir, 'training'),
            os.path.join(self.output_dir, 'processed'),
            os.path.join(self.output_dir, 'raw')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _save_data(self, 
                   data: List[Dict], 
                   filename: str, 
                   subdir: str = 'training'):
        """
        Save collected data to JSON file
        
        Args:
            data: List of dictionaries to save
            filename: Output filename
            subdir: Subdirectory to save in
        """
        try:
            filepath = os.path.join(self.output_dir, subdir, filename)
            
            # Ensure data is unique
            unique_data = self._deduplicate_data(data)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(unique_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(unique_data)} unique items to {filepath}")
            return unique_data
        
        except Exception as e:
            self.logger.error(f"Error saving {filename}: {e}")
            return []
    
    def _deduplicate_data(self, data: List[Dict]) -> List[Dict]:
        """
        Remove duplicate entries based on content
        
        Args:
            data: List of dictionaries to deduplicate
        
        Returns:
            List of unique dictionaries
        """
        seen = set()
        unique_data = []
        
        for item in data:
            # Convert dictionary to a hashable representation
            item_hash = json.dumps(item, sort_keys=True)
            
            if item_hash not in seen:
                seen.add(item_hash)
                unique_data.append(item)
        
        return unique_data
    
    def collect_social_media_insights(
        self, 
        products: Optional[List[str]] = None,
        industries: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Collect social media insights for multiple products
        
        Args:
            products: List of products to analyze
            industries: List of industries to explore
        
        Returns:
            List of social media insights
        """
        try:
            # Default products if not provided
            products = products or [
                'iPhone 15', 'Nike Running Shoes', 
                'Tesla Model 3', 'MacBook Pro',
                'Samsung Galaxy', 'Adidas Ultraboost',
                'Dell XPS', 'Bose Headphones'
            ]
            
            # Default industries if not provided
            industries = industries or [
                'technology', 'fashion', 'automotive', 
                'electronics', 'sports', 'luxury'
            ]
            
            social_insights = []
            
            # Collect insights with varied industry contexts
            for product in products:
                # Try multiple industry contexts
                for industry in industries:
                    try:
                        # Extract brand name (first word)
                        brand_name = product.split()[0]
                        
                        # Get social media insights
                        insights = search_social_media_ads(
                            product=product, 
                            brand_name=brand_name, 
                            industry=industry
                        )
                        
                        # Enrich insights with additional metadata
                        insights['source_product'] = product
                        insights['source_industry'] = industry
                        
                        social_insights.append(insights)
                    
                    except Exception as industry_error:
                        self.logger.warning(f"Error collecting insights for {product} in {industry}: {industry_error}")
            
            # Save raw social media insights
            return self._save_data(social_insights, 'social_media_insights.json')
        
        except Exception as e:
            self.logger.error(f"Social media insights collection error: {e}")
            return []
    
    def collect_adspy_ads(
        self, 
        keywords: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None,
        min_engagement: int = 500
    ) -> List[Dict]:
        """
        Collect ads from AdSpy with comprehensive filtering
        
        Args:
            keywords: List of search keywords
            platforms: Social media platforms to search
            min_engagement: Minimum engagement threshold
        
        Returns:
            List of collected ad dictionaries
        """
        try:
            # Get AdSpy credentials
            username = os.getenv('ADSPY_USERNAME')
            password = os.getenv('ADSPY_PASSWORD')
            
            if not username or not password:
                self.logger.error("AdSpy credentials not found!")
                return []
            
            # Default keywords
            keywords = keywords or [
                'fitness', 'technology', 'ecommerce', 
                'fashion', 'digital marketing', 
                'health', 'beauty', 'electronics',
                'software', 'automotive', 'luxury'
            ]
            
            # Default platforms
            platforms = platforms or ['facebook', 'instagram']
            
            # Initialize scraper
            scraper = AdSpyScraper(username, password, headless=True)
            
            # Collect ads
            all_adspy_ads = []
            
            try:
                # Login to AdSpy
                if not scraper.login():
                    self.logger.error("AdSpy login failed")
                    return []
                
                # Scrape ads across keywords and platforms
                for keyword in keywords:
                    for platform in platforms:
                        scraper.paginate_and_scrape(
                            keyword=keyword, 
                            platform=platform, 
                            min_engagement=min_engagement,
                            max_pages=3
                        )
                        all_adspy_ads.extend(scraper.scraped_ads)
            
            except Exception as scrape_error:
                self.logger.error(f"AdSpy scraping error: {scrape_error}")
            
            finally:
                # Always close the browser
                scraper.quit()
            
            # Save and return processed ads
            return self._save_data(all_adspy_ads, 'adspy_ads.json')
        
        except Exception as e:
            self.logger.error(f"Comprehensive AdSpy collection error: {e}")
            return []
    
    def prepare_training_data(self) -> List[Dict]:
        """
        Consolidate and preprocess collected data for LLM training
        
        Returns:
            List of training data entries
        """
        try:
            # Collect data from multiple sources
            social_insights = self.collect_social_media_insights()
            adspy_ads = self.collect_adspy_ads()
            
            # Create comprehensive training dataset
            training_data = []
            
            # Process social media insights
            for insight in social_insights:
                # Variation in input prompts
                input_variations = [
                    f"Create an ad for a {insight.get('recommended_format', 'product')}",
                    f"Design an advertisement highlighting {', '.join(insight.get('key_elements', [])[:2])}",
                    f"Craft a {insight.get('source_industry', 'technology')} ad focusing on key trends"
                ]
                
                for input_prompt in input_variations:
                    training_entry = {
                        "input": input_prompt,
                        "output": {
                            "headline": f"{insight.get('recommended_format', 'Product Showcase')} - {' '.join(insight.get('trending_keywords', [])[:2]).title()}",
                            "description": f"Key insights: {', '.join(insight.get('key_elements', [])[:3])}",
                            "trending_keywords": insight.get('trending_keywords', []),
                            "visual_focus": insight.get('visual_focus', 'product details'),
                            "text_placement": insight.get('text_placement', 'centered'),
                            "text_style": insight.get('text_style', 'professional'),
                            "source_product": insight.get('source_product', 'Unknown'),
                            "source_industry": insight.get('source_industry', 'General')
                        }
                    }
                    training_data.append(training_entry)
            
            # Process AdSpy ads
            for ad in adspy_ads:
                if not ad.get('title') or not ad.get('description'):
                    continue
                
                training_entry = {
                    "input": f"Create an ad for {ad.get('title', 'product')}",
                    "output": {
                        "headline": ad.get('title', ''),
                        "description": ad.get('description', ''),
                        "engagement": ad.get('engagement', {}),
                        "image_url": ad.get('image_url', ''),
                        "ad_link": ad.get('ad_link', '')
                    }
                }
                training_data.append(training_entry)
            
            # Save processed training data
            return self._save_data(
                training_data, 
                'ad_training_data.json', 
                subdir='processed'
            )
        
        except Exception as e:
            self.logger.error(f"Training data preparation error: {e}")
            traceback.print_exc()
            return []

def main():
    """
    Main function to run comprehensive data collection
    """
    collector = ComprehensiveDataCollector()
    collector.prepare_training_data()

if __name__ == "__main__":
    main()