"""
Configuration settings for Ad Insights Scraper system
"""
import os
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

class Config:
    """
    Configuration class to manage settings across the application
    with environment variable loading and validation.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration with optional config file.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        # Setup logging
        self.logger = logging.getLogger('Config')
        
        # Load environment variables from .env file
        load_dotenv()
        
        # Initialize configuration
        self._load_environment_variables()
        
        # Load custom config file if provided
        if config_file and os.path.exists(config_file):
            self._load_config_file(config_file)
        
        # Validate configuration
        self._validate_configuration()
    
    def _load_environment_variables(self) -> None:
        """
        Load configuration from environment variables.
        """
        # Output directories
        self.OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'data')
        self.RAW_DATA_DIR = os.getenv('RAW_DATA_DIR', os.path.join(self.OUTPUT_DIR, 'raw'))
        self.PROCESSED_DATA_DIR = os.getenv('PROCESSED_DATA_DIR', os.path.join(self.OUTPUT_DIR, 'processed'))
        self.INSIGHTS_DIR = os.getenv('INSIGHTS_DIR', os.path.join(self.OUTPUT_DIR, 'insights'))
        self.TRAINING_DIR = os.getenv('TRAINING_DIR', os.path.join(self.OUTPUT_DIR, 'training'))
        self.MODELS_DIR = os.getenv('MODELS_DIR', os.path.join(self.OUTPUT_DIR, 'models'))
        
        # Facebook scraper settings
        self.FACEBOOK_USE_PROXIES = os.getenv('FACEBOOK_USE_PROXIES', 'False').lower() == 'true'
        self.FACEBOOK_HEADLESS = os.getenv('FACEBOOK_HEADLESS', 'True').lower() == 'true'
        self.FACEBOOK_COUNTRIES = os.getenv('FACEBOOK_COUNTRIES', 'US').split(',')
        self.FACEBOOK_AD_TYPES = os.getenv('FACEBOOK_AD_TYPES', 'all').split(',')
        self.FACEBOOK_MAX_ADS_PER_KEYWORD = int(os.getenv('FACEBOOK_MAX_ADS_PER_KEYWORD', '100'))
        
        # Reddit scraper settings
        self.REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
        self.REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
        self.REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'AdInsightsScraper/1.0')
        self.REDDIT_MAX_RETRIES = int(os.getenv('REDDIT_MAX_RETRIES', '3'))
        
        # AdSpy scraper settings
        self.ADSPY_USERNAME = os.getenv('ADSPY_USERNAME', '')
        self.ADSPY_PASSWORD = os.getenv('ADSPY_PASSWORD', '')
        self.ADSPY_USE_PROXIES = os.getenv('ADSPY_USE_PROXIES', 'False').lower() == 'true'
        self.ADSPY_HEADLESS = os.getenv('ADSPY_HEADLESS', 'True').lower() == 'true'
        self.ADSPY_PLATFORMS = os.getenv('ADSPY_PLATFORMS', 'facebook,instagram').split(',')
        
        # Proxy settings
        self.PROXY_LIST_PATH = os.getenv('PROXY_LIST_PATH', 'proxies.json')
        self.PROXY_API_KEY = os.getenv('PROXY_API_KEY', '')
        self.PROXY_MIN_COUNT = int(os.getenv('PROXY_MIN_COUNT', '10'))
        
        # CAPTCHA solver settings
        self.CAPTCHA_API_KEY = os.getenv('CAPTCHA_API_KEY', '')
        self.CAPTCHA_SERVICE = os.getenv('CAPTCHA_SERVICE', 'auto')
        
        # LLM settings
        self.LLM_MODEL_TYPE = os.getenv('LLM_MODEL_TYPE', 'gpt')
        self.LLM_EPOCHS = int(os.getenv('LLM_EPOCHS', '3'))
        self.LLM_BATCH_SIZE = int(os.getenv('LLM_BATCH_SIZE', '8'))
        self.LLM_LEARNING_RATE = float(os.getenv('LLM_LEARNING_RATE', '2e-5'))
    
    def _load_config_file(self, config_file: str) -> None:
        """
        Load configuration from file.
        
        Args:
            config_file: Path to configuration file
        """
        try:
            # Simple config file parsing
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Convert string to appropriate type
                        if value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False
                        elif value.isdigit():
                            value = int(value)
                        elif ',' in value:
                            value = [v.strip() for v in value.split(',')]
                        
                        # Set attribute
                        setattr(self, key, value)
            
            self.logger.info(f"Loaded configuration from {config_file}")
            
        except Exception as e:
            self.logger.warning(f"Error loading config file {config_file}: {str(e)}")
    
    def _validate_configuration(self) -> None:
        """
        Validate the configuration and provide warnings for missing settings.
        """
        # Check required directories
        for dir_path in [self.OUTPUT_DIR, self.RAW_DATA_DIR, self.PROCESSED_DATA_DIR, 
                         self.INSIGHTS_DIR, self.TRAINING_DIR, self.MODELS_DIR]:
            os.makedirs(dir_path, exist_ok=True)
        
        # Check Reddit API credentials
        if not self.REDDIT_CLIENT_ID or not self.REDDIT_CLIENT_SECRET:
            self.logger.warning("Reddit API credentials not set. Reddit scraper will have limited functionality.")
        
        # Check AdSpy credentials
        if not self.ADSPY_USERNAME or not self.ADSPY_PASSWORD:
            self.logger.warning("AdSpy credentials not set. AdSpy scraper will not function.")
        
        # Check proxy settings
        if self.FACEBOOK_USE_PROXIES or self.ADSPY_USE_PROXIES:
            if not os.path.exists(self.PROXY_LIST_PATH) and not self.PROXY_API_KEY:
                self.logger.warning("Proxy rotation is enabled but no proxy list or API key is provided.")
        
        # Check CAPTCHA solver settings
        if not self.CAPTCHA_API_KEY:
            self.logger.warning("CAPTCHA API key not set. CAPTCHA solving will not function.")
    
    def get_scraper_config(self, scraper_type: str) -> Dict[str, Any]:
        """
        Get configuration for a specific scraper type.
        
        Args:
            scraper_type: Type of scraper ('facebook', 'reddit', 'adspy')
            
        Returns:
            Dictionary with scraper configuration
        """
        if scraper_type.lower() == 'facebook':
            return {
                'output_dir': self.OUTPUT_DIR,
                'use_proxies': self.FACEBOOK_USE_PROXIES,
                'headless': self.FACEBOOK_HEADLESS,
                'countries': self.FACEBOOK_COUNTRIES,
                'ad_types': self.FACEBOOK_AD_TYPES,
                'max_ads_per_keyword': self.FACEBOOK_MAX_ADS_PER_KEYWORD
            }
        
        elif scraper_type.lower() == 'reddit':
            return {
                'client_id': self.REDDIT_CLIENT_ID,
                'client_secret': self.REDDIT_CLIENT_SECRET,
                'user_agent': self.REDDIT_USER_AGENT,
                'output_dir': self.OUTPUT_DIR,
                'max_retries': self.REDDIT_MAX_RETRIES
            }
        
        elif scraper_type.lower() == 'adspy':
            return {
                'username': self.ADSPY_USERNAME,
                'password': self.ADSPY_PASSWORD,
                'output_dir': self.OUTPUT_DIR,
                'use_proxies': self.ADSPY_USE_PROXIES,
                'headless': self.ADSPY_HEADLESS,
                'platforms': self.ADSPY_PLATFORMS
            }
        
        else:
            self.logger.warning(f"Unknown scraper type: {scraper_type}")
            return {}
    
    def get_proxy_config(self) -> Dict[str, Any]:
        """
        Get proxy configuration.
        
        Returns:
            Dictionary with proxy configuration
        """
        return {
            'proxy_list_path': self.PROXY_LIST_PATH,
            'proxy_api_key': self.PROXY_API_KEY,
            'min_proxies': self.PROXY_MIN_COUNT
        }
    
    def get_captcha_config(self) -> Dict[str, Any]:
        """
        Get CAPTCHA solver configuration.
        
        Returns:
            Dictionary with CAPTCHA solver configuration
        """
        return {
            'api_key': self.CAPTCHA_API_KEY,
            'service': self.CAPTCHA_SERVICE
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """
        Get LLM training configuration.
        
        Returns:
            Dictionary with LLM training configuration
        """
        return {
            'model_type': self.LLM_MODEL_TYPE,
            'epochs': self.LLM_EPOCHS,
            'batch_size': self.LLM_BATCH_SIZE,
            'learning_rate': self.LLM_LEARNING_RATE,
            'training_dir': self.TRAINING_DIR,
            'models_dir': self.MODELS_DIR
        }