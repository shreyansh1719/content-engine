"""
Optimized Facebook Ads Library Scraper with enhanced extraction of commercial ads
and comprehensive metadata collection for ad generation training
"""
import os
import re
import time
import json
import logging
import random
import platform
import subprocess
import hashlib
import colorsys
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from urllib.parse import quote, unquote
from pathlib import Path
import concurrent.futures

import requests
from bs4 import BeautifulSoup
import numpy as np

# Set up robust exception handling for imports
browser_automation_available = False
automation_method = None

# Try importing undetected_chromedriver first (best for avoiding detection)
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    browser_automation_available = True
    automation_method = "undetected_chromedriver"
except ImportError:
    pass

# If undetected_chromedriver failed, try standard selenium
if not browser_automation_available:
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        browser_automation_available = True
        automation_method = "selenium_chrome"
        
        # Try to import the ChromeDriverManager
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            automation_method = "selenium_chrome_manager"
        except ImportError:
            pass
            
    except ImportError:
        pass

# Last resort: Try Firefox
if not browser_automation_available:
    try:
        from selenium import webdriver
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        browser_automation_available = True
        automation_method = "selenium_firefox"
        
        # Try to import the GeckoDriverManager
        try:
            from webdriver_manager.firefox import GeckoDriverManager
            automation_method = "selenium_firefox_manager"
        except ImportError:
            pass
            
    except ImportError:
        pass

# Common selenium imports
try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import (
        TimeoutException, 
        WebDriverException, 
        NoSuchElementException,
        StaleElementReferenceException
    )
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
except ImportError:
    # These will only be used if browser automation is available
    pass

# Try importing optional image processing libraries
try:
    from PIL import Image
    import io
    image_processing_available = True
except ImportError:
    image_processing_available = False

# Try to import NLP libraries for text analysis
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    nltk_available = True
    
    # Download required NLTK resources
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
    except:
        pass
except ImportError:
    nltk_available = False

# Industry classification data
INDUSTRY_KEYWORDS = {
    "Beauty & Personal Care": [
        "beauty", "makeup", "skincare", "cosmetic", "fragrance", "perfume", "cologne",
        "moisturizer", "serum", "shampoo", "conditioner", "hair", "facial", "cream",
        "lotion", "soap", "cleanser", "deodorant", "lipstick", "mascara", "eyeliner"
    ],
    "Fashion & Apparel": [
        "fashion", "clothing", "apparel", "dress", "shirt", "pants", "jeans", "shoes",
        "sneakers", "jacket", "coat", "suit", "jewelry", "accessories", "handbag", 
        "purse", "wallet", "watch", "footwear", "activewear", "athleisure"
    ],
    "Food & Beverage": [
        "food", "beverage", "drink", "coffee", "tea", "juice", "water", "soda",
        "beer", "wine", "alcohol", "snack", "meal", "restaurant", "bar", "café",
        "bakery", "organic", "vegan", "meat", "seafood", "dairy"
    ],
    "Health & Wellness": [
        "health", "wellness", "fitness", "vitamin", "supplement", "protein",
        "workout", "exercise", "gym", "yoga", "meditation", "nutrition",
        "diet", "weight loss", "detox", "natural", "organic", "therapy"
    ],
    "Technology & Electronics": [
        "tech", "technology", "electronics", "phone", "smartphone", "computer", 
        "laptop", "tablet", "gadget", "device", "headphone", "earbud", "speaker",
        "camera", "tv", "television", "software", "app", "smart home", "gaming"
    ],
    "Home & Garden": [
        "home", "furniture", "decor", "garden", "kitchen", "bathroom", "bedroom",
        "living room", "dining", "patio", "outdoor", "indoor", "mattress", "bed",
        "sofa", "chair", "table", "appliance", "lamp", "lighting"
    ],
    "Automotive": [
        "car", "auto", "automotive", "vehicle", "truck", "suv", "sedan", "electric",
        "hybrid", "gas", "diesel", "tire", "engine", "motor", "battery", "accessory"
    ],
    "Financial Services": [
        "bank", "banking", "finance", "financial", "credit", "loan", "mortgage",
        "insurance", "invest", "investment", "retirement", "saving", "money",
        "payment", "card", "wallet", "accounting", "tax", "wealth"
    ],
    "Travel & Hospitality": [
        "travel", "hotel", "resort", "vacation", "holiday", "flight", "airline",
        "booking", "reservation", "trip", "tour", "cruise", "adventure", "experience",
        "destination", "accommodation", "tourism", "passport", "luggage"
    ],
    "Education & Learning": [
        "education", "school", "college", "university", "course", "class", "workshop",
        "training", "skill", "learn", "teach", "tutor", "coach", "certificate", 
        "degree", "knowledge", "student", "teacher", "professor", "curriculum"
    ],
    "Entertainment & Media": [
        "entertainment", "media", "movie", "film", "music", "game", "video", "stream",
        "streaming", "netflix", "spotify", "disney", "hbo", "amazon prime", "podcast", 
        "radio", "tv show", "series", "concert", "event"
    ],
    "Real Estate": [
        "real estate", "property", "house", "home", "apartment", "condo", "rent",
        "rental", "buy", "sell", "mortgage", "loan", "agent", "broker", "listing",
        "commercial", "residential", "development", "land", "building"
    ],
    "Business Services": [
        "business", "service", "consulting", "marketing", "advertising", "agency",
        "management", "solution", "software", "crm", "erp", "cloud", "saas",
        "b2b", "enterprise", "corporate", "professional", "client"
    ],
    "E-commerce & Retail": [
        "shop", "store", "retail", "ecommerce", "e-commerce", "marketplace", "mall",
        "online store", "sale", "discount", "deal", "offer", "shipping", "delivery",
        "order", "product", "purchase", "buy", "customer", "shopping"
    ]
}

# Brand positioning keywords
POSITIONING_KEYWORDS = {
    "Luxury": [
        "luxury", "premium", "exclusive", "elite", "sophisticated", "elegant",
        "high-end", "upscale", "prestigious", "exquisite", "refined", "superior",
        "opulent", "lavish", "indulgent", "deluxe", "finest", "quality"
    ],
    "Value": [
        "value", "affordable", "budget", "economical", "inexpensive", "reasonable",
        "cost-effective", "bargain", "deal", "save", "saving", "discount", "sale",
        "offer", "promotion", "low price", "cheap", "competitive", "best price"
    ],
    "Performance": [
        "performance", "effective", "powerful", "reliable", "durable", "efficient",
        "professional", "results", "outcome", "impact", "proven", "tested", "certified",
        "guaranteed", "high-performance", "maximum", "optimal", "precision"
    ],
    "Innovation": [
        "innovation", "innovative", "new", "revolutionary", "breakthrough", "cutting-edge",
        "advanced", "tech", "technology", "modern", "future", "futuristic", "forward-thinking",
        "state-of-the-art", "pioneering", "groundbreaking", "first", "leading"
    ],
    "Wellness": [
        "wellness", "health", "healthy", "natural", "organic", "clean", "pure",
        "holistic", "sustainable", "eco-friendly", "green", "vegan", "cruelty-free",
        "non-toxic", "chemical-free", "preservative-free", "allergen-free"
    ],
    "Lifestyle": [
        "lifestyle", "trendy", "stylish", "fashion", "design", "aesthetic", "chic",
        "cool", "hip", "urban", "contemporary", "modern", "minimal", "authentic",
        "unique", "identity", "personality", "character", "expression"
    ],
    "Family": [
        "family", "parenting", "children", "kids", "babies", "moms", "dads", "parents",
        "household", "home", "safety", "secure", "caring", "loving", "nurturing",
        "supportive", "protection", "together", "bonding", "relationship"
    ],
    "Experience": [
        "experience", "feel", "sensation", "emotion", "joy", "happiness", "pleasure",
        "satisfaction", "enjoyment", "excitement", "thrill", "adventure", "journey",
        "discovery", "explore", "immersive", "engaging", "interactive"
    ]
}

# CTA classification
CTA_CATEGORIES = {
    "Shop": ["shop", "buy", "purchase", "get", "order", "add to cart", "checkout"],
    "Learn": ["learn", "discover", "explore", "find", "see", "read", "view"],
    "Sign Up": ["sign up", "register", "join", "subscribe", "start", "create account"],
    "Contact": ["contact", "call", "message", "email", "reach out", "get in touch"],
    "Download": ["download", "install", "get app", "get now", "get free"],
    "Trial": ["try", "free trial", "demo", "sample", "test", "experience"],
    "Book": ["book", "reserve", "schedule", "appointment", "consultation"]
}


class FacebookAdsScraper:
    """
    Enhanced Facebook Ads Library scraper with improved extraction of commercial ads
    and comprehensive metadata collection for ad generation training.
    
    Features:
    - Commercial ad targeting with smart filtering of UI elements
    - Visual element extraction (colors, layout, typography)
    - Engagement metrics collection
    - Industry and positioning categorization
    - Ad quality scoring
    - Comprehensive metadata for LLM training
    """
    
    def __init__(
        self,
        output_dir: str = 'data',
        use_proxies: bool = False,
        headless: bool = False,  # Default to visible browser for debugging
        log_level: int = logging.INFO,
        browser_type: str = 'chrome',  # Force Chrome as default
        debug_mode: bool = True,  # Enable debugging by default
        max_run_time_minutes: int = 30,  # Maximum runtime per search in minutes
        max_wait_time: float = 2.0,  # Maximum wait time between actions
        parallel_keywords: bool = True,  # Enable parallel processing of keywords
        chromedriver_path: Optional[str] = None,  # Allow custom ChromeDriver path
        extract_visual_elements: bool = True,  # Extract color schemes, layout, etc.
        extract_engagement_metrics: bool = True,  # Extract likes, comments, shares
        categorize_ads: bool = True,  # Categorize by industry and positioning
        compute_quality_score: bool = True,  # Calculate quality score for filtering
        min_quality_score: float = 5.0  # Minimum quality score to keep an ad
    ):
        """
        Initialize the enhanced Facebook Ads Library scraper.
        
        Args:
            output_dir: Directory to save scraped data
            use_proxies: Whether to use proxy rotation
            headless: Run browser in headless mode
            log_level: Logging level
            browser_type: Type of browser to use ('chrome', 'firefox', 'request')
            debug_mode: Enable detailed debugging output
            max_run_time_minutes: Maximum runtime per search in minutes
            max_wait_time: Maximum wait time between actions
            parallel_keywords: Enable parallel processing of keywords
            chromedriver_path: Custom path to ChromeDriver executable
            extract_visual_elements: Whether to extract visual elements like colors
            extract_engagement_metrics: Whether to extract likes, comments, shares
            categorize_ads: Whether to categorize ads by industry and positioning
            compute_quality_score: Whether to compute quality score for filtering
            min_quality_score: Minimum quality score to keep an ad
        """
        # Setup logging
        self.logger = logging.getLogger('FacebookAdsScraper')
        self.logger.setLevel(log_level)
        
        if not self.logger.handlers:
            # Create handlers
            console_handler = logging.StreamHandler()
            file_handler = logging.FileHandler(
                os.path.join(output_dir, 'facebook_scraper.log'),
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
        
        # Ensure output directory exists
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'raw'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'processed'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
        
        # Check if browser automation is available
        if not browser_automation_available and browser_type != 'request':
            self.logger.warning("Browser automation packages not available. "
                              "Will fall back to request-based scraping.")
            browser_type = 'request'
        
        # Browser configuration
        self.browser_type = browser_type
        self.headless = headless
        self.use_proxies = use_proxies
        self.driver = None
        self.session_start_time = datetime.now()
        self.last_action_time = self.session_start_time
        self.page_load_count = 0
        self.max_run_time_seconds = max_run_time_minutes * 60
        self.max_wait_time = max_wait_time
        self.debug_mode = debug_mode
        self.parallel_keywords = parallel_keywords
        self.chromedriver_path = chromedriver_path or os.environ.get('CHROMEDRIVER_PATH')
        
        # Enhanced extraction settings
        self.extract_visual_elements = extract_visual_elements
        self.extract_engagement_metrics = extract_engagement_metrics
        self.categorize_ads = categorize_ads
        self.compute_quality_score = compute_quality_score
        self.min_quality_score = min_quality_score
        
        # Current keyword for contextual filtering
        self.current_keyword = ""
        
        # Scraping parameters
        self.ads_collected = 0
        self.max_ads_per_session = 200  # Limit per browser session
        self.scrape_attempts = 0
        self.max_scrape_attempts = 3
        
        # Storage for scraped ads
        self.scraped_ads = []
        
        # Global cache of known ads to avoid duplicates across sessions
        self.known_ad_ids = set()
        
        # User agents collection for rotation - 2024 updated list
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/108.0.0.0",
        ]
        
        # For request-based scraping
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'DNT': '1',
            'Cache-Control': 'max-age=0',
        })
        
        # Performance tracking
        self.performance_metrics = {
            'browser_launch_time': 0,
            'total_scroll_count': 0,
            'extraction_times': [],
            'scroll_times': [],
            'load_more_clicks': 0,
            'captcha_encounters': 0,
            'login_block_encounters': 0,
            'ads_per_minute': [],
            'selector_effectiveness': {}
        }
        
        # UI element patterns to exclude - crucial for avoiding non-ad content
        self.ui_element_patterns = [
            "these results include",
            "no ads found",
            "ad library report",
            "search for ads",
            "can't find the ad you're looking for",
            "to view more details",
            "these ads ran",
            "ad about social issues",
            "disclaimer",
            "see more ads from",
            "filter results",
            "filter by",
            "sort by"
        ]
        
        # Cache for industry and positioning classification
        self._industry_cache = {}
        self._positioning_cache = {}
        
        self.logger.info(f"Enhanced FacebookAdsScraper initialized with browser type: {browser_type}")
        self.logger.info(f"Automation method available: {automation_method}")
        self.logger.info(f"Visual elements extraction: {extract_visual_elements}")
        self.logger.info(f"Engagement metrics extraction: {extract_engagement_metrics}")
        self.logger.info(f"Ad categorization: {categorize_ads}")
        self.logger.info(f"Quality scoring: {compute_quality_score} (min score: {min_quality_score})")
        if self.chromedriver_path:
            self.logger.info(f"Using custom ChromeDriver path: {self.chromedriver_path}")
    
    def _human_like_wait(self, min_seconds: float = 0.5, max_seconds: float = None) -> None:
        """
        Wait for a random amount of time to mimic human behavior, with optimized times.
        
        Args:
            min_seconds: Minimum wait time in seconds
            max_seconds: Maximum wait time in seconds (defaults to self.max_wait_time)
        """
        if max_seconds is None:
            max_seconds = min(self.max_wait_time, min_seconds + 1.0)
        
        # Generate a random wait time using a normal distribution centered around the midpoint
        midpoint = (min_seconds + max_seconds) / 2
        stddev = (max_seconds - min_seconds) / 4  # 95% of values within range
        wait_time = random.normalvariate(midpoint, stddev)
        
        # Ensure wait time is within bounds
        wait_time = max(min_seconds, min(max_seconds, wait_time))
        
        # Wait
        time.sleep(wait_time)
        
        # Update last action time
        self.last_action_time = datetime.now()
    
    def _human_like_scroll(self, direction: str = 'down', distance: Optional[int] = None) -> None:
        """
        Perform scrolling in a human-like manner, optimized for speed and detection avoidance.
        
        Args:
            direction: 'up' or 'down'
            distance: Scroll distance in pixels (if None, uses random distance)
        """
        if not self.driver:
            return
        
        try:
            start_time = time.time()
            
            # Get viewport height
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Determine scroll distance - optimized for faster data collection
            if distance is None:
                if direction == 'down':
                    # Scroll between 60% and 90% of viewport height - more aggressive
                    distance = int(viewport_height * random.uniform(0.6, 0.9))
                else:
                    # Scroll up between 30% and 50% of viewport height - minimized
                    distance = int(viewport_height * random.uniform(0.3, 0.5))
                    distance = -distance  # Negative for upward scrolling
            
            # Scroll with variable speed (not all at once)
            remaining = abs(distance)
            scroll_direction = 1 if distance > 0 else -1
            
            # Use fewer, larger steps for faster scrolling
            while remaining > 0:
                # Determine step size with some randomness - larger steps
                step = min(remaining, random.randint(200, 500))
                remaining -= step
                
                # Execute scroll
                self.driver.execute_script(
                    "window.scrollBy(0, arguments[0])", 
                    step * scroll_direction
                )
                
                # Very small random pause between scroll steps
                time.sleep(random.uniform(0.01, 0.1))
            
            # Shorter wait after scrolling
            self._human_like_wait(0.1, 0.5)
            
            # Move mouse a little (helps avoid detection) - but only occasionally
            if random.random() < 0.3:  # 30% chance
                try:
                    action = ActionChains(self.driver)
                    action.move_by_offset(random.randint(-10, 10), random.randint(-10, 10))
                    action.perform()
                except:
                    pass  # Ignore if action fails
            
            # Update performance metrics
            scroll_time = time.time() - start_time
            self.performance_metrics['scroll_times'].append(scroll_time)
            self.performance_metrics['total_scroll_count'] += 1
            
            if self.debug_mode:
                self.logger.debug(f"Scroll {direction} took {scroll_time:.2f}s")
            
        except Exception as e:
            self.logger.warning(f"Scroll error: {str(e)}")
    
    def _launch_browser(self) -> bool:
        """
        Launch browser with appropriate automation method, optimized for 2024.
        
        Returns:
            True if browser launched successfully, False otherwise
        """
        start_time = time.time()
        
        # Determine the browser type to use
        browser_to_use = self.browser_type
        
        # Close any existing browser session
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
        
        try:
            # Launch the appropriate browser
            if browser_to_use == 'chrome':
                result = self._launch_chrome_browser()
            elif browser_to_use == 'firefox':
                result = self._launch_firefox_browser()
            else:
                self.logger.info("Using request-based scraping (no browser)")
                return False  # No browser to launch for request mode
            
            # Record browser launch time
            self.performance_metrics['browser_launch_time'] = time.time() - start_time
            
            return result
                
        except Exception as e:
            self.logger.error(f"Error in browser launch: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
            # Fall back to alternative methods
            if browser_to_use == 'chrome':
                self.logger.info("Chrome launch failed, trying Firefox...")
                try:
                    return self._launch_firefox_browser()
                except Exception as e2:
                    self.logger.error(f"Firefox launch also failed: {str(e2)}")
                    return False
            
            return False
    
    def _launch_chrome_browser(self) -> bool:
        """
        Launch Chrome browser using the best available method, optimized for ChromeDriver 134.
        
        Returns:
            True if browser launched successfully, False otherwise
        """
        try:
            # Set up common Chrome options
            options = ChromeOptions()
            
            # Set a random user agent
            user_agent = random.choice(self.user_agents)
            options.add_argument(f'--user-agent={user_agent}')
            
            # Configure headless mode if requested
            if self.headless:
                options.add_argument('--headless=new')
                options.add_argument('--window-size=1920,1080')
            
            # Disable notifications and other distractions
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-infobars')
            options.add_argument('--mute-audio')
            
            # Add additional anti-bot detection flags
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            
            # Set language to English
            options.add_argument('--lang=en-US')
            
            # Set parameters for better performance
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-web-security')
            
            # PRIORITY 1: Use specified ChromeDriver path from environment or init
            if self.chromedriver_path and os.path.exists(self.chromedriver_path):
                self.logger.info(f"Using specified ChromeDriver path: {self.chromedriver_path}")
                
                # Use different approaches based on automation method
                if automation_method == "undetected_chromedriver":
                    # Pass executable_path to undetected_chromedriver
                    try:
                        self.driver = uc.Chrome(
                            executable_path=self.chromedriver_path,
                            options=options,
                            use_subprocess=True
                        )
                        self.logger.info("Successfully launched Chrome with specified ChromeDriver using undetected_chromedriver")
                        
                        # Set timeouts and window size
                        self._configure_browser()
                        return True
                    except Exception as e:
                        self.logger.warning(f"Failed to use specified ChromeDriver with undetected_chromedriver: {str(e)}")
                else:
                    # Use Service class from selenium for the driver path
                    try:
                        service = ChromeService(executable_path=self.chromedriver_path)
                        self.driver = webdriver.Chrome(service=service, options=options)
                        self.logger.info("Successfully launched Chrome with specified ChromeDriver")
                        
                        # Set timeouts and window size
                        self._configure_browser()
                        return True
                    except Exception as e:
                        self.logger.warning(f"Failed to use specified ChromeDriver: {str(e)}")
            
            # PRIORITY 2: Try using undetected_chromedriver (best for avoiding detection)
            if automation_method == "undetected_chromedriver":
                self.logger.info("Trying undetected_chromedriver")
                try:
                    self.driver = uc.Chrome(
                        options=options, 
                        use_subprocess=True
                    )
                    self.logger.info("Successfully launched Chrome with undetected_chromedriver")
                    
                    # Set timeouts and window size
                    self._configure_browser()
                    return True
                except Exception as e:
                    self.logger.warning(f"Failed to use undetected_chromedriver: {str(e)}")
            
            # PRIORITY 3: Use selenium with ChromeDriverManager
            if not self.driver and automation_method == "selenium_chrome_manager":
                self.logger.info("Trying ChromeDriverManager")
                try:
                    self.driver = webdriver.Chrome(
                        service=ChromeService(ChromeDriverManager().install()),
                        options=options
                    )
                    self.logger.info("Successfully launched Chrome with ChromeDriverManager")
                    
                    # Set timeouts and window size
                    self._configure_browser()
                    return True
                except Exception as e:
                    self.logger.warning(f"Failed to use ChromeDriverManager: {str(e)}")
            
            # PRIORITY 4: Try with basic selenium
            if not self.driver and automation_method == "selenium_chrome":
                self.logger.info("Trying basic Selenium")
                try:
                    # Try to find chromedriver in common locations
                    chromedriver_paths = [
                        "./chromedriver",
                        "./chromedriver.exe",
                        "/usr/local/bin/chromedriver",
                        "C:\\chromedriver.exe"
                    ]
                    
                    for path in chromedriver_paths:
                        if os.path.exists(path):
                            self.logger.info(f"Using ChromeDriver at: {path}")
                            self.driver = webdriver.Chrome(
                                service=ChromeService(path),
                                options=options
                            )
                            break
                    
                    # If no explicit path worked, try default
                    if not self.driver:
                        self.driver = webdriver.Chrome(options=options)
                    
                    self.logger.info("Successfully launched Chrome with basic Selenium")
                    
                    # Set timeouts and window size
                    self._configure_browser()
                    return True
                except Exception as e:
                    self.logger.warning(f"Failed to use basic Selenium: {str(e)}")
            
            self.logger.error("Failed to initialize Chrome driver with any method")
            return False
                
        except Exception as e:
            self.logger.error(f"Chrome browser launch failed: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def _configure_browser(self) -> None:
        """
        Configure browser timeouts and settings after successful launch.
        """
        if not self.driver:
            return
            
        # Set generous timeouts to avoid timing out during slow loads
        self.driver.set_page_load_timeout(60)
        self.driver.implicitly_wait(10)  # Reduced from 20 to improve performance
        
        # Set window size - random but realistic
        if not self.headless:
            width = random.randint(1280, 1920)
            height = random.randint(800, 1080)
            self.driver.set_window_size(width, height)
        
        # Reset session counters
        self.session_start_time = datetime.now()
        self.last_action_time = self.session_start_time
        self.page_load_count = 0
    
    def _launch_firefox_browser(self) -> bool:
        """
        Launch Firefox browser as a fallback option.
        
        Returns:
            True if browser launched successfully, False otherwise
        """
        try:
            if not automation_method in ["selenium_firefox", "selenium_firefox_manager"]:
                self.logger.error("Firefox automation not available")
                return False
                
            # Set up Firefox options
            options = FirefoxOptions()
            
            # Set a random user agent
            user_agent = random.choice(self.user_agents)
            options.set_preference("general.useragent.override", user_agent)
            
            # Configure headless mode if requested
            if self.headless:
                options.add_argument('--headless')
            
            # Disable notifications
            options.set_preference("dom.webnotifications.enabled", False)
            
            # Set language to English
            options.set_preference("intl.accept_languages", "en-US, en")
            
            # Disable cache
            options.set_preference("browser.cache.disk.enable", False)
            options.set_preference("browser.cache.memory.enable", False)
            options.set_preference("browser.cache.offline.enable", False)
            options.set_preference("network.http.use-cache", False)
            
            # Use GeckoDriverManager if available
            if automation_method == "selenium_firefox_manager":
                self.logger.info("Launching Firefox with GeckoDriverManager")
                
                # Create Firefox instance with driver manager
                self.driver = webdriver.Firefox(
                    service=FirefoxService(GeckoDriverManager().install()),
                    options=options
                )
                
            # Use basic selenium for Firefox
            else:
                self.logger.info("Launching Firefox with basic Selenium")
                    
                # Try to find geckodriver in common locations
                geckodriver_path = None
                for path in [
                    "./geckodriver",
                    "./geckodriver.exe",
                    "/usr/local/bin/geckodriver",
                    "C:\\geckodriver.exe"
                ]:
                    if os.path.exists(path):
                        geckodriver_path = path
                        break
                        
                if geckodriver_path:
                    self.driver = webdriver.Firefox(
                        service=FirefoxService(geckodriver_path),
                        options=options
                    )
                else:
                    # Try without specifying driver path
                    self.driver = webdriver.Firefox(options=options)
            
            # Set timeouts
            if self.driver:
                # Set timeouts
                self._configure_browser()
                
                self.logger.info("Firefox browser launched successfully")
                return True
            else:
                self.logger.error("Failed to initialize Firefox driver")
                return False
                
        except Exception as e:
            self.logger.error(f"Firefox browser launch failed: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def _handle_cookies_and_popups(self) -> None:
        """
        Handle cookie consent and various popups that might appear - 2024 updated selectors.
        """
        if not self.driver:
            return
            
        try:
            # Common cookie consent buttons - 2024 Updated
            cookie_selectors = [
                "//div[@aria-label='Allow essential and optional cookies']",
                "//div[@role='button' and contains(., 'Only allow essential cookies')]",
                "//button[@data-testid='cookie-policy-manage-dialog-accept-button']",
                "//button[contains(text(), 'Accept') or contains(text(), 'Accept All') or contains(text(), 'I Accept')]",
                "//button[contains(text(), 'Agree') or contains(text(), 'I Agree') or contains(text(), 'OK')]"
            ]
            
            # Try each selector with a short timeout
            for selector in cookie_selectors:
                try:
                    buttons = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_all_elements_located((By.XPATH, selector))
                    )
                    for button in buttons:
                        if button.is_displayed():
                            self.logger.info(f"Found and clicking cookie consent button: {selector}")
                            button.click()
                            self._human_like_wait(0.5, 1.0)
                            break
                except:
                    continue
                    
            # Handle "Not Now" buttons for login prompts - 2024 Updated
            not_now_selectors = [
                "//div[@role='button' and contains(text(), 'Not Now')]",
                "//div[@aria-label='Not Now']",
                "//button[text()='Not Now']",
                "//a[text()='Not Now']"
            ]
            
            for selector in not_now_selectors:
                try:
                    buttons = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_all_elements_located((By.XPATH, selector))
                    )
                    for button in buttons:
                        if button.is_displayed():
                            self.logger.info(f"Found and clicking 'Not Now' button: {selector}")
                            button.click()
                            self._human_like_wait(0.5, 1.0)
                            break
                except:
                    continue
                
        except Exception as e:
            self.logger.warning(f"Error handling cookies and popups: {str(e)}")
    
    def _check_for_captcha(self) -> bool:
        """
        Check if a CAPTCHA is present and attempt to handle it - 2024 updated.
        
        Returns:
            True if CAPTCHA was solved or not present, False if failed to solve
        """
        if not self.driver:
            return False
        
        try:
            # Look for common CAPTCHA indicators - 2024 updated
            captcha_indicators = [
                "//div[contains(@aria-label, 'Security check')]",
                "//div[contains(@aria-label, 'Solve the reCAPTCHA')]",
                "//div[contains(@class, 'captcha')]",
                "//iframe[contains(@src, 'captcha')]",
                "//div[contains(text(), 'Security check')]"
            ]
            
            for indicator in captcha_indicators:
                try:
                    elements = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_all_elements_located((By.XPATH, indicator))
                    )
                    if elements and any(elem.is_displayed() for elem in elements):
                        self.logger.warning(f"CAPTCHA detected! ({indicator})")
                        
                        # Increment counter
                        self.performance_metrics['captcha_encounters'] += 1
                        
                        # Take a screenshot if possible
                        try:
                            screenshot_path = os.path.join(
                                self.output_dir, 
                                f"captcha_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                            )
                            self.driver.save_screenshot(screenshot_path)
                            self.logger.info(f"Saved CAPTCHA screenshot to {screenshot_path}")
                        except:
                            pass
                        
                        # Reset browser session to get a new IP
                        self.logger.info("Detected CAPTCHA - resetting browser session")
                        self._reset_session()
                        return False
                except:
                    continue
            
            # No CAPTCHA found
            return True
            
        except Exception as e:
            self.logger.warning(f"CAPTCHA check error: {str(e)}")
            return False
    
    def _check_for_login_block(self) -> bool:
        """
        Check if Facebook is requesting login and handle it - 2024 updated.
        
        Returns:
            True if page is accessible, False if blocked by login
        """
        if not self.driver:
            return False
        
        try:
            # Common login block indicators - 2024 updated
            login_indicators = [
                "//div[contains(text(), 'Log in to continue')]",
                "//form[@id='login_form']",
                "//button[contains(text(), 'Log In')]",
                "//div[@role='dialog']//div[contains(text(), 'Log in')]",
                "//input[@id='email']",
                "//div[contains(@class, 'login')]//input[@name='email']"
            ]
            
            for indicator in login_indicators:
                try:
                    elements = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_all_elements_located((By.XPATH, indicator))
                    )
                    if elements and any(elem.is_displayed() for elem in elements):
                        self.logger.warning(f"Login block detected! ({indicator})")
                        
                        # Increment counter
                        self.performance_metrics['login_block_encounters'] += 1
                        
                        # Try to bypass using a special URL parameter
                        current_url = self.driver.current_url
                        if '?' in current_url:
                            bypass_url = current_url + '&bypass=true'
                        else:
                            bypass_url = current_url + '?bypass=true'
                        
                        self.driver.get(bypass_url)
                        self._human_like_wait(1.0, 2.0)
                        
                        # Check if login is still required
                        login_still_present = False
                        for check_indicator in login_indicators:
                            try:
                                check_elements = WebDriverWait(self.driver, 2).until(
                                    EC.presence_of_all_elements_located((By.XPATH, check_indicator))
                                )
                                if check_elements and any(elem.is_displayed() for elem in check_elements):
                                    login_still_present = True
                                    break
                            except:
                                continue
                                
                        if login_still_present:
                            self.logger.error("Login block persists, resetting session")
                            self._reset_session()
                            return False
                        else:
                            self.logger.info("Successfully bypassed login block")
                            return True
                except:
                    continue
            
            # No login block detected
            return True
            
        except Exception as e:
            self.logger.warning(f"Login block check error: {str(e)}")
            return True  # Assume no login block if check fails
    
    def _check_browser_status(self) -> bool:
        """
        Check if the browser is still responsive.
        
        Returns:
            True if browser is responsive, False otherwise
        """
        if not self.driver:
            return False
            
        try:
            # Try to get current URL
            current_url = self.driver.current_url
            # Try a simple JavaScript execution
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            if self.debug_mode:
                self.logger.debug(f"Browser is responsive at URL: {current_url}")
            return True
        except Exception as e:
            self.logger.warning(f"Browser appears to be unresponsive: {e}")
            return False
    
    def _reset_session(self) -> None:
        """
        Reset browser session to avoid detection from extended usage.
        """
        # Close the current driver
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
        
        # Reset session counters
        self.ads_collected = 0
        self.page_load_count = 0
        
        # Wait a random time before starting new session - reduced for optimization
        wait_time = random.uniform(5, 15)  # Reduced from 30-60s
        self.logger.info(f"Waiting {wait_time:.2f} seconds before starting new session")
        time.sleep(wait_time)
        
        # For request-based scraping, rotate user agent
        if self.browser_type == 'request':
            self.session.headers.update({
                'User-Agent': random.choice(self.user_agents)
            })
    
    def scrape_ads_library(
        self, 
        keywords: List[str], 
        countries: List[str] = ['US'],
        ad_types: List[str] = ['all'],
        max_ads_per_keyword: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Scrape ads from Facebook Ads Library for multiple keywords and countries.
        
        Args:
            keywords: List of keywords/brands to search for
            countries: List of country codes
            ad_types: List of ad types ('all', 'political', 'housing', etc.)
            max_ads_per_keyword: Maximum ads to collect per keyword
            
        Returns:
            List of ad dictionaries
        """
        all_ads = []
        
        # Display run parameters
        self.logger.info(f"Starting batch scrape for {len(keywords)} keywords across {len(countries)} countries")
        self.logger.info(f"Targeting {max_ads_per_keyword} ads per keyword-country combination")
        
        # Determine if we should use parallel processing
        if self.parallel_keywords and len(keywords) > 1 and self.browser_type != 'request':
            self.logger.info("Using parallel processing for multiple keywords")
            return self._scrape_in_parallel(keywords, countries, ad_types, max_ads_per_keyword)
        
        # Sequential processing
        for keyword in keywords:
            for country in countries:
                for ad_type in ad_types:
                    try:
                        search_start_time = time.time()
                        self.logger.info(f"Processing: keyword='{keyword}', country='{country}', ad_type='{ad_type}'")
                        
                        # Use appropriate scraping method based on browser type
                        if self.browser_type == 'request':
                            ads = self._scrape_with_requests(
                                keyword=keyword,
                                country=country,
                                ad_type=ad_type,
                                max_ads=max_ads_per_keyword
                            )
                        else:
                            ads = self._scrape_single_search(
                                keyword=keyword,
                                country=country,
                                ad_type=ad_type,
                                max_ads=max_ads_per_keyword
                            )
                        
                        # Report search timing
                        search_time = time.time() - search_start_time
                        self.logger.info(f"Search completed in {search_time:.2f} seconds, found {len(ads)} ads")
                        
                        # Calculate and store ads per minute
                        if search_time > 0:
                            ads_per_minute = (len(ads) / search_time) * 60
                            self.performance_metrics['ads_per_minute'].append(ads_per_minute)
                            self.logger.info(f"Collection rate: {ads_per_minute:.1f} ads per minute")
                        
                        if ads:
                            # Add source metadata to each ad
                            for ad in ads:
                                ad['search_keyword'] = keyword
                                ad['search_country'] = country
                                ad['search_ad_type'] = ad_type
                                ad['scrape_time'] = datetime.now().isoformat()
                            
                            all_ads.extend(ads)
                            
                            # Save intermediate results
                            self._save_ads_batch(
                                ads,
                                f"fb_ads_{keyword.replace(' ', '_')}_{country}_{ad_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                            )
                        else:
                            self.logger.warning(f"No ads found for keyword='{keyword}', country='{country}', ad_type='{ad_type}'")
                        
                        # Reset browser if needed
                        if self.browser_type != 'request' and len(all_ads) >= self.max_ads_per_session:
                            self.logger.info(f"Maximum ads per session reached ({self.max_ads_per_session}), restarting browser")
                            self._reset_session()
                    
                    except Exception as e:
                        self.logger.error(f"Error scraping {keyword} in {country} for {ad_type} ads: {str(e)}")
                        import traceback
                        self.logger.error(traceback.format_exc())
        
        # Save final results
        if all_ads:
            self.scraped_ads = all_ads
            self._save_ads_batch(
                all_ads,
                f"fb_ads_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            # Report overall performance
            self._report_performance(all_ads)
            
        else:
            self.logger.warning("No ads were collected in the entire batch")
        
        return all_ads
    
    def _scrape_in_parallel(
        self,
        keywords: List[str],
        countries: List[str] = ['US'],
        ad_types: List[str] = ['all'],
        max_ads_per_keyword: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple keywords in parallel using multiple browser instances.
        
        Args:
            keywords: List of keywords/brands to search for
            countries: List of country codes
            ad_types: List of ad types
            max_ads_per_keyword: Maximum ads to collect per keyword
            
        Returns:
            List of ad dictionaries
        """
        all_ads = []
        
        # Determine max workers based on system resources
        max_workers = min(4, len(keywords))  # Don't use more than 4 workers
        self.logger.info(f"Starting parallel scraping with {max_workers} workers")
        
        # Create tasks for parallel execution
        tasks = []
        for keyword in keywords:
            for country in countries:
                for ad_type in ad_types:
                    tasks.append((keyword, country, ad_type))
        
        # Use ThreadPoolExecutor for parallelization
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create a new scraper instance for each task
            future_to_task = {}
            for task in tasks:
                keyword, country, ad_type = task
                
                # Create a new scraper instance with the same settings
                scraper = FacebookAdsScraper(
                    output_dir=self.output_dir,
                    use_proxies=self.use_proxies,
                    headless=self.headless,
                    log_level=self.logger.level,
                    browser_type=self.browser_type,
                    debug_mode=self.debug_mode,
                    max_run_time_minutes=self.max_run_time_seconds // 60,
                    max_wait_time=self.max_wait_time,
                    parallel_keywords=False,  # Prevent recursive parallelization
                    chromedriver_path=self.chromedriver_path,
                    extract_visual_elements=self.extract_visual_elements,
                    extract_engagement_metrics=self.extract_engagement_metrics,
                    categorize_ads=self.categorize_ads,
                    compute_quality_score=self.compute_quality_score,
                    min_quality_score=self.min_quality_score
                )
                
                # Share known ad IDs to prevent duplicates across workers
                scraper.known_ad_ids = self.known_ad_ids.copy()
                
                # Submit task to executor
                future = executor.submit(
                    scraper._scrape_single_search,
                    keyword=keyword,
                    country=country,
                    ad_type=ad_type,
                    max_ads=max_ads_per_keyword
                )
                future_to_task[future] = (scraper, task)
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_task):
                scraper, (keyword, country, ad_type) = future_to_task[future]
                try:
                    ads = future.result()
                    
                    # Add metadata
                    for ad in ads:
                        ad['search_keyword'] = keyword
                        ad['search_country'] = country
                        ad['search_ad_type'] = ad_type
                        ad['scrape_time'] = datetime.now().isoformat()
                    
                    # Save batch
                    scraper._save_ads_batch(
                        ads,
                        f"fb_ads_{keyword.replace(' ', '_')}_{country}_{ad_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    )
                    
                    # Add to overall collection
                    all_ads.extend(ads)
                    
                    # Update global known ad IDs
                    self.known_ad_ids.update(scraper.known_ad_ids)
                    
                    # Merge performance metrics
                    for metric in scraper.performance_metrics:
                        if isinstance(self.performance_metrics[metric], list):
                            self.performance_metrics[metric].extend(scraper.performance_metrics[metric])
                        elif isinstance(self.performance_metrics[metric], (int, float)):
                            self.performance_metrics[metric] += scraper.performance_metrics[metric]
                    
                    self.logger.info(f"Parallel task for '{keyword}' in {country} completed with {len(ads)} ads")
                    
                    # Clean up scraper
                    scraper.quit()
                    
                except Exception as e:
                    self.logger.error(f"Error in parallel task for '{keyword}' in {country}: {str(e)}")
                    # Clean up scraper
                    try:
                        scraper.quit()
                    except:
                        pass
        
        # Save combined results
        if all_ads:
            self.scraped_ads = all_ads
            self._save_ads_batch(
                all_ads,
                f"fb_ads_all_parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            # Report performance
            self._report_performance(all_ads)
        
        return all_ads
    
    def _report_performance(self, ads: List[Dict[str, Any]]) -> None:
        """
        Report performance metrics after scraping.
        
        Args:
            ads: List of collected ads
        """
        # Calculate average ads per minute
        avg_ads_per_minute = 0
        if self.performance_metrics['ads_per_minute']:
            avg_ads_per_minute = sum(self.performance_metrics['ads_per_minute']) / len(self.performance_metrics['ads_per_minute'])
        
        # Calculate average extraction time
        avg_extraction_time = 0
        if self.performance_metrics['extraction_times']:
            avg_extraction_time = sum(self.performance_metrics['extraction_times']) / len(self.performance_metrics['extraction_times'])
        
        # Report performance
        self.logger.info(f"Scraping batch complete. Performance summary:")
        self.logger.info(f"- Total ads collected: {len(ads)}")
        self.logger.info(f"- Average collection rate: {avg_ads_per_minute:.1f} ads per minute")
        self.logger.info(f"- Average extraction time: {avg_extraction_time:.2f}s")
        self.logger.info(f"- Total scrolls: {self.performance_metrics['total_scroll_count']}")
        self.logger.info(f"- Load more clicks: {self.performance_metrics['load_more_clicks']}")
        self.logger.info(f"- CAPTCHA encounters: {self.performance_metrics['captcha_encounters']}")
        self.logger.info(f"- Login blocks: {self.performance_metrics['login_block_encounters']}")
        
        # Report selector effectiveness
        if self.performance_metrics['selector_effectiveness']:
            self.logger.info("Selector effectiveness:")
            for selector, (count, total) in self.performance_metrics['selector_effectiveness'].items():
                if total > 0:
                    success_rate = (count / total) * 100
                    self.logger.info(f"- {selector}: {success_rate:.1f}% ({count}/{total})")
        
        # Report industry breakdown
        industries = {}
        for ad in ads:
            industry = ad.get('metadata', {}).get('industry', 'Unknown')
            industries[industry] = industries.get(industry, 0) + 1
        
        if industries:
            self.logger.info("Industry breakdown:")
            for industry, count in sorted(industries.items(), key=lambda x: x[1], reverse=True):
                self.logger.info(f"- {industry}: {count} ads ({count/len(ads)*100:.1f}%)")
        
        # Report positioning breakdown
        positioning = {}
        for ad in ads:
            pos = ad.get('metadata', {}).get('positioning', 'Unknown')
            positioning[pos] = positioning.get(pos, 0) + 1
        
        if positioning:
            self.logger.info("Positioning breakdown:")
            for pos, count in sorted(positioning.items(), key=lambda x: x[1], reverse=True):
                self.logger.info(f"- {pos}: {count} ads ({count/len(ads)*100:.1f}%)")
    
    def _scrape_with_requests(
        self,
        keyword: str,
        country: str = 'US',
        ad_type: str = 'all',
        max_ads: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Scrape ads using requests library (no browser) - fallback method.
        
        Args:
            keyword: Search keyword or brand name
            country: Country code
            ad_type: Type of ads to search for
            max_ads: Maximum number of ads to collect
            
        Returns:
            List of ad dictionaries
        """
        collected_ads = []
        self.current_keyword = keyword  # Set current keyword for filtering
        
        try:
            # Construct search URL
            encoded_keyword = quote(keyword)
            search_url = (
                f"https://www.facebook.com/ads/library/?"
                f"active_status=all&ad_type={ad_type}&country={country}&"
                f"q={encoded_keyword}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped"
            )
            
            self.logger.info(f"Searching for '{keyword}' ads in {country} using requests")
            
            # Make request
            response = self.session.get(search_url, timeout=30)
            
            if response.status_code != 200:
                self.logger.warning(f"Failed to load page: {response.status_code}")
                return []
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for no results indicator
            no_results = soup.select('div:-soup-contains("No ads")')
            if no_results:
                self.logger.info(f"No ads found for '{keyword}' in {country}")
                return []
            
            # Extract ads using multiple selectors to find actual ad containers
            ad_containers = []
            
            # IMPORTANT: Updated selectors for Facebook Ads Library - 2024
            # These selectors specifically target commercial ad containers, not UI elements
            selectors = [
                # Core ad container selectors - target actual ads, not UI elements
                'div[data-testid="ad_card"]',  # Latest primary ad card selector
                'div[data-testid="fb-ad-card"]',  # Alternative ad card selector
                'div[data-ad-preview="message"]',  # Ad message container
                
                # Selector targeting the parent container of the actual ad content
                'div[class*="x78zum5"][class*="xdt5ytf"]',  # Combined class pattern
                
                # Ad media container indicators
                'div[data-testid="ad_carousel"]',  # Carousel ads
                'div[data-testid="ad_image"]',  # Image ads
                'div[data-testid="ad_video"]',  # Video ads
                
                # Fallback selectors for actual ad elements
                'div[aria-label="Ad"] > div > div',  # Direct ad container
                'div[aria-label="Advertisement"] > div > div',  # Direct advertisement container
                
                # Ad text content selectors
                'div:has(> div[data-ad-preview="message"])',  # Has ad message
                'div:has(> div[data-ad-comet-preview="message"])'  # Has newer ad message format
            ]
            
            # Track successful selectors for reporting
            selector_counts = {}
            
            for selector in selectors:
                try:
                    containers = soup.select(selector)
                    
                    # Filter out UI elements by checking content length and keyword relevance
                    filtered_containers = []
                    for container in containers:
                        # Skip if this is a UI element
                        if self._is_ui_element(container):
                            continue
                        
                        # Check if container has substantial content
                        if len(container.get_text()) > 50:  # Minimum text length for real ads
                            # Check if text contains the keyword (case-insensitive)
                            if keyword.lower() in container.get_text().lower():
                                filtered_containers.append(container)
                    
                    if filtered_containers:
                        ad_containers.extend(filtered_containers)
                        selector_counts[selector] = len(filtered_containers)
                        self.logger.info(f"Found {len(filtered_containers)} ad containers with selector '{selector}'")
                except Exception as e:
                    self.logger.debug(f"Error with selector '{selector}': {str(e)}")
            
            # Remove duplicate containers
            unique_containers = []
            unique_texts = set()
            
            for container in ad_containers:
                # Use text content as a simple deduplication key
                text = container.get_text()[:200]  # First 200 chars as signature
                text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
                
                if text_hash not in unique_texts:
                    unique_texts.add(text_hash)
                    unique_containers.append(container)
            
            self.logger.info(f"Filtered to {len(unique_containers)} unique ad containers")
            
            # Process each container
            for container in unique_containers[:max_ads]:
                try:
                    # Extract ad data with enhanced metadata
                    ad_data = self._extract_ad_from_html(container)
                    
                    # Skip ads that are clearly UI elements or system messages
                    if ad_data and not self._is_ui_text(ad_data.get('headline', '')) and not self._is_ui_text(ad_data.get('ad_text', '')):
                        # Skip if this ad ID is already known
                        if ad_data.get('ad_id') in self.known_ad_ids:
                            continue
                        
                        # Extract enhanced metadata
                        self._enhance_ad_data(ad_data, container)
                        
                        # Calculate quality score
                        if self.compute_quality_score:
                            quality_score = self._compute_ad_quality_score(ad_data)
                            if quality_score < self.min_quality_score:
                                self.logger.debug(f"Ad rejected: quality score {quality_score:.1f} below threshold {self.min_quality_score}")
                                continue
                            
                            # Add quality score to metadata
                            if 'metadata' not in ad_data:
                                ad_data['metadata'] = {}
                            ad_data['metadata']['quality_score'] = quality_score
                        
                        # Add to collected ads
                        collected_ads.append(ad_data)
                        
                        # Add to known ad IDs
                        if ad_data.get('ad_id'):
                            self.known_ad_ids.add(ad_data['ad_id'])
                        
                        if len(collected_ads) % 10 == 0:
                            self.logger.info(f"Extracted {len(collected_ads)} ads with requests-based approach")
                            
                except Exception as ad_error:
                    self.logger.debug(f"Error extracting ad details from HTML: {str(ad_error)}")
            
            self.logger.info(f"Extracted {len(collected_ads)} ads with requests-based approach")
            return collected_ads
            
        except Exception as e:
            self.logger.error(f"Error in requests-based scraping: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []
    
    def _is_ui_element(self, element) -> bool:
        """
        Check if an element is a UI element rather than an actual ad.
        
        Args:
            element: BeautifulSoup element to check
            
        Returns:
            True if element is a UI element, False otherwise
        """
        # Check element text for common UI phrases
        text = element.get_text().lower()
        
        # Check against known UI patterns
        for pattern in self.ui_element_patterns:
            if pattern in text:
                return True
        
        # Check for common UI attributes
        for attr in ['role', 'aria-label', 'data-testid']:
            attr_value = element.get(attr, '').lower()
            if attr_value and ('filter' in attr_value or 'search' in attr_value or 
                               'navigation' in attr_value or 'button' in attr_value or
                               'dialog' in attr_value or 'menu' in attr_value):
                return True
        
        # Check for short text (UI elements often have short text)
        if len(text) < 30:
            # But make sure it's not just a short ad headline
            if not any(kw in text for kw in ['shop', 'learn', 'download', 'get', 'buy', 'sign up']):
                return True
        
        return False
    
    def _is_ui_text(self, text: str) -> bool:
        """
        Check if text is from a UI element rather than an actual ad.
        
        Args:
            text: Text to check
            
        Returns:
            True if text is from a UI element, False otherwise
        """
        if not text:
            return False
            
        text = text.lower()
        
        # Check against known UI text patterns
        for pattern in self.ui_element_patterns:
            if pattern in text:
                return True
                
        # Check for specific UI-only phrases
        ui_only_phrases = [
            "these results include ads",
            "ad library",
            "search results",
            "filter by",
            "sort by",
            "clear all",
            "advanced search",
            "search for ads",
            "all countries",
            "help center",
            "learn more about"
        ]
        
        for phrase in ui_only_phrases:
            if phrase in text:
                return True
        
        return False
    
    def _extract_ad_from_html(self, container) -> Optional[Dict[str, Any]]:
        """
        Extract ad data from BeautifulSoup HTML element - 2024 updated with better targeting of actual ads.
        
        Args:
            container: BeautifulSoup element containing an ad
            
        Returns:
            Ad data dictionary or None if extraction failed
        """
        ad_data = {
            "ad_id": "",
            "page_name": "",
            "page_id": "",
            "ad_text": "",
            "headline": "",
            "cta_text": "",
            "link_url": "",
            "platform": ["Facebook"],  # Default
            "start_date": "",
            "end_date": "",
            "status": "",
            "image_urls": [],
            "video_urls": []
        }
        
        try:
            # Extract ad ID from attributes or links - 2024 updated approach
            # Look for links with ad_id parameter
            links = container.select('a[href*="ad_id="]')
            for link in links:
                href = link.get('href', '')
                match = re.search(r'ad_id=(\d+)', href)
                if match:
                    ad_data["ad_id"] = match.group(1)
                    break
            
            # If no ID found, try data attributes
            if not ad_data["ad_id"]:
                # Try to get from data attributes
                for attr in ['id', 'data-id', 'data-ad-id', 'data-testid']:
                    if container.has_attr(attr) and re.search(r'\d+', container[attr]):
                        ad_data["ad_id"] = re.search(r'\d+', container[attr]).group(0)
                        break
            
            # If still no ID, generate a random one
            if not ad_data["ad_id"]:
                import uuid
                ad_data["ad_id"] = f"gen_{str(uuid.uuid4())[:8]}"
            
            # Extract page name - 2024 updated selectors
            page_name_selectors = [
                'a[aria-label*="Advertiser"]',  # Primary advertiser link
                'span[class*="x8t9es0"]',  # 2024 primary
                'span[class*="x1hl2dhg"]',  # 2024 alternative
                'div[class*="x78zum5"] > a',  # Container with link
                'a[role="link"] > span',  # Role-based selector
                'a[class*="x1i10hfl"]',  # Class-based selector
                'a[href*="/pages/"]',  # Pages URL
                'a[href*="facebook.com/"]:not([href*="facebook.com/ads/"])'  # Facebook profile URL
            ]
            
            for selector in page_name_selectors:
                elements = container.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    # Check if this looks like a page name (not too long, not empty)
                    if text and len(text) < 60 and not text.startswith("http"):
                        ad_data["page_name"] = text
                        
                        # Also try to get page ID from href
                        href = element.get('href') or ""
                        if href and '/pages/' in href:
                            match = re.search(r'/pages/[^/]+/(\d+)', href)
                            if match:
                                ad_data["page_id"] = match.group(1)
                        elif href and 'facebook.com/' in href:
                            match = re.search(r'facebook\.com/(?!ads/)([^/\?]+)', href)
                            if match:
                                ad_data["page_id"] = match.group(1)
                        break
                
                if ad_data["page_name"]:
                    break
            
            # Extract ad text - 2024 updated selectors targeting actual ad content
            text_selectors = [
                'div[data-ad-preview="message"]',  # Primary data attribute
                'div[data-ad-comet-preview="message"]',  # Alternative data attribute
                'div[class*="xzsf02u"]',  # 2024 primary text class
                'div[class*="x1iorvi4"]',  # 2024 secondary text class
                'div[class*="x1lliihq"]',  # Alternative class
                'div[dir="auto"][class*="x"]'  # Generic direction-based selector
            ]
            
            for selector in text_selectors:
                elements = container.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    # Check if this looks like main ad text (not too short)
                    if text and len(text) > 15:
                        ad_data["ad_text"] = text
                        break
                
                if ad_data["ad_text"]:
                    break
            
            # Extract headline - 2024 updated selectors
            headline_selectors = [
                'div[data-ad-preview="headline"]',  # Primary data attribute 
                'div[data-ad-comet-preview="headline"]',  # Alternative data attribute
                'div[class*="x1xmf6yo"]',  # 2024 primary headline class
                'div[class*="xzsf02u"] span',  # Container with span
                'span[class*="x1lliihq"]'  # Direct span class
            ]
            
            for selector in headline_selectors:
                elements = container.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    # Check if this looks like a headline (not too long, not too short)
                    if text and 5 <= len(text) <= 100:
                        ad_data["headline"] = text
                        break
                
                if ad_data["headline"]:
                    break
            
            # Extract CTA - 2024 updated selectors targeting actual CTAs
            cta_selectors = [
                'div[data-ad-preview="cta"]',  # Primary data attribute
                'div[data-ad-comet-preview="cta"]',  # Alternative data attribute
                'div[class*="x1qc7bx0"] > a',  # 2024 primary CTA container
                'a[class*="x1lku1pv"]',  # 2024 button class
                'a[role="button"]',  # Role-based button
            ]
            
            for selector in cta_selectors:
                elements = container.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    # Check if this looks like a CTA button (short text)
                    if text and 2 <= len(text) <= 25 and not text.startswith("http"):
                        ad_data["cta_text"] = text
                        
                        # Also get landing URL
                        href = element.get('href', '')
                        if href and href.startswith("http"):
                            try:
                                # Extract actual destination from Facebook redirect
                                if 'facebook.com/l.php?u=' in href:
                                    redirect_part = re.search(r'u=(.*?)(?:&|$)', href)
                                    if redirect_part:
                                        href = unquote(redirect_part.group(1))
                            except:
                                pass
                            
                            ad_data["link_url"] = href
                        break
                
                if ad_data["cta_text"]:
                    break
            
            # Extract images - 2024 updated approach targeting actual ad images
            image_selectors = [
                'img[src*="scontent"]',  # Facebook CDN images
                'img[data-visualcompletion="media-vc-image"]',  # Media image attribute
                'img[alt*="Image may contain"]',  # Image with descriptive alt
                'img[class*="x5yr21d"]',  # 2024 image class
                'img[class*="x17dymka"]',  # Alternative image class
            ]
            
            for selector in image_selectors:
                images = container.select(selector)
                for img in images:
                    src = img.get('src', '')
                    if src and src.startswith("http") and "profile_pic" not in src and "icon" not in src:
                        # Try to filter out tiny icons using attributes or class patterns
                        width = int(img.get('width', 0))
                        height = int(img.get('height', 0))
                        
                        # Skip small icons or specific classes
                        if (width < 50 or height < 50) or any(c in str(img.get('class', '')) for c in ['icon', 'emoji', 'avatar']):
                            continue
                            
                        # Add to image URLs if not already there
                        if src not in ad_data["image_urls"]:
                            ad_data["image_urls"].append(src)
            
            # Extract date information - 2024 updated patterns
            date_text = container.get_text()
            
            # Try various date formats
            date_patterns = [
                r'Start(?:ed|ing)?\s*:?\s*([A-Za-z]+\s+\d+,\s+\d{4})\s*(?:to\s*([A-Za-z]+\s+\d+,\s+\d{4}|present)|$)',
                r'Active date[s]?:?\s*([A-Za-z]+\s+\d+,\s+\d{4})',
                r'Started running on\s*([A-Za-z]+\s+\d+,\s+\d{4})',
                r'Running from\s*([A-Za-z]+\s+\d+,\s+\d{4})\s*(?:to\s*([A-Za-z]+\s+\d+,\s+\d{4}|present)|$)'
            ]
            
            for pattern in date_patterns:
                date_match = re.search(pattern, date_text)
                if date_match:
                    ad_data["start_date"] = date_match.group(1).strip()
                    if len(date_match.groups()) > 1 and date_match.group(2) and date_match.group(2).lower() != 'present':
                        ad_data["end_date"] = date_match.group(2).strip()
                    break
            
            # Determine ad status based on date info
            if ad_data["start_date"]:
                if ad_data["end_date"]:
                    ad_data["status"] = "inactive"
                else:
                    ad_data["status"] = "active"
            
            # Extract platform information - 2024 updated approach
            platform_selectors = [
                'div:contains("Platform") + div',
                'div:contains("Platforms") + div',
                'div:contains("Shown on") + div'
            ]
            
            platforms = []
            for selector in platform_selectors:
                elements = container.select(selector)
                for element in elements:
                    text = element.get_text().lower()
                    if "facebook" in text:
                        platforms.append("Facebook")
                    if "instagram" in text:
                        platforms.append("Instagram")
                    if "messenger" in text:
                        platforms.append("Messenger")
                    if platforms:
                        break
                
                if platforms:
                    ad_data["platform"] = platforms
                    break
            
            # Check minimal requirements for a valid ad
            if ((ad_data["page_name"] or ad_data["ad_text"] or ad_data["headline"]) 
                and ad_data["ad_id"]
                and not self._is_ui_text(ad_data["ad_text"])
                and not self._is_ui_text(ad_data["headline"])):
                return ad_data
            else:
                return None
            
        except Exception as e:
            self.logger.debug(f"Error extracting ad data from HTML: {str(e)}")
            return None
    
    def _scrape_single_search(
        self,
        keyword: str,
        country: str = 'US',
        ad_type: str = 'all',
        max_ads: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Scrape ads for a single keyword, country, and ad type using browser automation.
        
        Args:
            keyword: Search keyword or brand name
            country: Country code
            ad_type: Type of ads to search for
            max_ads: Maximum number of ads to collect
            
        Returns:
            List of ad dictionaries
        """
        collected_ads = []
        self.current_keyword = keyword
        
        # Attempt scraping with retries
        self.scrape_attempts = 0
        while self.scrape_attempts < self.max_scrape_attempts and len(collected_ads) < max_ads:
            try:
                # Track start time for this attempt
                attempt_start_time = time.time()
                
                self.logger.info(f"TIMING: Starting search attempt #{self.scrape_attempts+1} for '{keyword}'")
                
                # Launch browser if needed
                if not self.driver:
                    browser_start = time.time()
                    if not self._launch_browser():
                        self.logger.error("Failed to launch browser, aborting scrape")
                        # Fall back to requests-based scraping
                        self.logger.info("Falling back to requests-based scraping")
                        return self._scrape_with_requests(keyword, country, ad_type, max_ads)
                    browser_time = time.time() - browser_start
                    self.logger.info(f"TIMING: Browser launch took {browser_time:.2f}s")
                
                # Construct search URL - Using the most effective parameters for commercial ads
                encoded_keyword = quote(keyword)
                # Updated URL construction with relevancy sorting for commercial ads
                search_url = (
                    f"https://www.facebook.com/ads/library/?"
                    f"active_status=active&ad_type={ad_type}&country={country}&"
                    f"q={encoded_keyword}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped"
                    f"&media_type=all&search_type=keyword_unordered&media_type=all"
                )
                
                # Navigate to ads library
                self.logger.info(f"Searching for '{keyword}' ads in {country}")
                url_load_start = time.time()
                self.driver.get(search_url)
                self.page_load_count += 1
                url_load_time = time.time() - url_load_start
                self.logger.info(f"TIMING: Initial URL load took {url_load_time:.2f}s")
                
                # Shorter initial wait - optimized
                self._human_like_wait(2.0, 3.0)
                
                # Handle cookies and popups
                popup_start = time.time()
                self._handle_cookies_and_popups()
                popup_time = time.time() - popup_start
                if self.debug_mode:
                    self.logger.debug(f"TIMING: Popup handling took {popup_time:.2f}s")
                
                # Check for CAPTCHA and login blocks
                check_start = time.time()
                captcha_ok = self._check_for_captcha()
                login_ok = self._check_for_login_block()
                check_time = time.time() - check_start
                if self.debug_mode:
                    self.logger.debug(f"TIMING: Security checks took {check_time:.2f}s")
                
                if not captcha_ok or not login_ok:
                    self.logger.warning("Access issues detected, retrying with new session")
                    self._reset_session()
                    self.scrape_attempts += 1
                    continue
                
                # Try some initial scrolling to trigger content loading
                scroll_start = time.time()
                self._human_like_scroll('down', 600)
                scroll_time = time.time() - scroll_start
                if self.debug_mode:
                    self.logger.debug(f"TIMING: Initial scroll took {scroll_time:.2f}s")
                
                # Shorter wait time
                self._human_like_wait(1.0, 1.5)
                
                # Updated selectors specifically targeting actual ads, not UI elements
                # CRITICAL: These selectors are designed to find commercial ads, not UI components
                ad_selectors = [
                    # Primary ad container selectors for 2024
                    "//div[@data-testid='ad_card']",  # Most reliable 2024 selector
                    "//div[@data-testid='fb-ad-card']",  # Alternative ad card selector
                    
                    # Parent containers for ad content
                    "//div[contains(@class, 'x78zum5') and contains(@class, 'xdt5ytf')]",  # Combined class pattern
                    
                    # Ad content with specific preview attributes
                    "//div[@data-ad-preview='message']/ancestor::div[contains(@class, 'x')]",  # Message ancestor
                    "//div[@data-ad-comet-preview='message']/ancestor::div[contains(@class, 'x')]",  # Alternative message
                    
                    # Ad message containers
                    "//div[contains(@class, 'xzsf02u')]/ancestor::div[position()=3]",  # Message container ancestor
                    
                    # Media-containing ad containers
                    "//div[@data-testid='ad_carousel']/ancestor::div[position()=3]",  # Carousel ancestor
                    "//div[@data-testid='ad_image']/ancestor::div[position()=3]",  # Image ancestor
                    "//div[@data-testid='ad_video']/ancestor::div[position()=3]",  # Video ancestor
                    
                    # Headline-based selectors
                    "//div[@data-ad-comet-preview='headline']/ancestor::div[position()=4]",  # Headline ancestor
                    "//div[contains(@class, 'x1xmf6yo')]/ancestor::div[position()=3]",  # Headline class ancestor
                    
                    # Fallback selectors
                    "//div[@aria-label='Ad']/div[position()=1]",  # Direct aria-label
                    "//div[@aria-label='Advertisement']/div[position()=1]",  # Alternative aria-label
                ]
                
                # Check for ad elements with each selector if in debug mode
                if self.debug_mode:
                    self.logger.info("Testing ad selectors:")
                    for selector in ad_selectors:
                        try:
                            elements = self.driver.find_elements(By.XPATH, selector)
                            if elements:
                                self.logger.info(f"✓ {selector}: found {len(elements)} elements")
                            else:
                                self.logger.info(f"✗ {selector}: found 0 elements")
                        except Exception as e:
                            self.logger.debug(f"Error testing selector {selector}: {str(e)}")
                    
                # Try each selector with a short timeout
                ads_found = False
                successful_selector = None
                    
                selector_start = time.time()
                for selector in ad_selectors:
                    try:
                        # Wait for ad elements to load
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                            
                        # Count the ad elements and log
                        ad_elements = self.driver.find_elements(By.XPATH, selector)
                        if ad_elements:
                            # Quick check if this selector is finding UI elements
                            sample_texts = [elem.text.lower() for elem in ad_elements[:3]]
                            ui_match_count = sum(1 for text in sample_texts if any(pat in text for pat in self.ui_element_patterns))
                            
                            # If most samples match UI patterns, skip this selector
                            if ui_match_count >= 2:  # 2 out of 3 match UI patterns
                                self.logger.info(f"Skipping selector {selector} - likely finding UI elements")
                                continue
                                
                            ads_found = True
                            successful_selector = selector
                            self.logger.info(f"Found {len(ad_elements)} ad elements with selector {selector}")
                            break
                    except TimeoutException:
                        continue
                
                selector_time = time.time() - selector_start
                self.logger.info(f"TIMING: Finding selector took {selector_time:.2f}s")
                
                # Check for "No ads found" message if no ads detected
                if not ads_found:
                    no_ads_elements = self.driver.find_elements(
                        By.XPATH, 
                        "//*[contains(text(), 'No ads') or contains(text(), 'We couldn')]"
                    )
                        
                    if no_ads_elements:
                        self.logger.info(f"No ads found for '{keyword}' in {country}")
                        return []
                        
                    # If no ads found but also no "No ads" message, try waiting more or reloading
                    self.logger.warning("Ads not found initially, trying again...")
                    self._human_like_wait(2.0, 3.0)
                    self.driver.refresh()
                    self._human_like_wait(1.5, 2.5)
                        
                    # Try scrolling to trigger ad loading
                    self._human_like_scroll('down', 800)
                    self._human_like_wait(1.0, 2.0)
                        
                    # Check again for ads
                    for selector in ad_selectors:
                        ad_elements = self.driver.find_elements(By.XPATH, selector)
                        if ad_elements:
                            ads_found = True
                            successful_selector = selector
                            self.logger.info(f"Found {len(ad_elements)} ad elements after retry with selector {selector}")
                            break
                        
                    if not ads_found:
                        self.logger.warning("Ads still not loading, incrementing attempt counter")
                        self.scrape_attempts += 1
                        continue
                
                # Scroll and collect ads - optimized for performance
                prev_ad_count = 0
                scroll_count = 0
                max_scrolls = 30  # Reduced from 50 to avoid diminishing returns
                consecutive_no_new_ads = 0
                max_consecutive_no_new = 2  # Reduced to speed up completion
                extracted_count = 0
                
                # Set up timeout for the scroll and extract loop
                search_start_time = time.time()
                
                # Track unique ad IDs to avoid duplicates
                unique_ad_ids = set()
                
                while len(collected_ads) < max_ads and scroll_count < max_scrolls:
                    # Check if we've exceeded max runtime
                    current_runtime = time.time() - search_start_time
                    if current_runtime > self.max_run_time_seconds:
                        self.logger.warning(f"Maximum runtime of {self.max_run_time_seconds/60:.1f} minutes reached. Stopping search.")
                        break
                    
                    # Verify browser is still responsive every 5 scrolls
                    if scroll_count % 5 == 0:  # Check every 5 scrolls
                        if not self._check_browser_status():
                            self.logger.error("Browser is unresponsive, restarting session")
                            self._reset_session()
                            self.scrape_attempts += 1
                            break
                    
                    # Extract ads from current view using successful selector
                    extract_start = time.time()
                    if successful_selector:
                        new_ads = self._extract_ads_from_page(successful_selector, unique_ad_ids)
                    else:
                        # Try all selectors if none was successful
                        new_ads = []
                        for selector in ad_selectors:
                            new_ads = self._extract_ads_from_page(selector, unique_ad_ids)
                            if new_ads:
                                successful_selector = selector
                                break
                    extract_time = time.time() - extract_start
                    
                    if self.debug_mode:
                        self.logger.debug(f"TIMING: Extraction took {extract_time:.2f}s, found {len(new_ads)} new ads")
                    
                    # Add timing to performance metrics
                    # Continuation of the FacebookAdsScraper class methods
# Add this to the same file after the previous code

                    # Add timing to performance metrics
                    self.performance_metrics['extraction_times'].append(extract_time)
                    
                    # Add new unique ads to collection
                    prev_count = len(collected_ads)
                    for ad in new_ads:
                        if 'ad_id' in ad:
                            unique_ad_ids.add(ad['ad_id'])
                            
                            # Also add to global known ad IDs to avoid duplicates across sessions
                            self.known_ad_ids.add(ad['ad_id'])
                            
                            collected_ads.append(ad)
                    
                    # Check for new ads
                    if len(collected_ads) > prev_count:
                        consecutive_no_new_ads = 0
                        extracted_count += len(collected_ads) - prev_count
                        
                        # Log progress with more detail
                        self.logger.info(f"Collected {len(collected_ads)}/{max_ads} ads for '{keyword}' in {country} (scroll #{scroll_count})")
                        
                        # Calculate and log extraction rate
                        if extract_time > 0:
                            extraction_rate = (len(collected_ads) - prev_count) / extract_time
                            if self.debug_mode:
                                self.logger.debug(f"Extraction rate: {extraction_rate:.1f} ads/second")
                    else:
                        consecutive_no_new_ads += 1
                        if self.debug_mode:
                            self.logger.debug(f"No new ads found on scroll #{scroll_count}, consecutive: {consecutive_no_new_ads}")
                    
                    # Break if we've scrolled multiple times with no new ads
                    if consecutive_no_new_ads >= max_consecutive_no_new:
                        self.logger.info(f"No new ads after {consecutive_no_new_ads} consecutive scrolls, probably reached the end")
                        break
                    
                    # Check if we've reached the target number of ads
                    if len(collected_ads) >= max_ads:
                        self.logger.info(f"Reached target of {max_ads} ads, stopping collection")
                        break
                    
                    # Scroll down to load more ads - faster scrolling
                    scroll_start = time.time()
                    self._human_like_scroll('down')
                    scroll_time = time.time() - scroll_start
                    if self.debug_mode:
                        self.logger.debug(f"TIMING: Scroll took {scroll_time:.2f}s")
                    
                    scroll_count += 1
                    
                    # Occasionally scroll up slightly to mimic human behavior - but less frequently
                    if scroll_count % 8 == 0:  # Reduced frequency from 5 to 8
                        self._human_like_scroll('up', distance=random.randint(200, 400))
                    
                    # Click "See More" or "Load More" buttons - 2024 updated selectors
                    load_more_selectors = [
                        "//div[@role='button' and contains(., 'See More')]",  # Most reliable 2024 selector
                        "//div[@role='button' and contains(., 'Load More')]",
                        "//span[contains(text(), 'See More')]",
                        "//button[contains(text(), 'See More')]"
                    ]
                    
                    # Only try to click load more occasionally to save time
                    if scroll_count % 3 == 0:  # Every 3 scrolls
                        for selector in load_more_selectors:
                            try:
                                load_more_elements = self.driver.find_elements(By.XPATH, selector)
                                for element in load_more_elements:
                                    if element.is_displayed() and element.is_enabled():
                                        self.logger.info(f"Clicking '{selector}' button")
                                        element.click()
                                        self.performance_metrics['load_more_clicks'] += 1
                                        self._human_like_wait(1.0, 1.5)  # Reduced wait time
                                        break
                            except:
                                continue
                    
                    # Check for end of results less frequently
                    if scroll_count % 5 == 0:  # Reduced from 3 to 5
                        end_indicators = [
                            "//*[contains(text(), 'End of results')]",
                            "//*[contains(text(), 'No more ads')]",
                            "//*[contains(text(), 'That's all')]",
                            "//*[contains(text(), 'That's all we found')]"
                        ]
                        
                        for indicator in end_indicators:
                            if self.driver.find_elements(By.XPATH, indicator):
                                self.logger.info("Reached end of results")
                                scroll_count = max_scrolls  # Break out of loop
                                break
                
                # Log the attempt results
                attempt_duration = time.time() - attempt_start_time
                self.logger.info(f"Search attempt completed in {attempt_duration:.2f} seconds")
                self.logger.info(f"Collected {len(collected_ads)} ads in {scroll_count} scrolls")
                
                # Calculate processing rates
                if attempt_duration > 0:
                    ads_per_second = len(collected_ads) / attempt_duration
                    ads_per_minute = ads_per_second * 60
                    scrolls_per_minute = (scroll_count / attempt_duration) * 60
                    
                    self.logger.info(f"Processing rates: {ads_per_minute:.1f} ads/minute, {scrolls_per_minute:.1f} scrolls/minute")
                    
                    # Store for performance metrics
                    self.performance_metrics['ads_per_minute'].append(ads_per_minute)
                
                # If we collected at least some ads, consider it a success
                if collected_ads:
                    self.scrape_attempts = 0  # Reset counter on success
                else:
                    self.scrape_attempts += 1
                    self.logger.warning(f"No ads collected on attempt {self.scrape_attempts}, will retry")
                
            except TimeoutException:
                self.logger.warning("Timeout waiting for ads to load, retrying")
                self.scrape_attempts += 1
                continue
                
            except Exception as e:
                self.logger.error(f"Error during scraping: {str(e)}")
                import traceback
                self.logger.error(traceback.format_exc())
                
                # Increment attempt counter and reset session
                self.scrape_attempts += 1
                self._reset_session()
        
        return collected_ads

    def _extract_ads_from_page(self, selector: str, unique_ids: Optional[Set[str]] = None) -> List[Dict[str, Any]]:
        """
        Extract ads from the current page using the given selector, with enhanced filtering.
        
        Args:
            selector: XPath selector to find ad elements
            unique_ids: Set of already collected ad IDs to avoid duplicates
            
        Returns:
            List of extracted ad dictionaries
        """
        start_time = time.time()
        ads = []
    
        if unique_ids is None:
            unique_ids = set()
    
        try:
            # Find all ad elements using the provided selector
            ad_elements = self.driver.find_elements(By.XPATH, selector)
        
            if not ad_elements:
                return []
            
            total_elements = len(ad_elements)
        
            # Filter to relevant product ads only - vital for excluding UI elements!
            keyword = self.current_keyword if hasattr(self, 'current_keyword') else ""
            filtered_elements = self._filter_relevant_ads(ad_elements, keyword)
            
            if self.debug_mode:
                self.logger.debug(f"Filtered from {total_elements} to {len(filtered_elements)} relevant ad elements")
        
            # Process each filtered ad element
            for i, ad_element in enumerate(filtered_elements):
                try:
                    # Extract core ad data
                    ad_data = self._extract_single_ad(ad_element)
                    
                    # Skip if extraction failed or duplicate ID
                    if not ad_data or 'ad_id' not in ad_data or ad_data['ad_id'] in unique_ids:
                        continue
                    
                    # Skip if text suggests this is a UI element, not an ad
                    if self._is_ui_text(ad_data.get('headline', '')) or self._is_ui_text(ad_data.get('ad_text', '')):
                        if self.debug_mode:
                            self.logger.debug(f"Skipping UI element with text: {ad_data.get('headline', '')} / {ad_data.get('ad_text', '')[:50]}")
                        continue
                    
                    # Extract enhanced metadata and visual elements
                    try:
                        self._enhance_ad_data(ad_data, ad_element)
                    except Exception as e:
                        self.logger.debug(f"Error enhancing ad data: {str(e)}")
                    
                    # Compute quality score
                    if self.compute_quality_score:
                        quality_score = self._compute_ad_quality_score(ad_data)
                        
                        # Skip if below quality threshold
                        if quality_score < self.min_quality_score:
                            if self.debug_mode:
                                self.logger.debug(f"Skipping low quality ad (score: {quality_score:.1f})")
                            continue
                            
                        # Add quality score to metadata
                        if 'metadata' not in ad_data:
                            ad_data['metadata'] = {}
                        ad_data['metadata']['quality_score'] = quality_score
                    
                    # Add the ad to our collection
                    ads.append(ad_data)
                    
                except Exception as ad_error:
                    if self.debug_mode:
                        self.logger.debug(f"Error extracting ad details: {str(ad_error)}")
        
            # Record extraction time for performance monitoring
            extraction_time = time.time() - start_time
        
            if self.debug_mode:
                self.logger.debug(f"Extracted {len(ads)}/{len(filtered_elements)} filtered ads in {extraction_time:.2f}s")
            
            return ads
        
        except Exception as e:
            self.logger.warning(f"Error extracting ads from page: {str(e)}")
            return []
            
    def _extract_single_ad(self, ad_element) -> Optional[Dict[str, Any]]:
        """
        Extract data from a single ad element - 2024 optimized with modern selectors,
        specifically targeting commercial ads, not UI components.
        
        Args:
            ad_element: WebElement containing a single ad
        
        Returns:
            Dictionary with ad data or None if extraction failed
        """
        ad_data = {
            "ad_id": "",
            "page_name": "",
            "page_id": "",
            "ad_text": "",
            "headline": "",
            "cta_text": "",
            "link_url": "",
            "platform": [],
            "start_date": "",
            "end_date": "",
            "status": "",
            "image_urls": [],
            "video_urls": []
        }
        
        try:
            # CRITICAL: First check if this element is a UI component
            element_text = ad_element.text.lower()
            if any(pattern in element_text for pattern in self.ui_element_patterns):
                if self.debug_mode:
                    self.logger.debug(f"Skipping UI element with text: {element_text[:100]}")
                return None
            
            # Extract ad ID from HTML attributes or URLs - prioritize href method
            # First look for ad_id in URL parameters
            links = ad_element.find_elements(By.TAG_NAME, 'a')
            for link in links:
                href = link.get_attribute('href') or ""
                if 'ad_id=' in href:
                    match = re.search(r'ad_id=(\d+)', href)
                    if match:
                        ad_data["ad_id"] = match.group(1)
                        break
            
            # If no ID found, check attributes
            if not ad_data["ad_id"]:
                id_attrs = ['id', 'data-id', 'data-ad-id', 'data-testid']
                for attr in id_attrs:
                    attr_value = ad_element.get_attribute(attr)
                    if attr_value and re.search(r'\d+', attr_value):
                        ad_data["ad_id"] = re.search(r'\d+', attr_value).group(0)
                        break
                
                # If still no ID found, generate a random one
                if not ad_data["ad_id"]:
                    import uuid
                    ad_data["ad_id"] = f"gen_{str(uuid.uuid4())[:8]}"
            
            # 2024 optimized extraction strategy - use more specific xpaths
            
            # Extract page name - 2024 updated selectors for advertiser
            page_name_selectors = [
                ".//a[@aria-label='Advertiser']",  # Direct advertiser label
                ".//a[contains(@aria-label, 'Advertiser')]",  # Contains advertiser in label
                ".//span[contains(@class, 'x8t9es0')]",  # Primary 2024 class
                ".//span[contains(@class, 'x1hl2dhg')]",  # Alternative class
                ".//div[contains(@class, 'x78zum5')]/a",  # Container with link
                ".//a[@role='link']/span",  # Role-based link
                ".//a[contains(@class, 'x1i10hfl')]",  # Class-based link
                ".//a[contains(@href, '/pages/')]"  # Pages URL
            ]
            
            for selector in page_name_selectors:
                elements = ad_element.find_elements(By.XPATH, selector)
                for element in elements:
                    text = element.text.strip()
                    # Check if this looks like a page name
                    if text and len(text) < 60 and not text.startswith("http"):
                        # Skip if it's a UI element
                        if text.lower() in ["see more", "view more", "learn more", "ad library"]:
                            continue
                            
                        ad_data["page_name"] = text
                        
                        # Also try to get page ID from href
                        href = element.get_attribute('href') or ""
                        if href:
                            if '/pages/' in href:
                                match = re.search(r'/pages/[^/]+/(\d+)', href)
                                if match:
                                    ad_data["page_id"] = match.group(1)
                            elif 'facebook.com/' in href:
                                match = re.search(r'facebook\.com/(?!ads/)([^/\?]+)', href)
                                if match:
                                    ad_data["page_id"] = match.group(1)
                        break
                
                if ad_data["page_name"]:
                    break
            
            # Extract ad text - 2024 updated selectors targeting ad content
            text_selectors = [
                ".//div[@data-ad-preview='message']",  # Primary data attribute
                ".//div[@data-ad-comet-preview='message']",  # Alternative data attribute
                ".//div[contains(@class, 'xzsf02u')]",  # Primary 2024 class
                ".//div[contains(@class, 'x1iorvi4')]",  # Secondary class
                ".//div[contains(@class, 'x1lliihq')]",  # Alternative class
                ".//div[@dir='auto'][contains(@class, 'x')]"  # Generic direction
            ]
            
            for selector in text_selectors:
                elements = ad_element.find_elements(By.XPATH, selector)
                for element in elements:
                    text = element.text.strip()
                    # Check if this looks like main ad text
                    if text and len(text) > 15:
                        # Skip if this is clearly a UI element
                        if any(pattern in text.lower() for pattern in self.ui_element_patterns):
                            continue
                            
                        ad_data["ad_text"] = text
                        break
                
                if ad_data["ad_text"]:
                    break
            
            # Extract headline - 2024 updated selectors
            headline_selectors = [
                ".//div[@data-ad-preview='headline']",  # Primary data attribute
                ".//div[@data-ad-comet-preview='headline']",  # Alternative data attribute
                ".//div[contains(@class, 'x1xmf6yo')]",  # Primary 2024 class
                ".//div[contains(@class, 'xzsf02u')]//span",  # Container with span
                ".//span[contains(@class, 'x1lliihq')]"  # Direct span
            ]
            
            for selector in headline_selectors:
                elements = ad_element.find_elements(By.XPATH, selector)
                for element in elements:
                    text = element.text.strip()
                    # Check if this looks like a headline
                    if text and 5 <= len(text) <= 100:
                        # Skip if this is clearly a UI element
                        if any(pattern in text.lower() for pattern in self.ui_element_patterns):
                            continue
                            
                        ad_data["headline"] = text
                        break
                
                if ad_data["headline"]:
                    break
            
            # Extract CTA - 2024 updated selectors targeting actual buttons
            cta_selectors = [
                ".//div[@data-ad-preview='cta']",  # Primary data attribute
                ".//div[@data-ad-comet-preview='cta']",  # Alternative data attribute
                ".//div[contains(@class, 'x1qc7bx0')]//a",  # Primary 2024 container
                ".//a[contains(@class, 'x1lku1pv')]",  # Button class
                ".//a[@role='button']",  # Role-based
            ]
            
            for selector in cta_selectors:
                elements = ad_element.find_elements(By.XPATH, selector)
                for element in elements:
                    text = element.text.strip()
                    # Check if this looks like a CTA button
                    if text and 2 <= len(text) <= 25 and not text.startswith("http"):
                        # Common CTA buttons - filter out non-CTAs
                        if text.lower() in ["see more", "learn more", "show more"]:
                            # These could be "see more" buttons for expanding text, not CTAs
                            # Only accept if there's no other CTA
                            if "learn more" in text.lower():  # This is actually a common CTA
                                pass  # Keep it
                            else:
                                continue  # Skip potential text expanders
                        
                        ad_data["cta_text"] = text
                        
                        # Also get landing URL
                        href = element.get_attribute('href') or ""
                        if href and href.startswith("http"):
                            try:
                                # Extract actual destination from Facebook redirect
                                if 'facebook.com/l.php?u=' in href:
                                    redirect_part = re.search(r'u=(.*?)(?:&|$)', href)
                                    if redirect_part:
                                        href = unquote(redirect_part.group(1))
                            except:
                                pass
                                
                            ad_data["link_url"] = href
                        break
                
                if ad_data["cta_text"]:
                    break
            
            # Extract platforms - 2024 updated selectors
            platform_selectors = [
                ".//div[contains(text(), 'Platform')]//following-sibling::div",
                ".//div[contains(text(), 'Shown on')]//following-sibling::div",
                ".//div[contains(text(), 'Platforms')]//following-sibling::div"
            ]
            
            platforms = []
            for selector in platform_selectors:
                elements = ad_element.find_elements(By.XPATH, selector)
                for element in elements:
                    text = element.text.lower()
                    if "facebook" in text:
                        platforms.append("Facebook")
                    if "instagram" in text:
                        platforms.append("Instagram")
                    if "messenger" in text:
                        platforms.append("Messenger")
                    if platforms:
                        break
            
            if platforms:
                ad_data["platform"] = platforms
            else:
                # Default to Facebook if no platform info found
                ad_data["platform"] = ["Facebook"]
            
            # Extract images - 2024 updated selectors for actual ad images
            image_selectors = [
                ".//img[@data-visualcompletion='media-vc-image']",  # Media completion attr
                ".//img[contains(@src, 'scontent')]",  # Facebook CDN
                ".//img[contains(@alt, 'Image may contain')]",  # Content description
                ".//img[contains(@class, 'x5yr21d')]",  # Primary 2024 class
                ".//img[contains(@class, 'x17dymka')]",  # Alternative class
                ".//img[not(contains(@src, 'icon'))]"  # Generic images
            ]
            
            for selector in image_selectors:
                elements = ad_element.find_elements(By.XPATH, selector)
                for element in elements:
                    src = element.get_attribute('src')
                    if src and src.startswith("http") and "profile_pic" not in src and "icon" not in src:
                        # Check dimensions to filter out tiny icons
                        try:
                            width = int(element.get_attribute('width') or 0)
                            height = int(element.get_attribute('height') or 0)
                            if width < 50 or height < 50:
                                continue
                        except:
                            pass
                            
                        # Add to image URLs if not already there
                        if src not in ad_data["image_urls"]:
                            ad_data["image_urls"].append(src)
                            
                            # Try to capture image for color analysis
                            if self.extract_visual_elements and image_processing_available:
                                try:
                                    # We'll collect image content for processing later
                                    pass
                                except:
                                    pass
            
            # Extract videos - 2024 updated selectors
            video_selectors = [
                ".//video",
                ".//div[contains(@class, 'xh8yej3')]//video",  # 2024 container
                ".//div[contains(@class, 'x1lq5wgf')]//video",  # Alternative container
                ".//div[contains(@data-videourl, 'http')]"  # Data attribute
            ]
            
            for selector in video_selectors:
                elements = ad_element.find_elements(By.XPATH, selector)
                for element in elements:
                    src = element.get_attribute('src')
                    if not src:
                        # Try to get from data attribute
                        src = element.get_attribute('data-videourl')
                    
                    if src and src.startswith("http"):
                        # Add to video URLs if not already there
                        if src not in ad_data["video_urls"]:
                            ad_data["video_urls"].append(src)
            
            # Extract date information - 2024 updated selectors and patterns
            date_selectors = [
                ".//div[contains(text(), 'Start')]//parent::div",
                ".//div[contains(text(), 'Active date')]//following-sibling::div",
                ".//div[contains(text(), 'Started running')]//parent::div",
                ".//div[contains(text(), 'Running from')]//parent::div"
            ]
            
            for selector in date_selectors:
                elements = ad_element.find_elements(By.XPATH, selector)
                for element in elements:
                    text = element.text.strip()
                    if text:
                        # Try different date formats
                        if " to " in text:
                            parts = text.split(" to ")
                            if len(parts) == 2:
                                ad_data["start_date"] = parts[0].strip()
                                if parts[1].strip().lower() != "present":
                                    ad_data["end_date"] = parts[1].strip()
                        elif "Started" in text:
                            match = re.search(r'Started[:\s]+(.+?)(?:$|\n)', text)
                            if match:
                                ad_data["start_date"] = match.group(1).strip()
                        elif "running on" in text:
                            match = re.search(r'running on[:\s]+(.+?)(?:$|\n)', text)
                            if match:
                                ad_data["start_date"] = match.group(1).strip()
                        elif "from" in text:
                            match = re.search(r'from[:\s]+(.+?)(?:\s+to\s+(.+?))?(?:$|\n)', text)
                            if match:
                                ad_data["start_date"] = match.group(1).strip()
                                if match.group(2) and match.group(2).lower() != "present":
                                    ad_data["end_date"] = match.group(2).strip()
                        break
                
                if ad_data["start_date"]:
                    break
            
            # Determine ad status based on date info
            if ad_data["start_date"]:
                if ad_data["end_date"]:
                    ad_data["status"] = "inactive"
                else:
                    ad_data["status"] = "active"
            
            # Extract engagement metrics if enabled
            if self.extract_engagement_metrics:
                self._extract_engagement_metrics(ad_data, ad_element)
            
            # Final validation - check minimal requirements for a valid ad
            if ((ad_data["page_name"] or ad_data["ad_text"] or ad_data["headline"]) and 
                ad_data["ad_id"] and 
                not self._is_ui_text(ad_data["headline"]) and 
                not self._is_ui_text(ad_data["ad_text"])):
                return ad_data
            else:
                return None
            
        except Exception as e:
            if self.debug_mode:
                self.logger.debug(f"Error extracting ad data: {str(e)}")
            return None
    
    def _filter_relevant_ads(self, elements, keyword_terms):
        """
        Filter elements to only those that appear to be relevant product ads,
        excluding UI elements and system messages.
        
        Args:
            elements: List of WebElements to filter
            keyword_terms: Search keyword string
            
        Returns:
            List of WebElements containing relevant ads
        """
        relevant_elements = []
        
        # Split keyword into separate terms for more flexible matching
        keyword_terms = [term.lower() for term in keyword_terms.split()]
        
        # First pass - remove obvious UI elements and get text for all elements
        element_texts = []
        filtered_elements = []
        
        for element in elements[:100]:  # Only check first 100 elements for performance
            try:
                # Get text content
                text = element.text.lower()
                
                # Skip empty elements
                if not text.strip():
                    continue
                
                # Skip UI elements - critical for avoiding Facebook interface components!
                if any(pattern in text for pattern in self.ui_element_patterns):
                    continue
                
                # Add to our initial filtered list
                filtered_elements.append(element)
                element_texts.append(text)
            except Exception as e:
                if self.debug_mode:
                    self.logger.debug(f"Error filtering element: {str(e)}")
                continue
        
        # Second pass - check for keyword relevance and ad features
        for i, element in enumerate(filtered_elements):
            try:
                text = element_texts[i]
                
                # Skip elements that are too short (likely UI elements)
                if len(text) < 50:
                    continue
                
                # Primary relevance check - contains keywords
                keyword_match = any(term in text for term in keyword_terms)
                
                # Secondary features that suggest this is an ad
                has_cta = any(cta.lower() in text for cta in ["shop", "buy", "learn", "sign up", "download", "get", "order"])
                has_ad_phrases = any(phrase in text for phrase in ["limited time", "offer", "sale", "discount", "new", "introducing", "try now"])
                
                # Check if element has image/video (common in ads)
                has_media = bool(element.find_elements(By.TAG_NAME, "img") or element.find_elements(By.TAG_NAME, "video"))
                
                # Scoring system - ads should match multiple criteria
                score = 0
                if keyword_match: score += 3  # High importance
                if has_cta: score += 2        # Medium importance
                if has_ad_phrases: score += 1  # Low importance
                if has_media: score += 1      # Low importance
                
                # For broader keyword matches (like brand names), be more lenient
                if len(keyword_terms) == 1 and len(keyword_terms[0]) < 6:  # Short single keyword
                    min_score = 3  # Require stronger evidence for short keywords
                else:
                    min_score = 2  # More lenient for longer/multiple keywords
                
                # Add if passes threshold
                if score >= min_score:
                    relevant_elements.append(element)
                    
                    # Cap at reasonable number per search
                    if len(relevant_elements) >= 30:
                        break
            except Exception as e:
                if self.debug_mode:
                    self.logger.debug(f"Error in relevance check: {str(e)}")
                continue
        
        self.logger.info(f"Filtered down to {len(relevant_elements)} relevant ad elements from {len(elements)} total")
        return relevant_elements
    
    def _enhance_ad_data(self, ad_data: Dict[str, Any], element_or_soup) -> None:
        """
        Enhance ad data with advanced metadata: visual elements, engagement metrics,
        industry categorization, and positioning analysis.
        
        Args:
            ad_data: Ad dictionary to enhance
            element_or_soup: WebElement or BeautifulSoup element containing the ad
        """
        # Initialize metadata if needed
        if 'metadata' not in ad_data:
            ad_data['metadata'] = {}
        
        # Extract formatted ad parameters
        ad_format = self._determine_ad_format(ad_data)
        ad_data['metadata']['ad_format'] = ad_format
        
        # Determine product features from text
        if 'ad_text' in ad_data and ad_data['ad_text']:
            # Extract product features
            features = self._extract_product_features(ad_data['ad_text'])
            if features:
                ad_data['metadata']['product_features'] = features
        
        # Categorize ad by industry if enabled
        if self.categorize_ads:
            # Determine industry
            industry = self._categorize_industry(ad_data)
            if industry:
                ad_data['metadata']['industry'] = industry
            
            # Determine positioning
            positioning = self._determine_positioning(ad_data)
            if positioning:
                ad_data['metadata']['positioning'] = positioning
        
        # Extract visual elements if enabled
        if self.extract_visual_elements and ad_data.get('image_urls'):
            try:
                # Process in browser or with requests based on element type
                if hasattr(element_or_soup, 'find_elements'):  # Selenium WebElement
                    visual_elements = self._extract_visual_elements_from_element(element_or_soup, ad_data)
                else:  # BeautifulSoup element
                    visual_elements = self._extract_visual_elements_from_soup(element_or_soup, ad_data)
                
                if visual_elements:
                    ad_data['metadata']['visual_elements'] = visual_elements
            except Exception as e:
                self.logger.debug(f"Error extracting visual elements: {str(e)}")
        
        # Generate image prompt from ad content
        image_prompt = self._generate_image_prompt(ad_data)
        if image_prompt:
            ad_data['metadata']['image_prompt'] = image_prompt
    
    def _determine_ad_format(self, ad_data: Dict[str, Any]) -> str:
        """
        Determine the format of an ad based on its content.
        
        Args:
            ad_data: Ad dictionary
            
        Returns:
            Ad format string
        """
        if ad_data.get('video_urls'):
            return "video"
        elif len(ad_data.get('image_urls', [])) > 1:
            return "carousel"
        elif ad_data.get('image_urls'):
            return "image"
        else:
            return "text"
    
    def _extract_product_features(self, text: str) -> List[str]:
        """
        Extract product features from ad text.
        
        Args:
            text: Ad text to analyze
            
        Returns:
            List of product features
        """
        features = []
        
        # Check for bullet points and lists
        bullet_patterns = [
            r'•\s*([^•\n]+)',  # Bullet points
            r'✓\s*([^✓\n]+)',  # Checkmarks
            r'✅\s*([^✅\n]+)',  # Check emoji
            r'★\s*([^★\n]+)',  # Stars
            r'\d+\.\s+([^\d\n]+)',  # Numbered lists
            r'\n-\s*([^-\n]+)'  # Dash bullet points
        ]
        
        for pattern in bullet_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                feature = match.strip()
                if 5 < len(feature) < 100 and feature not in features:
                    features.append(feature)
        
        # Check for feature phrases
        feature_phrases = [
            r'featuring ([^\.]+)',
            r'comes with ([^\.]+)',
            r'includes ([^\.]+)',
            r'offers ([^\.]+)',
            r'provides ([^\.]+)'
        ]
        
        for pattern in feature_phrases:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                feature = match.strip()
                if 5 < len(feature) < 100 and feature not in features:
                    features.append(feature)
        
        # If we have few features, look for emoji-separated text
        if len(features) < 2:
            emoji_parts = re.split(r'[⭐️✅✓★➡️🔥🌟👉👍]', text)
            if len(emoji_parts) > 1:
                for part in emoji_parts[1:]:  # Skip first part which is often not a feature
                    clean_part = part.strip()
                    if 5 < len(clean_part) < 100 and not clean_part in features:
                        # Check if this looks like a feature (short, punchy)
                        if len(clean_part.split()) < 10:
                            features.append(clean_part)
        
        # If still no features, try to extract short phrases that could be features
        if len(features) < 2:
            sentences = re.split(r'[.!?]', text)
            for sentence in sentences:
                words = sentence.split()
                if 2 <= len(words) <= 7:  # Short phrases that could be features
                    clean_sentence = sentence.strip()
                    if clean_sentence and not clean_sentence in features:
                        features.append(clean_sentence)
        
        # Return a limited number of the most likely features
        return features[:5]
    
    def _categorize_industry(self, ad_data: Dict[str, Any]) -> str:
        """
        Categorize ad by industry based on content.
        
        Args:
            ad_data: Ad dictionary
            
        Returns:
            Industry category string
        """
        # Try to use cached result first
        ad_id = ad_data.get('ad_id', '')
        if ad_id and ad_id in self._industry_cache:
            return self._industry_cache[ad_id]
        
        # Combine all text content for analysis
        combined_text = ' '.join([
            ad_data.get('page_name', ''),
            ad_data.get('headline', ''),
            ad_data.get('ad_text', ''),
            ad_data.get('cta_text', '')
        ]).lower()
        
        # Count keyword matches for each industry
        industry_scores = {}
        
        for industry, keywords in INDUSTRY_KEYWORDS.items():
            matches = 0
            for keyword in keywords:
                if keyword in combined_text:
                    # Count number of matches (more weight for multiple occurrences)
                    count = combined_text.count(keyword)
                    matches += count
            
            if matches > 0:
                industry_scores[industry] = matches
        
        # Select industry with highest score
        if industry_scores:
            top_industry = max(industry_scores.items(), key=lambda x: x[1])[0]
            
            # Cache the result
            if ad_id:
                self._industry_cache[ad_id] = top_industry
                
            return top_industry
        
        # Default if no matches
        return "Other"
    
    def _determine_positioning(self, ad_data: Dict[str, Any]) -> str:
        """
        Determine the brand positioning based on ad content.
        
        Args:
            ad_data: Ad dictionary
            
        Returns:
            Positioning category string
        """
        # Try to use cached result first
        ad_id = ad_data.get('ad_id', '')
        if ad_id and ad_id in self._positioning_cache:
            return self._positioning_cache[ad_id]
        
        # Combine all text content for analysis
        combined_text = ' '.join([
            ad_data.get('page_name', ''),
            ad_data.get('headline', ''),
            ad_data.get('ad_text', ''),
            ad_data.get('cta_text', '')
        ]).lower()
        
        # Count keyword matches for each positioning
        positioning_scores = {}
        
        for positioning, keywords in POSITIONING_KEYWORDS.items():
            matches = 0
            for keyword in keywords:
                if keyword in combined_text:
                    # Count number of matches
                    count = combined_text.count(keyword)
                    matches += count
            
            if matches > 0:
                positioning_scores[positioning] = matches
        
        # Select positioning with highest score
        if positioning_scores:
            top_positioning = max(positioning_scores.items(), key=lambda x: x[1])[0]
            
            # Cache the result
            if ad_id:
                self._positioning_cache[ad_id] = top_positioning
                
            return top_positioning
        
        # Default if no matches
        return "General"# Continuation of the FacebookAdsScraper class methods
# Add this to the same file after the previous code
    
    def _extract_engagement_metrics(self, ad_data: Dict[str, Any], element) -> None:
        """
        Extract engagement metrics (likes, comments, shares) from ad element.
        
        Args:
            ad_data: Ad dictionary to update
            element: WebElement or BeautifulSoup element containing the ad
        """
        if not self.extract_engagement_metrics:
            return
            
        try:
            engagement_metrics = {
                "likes": 0,
                "comments": 0,
                "shares": 0,
            }
            
            # For Selenium WebElement
            if hasattr(element, 'find_elements'):
                # Look for like count
                like_selectors = [
                    ".//span[contains(text(), 'like') or contains(text(), 'Love')]",
                    ".//span[contains(@aria-label, 'like') or contains(@aria-label, 'Love')]"
                ]
                
                for selector in like_selectors:
                    elements = element.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.lower()
                        if 'like' in text or 'love' in text:
                            match = re.search(r'(\d+)[k\s]*', text)
                            if match:
                                num = match.group(1)
                                if 'k' in text.lower():
                                    engagement_metrics["likes"] = int(float(num) * 1000)
                                else:
                                    engagement_metrics["likes"] = int(num)
                                break
                
                # Look for comment count
                comment_selectors = [
                    ".//span[contains(text(), 'comment')]",
                    ".//span[contains(@aria-label, 'comment')]"
                ]
                
                for selector in comment_selectors:
                    elements = element.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.lower()
                        if 'comment' in text:
                            match = re.search(r'(\d+)[k\s]*', text)
                            if match:
                                num = match.group(1)
                                if 'k' in text.lower():
                                    engagement_metrics["comments"] = int(float(num) * 1000)
                                else:
                                    engagement_metrics["comments"] = int(num)
                                break
                
                # Look for share count
                share_selectors = [
                    ".//span[contains(text(), 'share')]",
                    ".//span[contains(@aria-label, 'share')]"
                ]
                
                for selector in share_selectors:
                    elements = element.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.lower()
                        if 'share' in text:
                            match = re.search(r'(\d+)[k\s]*', text)
                            if match:
                                num = match.group(1)
                                if 'k' in text.lower():
                                    engagement_metrics["shares"] = int(float(num) * 1000)
                                else:
                                    engagement_metrics["shares"] = int(num)
                                break
            
            # For BeautifulSoup element
            else:
                # Look for like count
                like_elements = element.select('span:-soup-contains("like"), span:-soup-contains("Love")')
                for elem in like_elements:
                    text = elem.get_text().lower()
                    if 'like' in text or 'love' in text:
                        match = re.search(r'(\d+)[k\s]*', text)
                        if match:
                            num = match.group(1)
                            if 'k' in text.lower():
                                engagement_metrics["likes"] = int(float(num) * 1000)
                            else:
                                engagement_metrics["likes"] = int(num)
                            break
                
                # Look for comment count
                comment_elements = element.select('span:-soup-contains("comment")')
                for elem in comment_elements:
                    text = elem.get_text().lower()
                    if 'comment' in text:
                        match = re.search(r'(\d+)[k\s]*', text)
                        if match:
                            num = match.group(1)
                            if 'k' in text.lower():
                                engagement_metrics["comments"] = int(float(num) * 1000)
                            else:
                                engagement_metrics["comments"] = int(num)
                            break
                
                # Look for share count
                share_elements = element.select('span:-soup-contains("share")')
                for elem in share_elements:
                    text = elem.get_text().lower()
                    if 'share' in text:
                        match = re.search(r'(\d+)[k\s]*', text)
                        if match:
                            num = match.group(1)
                            if 'k' in text.lower():
                                engagement_metrics["shares"] = int(float(num) * 1000)
                            else:
                                engagement_metrics["shares"] = int(num)
                            break
            
            # Add metrics to ad data if any were found
            if any(engagement_metrics.values()):
                ad_data['metadata']['engagement_metrics'] = engagement_metrics
                
        except Exception as e:
            self.logger.debug(f"Error extracting engagement metrics: {str(e)}")
    
    def _extract_visual_elements_from_element(self, element, ad_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract visual elements from a Selenium WebElement.
        
        Args:
            element: WebElement containing the ad
            ad_data: Ad dictionary with image URLs
            
        Returns:
            Dictionary of visual elements
        """
        if not image_processing_available:
            return {}
            
        visual_elements = {
            "color_scheme": [],
            "image_text_ratio": 0.0,
            "background_style": "Unknown",
            "typography_style": "Unknown",
            "product_placement": "Unknown"
        }
        
        try:
            # Detect text/image ratio
            text_elements = len(element.find_elements(By.XPATH, ".//div[string-length(text()) > 10]"))
            image_elements = len(element.find_elements(By.TAG_NAME, "img"))
            
            if text_elements + image_elements > 0:
                visual_elements["image_text_ratio"] = round(image_elements / (text_elements + image_elements), 2)
            
            # Try to capture screenshot for color analysis
            if not ad_data.get('image_urls'):
                return visual_elements
                
            # Extract colors from images
            image_url = ad_data['image_urls'][0] if ad_data['image_urls'] else None
            if image_url:
                try:
                    # Get image using requests
                    response = requests.get(image_url, timeout=5)
                    if response.status_code == 200:
                        image = Image.open(io.BytesIO(response.content))
                        colors = self._extract_colors_from_image(image)
                        if colors:
                            visual_elements["color_scheme"] = colors
                except Exception as img_error:
                    self.logger.debug(f"Error analyzing image colors: {str(img_error)}")
            
            # Detect typography style based on font classes
            typography_indicators = {
                "Sans-serif": ["arial", "helvetica", "x1lliihq", "sans"],
                "Serif": ["georgia", "times", "serif"],
                "Modern": ["futura", "avenir", "modern"],
                "Bold": ["bold", "strong", "x1heor9g"],
                "Light": ["light", "thin"],
                "Script": ["script", "cursive", "handwriting"]
            }
            
            for style, indicators in typography_indicators.items():
                html = element.get_attribute('innerHTML').lower()
                if any(ind in html for ind in indicators):
                    visual_elements["typography_style"] = style
                    break
            
            # Detect background style
            background_indicators = {
                "Solid Color": ["background-color:", "background:", "solid"],
                "Gradient": ["gradient", "linear-gradient"],
                "Image": ["background-image:", "scontent"],
                "Pattern": ["pattern", "texture", "repeat"],
                "Lifestyle": ["lifestyle", "people", "person", "using", "wearing"]
            }
            
            for style, indicators in background_indicators.items():
                html = element.get_attribute('innerHTML').lower()
                if any(ind in html for ind in indicators):
                    visual_elements["background_style"] = style
                    break
            
            # Detect product placement
            img_elements = element.find_elements(By.TAG_NAME, "img")
            if img_elements:
                # Check image positions
                for img in img_elements:
                    if img.is_displayed() and img.size['width'] > 100:  # Only consider visible, reasonably sized images
                        try:
                            location = img.location
                            size = img.size
                            
                            # Determine position based on X coordinate
                            viewport_width = element.size['width']
                            center_x = location['x'] + (size['width'] / 2)
                            
                            if center_x < viewport_width * 0.4:
                                visual_elements["product_placement"] = "Left side"
                            elif center_x > viewport_width * 0.6:
                                visual_elements["product_placement"] = "Right side"
                            else:
                                visual_elements["product_placement"] = "Center"
                                
                            break  # Just use the first significant image
                        except:
                            pass
            
            return visual_elements
            
        except Exception as e:
            self.logger.debug(f"Error extracting visual elements from element: {str(e)}")
            return visual_elements
    
    def _extract_visual_elements_from_soup(self, soup_element, ad_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract visual elements from a BeautifulSoup element.
        
        Args:
            soup_element: BeautifulSoup element containing the ad
            ad_data: Ad dictionary with image URLs
            
        Returns:
            Dictionary of visual elements
        """
        if not image_processing_available:
            return {}
            
        visual_elements = {
            "color_scheme": [],
            "image_text_ratio": 0.0,
            "background_style": "Unknown",
            "typography_style": "Unknown",
            "product_placement": "Unknown"
        }
        
        try:
            # Detect text/image ratio
            text_elements = len(soup_element.select('div'))  # Approximate
            image_elements = len(soup_element.select('img'))
            
            if text_elements + image_elements > 0:
                visual_elements["image_text_ratio"] = round(image_elements / (text_elements + image_elements), 2)
            
            # Extract colors from images
            image_url = ad_data['image_urls'][0] if ad_data.get('image_urls') else None
            if image_url:
                try:
                    # Get image using requests
                    response = requests.get(image_url, timeout=5)
                    if response.status_code == 200:
                        image = Image.open(io.BytesIO(response.content))
                        colors = self._extract_colors_from_image(image)
                        if colors:
                            visual_elements["color_scheme"] = colors
                except Exception as img_error:
                    self.logger.debug(f"Error analyzing image colors: {str(img_error)}")
            
            # Detect typography style based on classes
            typography_indicators = {
                "Sans-serif": ["arial", "helvetica", "x1lliihq", "sans"],
                "Serif": ["georgia", "times", "serif"],
                "Modern": ["futura", "avenir", "modern"],
                "Bold": ["bold", "strong", "x1heor9g"],
                "Light": ["light", "thin"],
                "Script": ["script", "cursive", "handwriting"]
            }
            
            html_str = str(soup_element).lower()
            for style, indicators in typography_indicators.items():
                if any(ind in html_str for ind in indicators):
                    visual_elements["typography_style"] = style
                    break
            
            # Detect background style
            background_indicators = {
                "Solid Color": ["background-color:", "background:", "solid"],
                "Gradient": ["gradient", "linear-gradient"],
                "Image": ["background-image:", "scontent"],
                "Pattern": ["pattern", "texture", "repeat"],
                "Lifestyle": ["lifestyle", "people", "person", "using", "wearing"]
            }
            
            for style, indicators in background_indicators.items():
                if any(ind in html_str for ind in indicators):
                    visual_elements["background_style"] = style
                    break
            
            # Detect product placement
            images = soup_element.select('img')
            if images:
                # Extract any positioning attributes
                for img in images:
                    if 'style' in img.attrs:
                        style = img['style'].lower()
                        if 'left' in style:
                            visual_elements["product_placement"] = "Left side"
                        elif 'right' in style:
                            visual_elements["product_placement"] = "Right side"
                        elif 'center' in style or 'margin:auto' in style:
                            visual_elements["product_placement"] = "Center"
                        break
            
            return visual_elements
            
        except Exception as e:
            self.logger.debug(f"Error extracting visual elements from soup: {str(e)}")
            return visual_elements
    
    def _extract_colors_from_image(self, image) -> List[str]:
        """
        Extract dominant colors from an image.
        
        Args:
            image: PIL Image object
            
        Returns:
            List of hex color codes
        """
        try:
            # Resize image for faster processing
            image = image.resize((100, 100))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get image data
            pixels = list(image.getdata())
            
            # Cluster similar colors
            color_counts = {}
            for pixel in pixels:
                # Normalize the color to reduce variations
                normalized = (pixel[0] // 10 * 10, pixel[1] // 10 * 10, pixel[2] // 10 * 10)
                if normalized in color_counts:
                    color_counts[normalized] += 1
                else:
                    color_counts[normalized] = 1
            
            # Sort by frequency
            sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Convert to hex, keeping only distinct colors (using HSV distance)
            distinct_colors = []
            for color, _ in sorted_colors[:10]:  # Check top 10 colors
                # Convert to hex
                hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
                
                # Calculate HSV for better perceptual distance
                h, s, v = colorsys.rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)
                
                # Check if this color is distinct from colors we've already added
                is_distinct = True
                for existing_color in distinct_colors:
                    # Convert existing hex to RGB
                    r = int(existing_color[1:3], 16)
                    g = int(existing_color[3:5], 16)
                    b = int(existing_color[5:7], 16)
                    
                    # Convert to HSV
                    existing_h, existing_s, existing_v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
                    
                    # Calculate distance in HSV space
                    h_diff = min(abs(h - existing_h), 1 - abs(h - existing_h))
                    s_diff = abs(s - existing_s)
                    v_diff = abs(v - existing_v)
                    
                    # If colors are too similar, don't add
                    if h_diff * 0.5 + s_diff * 0.3 + v_diff * 0.2 < 0.15:  # Weighted distance threshold
                        is_distinct = False
                        break
                
                if is_distinct:
                    distinct_colors.append(hex_color)
                    if len(distinct_colors) >= 3:  # Only need top 3 distinct colors
                        break
            
            return distinct_colors
        except Exception as e:
            self.logger.debug(f"Error extracting colors from image: {str(e)}")
            return []
    
    def _compute_ad_quality_score(self, ad_data: Dict[str, Any]) -> float:
        """
        Compute a quality score for an ad based on various factors.
        
        Args:
            ad_data: Ad dictionary
            
        Returns:
            Quality score from 0-10
        """
        score = 5.0  # Start with a neutral score
        
        try:
            # Factor 1: Content completeness (0-2 points)
            completeness = 0
            if ad_data.get('page_name'): completeness += 0.4
            if ad_data.get('headline'): completeness += 0.4
            if ad_data.get('ad_text'): completeness += 0.6
            if ad_data.get('cta_text'): completeness += 0.4
            if ad_data.get('image_urls') or ad_data.get('video_urls'): completeness += 0.2
            
            score += completeness
            
            # Factor 2: Content length (0-2 points)
            content_length = 0
            headline_len = len(ad_data.get('headline', ''))
            ad_text_len = len(ad_data.get('ad_text', ''))
            
            if 15 <= headline_len <= 100: content_length += 0.5
            if headline_len > 100: content_length += 0.3  # Overly long headlines are less ideal
            
            if 50 <= ad_text_len <= 300: content_length += 1.0
            elif 300 < ad_text_len <= 500: content_length += 0.7  # Longer but still reasonable
            elif ad_text_len > 500: content_length += 0.3  # Overly long text is less ideal
            
            if ad_data.get('cta_text') and 2 <= len(ad_data.get('cta_text', '')) <= 20:
                content_length += 0.5
            
            score += content_length
            
            # Factor 3: Media richness (0-1.5 points)
            media_score = 0
            if ad_data.get('video_urls'): media_score += 1.5
            elif len(ad_data.get('image_urls', [])) > 1: media_score += 1.0  # Multiple images
            elif ad_data.get('image_urls'): media_score += 0.7  # Single image
            
            score += media_score
            
            # Factor 4: Engagement metrics if available (0-1.5 points)
            engagement_score = 0
            engagement_metrics = ad_data.get('metadata', {}).get('engagement_metrics', {})
            
            if engagement_metrics:
                likes = engagement_metrics.get('likes', 0)
                comments = engagement_metrics.get('comments', 0)
                shares = engagement_metrics.get('shares', 0)
                
                # More weight to shares and comments as they indicate higher engagement
                engagement_value = likes * 0.2 + comments * 0.4 + shares * 0.4
                
                # Logarithmic scale to handle wide range of values
                if engagement_value > 0:
                    engagement_score = min(1.5, 0.3 * np.log10(1 + engagement_value))
            
            score += engagement_score
            
            # Factor 5: Brand and industry clarity (0-1 point)
            brand_score = 0
            if ad_data.get('page_name') and len(ad_data.get('page_name', '')) > 2:
                brand_score += 0.3
            
            if ad_data.get('metadata', {}).get('industry'):
                brand_score += 0.5
            
            if ad_data.get('metadata', {}).get('positioning'):
                brand_score += 0.2
            
            score += brand_score
            
            # Factor 6: Call to action quality (0-1 point)
            cta_score = 0
            cta_text = ad_data.get('cta_text', '').lower()
            
            # Check if CTA is in standard categories
            for category, phrases in CTA_CATEGORIES.items():
                if any(phrase in cta_text for phrase in phrases):
                    cta_score += 0.7
                    break
            
            # Extra points for link URL
            if ad_data.get('link_url'):
                cta_score += 0.3
            
            score += cta_score
            
            # Factor 7: Product features clarity (0-1 point)
            feature_score = 0
            if ad_data.get('metadata', {}).get('product_features'):
                features = ad_data.get('metadata', {}).get('product_features')
                feature_score += min(1.0, len(features) * 0.2)  # Up to 1 point based on number of features
            
            score += feature_score
            
            # Cap the score at 10
            score = min(10.0, score)
            
            # Round to one decimal place
            return round(score, 1)
            
        except Exception as e:
            self.logger.debug(f"Error computing ad quality score: {str(e)}")
            return 5.0  # Return neutral score on error
    
    def _generate_image_prompt(self, ad_data: Dict[str, Any]) -> str:
        """
        Generate an image prompt for recreating the ad's visual appearance.
        
        Args:
            ad_data: Ad dictionary
            
        Returns:
            Image prompt string
        """
        try:
            # Extract relevant information
            brand = ad_data.get('page_name', '')
            headline = ad_data.get('headline', '')
            industry = ad_data.get('metadata', {}).get('industry', '')
            positioning = ad_data.get('metadata', {}).get('positioning', '')
            
            # Default prompt structure
            prompt_parts = []
            
            # Start with ad type and style
            ad_format = ad_data.get('metadata', {}).get('ad_format', 'image')
            
            if ad_format == 'video':
                prompt_parts.append(f"Create a video advertisement")
            elif ad_format == 'carousel':
                prompt_parts.append(f"Create a carousel advertisement with multiple images")
            else:
                prompt_parts.append(f"Create a commercial advertisement image")
            
            # Add brand and product info
            if brand:
                if headline:
                    prompt_parts.append(f"for {brand} featuring \"{headline}\"")
                else:
                    prompt_parts.append(f"for {brand}")
            
            # Add industry context
            if industry and industry != "Other":
                prompt_parts.append(f"in the {industry} industry")
            
            # Add positioning
            if positioning and positioning != "General":
                if positioning == "Luxury":
                    prompt_parts.append(f"with a luxury, high-end aesthetic")
                elif positioning == "Value":
                    prompt_parts.append(f"emphasizing value and affordability")
                elif positioning == "Performance":
                    prompt_parts.append(f"focusing on performance and effectiveness")
                elif positioning == "Innovation":
                    prompt_parts.append(f"highlighting innovative and cutting-edge aspects")
                elif positioning == "Wellness":
                    prompt_parts.append(f"with a clean, healthy, wellness aesthetic")
                elif positioning == "Lifestyle":
                    prompt_parts.append(f"with a lifestyle-oriented approach")
                elif positioning == "Family":
                    prompt_parts.append(f"with a family-friendly approach")
                elif positioning == "Experience":
                    prompt_parts.append(f"emphasizing the experiential aspects")
            
            # Add visual elements if available
            visual_elements = ad_data.get('metadata', {}).get('visual_elements', {})
            
            if visual_elements:
                # Add color scheme
                if visual_elements.get('color_scheme'):
                    colors = ', '.join(visual_elements.get('color_scheme', [])[:3])
                    prompt_parts.append(f"using a color scheme of {colors}")
                
                # Add background style
                background = visual_elements.get('background_style')
                if background and background != "Unknown":
                    prompt_parts.append(f"with a {background.lower()} background")
                
                # Add typography style
                typography = visual_elements.get('typography_style')
                if typography and typography != "Unknown":
                    prompt_parts.append(f"using {typography.lower()} typography")
                
                # Add product placement
                placement = visual_elements.get('product_placement')
                if placement and placement != "Unknown":
                    prompt_parts.append(f"with the product positioned on the {placement.lower()}")
            
            # Add product features if available
            features = ad_data.get('metadata', {}).get('product_features', [])
            if features and len(features) > 0:
                # Take up to 3 features
                feature_list = ', '.join([f'"{f}"' for f in features[:3]])
                prompt_parts.append(f"highlighting key features: {feature_list}")
            
            # Combine parts into a complete prompt
            prompt = ' '.join(prompt_parts)
            
            return prompt
            
        except Exception as e:
            self.logger.debug(f"Error generating image prompt: {str(e)}")
            return ""# Final methods for the FacebookAdsScraper class
# Add this to the same file after the previous code

    def _save_ads_batch(self, ads: List[Dict[str, Any]], filename: str) -> None:
        """
        Save a batch of ads to a JSON file.
        
        Args:
            ads: List of ad dictionaries
            filename: Output filename
        """
        try:
            if not ads:
                return
            
            # Create full output path
            filepath = os.path.join(self.output_dir, 'raw', filename)
            
            # Save to JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(
                    {
                        "metadata": {
                            "scrape_time": datetime.now().isoformat(),
                            "ads_count": len(ads),
                            "performance": {
                                "browser_type": self.browser_type,
                                "automation_method": automation_method,
                                "scrolls": self.performance_metrics['total_scroll_count'],
                                "captcha_encounters": self.performance_metrics['captcha_encounters'],
                                "login_blocks": self.performance_metrics['login_block_encounters'],
                                "avg_extraction_time": sum(self.performance_metrics['extraction_times'])/max(1, len(self.performance_metrics['extraction_times']))
                            }
                        },
                        "ads": ads
                    },
                    f,
                    indent=2
                )
            
            self.logger.info(f"Saved {len(ads)} ads to {filepath}")
            
            # Save example images for a subset of ads
            self._save_sample_images(ads[:min(5, len(ads))])
            
        except Exception as e:
            self.logger.error(f"Error saving ads: {str(e)}")
    
    def _save_sample_images(self, ads: List[Dict[str, Any]]) -> None:
        """
        Save sample images from ads for inspection.
        
        Args:
            ads: List of ad dictionaries
        """
        if not image_processing_available:
            return
            
        try:
            for i, ad in enumerate(ads):
                # Skip if no images
                if not ad.get('image_urls'):
                    continue
                    
                # Get the first image
                image_url = ad['image_urls'][0]
                
                try:
                    # Download image
                    response = requests.get(image_url, timeout=5)
                    if response.status_code == 200:
                        # Create image filename
                        brand = re.sub(r'[^\w\s-]', '', ad.get('page_name', f'ad_{i}'))[:30]
                        brand = brand.replace(' ', '_')
                        
                        filename = f"{brand}_{ad.get('ad_id', str(i))[:8]}.jpg"
                        filepath = os.path.join(self.output_dir, 'images', filename)
                        
                        # Save image
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                            
                        # Add image path to ad data
                        if 'metadata' not in ad:
                            ad['metadata'] = {}
                        ad['metadata']['saved_image_path'] = filepath
                        
                except Exception as img_error:
                    self.logger.debug(f"Error saving sample image: {str(img_error)}")
                    
        except Exception as e:
            self.logger.debug(f"Error saving sample images: {str(e)}")
    
    def process_ads_for_training(self) -> List[Dict[str, Any]]:
        """
        Process collected ads into a format suitable for LLM training with enhanced metadata.
        
        Returns:
            List of processed ad examples in the requested training format
        """
        processed_data = []
        
        try:
            if not self.scraped_ads:
                self.logger.warning("No ads to process")
                return []
            
            # Log progress
            self.logger.info(f"Processing {len(self.scraped_ads)} ads for training data")
            
            for ad in self.scraped_ads:
                # Skip ads without essential content
                if not (ad.get('ad_text') or ad.get('headline')):
                    continue
                
                # Skip low quality ads if quality score is available
                quality_score = ad.get('metadata', {}).get('quality_score', 0)
                if quality_score > 0 and quality_score < self.min_quality_score:
                    continue
                
                # Format as requested in the ideal output specification
                # This format specifically matches what was requested in the prompt
                
                # Create input section
                input_data = {
                    "product_description": ad.get('headline', ''),
                    "industry": ad.get('metadata', {}).get('industry', 'General'),
                    "positioning": ad.get('metadata', {}).get('positioning', 'General'),
                    "target_audience": self._determine_target_audience(ad)
                }
                
                # Create output section
                output_data = {
                    "headline": ad.get('headline', ''),
                    "subheadline": "",  # Extract from ad_text if possible
                    "body_text": ad.get('ad_text', ''),
                    "call_to_action": ad.get('cta_text', ''),
                    "product_features": ad.get('metadata', {}).get('product_features', []),
                    "image_prompt": ad.get('metadata', {}).get('image_prompt', '')
                }
                
                # Extract subheadline from ad_text if possible
                if ad.get('ad_text'):
                    lines = ad.get('ad_text', '').split('\n')
                    if len(lines) > 1 and 10 <= len(lines[0]) <= 100:
                        output_data["subheadline"] = lines[0]
                
                # Create metadata section
                metadata = {
                    "brand": ad.get('page_name', ''),
                    "engagement_metrics": ad.get('metadata', {}).get('engagement_metrics', {}),
                    "visual_elements": ad.get('metadata', {}).get('visual_elements', {}),
                    "quality_score": ad.get('metadata', {}).get('quality_score', 0)
                }
                
                # Create complete example
                example = {
                    "input": input_data,
                    "output": output_data,
                    "metadata": metadata
                }
                
                processed_data.append(example)
            
            # Save processed data
            processed_filepath = os.path.join(
                self.output_dir, 
                'processed', 
                f"fb_ads_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(processed_filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "source": "facebook_ads_library",
                        "processing_time": datetime.now().isoformat(),
                        "example_count": len(processed_data)
                    },
                    "examples": processed_data
                }, f, indent=2)
            
            self.logger.info(f"Saved {len(processed_data)} processed examples to {processed_filepath}")
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error processing ads for training: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []
    
    def _determine_target_audience(self, ad: Dict[str, Any]) -> str:
        """
        Determine the likely target audience from ad content.
        
        Args:
            ad: Ad dictionary
            
        Returns:
            Target audience description
        """
        try:
            audience = ""
            
            # Get relevant data
            industry = ad.get('metadata', {}).get('industry', '')
            positioning = ad.get('metadata', {}).get('positioning', '')
            text = (ad.get('headline', '') + ' ' + ad.get('ad_text', '')).lower()
            
            # Industry-specific audiences
            if industry == "Beauty & Personal Care":
                if "men" in text:
                    audience = "Men interested in personal care products"
                elif "women" in text:
                    audience = "Women seeking beauty and personal care products"
                else:
                    audience = "Beauty and personal care product shoppers"
                    
            elif industry == "Fashion & Apparel":
                if "women" in text or "female" in text:
                    audience = "Women's fashion shoppers"
                elif "men" in text or "male" in text:
                    audience = "Men's fashion shoppers"
                elif "kids" in text or "children" in text:
                    audience = "Parents shopping for children's clothing"
                else:
                    audience = "Fashion-conscious consumers"
                    
            elif industry == "Food & Beverage":
                if "organic" in text or "healthy" in text:
                    audience = "Health-conscious food shoppers"
                elif "restaurant" in text or "dine" in text:
                    audience = "Restaurant-goers and food enthusiasts"
                else:
                    audience = "Food and beverage consumers"
                    
            elif industry == "Health & Wellness":
                audience = "Health-conscious individuals interested in wellness products"
                
            elif industry == "Technology & Electronics":
                if "gaming" in text:
                    audience = "Gamers looking for tech products"
                else:
                    audience = "Tech-savvy consumers interested in electronics"
                    
            elif industry == "Home & Garden":
                audience = "Homeowners and home decor enthusiasts"
                
            elif industry == "Automotive":
                audience = "Car owners and automotive enthusiasts"
                
            elif industry == "Financial Services":
                audience = "Consumers seeking financial products and services"
                
            elif industry == "Travel & Hospitality":
                audience = "Travel enthusiasts and vacationers"
                
            # Default with positioning if no industry match
            if not audience and positioning:
                if positioning == "Luxury":
                    audience = "Affluent consumers seeking premium products"
                elif positioning == "Value":
                    audience = "Budget-conscious shoppers seeking good value"
                elif positioning == "Performance":
                    audience = "Performance-focused consumers"
                elif positioning == "Innovation":
                    audience = "Early adopters interested in innovative products"
                elif positioning == "Wellness":
                    audience = "Health and wellness-focused individuals"
                elif positioning == "Lifestyle":
                    audience = "Lifestyle-conscious consumers"
                elif positioning == "Family":
                    audience = "Families and parents"
                    
            # Extract demographic terms
            demographic_terms = {
                "age": ["young", "teen", "20s", "30s", "middle-aged", "seniors", "elderly"],
                "gender": ["men", "women", "male", "female"],
                "interests": ["fitness", "sports", "outdoors", "professional", "luxury", "budget", 
                             "gamer", "tech", "fashion", "health"]
            }
            
            demographics = []
            for category, terms in demographic_terms.items():
                for term in terms:
                    if term in text:
                        demographics.append(term)
            
            # Combine demographics with audience if found
            if demographics and audience:
                demographics_str = ', '.join(demographics[:3])
                audience = f"{demographics_str} {audience}"
            
            # Default if nothing found
            if not audience:
                audience = "General consumers interested in this product category"
            
            return audience
                
        except Exception as e:
            self.logger.debug(f"Error determining target audience: {str(e)}")
            return "General consumers interested in this product"
    
    def analyze_ad_patterns(self) -> Dict[str, Any]:
        """
        Analyze patterns in collected ads to identify high-performing formats.
        Includes comprehensive analysis of industries, ad formats, headline patterns,
        text structures, call-to-action types, and visual element trends.
        
        Returns:
            Dictionary with detailed pattern analysis
        """
        try:
            if not self.scraped_ads:
                self.logger.warning("No ads to analyze")
                return {}
            
            self.logger.info(f"Analyzing patterns in {len(self.scraped_ads)} ads")
            
            # Initialize pattern categories
            patterns = {
                "formats": {
                    "image": 0,
                    "video": 0,
                    "carousel": 0,
                    "text_only": 0
                },
                "industry_distribution": {},
                "positioning_distribution": {},
                "cta_types": {},
                "headline_lengths": {
                    "short": 0,  # <5 words
                    "medium": 0,  # 5-10 words
                    "long": 0    # >10 words
                },
                "headline_structures": {
                    "question": 0,
                    "statement": 0,
                    "command": 0,
                    "number_based": 0,
                    "problem_solution": 0
                },
                "text_lengths": {
                    "short": 0,  # <50 words
                    "medium": 0,  # 50-100 words
                    "long": 0    # >100 words
                },
                "text_structures": {
                    "bullet_points": 0,
                    "paragraphs": 0,
                    "single_paragraph": 0,
                    "storytelling": 0
                },
                "common_phrases": {},
                "keyword_frequencies": {},
                "visual_elements": {
                    "color_schemes": {},
                    "typography_styles": {},
                    "background_styles": {},
                    "product_placement": {}
                },
                "high_engagement_characteristics": {
                    "formats": {},
                    "industries": {},
                    "positioning": {},
                    "cta_types": {},
                    "headline_structures": {},
                    "text_structures": {}
                }
            }
            
            # Collect high-engagement ads for pattern analysis
            high_engagement_ads = []
            engagement_thresholds = {
                "likes": 50,
                "comments": 10,
                "shares": 5
            }
            
            # Count ads using different formats
            for ad in self.scraped_ads:
                # Format counts
                if ad.get('video_urls'):
                    patterns["formats"]["video"] += 1
                elif len(ad.get('image_urls', [])) > 1:
                    patterns["formats"]["carousel"] += 1
                elif ad.get('image_urls'):
                    patterns["formats"]["image"] += 1
                else:
                    patterns["formats"]["text_only"] += 1
                
                # Industry distribution
                industry = ad.get('metadata', {}).get('industry', 'Unknown')
                if industry in patterns["industry_distribution"]:
                    patterns["industry_distribution"][industry] += 1
                else:
                    patterns["industry_distribution"][industry] = 1
                
                # Positioning distribution
                positioning = ad.get('metadata', {}).get('positioning', 'Unknown')
                if positioning in patterns["positioning_distribution"]:
                    patterns["positioning_distribution"][positioning] += 1
                else:
                    patterns["positioning_distribution"][positioning] = 1
                
                # CTA types
                cta = ad.get('cta_text', '')
                if cta:
                    # Categorize CTAs
                    cta_category = "Other"
                    for category, phrases in CTA_CATEGORIES.items():
                        if any(phrase in cta.lower() for phrase in phrases):
                            cta_category = category
                            break
                    
                    if cta_category in patterns["cta_types"]:
                        patterns["cta_types"][cta_category] += 1
                    else:
                        patterns["cta_types"][cta_category] = 1
                
                # Headline analysis
                headline = ad.get('headline', '')
                if headline:
                    # Headline length
                    word_count = len(headline.split())
                    if word_count < 5:
                        patterns["headline_lengths"]["short"] += 1
                    elif word_count <= 10:
                        patterns["headline_lengths"]["medium"] += 1
                    else:
                        patterns["headline_lengths"]["long"] += 1
                    
                    # Headline structure
                    headline_lower = headline.lower()
                    if headline.endswith('?'):
                        patterns["headline_structures"]["question"] += 1
                    elif headline.startswith('How to') or headline.startswith('Why') or headline.startswith('What'):
                        patterns["headline_structures"]["question"] += 1
                    elif headline.startswith('Get') or headline.startswith('Try') or headline.startswith('Discover') or headline.startswith('Learn'):
                        patterns["headline_structures"]["command"] += 1
                    elif any(headline.startswith(str(n)) for n in range(1, 11)) or "top" in headline_lower:
                        patterns["headline_structures"]["number_based"] += 1
                    elif any(phrase in headline_lower for phrase in ["problem", "solution", "struggle", "fix", "solve", "issue"]):
                        patterns["headline_structures"]["problem_solution"] += 1
                    else:
                        patterns["headline_structures"]["statement"] += 1
                
                # Text analysis
                text = ad.get('ad_text', '')
                if text:
                    # Text length
                    word_count = len(text.split())
                    if word_count < 50:
                        patterns["text_lengths"]["short"] += 1
                    elif word_count <= 100:
                        patterns["text_lengths"]["medium"] += 1
                    else:
                        patterns["text_lengths"]["long"] += 1
                    
                    # Text structure
                    if "•" in text or "✓" in text or "★" in text or "\n-" in text:
                        patterns["text_structures"]["bullet_points"] += 1
                    elif text.count('\n\n') > 1:
                        patterns["text_structures"]["paragraphs"] += 1
                    elif text.count('\n') < 2:
                        patterns["text_structures"]["single_paragraph"] += 1
                    
                    if any(phrase in text.lower() for phrase in ["once upon", "story", "journey", "experience", "when i", "when we"]):
                        patterns["text_structures"]["storytelling"] += 1
                    
                    # Extract phrases (3-4 words)
                    words = text.lower().split()
                    for i in range(len(words) - 2):
                        phrase = " ".join(words[i:i+3])
                        if len(phrase) > 10:  # Skip very short phrases
                            if phrase in patterns["common_phrases"]:
                                patterns["common_phrases"][phrase] += 1
                            else:
                                patterns["common_phrases"][phrase] = 1
                    
                    # Extract keywords (individual words)
                    if nltk_available:
                        try:
                            # Tokenize and clean up
                            tokens = word_tokenize(text.lower())
                            stop_words = set(stopwords.words('english'))
                            
                            # Filter stop words and short words
                            filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words and len(word) > 3]
                            
                            # Count frequencies
                            for word in filtered_tokens:
                                if word in patterns["keyword_frequencies"]:
                                    patterns["keyword_frequencies"][word] += 1
                                else:
                                    patterns["keyword_frequencies"][word] = 1
                        except:
                            # Fallback to simple word counting
                            for word in words:
                                if len(word) > 3 and word not in ["and", "the", "for", "this", "that", "with", "from"]:
                                    if word in patterns["keyword_frequencies"]:
                                        patterns["keyword_frequencies"][word] += 1
                                    else:
                                        patterns["keyword_frequencies"][word] = 1
                    else:
                        # Simple word counting
                        for word in words:
                            if len(word) > 3 and word not in ["and", "the", "for", "this", "that", "with", "from"]:
                                if word in patterns["keyword_frequencies"]:
                                    patterns["keyword_frequencies"][word] += 1
                                else:
                                    patterns["keyword_frequencies"][word] = 1
                
                # Visual elements analysis
                visual_elements = ad.get('metadata', {}).get('visual_elements', {})
                if visual_elements:
                    # Color schemes
                    colors = visual_elements.get('color_scheme', [])
                    if colors:
                        color_key = '_'.join(colors[:2]) if len(colors) >= 2 else colors[0]
                        if color_key in patterns["visual_elements"]["color_schemes"]:
                            patterns["visual_elements"]["color_schemes"][color_key] += 1
                        else:
                            patterns["visual_elements"]["color_schemes"][color_key] = 1
                    
                    # Typography styles
                    typography = visual_elements.get('typography_style')
                    if typography and typography != "Unknown":
                        if typography in patterns["visual_elements"]["typography_styles"]:
                            patterns["visual_elements"]["typography_styles"][typography] += 1
                        else:
                            patterns["visual_elements"]["typography_styles"][typography] = 1
                    
                    # Background styles
                    background = visual_elements.get('background_style')
                    if background and background != "Unknown":
                        if background in patterns["visual_elements"]["background_styles"]:
                            patterns["visual_elements"]["background_styles"][background] += 1
                        else:
                            patterns["visual_elements"]["background_styles"][background] = 1
                    
                    # Product placement
                    placement = visual_elements.get('product_placement')
                    if placement and placement != "Unknown":
                        if placement in patterns["visual_elements"]["product_placement"]:
                            patterns["visual_elements"]["product_placement"][placement] += 1
                        else:
                            patterns["visual_elements"]["product_placement"][placement] = 1
                
                # Check if this is a high-engagement ad
                engagement_metrics = ad.get('metadata', {}).get('engagement_metrics', {})
                if engagement_metrics:
                    likes = engagement_metrics.get('likes', 0)
                    comments = engagement_metrics.get('comments', 0)
                    shares = engagement_metrics.get('shares', 0)
                    
                    # Consider high engagement if it exceeds any threshold
                    if (likes >= engagement_thresholds["likes"] or 
                        comments >= engagement_thresholds["comments"] or 
                        shares >= engagement_thresholds["shares"]):
                        high_engagement_ads.append(ad)
            
            # Analyze high-engagement ads for patterns
            if high_engagement_ads:
                self.logger.info(f"Analyzing {len(high_engagement_ads)} high-engagement ads for patterns")
                
                # Count format distribution in high-engagement ads
                for ad in high_engagement_ads:
                    # Format
                    if ad.get('video_urls'):
                        format_type = "video"
                    elif len(ad.get('image_urls', [])) > 1:
                        format_type = "carousel"
                    elif ad.get('image_urls'):
                        format_type = "image"
                    else:
                        format_type = "text_only"
                        
                    if format_type in patterns["high_engagement_characteristics"]["formats"]:
                        patterns["high_engagement_characteristics"]["formats"][format_type] += 1
                    else:
                        patterns["high_engagement_characteristics"]["formats"][format_type] = 1
                    
                    # Industry
                    industry = ad.get('metadata', {}).get('industry', 'Unknown')
                    if industry in patterns["high_engagement_characteristics"]["industries"]:
                        patterns["high_engagement_characteristics"]["industries"][industry] += 1
                    else:
                        patterns["high_engagement_characteristics"]["industries"][industry] = 1
                    
                    # Positioning
                    positioning = ad.get('metadata', {}).get('positioning', 'Unknown')
                    if positioning in patterns["high_engagement_characteristics"]["positioning"]:
                        patterns["high_engagement_characteristics"]["positioning"][positioning] += 1
                    else:
                        patterns["high_engagement_characteristics"]["positioning"][positioning] = 1
                    
                    # CTA
                    cta = ad.get('cta_text', '')
                    if cta:
                        cta_category = "Other"
                        for category, phrases in CTA_CATEGORIES.items():
                            if any(phrase in cta.lower() for phrase in phrases):
                                cta_category = category
                                break
                        
                        if cta_category in patterns["high_engagement_characteristics"]["cta_types"]:
                            patterns["high_engagement_characteristics"]["cta_types"][cta_category] += 1
                        else:
                            patterns["high_engagement_characteristics"]["cta_types"][cta_category] = 1
                    
                    # Headline structure
                    headline = ad.get('headline', '')
                    if headline:
                        headline_lower = headline.lower()
                        headline_type = "statement"  # default
                        
                        if headline.endswith('?'):
                            headline_type = "question"
                        elif headline.startswith('How to') or headline.startswith('Why') or headline.startswith('What'):
                            headline_type = "question"
                        elif headline.startswith('Get') or headline.startswith('Try') or headline.startswith('Discover'):
                            headline_type = "command"
                        elif any(headline.startswith(str(n)) for n in range(1, 11)) or "top" in headline_lower:
                            headline_type = "number_based"
                        elif any(phrase in headline_lower for phrase in ["problem", "solution", "struggle", "fix"]):
                            headline_type = "problem_solution"
                        
                        if headline_type in patterns["high_engagement_characteristics"]["headline_structures"]:
                            patterns["high_engagement_characteristics"]["headline_structures"][headline_type] += 1
                        else:
                            patterns["high_engagement_characteristics"]["headline_structures"][headline_type] = 1
                    
                    # Text structure
                    text = ad.get('ad_text', '')
                    if text:
                        text_type = "single_paragraph"  # default
                        
                        if "•" in text or "✓" in text or "★" in text or "\n-" in text:
                            text_type = "bullet_points"
                        elif text.count('\n\n') > 1:
                            text_type = "paragraphs"
                        elif any(phrase in text.lower() for phrase in ["once upon", "story", "journey"]):
                            text_type = "storytelling"
                        
                        if text_type in patterns["high_engagement_characteristics"]["text_structures"]:
                            patterns["high_engagement_characteristics"]["text_structures"][text_type] += 1
                        else:
                            patterns["high_engagement_characteristics"]["text_structures"][text_type] = 1
            
            # Calculate percentages for formats
            total_ads = len(self.scraped_ads)
            patterns["format_percentages"] = {
                format_type: (count / total_ads) * 100 
                for format_type, count in patterns["formats"].items()
            }
            
            # Sort and clean up patterns
            self._sort_and_clean_patterns(patterns, total_ads)
            
            # Save analysis to file
            analysis_filepath = os.path.join(
                self.output_dir, 
                'processed', 
                f"fb_ads_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(analysis_filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "source": "facebook_ads_library",
                        "analysis_time": datetime.now().isoformat(),
                        "ad_count": len(self.scraped_ads),
                        "high_engagement_ad_count": len(high_engagement_ads)
                    },
                    "patterns": patterns
                }, f, indent=2)
            
            self.logger.info(f"Saved ad pattern analysis to {analysis_filepath}")
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error analyzing ad patterns: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {}
    
    def _sort_and_clean_patterns(self, patterns: Dict[str, Any], total_ads: int) -> None:
        """
        Sort pattern dictionaries by frequency and clean up noise.
        
        Args:
            patterns: Patterns dictionary to clean
            total_ads: Total number of ads analyzed
        """
        # Sort dictionary items by value and keep top N
        for key in patterns:
            if isinstance(patterns[key], dict):
                # Sort and trim dictionary values
                if key in ["common_phrases", "keyword_frequencies"]:
                    # Keep only top 50 phrases and 100 keywords
                    patterns[key] = dict(sorted(patterns[key].items(), key=lambda x: x[1], reverse=True)[:100])
                elif key in ["cta_types", "industry_distribution", "positioning_distribution"]:
                    patterns[key] = dict(sorted(patterns[key].items(), key=lambda x: x[1], reverse=True))
                elif key == "visual_elements":
                    # Sort each visual element category
                    for subkey in patterns[key]:
                        if isinstance(patterns[key][subkey], dict):
                            patterns[key][subkey] = dict(sorted(patterns[key][subkey].items(), key=lambda x: x[1], reverse=True))
                elif key == "high_engagement_characteristics":
                    # Sort each high engagement category
                    for subkey in patterns[key]:
                        if isinstance(patterns[key][subkey], dict):
                            patterns[key][subkey] = dict(sorted(patterns[key][subkey].items(), key=lambda x: x[1], reverse=True))
    
    def export_results_for_training(self) -> str:
        """
        Export all results in a format optimized for LLM training.
        Includes processed ads, pattern analysis, and comprehensive metadata.
        
        Returns:
            Path to the exported training data file
        """
        try:
            # Process ads for training with enhanced metadata
            examples = self.process_ads_for_training()
            
            # Analyze patterns
            patterns = self.analyze_ad_patterns()
            
            # Combine into a comprehensive training dataset
            training_data = {
                "metadata": {
                    "source": "facebook_ads_library",
                    "export_time": datetime.now().isoformat(),
                    "ad_count": len(self.scraped_ads),
                    "example_count": len(examples),
                    "scraper_version": "2.0",
                    "features_extracted": {
                        "visual_elements": self.extract_visual_elements,
                        "engagement_metrics": self.extract_engagement_metrics,
                        "industry_categorization": self.categorize_ads,
                        "quality_scoring": self.compute_quality_score
                    }
                },
                "pattern_analysis": patterns,
                "examples": examples
            }
            
            # Save to a single comprehensive file
            export_filepath = os.path.join(
                self.output_dir, 
                'processed', 
                f"fb_ads_training_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(export_filepath, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, indent=2)
            
            self.logger.info(f"Exported comprehensive training data to {export_filepath}")
            
            return export_filepath
            
        except Exception as e:
            self.logger.error(f"Error exporting results for training: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return ""
    
    def quit(self) -> None:
        """
        Close browser and clean up resources.
        """
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.warning(f"Error closing driver: {e}")
            
            self.driver = None
            
        self.logger.info("Scraper resources cleaned up")
        
        # Final performance report
        self.logger.info("Final performance metrics:")
        self.logger.info(f"- Browser launch time: {self.performance_metrics['browser_launch_time']:.2f}s")
        self.logger.info(f"- Total scrolls: {self.performance_metrics['total_scroll_count']}")
        
        if self.performance_metrics['extraction_times']:
            avg_extraction = sum(self.performance_metrics['extraction_times'])/len(self.performance_metrics['extraction_times'])
            self.logger.info(f"- Avg. extraction time: {avg_extraction:.2f}s")
        
        if self.performance_metrics['ads_per_minute']:
            avg_rate = sum(self.performance_metrics['ads_per_minute'])/len(self.performance_metrics['ads_per_minute'])
            self.logger.info(f"- Avg. collection rate: {avg_rate:.1f} ads/minute")
            
        self.logger.info(f"- Load more clicks: {self.performance_metrics['load_more_clicks']}")
        self.logger.info(f"- CAPTCHA encounters: {self.performance_metrics['captcha_encounters']}")
        self.logger.info(f"- Login blocks: {self.performance_metrics['login_block_encounters']}")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, 
                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Print ChromeDriver info
    chrome_driver_path = os.environ.get('CHROMEDRIVER_PATH')
    if chrome_driver_path:
        print(f"Using ChromeDriver from environment variable: {chrome_driver_path}")
    else:
        print("ChromeDriver environment variable not set. Will try auto-detection.")
    
    print("\n=== Enhanced Facebook Ads Library Scraper ===")
    print("This tool collects commercial ads with comprehensive metadata for AI training.")
    print("Features:")
    print("- Smart filtering to target actual ads, not UI elements")
    print("- Visual element extraction (colors, typography, layout)")
    print("- Engagement metrics collection")
    print("- Industry and positioning classification")
    print("- Quality scoring and formatting for LLM training")
    
    # Example usage with enhanced configuration
    scraper = FacebookAdsScraper(
        output_dir='data',
        headless=False,  # Visible browser for debugging
        browser_type='chrome',  # Force Chrome for best results
        debug_mode=True,  # Enable detailed logging
        max_run_time_minutes=30,  # 30 minutes per search
        max_wait_time=1.5,  # Reduced wait times
        parallel_keywords=True,  # Enable parallel processing
        extract_visual_elements=True,  # Extract color schemes, layout, etc.
        extract_engagement_metrics=True,  # Extract likes, comments, shares
        categorize_ads=True,  # Categorize by industry and positioning
        compute_quality_score=True,  # Calculate quality score for filtering
        min_quality_score=5.0  # Minimum quality score (0-10 scale)
    )
    
    # Example search
    try:
        # Get keywords from user input
        keywords_input = input("\nEnter keywords to search for (comma-separated): ")
        keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
        
        if not keywords:
            print("No keywords provided. Using default keywords.")
            keywords = ["shoes", "fitness", "insurance"]  # Default keywords
        
        # Get limit from user input    
        limit_input = input("Maximum ads to collect per keyword (default: 30): ")
        limit = int(limit_input) if limit_input.strip() else 30
        
        # Get country from user input
        country_input = input("Enter country code (default: US): ")
        country = country_input.strip() if country_input.strip() else "US"
        
        print(f"\nScraping Facebook Ads Library for: {', '.join(keywords)}")
        print(f"This will collect up to {limit} ads per keyword in {country}")
        print("Initializing browser...")
        
        # Perform the scraping
        start_time = time.time()
        
        ads = scraper.scrape_ads_library(
            keywords=keywords,
            countries=[country],
            max_ads_per_keyword=limit
        )
        
        total_time = time.time() - start_time
        print(f"\nScraping completed in {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        print(f"Collected {len(ads)} Facebook ads")
        
        # Process for training
        if ads:
            print("\nProcessing ads for training...")
            training_data = scraper.process_ads_for_training()
            print(f"Created {len(training_data)} training examples")
            
            print("\nAnalyzing ad patterns...")
            patterns = scraper.analyze_ad_patterns()
            
            # Display some interesting stats
            if patterns and "format_percentages" in patterns:
                print("\nFormat distribution:")
                for format_type, percentage in patterns["format_percentages"].items():
                    print(f"- {format_type}: {percentage:.1f}%")
            
            if patterns and "industry_distribution" in patterns:
                print("\nTop industries:")
                for industry, count in list(patterns["industry_distribution"].items())[:5]:
                    print(f"- {industry}: {count} ads")
            
            if patterns and "cta_types" in patterns:
                print("\nTop CTA buttons:")
                for cta, count in list(patterns["cta_types"].items())[:5]:
                    print(f"- {cta}: {count} ads")
                    
            if patterns and "high_engagement_characteristics" in patterns:
                if "formats" in patterns["high_engagement_characteristics"]:
                    print("\nHigh-engagement ad formats:")
                    for format_type, count in patterns["high_engagement_characteristics"]["formats"].items():
                        print(f"- {format_type}: {count} high-engagement ads")
            
            # Export combined results
            print("\nExporting comprehensive dataset for training...")
            export_path = scraper.export_results_for_training()
            if export_path:
                print(f"Training data exported to: {export_path}")
                print(f"Full path: {os.path.abspath(export_path)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always clean up
        print("\nCleaning up resources...")
        scraper.quit()
        print("Done!")