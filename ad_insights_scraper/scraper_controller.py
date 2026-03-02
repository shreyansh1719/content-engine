"""
Controller for managing multiple ad scrapers and orchestrating data collection
"""
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

class ScraperController:
    def __init__(self, output_dir='data'):
        """Initialize scraper controller with output directory configuration"""
        self.output_dir = output_dir
        self.logger = logging.getLogger('ScraperController')
        
        # Create directory structure
        os.makedirs(os.path.join(output_dir, 'raw'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'processed'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'insights'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'training'), exist_ok=True)
        
        # Cache for AdSpy credentials
        self.adspy_username = None
        self.adspy_password = None
    
    def set_adspy_credentials(self, username: str, password: str) -> None:
        """Store AdSpy credentials for later use"""
        self.adspy_username = username
        self.adspy_password = password
    
    def run_facebook_scraper(self, keywords: List[str], countries: List[str] = ['US'], 
                            max_ads: int = 100) -> List[Dict[str, Any]]:
        """Run Facebook Ads Library scraper for specified keywords"""
        from ad_insights_scraper.scrapers.facebook_scraper import FacebookAdsScraper
        
        scraper = FacebookAdsScraper(
            output_dir=self.output_dir,
            use_proxies=False,
            headless=True
        )
        
        try:
            ads = []
            for keyword in keywords:
                self.logger.info(f"Scraping Facebook ads for keyword: {keyword}")
                
                # Run scraper for single keyword
                keyword_ads = scraper.scrape_ads_library(
                    keywords=[keyword],
                    countries=countries,
                    max_ads_per_keyword=max_ads
                )
                
                ads.extend(keyword_ads)
                self.logger.info(f"Collected {len(keyword_ads)} Facebook ads for '{keyword}'")
            
            return ads
        finally:
            scraper.quit()
    
    def run_reddit_scraper(self, keywords: List[str], subreddits: Optional[List[str]] = None,
                          limit: int = 100) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Run Reddit scraper for specified keywords and subreddits"""
        from ad_insights_scraper.scrapers.reddit_scraper import RedditScraper
        
        scraper = RedditScraper(output_dir=self.output_dir)
        
        # Find relevant subreddits if none provided
        all_subreddits = []
        if not subreddits:
            self.logger.info("Finding relevant subreddits for keywords")
            all_subreddits = scraper.find_relevant_subreddits(keywords)
            self.logger.info(f"Found {len(all_subreddits)} relevant subreddits")
        else:
            all_subreddits = subreddits
        
        # Collect posts for each keyword
        all_posts = []
        for keyword in keywords:
            self.logger.info(f"Searching Reddit for keyword: {keyword}")
            
            posts = scraper.search_posts(
                query=keyword,
                subreddits=all_subreddits,
                limit=limit
            )
            
            all_posts.extend(posts)
            self.logger.info(f"Collected {len(posts)} Reddit posts for '{keyword}'")
        
        # Collect comments from posts
        if all_posts:
            post_ids = [post['id'] for post in all_posts]
            self.logger.info(f"Collecting comments from {len(post_ids)} Reddit posts")
            
            comments = scraper.scrape_comments(post_ids=post_ids)
            self.logger.info(f"Collected {len(comments)} Reddit comments")
            
            return all_posts, comments
        else:
            return [], []
    
    def run_adspy_scraper(self, keywords: List[str], 
                         platforms: List[str] = ['facebook', 'instagram'],
                         limit: int = 100) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Run AdSpy scraper for specified keywords"""
        from ad_insights_scraper.scrapers.adspy_scraper import AdSpyScraper
        
        scraper = AdSpyScraper(
            username=self.adspy_username,
            password=self.adspy_password,
            output_dir=self.output_dir,
            use_proxies=False,
            headless=True
        )
        
        try:
            self.logger.info(f"Scraping AdSpy for keywords: {keywords}")
            
            # Run scraper
            ads = scraper.scrape_ads(
                keywords=keywords,
                platforms=platforms,
                limit=limit
            )
            
            self.logger.info(f"Collected {len(ads)} ads from AdSpy")
            
            # Extract insights
            insights = scraper.extract_ad_insights(ads)
            self.logger.info(f"Generated insights for {len(insights)} advertisers")
            
            return ads, insights
        finally:
            scraper.quit()
    
    def process_all_data(self) -> Dict[str, int]:
        """Process and normalize all collected data"""
        from .processors.data_processor import DataProcessor
        
        self.logger.info("Processing all collected data")
        
        processor = DataProcessor(
            input_dir=os.path.join(self.output_dir, 'raw'),
            output_dir=os.path.join(self.output_dir, 'processed')
        )
        
        # Process and normalize all data
        results = processor.process_all()
        processor.clean_data()
        processor.merge_sources()
        processor.merge_all_processed()
        
        self.logger.info(f"Processed data: {results}")
        return results
    
    def extract_insights(self) -> List[Dict[str, Any]]:
        """Extract insights from processed data"""
        from .processors.insight_extractor import InsightExtractor
        
        self.logger.info("Extracting insights from processed data")
        
        extractor = InsightExtractor(
            input_dir=os.path.join(self.output_dir, 'processed'),
            output_dir=os.path.join(self.output_dir, 'insights')
        )
        
        # Extract insights
        insights = extractor.extract_all_insights()
        self.logger.info(f"Extracted {len(insights)} insights")
        
        return insights