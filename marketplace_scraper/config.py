"""
Configuration settings for Facebook Marketplace scraper
"""
import os
import logging
from datetime import datetime

# Logging configuration
LOGGING_CONFIG = {
    'level': logging.INFO,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'handlers': [
        logging.StreamHandler(),
    ]
}

# User agent list for rotation (to avoid blocking)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
]

# Facebook Marketplace categories and their URL paths
MARKETPLACE_CATEGORIES = {
    'all': '',
    'electronics': 'category/electronics',
    'vehicles': 'category/vehicles',
    'property_rentals': 'category/propertyrentals',
    'apparel': 'category/clothing',
    'entertainment': 'category/entertainment',
    'hobbies': 'category/hobbies',
    'home_garden': 'category/home_garden',
    'home_goods': 'category/home_goods',
    'home_improvement': 'category/home_improvement_tools', 
    'baby_kids': 'category/baby_kids',
    'sporting': 'category/sportsgear',
    'toys_games': 'category/toys_games',
    'musical_instruments': 'category/instruments',
    'pet_supplies': 'category/pet_supplies',
    'office_supplies': 'category/office_supplies',
    'health_beauty': 'category/health_beauty',
    'free': 'free'
}

# Default data directories
DEFAULT_OUTPUT_DIR = 'marketplace_data'
DEFAULT_LOGS_DIR = 'logs'

# Set up default directories
os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
os.makedirs(DEFAULT_LOGS_DIR, exist_ok=True)
os.makedirs(os.path.join(DEFAULT_OUTPUT_DIR, 'processed'), exist_ok=True)
os.makedirs(os.path.join(DEFAULT_OUTPUT_DIR, 'images'), exist_ok=True)

# Timeouts and delays
SCRAPER_TIMEOUTS = {
    'page_load': 30,
    'element_presence': 10,
    'scroll_delay': 1.5,
}

# Scraper settings
MAX_ADS_DEFAULT = 1000
SCROLL_PAUSE_DEFAULT = 1.5
MAX_RETRY_ATTEMPTS = 3