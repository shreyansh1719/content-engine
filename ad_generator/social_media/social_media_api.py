"""
Social media integration module that provides real-time insights for ad generation.
Uses Reddit API to analyze trends and preferences for more effective ads.
"""
import os
import logging
import random
import re
import time
from typing import Dict, List, Optional
from collections import Counter
from datetime import datetime, timedelta
import praw
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)

# Set up logger
logger = setup_logging()

# Default ad insights by industry (fallback if API fails)
DEFAULT_INSIGHTS = {
    "Technology": {
        "recommended_format": "Product-focused with clean background",
        "text_placement": "centered",
        "text_style": "minimal",
        "key_elements": ["product close-up", "key feature highlight", "brand name"],
        "visual_focus": "product details",
        "color_scheme": "blue and white gradient"
    },
    "Fashion": {
        "recommended_format": "Lifestyle with model",
        "text_placement": "bottom",
        "text_style": "elegant",
        "key_elements": ["attractive model", "product in use", "aspirational setting"],
        "visual_focus": "product in context",
        "color_scheme": "neutral with accent colors"
    },
    "Food": {
        "recommended_format": "Close-up with rich colors",
        "text_placement": "top",
        "text_style": "bold",
        "key_elements": ["mouth-watering visuals", "steam or movement", "perfect styling"],
        "visual_focus": "texture and details",
        "color_scheme": "warm and vibrant colors"
    },
    "Automotive": {
        "recommended_format": "Dramatic angle with motion suggestion",
        "text_placement": "bottom",
        "text_style": "bold",
        "key_elements": ["dynamic angle", "showroom finish", "dramatic lighting"],
        "visual_focus": "vehicle profile",
        "color_scheme": "dark with bright accents"
    },
    "Beauty": {
        "recommended_format": "Clean and elegant with model",
        "text_placement": "side",
        "text_style": "elegant",
        "key_elements": ["before/after suggestion", "product close-up", "skin texture"],
        "visual_focus": "transformation results",
        "color_scheme": "soft pastels or monochrome"
    },
    "Luxury": {
        "recommended_format": "Minimalist with premium feel",
        "text_placement": "centered",
        "text_style": "elegant",
        "key_elements": ["subtle luxury cues", "perfect craftsmanship", "exclusive atmosphere"],
        "visual_focus": "product details",
        "color_scheme": "black, gold, and white"
    },
    "Fitness": {
        "recommended_format": "Action-oriented with results",
        "text_placement": "side",
        "text_style": "bold",
        "key_elements": ["active lifestyle", "transformation suggestion", "energy"],
        "visual_focus": "people in motion",
        "color_scheme": "energetic contrasts"
    },
    "Home": {
        "recommended_format": "Lifestyle in context",
        "text_placement": "bottom",
        "text_style": "minimal",
        "key_elements": ["room setting", "lifestyle integration", "comfort cues"],
        "visual_focus": "product in home environment",
        "color_scheme": "warm neutrals"
    }
}

# Default fallback insights
DEFAULT_FALLBACK = {
    "recommended_format": "Product-centered with clean background",
    "text_placement": "centered",
    "text_style": "minimal",
    "key_elements": ["product close-up", "brand elements", "quality suggestion"],
    "visual_focus": "product details",
    "color_scheme": "blue gradient"
}

# Industry to subreddit mapping
INDUSTRY_SUBREDDITS = {
    "Technology": ["technology", "gadgets", "tech", "android", "apple", "iphone"],
    "Fashion": ["malefashionadvice", "femalefashionadvice", "streetwear", "sneakers"],
    "Food": ["food", "cooking", "foodporn", "recipes"],
    "Automotive": ["cars", "autos", "carporn", "teslamotors"],
    "Beauty": ["skincareaddiction", "makeupaddiction", "beauty"],
    "Luxury": ["watches", "luxury", "rolex", "luxurylifestyle"],
    "Fitness": ["fitness", "running", "bodybuilding", "weightlifting"],
    "Home": ["homedecorating", "interiordesign", "houseplants", "furniture"]
}

# Product to subreddit mapping
PRODUCT_SUBREDDITS = {
    "iphone": ["iphone", "apple", "ios", "applehelp"],
    "watch": ["watches", "applewatch", "watchexchange", "smartwatch"],
    "perfume": ["fragrance", "perfume", "scents"],
    "laptop": ["laptops", "macbook", "thinkpad", "suggestalaptop"],
    "shoe": ["sneakers", "goodyearwelt", "running", "shoes"],
    "headphone": ["headphones", "audiophile", "airpods"],
    "coffee": ["coffee", "espresso", "cafe"],
    "skincare": ["skincareaddiction", "asianbeauty", "tretinoin"]
}

# Product to keywords mapping - words to look for in Reddit analysis
PRODUCT_KEYWORDS = {
    "iphone": ["screen", "camera", "battery", "ios", "app", "design", "pro", "max", "color", "performance"],
    "watch": ["dial", "movement", "automatic", "quartz", "strap", "complication", "chronograph", "water resistance"],
    "perfume": ["scent", "fragrance", "note", "longevity", "sillage", "projection", "bottle", "designer"],
    "laptop": ["screen", "battery", "keyboard", "processor", "gpu", "ram", "storage", "performance", "design"],
    "shoe": ["comfort", "fit", "style", "cushioning", "support", "durability", "breathability", "color"],
    "headphone": ["sound", "noise cancellation", "battery", "comfort", "wireless", "bass", "microphone", "design"],
    "coffee": ["flavor", "brew", "roast", "aroma", "origin", "espresso", "grind", "machine"],
    "skincare": ["moisturizer", "cleanser", "serum", "spf", "retinol", "acid", "hydration", "skin type"]
}

class RedditAnalyzer:
    """Analyze Reddit for advertising insights."""
    
    def __init__(self):
        """Initialize Reddit API client."""
        try:
            reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
            reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
            
            if not reddit_client_id or not reddit_client_secret:
                logger.warning("Reddit API credentials not found in environment variables")
                self.reddit = None
            else:
                self.reddit = praw.Reddit(
                    client_id=reddit_client_id,
                    client_secret=reddit_client_secret,
                    user_agent="AdGenerator/1.0 (by /u/YourUsername)"  # Update with your username
                )
                logger.info("Reddit API client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Reddit client: {str(e)}")
            self.reddit = None
    
    def is_available(self) -> bool:
        """Check if Reddit API is available."""
        return self.reddit is not None
    
    def get_relevant_subreddits(self, product: str, industry: str) -> List[str]:
        """
        Get relevant subreddits for a product and industry.
        
        Args:
            product: Product name
            industry: Industry category
            
        Returns:
            List of subreddit names
        """
        subreddits = set()
        
        # Get product-specific subreddits
        product_lower = product.lower()
        for key, subs in PRODUCT_SUBREDDITS.items():
            if key in product_lower:
                subreddits.update(subs)
        
        # Get industry subreddits
        for ind, subs in INDUSTRY_SUBREDDITS.items():
            if ind.lower() in industry.lower():
                subreddits.update(subs)
        
        # If no matches, use some general subreddits
        if not subreddits:
            subreddits = {"askreddit", "popular", "all"}
        
        return list(subreddits)
    
    def analyze_subreddits(self, subreddit_names: List[str], product: str, brand_name: str) -> Dict:
        """
        Analyze subreddits for trends and insights.
        
        Args:
            subreddit_names: List of subreddit names
            product: Product name
            brand_name: Brand name
            
        Returns:
            Dictionary of insights
        """
        if not self.is_available():
            logger.warning("Reddit API not available, returning default insights")
            return {}
        
        try:
            # Get product keywords
            product_lower = product.lower()
            keywords = []
            for key, words in PRODUCT_KEYWORDS.items():
                if key in product_lower:
                    keywords.extend(words)
            
            if not keywords:
                # Default keywords
                keywords = ["quality", "design", "feature", "performance", "price", "value"]
            
            # Get brand name keywords
            brand_keywords = [brand_name.lower()]
            
            # Search for posts in subreddits
            all_posts = []
            all_comments = []
            for subreddit_name in subreddit_names[:3]:  # Limit to 3 subreddits to avoid rate limits
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Get top posts from past month
                    for post in subreddit.top(time_filter="month", limit=10):
                        all_posts.append({
                            "title": post.title,
                            "text": post.selftext,
                            "score": post.score,
                            "upvote_ratio": post.upvote_ratio
                        })
                        
                        # Get comments
                        post.comments.replace_more(limit=0)  # Avoid loading more comments (for speed)
                        for comment in list(post.comments)[:5]:  # Top 5 comments
                            all_comments.append({
                                "text": comment.body,
                                "score": comment.score
                            })
                    
                    # Search for posts related to product/brand
                    for post in subreddit.search(f"{product} OR {brand_name}", limit=10):
                        all_posts.append({
                            "title": post.title,
                            "text": post.selftext,
                            "score": post.score,
                            "upvote_ratio": post.upvote_ratio
                        })
                except Exception as subreddit_error:
                    logger.warning(f"Error processing subreddit {subreddit_name}: {str(subreddit_error)}")
                    continue
            
            # Analyze results
            return self._extract_insights(all_posts, all_comments, keywords, brand_keywords, product)
            
        except Exception as e:
            logger.error(f"Error analyzing Reddit: {str(e)}")
            return {}
    
    def _extract_insights(self, posts: List[Dict], comments: List[Dict], 
                         keywords: List[str], brand_keywords: List[str], product: str) -> Dict:
        """
        Extract advertising insights from posts and comments.
        
        Args:
            posts: List of posts
            comments: List of comments
            keywords: Product-specific keywords
            brand_keywords: Brand-specific keywords
            product: Product name
            
        Returns:
            Dictionary of insights
        """
        try:
            # Skip if no data
            if not posts and not comments:
                return {}
            
            # Combine all text for analysis
            all_text = ""
            for post in posts:
                all_text += post["title"] + " " + post["text"] + " "
            
            for comment in comments:
                all_text += comment["text"] + " "
            
            all_text = all_text.lower()
            
            # Count keyword occurrences
            keyword_counts = {}
            for keyword in keywords:
                count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', all_text))
                keyword_counts[keyword] = count
            
            # Top keywords
            top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
            top_keywords = [k for k, v in top_keywords if v > 0][:5]
            
            # Analyze sentiment (very basic approach)
            positive_words = ["good", "great", "excellent", "amazing", "awesome", "love", "best", "perfect"]
            negative_words = ["bad", "poor", "terrible", "worst", "hate", "dislike", "disappointing"]
            
            positive_count = sum(all_text.count(word) for word in positive_words)
            negative_count = sum(all_text.count(word) for word in negative_words)
            
            sentiment = "positive" if positive_count > negative_count else "neutral"
            
            # Determine visual focus based on keywords
            visual_focus = self._determine_visual_focus(top_keywords, product)
            
            # Determine text style based on sentiment
            text_style = "bold" if sentiment == "positive" else "minimal"
            
            # Key elements based on top keywords
            key_elements = [f"{keyword} feature" for keyword in top_keywords[:3]]
            if not key_elements:
                key_elements = ["product quality", "brand reliability", "key features"]
            
            # Insights dictionary
            insights = {
                "recommended_format": "Product showcase with key features highlighted",
                "text_placement": "centered",
                "text_style": text_style,
                "key_elements": key_elements,
                "visual_focus": visual_focus,
                "color_scheme": "brand colors with accent highlights",
                "trending_keywords": top_keywords,
                "sentiment": sentiment
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error extracting insights: {str(e)}")
            return {}
    
    def _determine_visual_focus(self, keywords: List[str], product: str) -> str:
        """
        Determine visual focus based on keywords.
        
        Args:
            keywords: Top keywords
            product: Product name
            
        Returns:
            Visual focus description
        """
        product_lower = product.lower()
        
        # iPhone specific
        if "iphone" in product_lower:
            if any(k in ["camera", "photo", "photography"] for k in keywords):
                return "camera system close-up"
            elif any(k in ["screen", "display"] for k in keywords):
                return "screen with vibrant content"
            else:
                return "phone profile with screen display"
        
        # Watch specific
        elif "watch" in product_lower:
            if any(k in ["dial", "face"] for k in keywords):
                return "watch face details"
            elif any(k in ["strap", "band"] for k in keywords):
                return "full watch with focus on band"
            else:
                return "watch at 10:10 position with reflections"
        
        # Generic approach based on keywords
        if any(k in ["design", "look", "style", "aesthetic"] for k in keywords):
            return "product design and styling"
        elif any(k in ["feature", "function", "capability"] for k in keywords):
            return "product in use showing key features"
        elif any(k in ["detail", "quality", "craftsmanship"] for k in keywords):
            return "close-up details showing quality"
        
        # Default
        return "product with professional lighting and staging"


def search_social_media_ads(product: str, brand_name: str, industry: str) -> Dict:
    """
    Search social media platforms for ad trends and insights.
    Uses Reddit API for real-time data when available.
    
    Args:
        product: Product name or description
        brand_name: Brand name
        industry: Industry category
        
    Returns:
        Dictionary of social media insights for ad creation
    """
    logger.info(f"Analyzing social media trends for {brand_name} {product} in {industry}")
    
    try:
        # Initialize Reddit analyzer
        reddit_analyzer = RedditAnalyzer()
        
        # Base insights dictionary
        insights = _get_insights_for_industry(industry)
        
        # Add product-specific customizations from simulated data
        product_insights = _get_product_specific_insights(product, brand_name)
        insights.update(product_insights)
        
        # If Reddit API is available, get real insights
        if reddit_analyzer.is_available():
            # Get relevant subreddits
            subreddits = reddit_analyzer.get_relevant_subreddits(product, industry)
            logger.info(f"Analyzing subreddits: {', '.join(subreddits[:3])}")
            
            # Analyze subreddits
            reddit_insights = reddit_analyzer.analyze_subreddits(subreddits, product, brand_name)
            
            # Update insights with Reddit data
            if reddit_insights:
                logger.info("Successfully obtained Reddit insights")
                insights.update(reddit_insights)
                
                # Log trending keywords if available
                if "trending_keywords" in reddit_insights:
                    logger.info(f"Trending keywords: {', '.join(reddit_insights['trending_keywords'])}")
            else:
                logger.info("No Reddit insights available, using default data")
        else:
            logger.info("Reddit API not available, using simulated insights")
        
        return insights
        
    except Exception as e:
        logger.error(f"Error analyzing social media trends: {str(e)}")
        # Return default insights as fallback
        return DEFAULT_FALLBACK


def _get_insights_for_industry(industry: str) -> Dict:
    """
    Get appropriate insights for a specific industry.
    
    Args:
        industry: Industry name or category
        
    Returns:
        Dictionary of social media insights
    """
    # Clean and normalize industry name
    industry_clean = industry.strip().lower()
    
    # Map to main categories
    if any(tech in industry_clean for tech in ["tech", "computer", "phone", "gadget", "electronics"]):
        return DEFAULT_INSIGHTS["Technology"]
    elif any(fashion in industry_clean for fashion in ["fashion", "clothing", "apparel", "wear", "shoe"]):
        return DEFAULT_INSIGHTS["Fashion"]
    elif any(food in industry_clean for food in ["food", "restaurant", "meal", "drink", "beverage"]):
        return DEFAULT_INSIGHTS["Food"]
    elif any(auto in industry_clean for auto in ["auto", "car", "vehicle", "motorcycle"]):
        return DEFAULT_INSIGHTS["Automotive"]
    elif any(beauty in industry_clean for beauty in ["beauty", "cosmetic", "makeup", "skin", "hair"]):
        return DEFAULT_INSIGHTS["Beauty"]
    elif any(luxury in industry_clean for luxury in ["luxury", "premium", "high-end", "exclusive"]):
        return DEFAULT_INSIGHTS["Luxury"]
    elif any(fitness in industry_clean for fitness in ["fitness", "gym", "workout", "health", "exercise"]):
        return DEFAULT_INSIGHTS["Fitness"]
    elif any(home in industry_clean for home in ["home", "furniture", "decor", "house", "interior"]):
        return DEFAULT_INSIGHTS["Home"]
    else:
        # Return technology as default if no match
        return DEFAULT_FALLBACK


def _get_product_specific_insights(product: str, brand_name: str) -> Dict:
    """
    Get product-specific customizations to insights.
    
    Args:
        product: Product name or description
        brand_name: Brand name
        
    Returns:
        Dictionary of product-specific customizations
    """
    product_lower = product.lower()
    
    # iPhone customizations
    if "iphone" in product_lower:
        return {
            "visual_focus": "phone screen and profile",
            "key_elements": ["iPhone at angle", "screen display", "sleek design"],
            "color_scheme": "dark blue to black gradient"
        }
    
    # Watch customizations
    elif any(watch in product_lower for watch in ["watch", "timepiece"]):
        return {
            "visual_focus": "watch face and details",
            "text_placement": "bottom",
            "key_elements": ["watch at 10:10 position", "metal details", "craftsmanship"],
            "color_scheme": "elegant dark gradient"
        }
    
    # Perfume customizations
    elif any(fragrance in product_lower for fragrance in ["perfume", "fragrance", "cologne"]):
        return {
            "visual_focus": "bottle silhouette",
            "text_placement": "side",
            "key_elements": ["bottle with reflection", "mist or essence suggestion", "luxury cues"],
            "color_scheme": "dark with shimmer"
        }
    
    # No specific customizations
    return {}


# For testing
if __name__ == "__main__":
    # Set up environment variables if running directly
    from dotenv import load_dotenv
    load_dotenv()
    
    product_tests = [
        ("iPhone 15 Pro", "APPLE", "Technology"),
        ("Running Shoes", "NIKE", "Footwear"),
        ("Luxury Watch", "ROLEX", "Accessories"),
        ("Coffee Maker", "BREVILLE", "Home Appliances")
    ]
    
    print("=== Social Media Ad Trend Analysis with Reddit API ===")
    for product, brand, industry in product_tests:
        print(f"\nAnalyzing: {brand} {product} ({industry})")
        insights = search_social_media_ads(product, brand, industry)
        
        print("Recommended Format:", insights["recommended_format"])
        print("Text Placement:", insights["text_placement"])
        print("Key Elements:", ", ".join(insights["key_elements"]))
        print("Color Scheme:", insights["color_scheme"])
        
        # Print trending keywords if available from Reddit
        if "trending_keywords" in insights:
            print("Trending Keywords:", ", ".join(insights["trending_keywords"]))
        
        if "sentiment" in insights:
            print("Sentiment:", insights["sentiment"])