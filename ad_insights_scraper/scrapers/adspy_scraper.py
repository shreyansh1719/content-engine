"""
Advanced AdSpy scraper for competitive ad research
"""
import os
import re
import time
import json
import logging
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from .utils.proxy_manager import ProxyManager
from .utils.user_agent import UserAgentRotator
from .utils.fingerprint import FingerprintRandomizer
from .utils.captcha_solver import CaptchaSolver

class AdSpyScraper:
    """
    Advanced AdSpy scraper with anti-detection measures.
    
    Features:
    - Scrapes ads from multiple social media platforms
    - Extracts ad creative, copy, targeting, and performance metrics
    - Implements anti-detection measures to avoid IP blocks
    - Handles login and authentication challenges
    - Exports data in structured format for analysis
    """
    
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        output_dir: str = 'data',
        use_proxies: bool = False,
        headless: bool = True,
        log_level: int = logging.INFO
    ):
        """
        Initialize AdSpy scraper.
        
        Args:
            username: AdSpy account username
            password: AdSpy account password
            output_dir: Directory to save scraped data
            use_proxies: Whether to use proxy rotation
            headless: Run browser in headless mode
            log_level: Logging level
        """
        # Setup logging
        self.logger = logging.getLogger('AdSpyScraper')
        self.logger.setLevel(log_level)
        
        if not self.logger.handlers:
            # Create handlers
            console_handler = logging.StreamHandler()
            file_handler = logging.FileHandler(
                os.path.join(output_dir, 'adspy_scraper.log'),
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
        
        # Credentials
        self.username = username or os.getenv('ADSPY_USERNAME')
        self.password = password or os.getenv('ADSPY_PASSWORD')
        
        if not self.username or not self.password:
            self.logger.warning("AdSpy credentials not provided. Functionality will be limited.")
        
        # Ensure output directory exists
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'raw'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'processed'), exist_ok=True)
        
        # Initialize utilities
        self.user_agent_rotator = UserAgentRotator()
        self.proxy_manager = ProxyManager() if use_proxies else None
        self.fingerprint_randomizer = FingerprintRandomizer()
        self.captcha_solver = CaptchaSolver()
        
        # Browser configuration
        self.headless = headless
        self.driver = None
        self.session_start_time = datetime.now()
        self.last_action_time = self.session_start_time
        self.page_load_count = 0
        
        # Scraping parameters
        self.ads_collected = 0
        self.max_ads_per_session = 200  # Limit per browser session
        self.scrape_attempts = 0
        self.max_scrape_attempts = 3
        
        # AdSpy constants
        self.base_url = "https://adspy.com"
        self.login_url = "https://adspy.com/login"
        self.search_url = "https://adspy.com/ads/search"
        
        # Storage for scraped ads
        self.scraped_ads = []
    
    def _launch_browser(self) -> bool:
        """
        Launch undetected-chromedriver with anti-detection measures.
        
        Returns:
            True if browser launched successfully, False otherwise
        """
        try:
            # Close any existing browser session
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            
            # Setup Chrome options with randomized fingerprint
            options = uc.ChromeOptions()
            
            # Apply fingerprint randomization
            self.fingerprint_randomizer.apply_to_options(options)
            
            # Set user agent
            options.add_argument(f'--user-agent={self.user_agent_rotator.get_random_user_agent()}')
            
            # Apply proxy if available
            proxy = None
            if self.proxy_manager:
                proxy = self.proxy_manager.get_next_proxy()
                if proxy:
                    self.logger.info(f"Using proxy: {proxy['host']}:{proxy['port']}")
                    options.add_argument(f'--proxy-server={proxy["host"]}:{proxy["port"]}')
            
            # Additional settings to prevent detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            
            if self.headless:
                options.add_argument('--headless=new')
                options.add_argument('--window-size=1920,1080')
            
            # Create a new driver instance
            self.driver = uc.Chrome(options=options, use_subprocess=True)
            
            # Set default timeouts
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            # Reset session counters
            self.session_start_time = datetime.now()
            self.last_action_time = self.session_start_time
            self.page_load_count = 0
            
            # Resize window to typical dimensions
            if not self.headless:
                width = random.randint(1024, 1920)
                height = random.randint(768, 1080)
                self.driver.set_window_size(width, height)
            
            self.logger.info("Browser launched successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Browser launch failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _human_like_wait(self, min_seconds: float = 1.0, max_seconds: float = 4.0) -> None:
        """
        Wait for a random amount of time to mimic human behavior.
        
        Args:
            min_seconds: Minimum wait time in seconds
            max_seconds: Maximum wait time in seconds
        """
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
        Perform scrolling in a human-like manner.
        
        Args:
            direction: 'up' or 'down'
            distance: Scroll distance in pixels (if None, uses random distance)
        """
        if not self.driver:
            return
        
        try:
            # Get viewport height
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Determine scroll distance
            if distance is None:
                if direction == 'down':
                    # Scroll between 50% and 90% of viewport height
                    distance = int(viewport_height * random.uniform(0.5, 0.9))
                else:
                    # Scroll up between 30% and 70% of viewport height
                    distance = int(viewport_height * random.uniform(0.3, 0.7))
                    distance = -distance  # Negative for upward scrolling
            
            # Scroll with variable speed (not all at once)
            remaining = abs(distance)
            scroll_direction = 1 if distance > 0 else -1
            
            while remaining > 0:
                # Determine step size with some randomness
                step = min(remaining, random.randint(100, 300))
                remaining -= step
                
                # Execute scroll
                self.driver.execute_script(
                    "window.scrollBy(0, arguments[0])", 
                    step * scroll_direction
                )
                
                # Small random pause between scroll steps
                time.sleep(random.uniform(0.05, 0.2))
            
            # Wait after scrolling
            self._human_like_wait(0.5, 2.0)
            
        except Exception as e:
            self.logger.warning(f"Scroll error: {str(e)}")
    
    def _login(self) -> bool:
        """
        Log in to AdSpy with provided credentials.
        
        Returns:
            True if login successful, False otherwise
        """
        if not self.driver:
            self.logger.error("Browser not initialized")
            return False
        
        if not self.username or not self.password:
            self.logger.error("AdSpy credentials not provided")
            return False
        
        try:
            # Navigate to login page
            self.logger.info("Navigating to login page")
            self.driver.get(self.login_url)
            self._human_like_wait(2.0, 4.0)
            
            # Check for CAPTCHA
            if not self._check_for_captcha():
                self.logger.error("Failed to solve CAPTCHA on login page")
                return False
            
            # Find login form elements
            username_field = self.driver.find_element(By.ID, "email")
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            
            # Clear fields and enter credentials with human-like typing
            username_field.clear()
            self._human_like_typing(username_field, self.username)
            
            self._human_like_wait(0.5, 1.5)
            
            password_field.clear()
            self._human_like_typing(password_field, self.password)
            
            self._human_like_wait(1.0, 2.0)
            
            # Click login button
            login_button.click()
            
            # Wait for login to complete
            self._human_like_wait(3.0, 5.0)
            
            # Check if login was successful
            if "login" in self.driver.current_url.lower():
                # Check for error messages
                error_messages = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'alert-danger')]")
                if error_messages:
                    for error in error_messages:
                        self.logger.error(f"Login error: {error.text}")
                else:
                    self.logger.error("Login failed: Still on login page")
                return False
            
            self.logger.info("Login successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Login error: {str(e)}")
            return False
    
    def _human_like_typing(self, element, text: str) -> None:
        """
        Simulate human typing with random delays.
        
        Args:
            element: WebElement to type into
            text: Text to type
        """
        for char in text:
            element.send_keys(char)
            # Random delay between keystrokes
            time.sleep(random.uniform(0.05, 0.2))
    
    def _check_for_captcha(self) -> bool:
        """
        Check if a CAPTCHA is present and attempt to solve it.
        
        Returns:
            True if CAPTCHA was solved or not present, False if failed to solve
        """
        if not self.driver:
            return False
        
        try:
            # Look for common CAPTCHA indicators
            captcha_indicators = [
                "//div[contains(@class, 'captcha')]",
                "//iframe[contains(@src, 'captcha')]",
                "//iframe[contains(@src, 'recaptcha')]",
                "//div[contains(@class, 'recaptcha')]",
                "//div[contains(text(), 'Confirm you are human')]",
                "//div[contains(text(), 'Please verify')]",
                "//div[contains(text(), 'Security check')]"
            ]
            
            for indicator in captcha_indicators:
                captcha_elements = self.driver.find_elements(By.XPATH, indicator)
                if captcha_elements:
                    self.logger.warning("CAPTCHA detected!")
                    
                    # Attempt to solve using captcha solver
                    solved = self.captcha_solver.solve_captcha(self.driver)
                    
                    if solved:
                        self.logger.info("CAPTCHA solved successfully")
                        self._human_like_wait(2.0, 4.0)
                        return True
                    else:
                        self.logger.error("Failed to solve CAPTCHA")
                        return False
            
            # No CAPTCHA found
            return True
            
        except Exception as e:
            self.logger.warning(f"CAPTCHA check error: {str(e)}")
            return False
    
    def scrape_ads(
        self, 
        keywords: List[str], 
        platforms: List[str] = ['facebook', 'instagram'],
        min_date: Optional[str] = None,
        max_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Scrape ads from AdSpy based on search criteria.
        
        Args:
            keywords: List of keywords to search for
            platforms: List of platforms to search on
            min_date: Minimum date for ads (YYYY-MM-DD format)
            max_date: Maximum date for ads (YYYY-MM-DD format)
            limit: Maximum number of ads to collect
            
        Returns:
            List of ad dictionaries
        """
        all_ads = []
        
        # Launch browser if needed
        if not self.driver and not self._launch_browser():
            self.logger.error("Failed to launch browser")
            return all_ads
        
        # Log in to AdSpy if not already logged in
        if not self._check_logged_in() and not self._login():
            self.logger.error("Failed to log in to AdSpy")
            return all_ads
        
        # Process each keyword
        for keyword in keywords:
            try:
                self.logger.info(f"Searching for ads with keyword: '{keyword}'")
                
                # Construct search URL with parameters
                search_params = {
                    'keyword': keyword,
                    'platforms': ','.join(platforms)
                }
                
                # Add date filters if provided
                if min_date:
                    search_params['min_date'] = min_date
                if max_date:
                    search_params['max_date'] = max_date
                
                # Perform search
                ads = self._search_and_extract(search_params, limit)
                
                # Add source metadata to each ad
                for ad in ads:
                    ad['search_keyword'] = keyword
                    ad['search_platforms'] = platforms
                    ad['scrape_time'] = datetime.now().isoformat()
                
                all_ads.extend(ads)
                
                # Save intermediate results
                if ads:
                    self._save_ads_batch(
                        ads,
                        f"adspy_{keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    )
                
                # Reset browser if needed
                if len(all_ads) >= self.max_ads_per_session:
                    self.logger.info(f"Maximum ads per session reached ({self.max_ads_per_session}), restarting browser")
                    self._reset_session()
                
            except Exception as e:
                self.logger.error(f"Error scraping ads for keyword '{keyword}': {str(e)}")
                import traceback
                self.logger.error(traceback.format_exc())
        
        # Store final results
        self.scraped_ads = all_ads
        
        # Save complete results
        if all_ads:
            self._save_ads_batch(
                all_ads,
                f"adspy_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
        
        return all_ads
    
    def _check_logged_in(self) -> bool:
        """
        Check if the user is currently logged in to AdSpy.
        
        Returns:
            True if logged in, False otherwise
        """
        if not self.driver:
            return False
        
        try:
            # Navigate to main page
            self.driver.get(self.base_url)
            self._human_like_wait(2.0, 3.0)
            
            # Check for login indicators
            login_indicators = [
                "//a[contains(text(), 'Login')]",
                "//a[contains(@href, 'login')]",
                f"//form[contains(@action, '{self.login_url}')]"
            ]
            
            for indicator in login_indicators:
                login_elements = self.driver.find_elements(By.XPATH, indicator)
                if login_elements and login_elements[0].is_displayed():
                    return False
            
            # Check for logged-in indicators
            logged_in_indicators = [
                "//a[contains(text(), 'Logout')]",
                "//a[contains(@href, 'logout')]",
                "//div[contains(@class, 'user-menu')]",
                "//span[contains(@class, 'user-name')]"
            ]
            
            for indicator in logged_in_indicators:
                logged_in_elements = self.driver.find_elements(By.XPATH, indicator)
                if logged_in_elements and logged_in_elements[0].is_displayed():
                    return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Error checking login status: {str(e)}")
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
        
        # Wait a random time before starting new session
        wait_time = random.uniform(30, 60)
        self.logger.info(f"Waiting {wait_time:.2f} seconds before starting new session")
        time.sleep(wait_time)
    
    def _search_and_extract(
        self,
        search_params: Dict[str, str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Perform search and extract ads from results.
        
        Args:
            search_params: Search parameters
            limit: Maximum number of ads to collect
            
        Returns:
            List of ad dictionaries
        """
        if not self.driver:
            return []
        
        collected_ads = []
        
        try:
            # Construct search URL
            url = self.search_url
            query_params = []
            
            for key, value in search_params.items():
                query_params.append(f"{key}={quote(value)}")
            
            if query_params:
                url += "?" + "&".join(query_params)
            
            # Navigate to search URL
            self.logger.info(f"Navigating to search URL: {url}")
            self.driver.get(url)
            self._human_like_wait(3.0, 5.0)
            
            # Check if search results loaded
            no_results_indicators = [
                "//div[contains(text(), 'No results found')]",
                "//div[contains(text(), 'No ads match')]",
                "//div[contains(@class, 'no-results')]"
            ]
            
            for indicator in no_results_indicators:
                no_results_elements = self.driver.find_elements(By.XPATH, indicator)
                if no_results_elements and no_results_elements[0].is_displayed():
                    self.logger.info("No results found for this search")
                    return []
            
            # Wait for ads to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ad-card')]"))
                )
            except TimeoutException:
                self.logger.warning("Timeout waiting for ad cards to load")
                return []
            
            # Scroll and collect ads
            scroll_count = 0
            max_scrolls = 50  # Limit to prevent infinite loops
            
            while len(collected_ads) < limit and scroll_count < max_scrolls:
                # Extract ads from current view
                new_ads = self._extract_ads_from_page()
                
                # Add new unique ads to collection
                existing_ids = {ad['ad_id'] for ad in collected_ads if 'ad_id' in ad}
                for ad in new_ads:
                    if 'ad_id' in ad and ad['ad_id'] not in existing_ids:
                        collected_ads.append(ad)
                        existing_ids.add(ad['ad_id'])
                
                # Log progress
                if new_ads:
                    self.logger.info(f"Collected {len(collected_ads)} ads so far")
                
                # Check if we've reached the target number of ads
                if len(collected_ads) >= limit:
                    break
                
                # Scroll down to load more ads
                self._human_like_scroll('down')
                scroll_count += 1
                
                # Occasionally scroll up slightly to mimic human behavior
                if scroll_count % 5 == 0:
                    self._human_like_scroll('up', distance=random.randint(300, 600))
                
                # Check for load more button
                load_more_buttons = self.driver.find_elements(
                    By.XPATH,
                    "//button[contains(text(), 'Load More') or contains(@class, 'load-more')]"
                )
                
                if load_more_buttons:
                    for button in load_more_buttons:
                        try:
                            if button.is_displayed():
                                button.click()
                                self._human_like_wait(2.0, 4.0)
                                break
                        except:
                            pass
                
                # Check if no more ads are loading
                if scroll_count > 5 and len(new_ads) == 0:
                    no_more_content = scroll_count % 5 == 0
                    end_of_results_elements = self.driver.find_elements(
                        By.XPATH,
                        "//div[contains(text(), 'End of results') or contains(text(), 'No more ads')]"
                    )
                    
                    if end_of_results_elements or no_more_content:
                        self.logger.info("Reached end of results")
                        break
            
            return collected_ads
            
        except Exception as e:
            self.logger.error(f"Error during search and extraction: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return collected_ads
    
    def _extract_ads_from_page(self) -> List[Dict[str, Any]]:
        """
        Extract ad data from the currently loaded page.
        
        Returns:
            List of ad dictionaries
        """
        ads = []
        
        try:
            # Find all ad containers
            ad_elements = self.driver.find_elements(
                By.XPATH, 
                "//div[contains(@class, 'ad-card')]"
            )
            
            for ad_element in ad_elements:
                try:
                    ad_data = self._extract_single_ad(ad_element)
                    if ad_data:
                        ads.append(ad_data)
                except Exception as ad_error:
                    self.logger.warning(f"Error extracting ad details: {str(ad_error)}")
            
            return ads
            
        except Exception as e:
            self.logger.warning(f"Error extracting ads from page: {str(e)}")
            return []
    
    def _extract_single_ad(self, ad_element) -> Optional[Dict[str, Any]]:
        """
        Extract data from a single ad element.
        
        Args:
            ad_element: WebElement containing a single ad
        
        Returns:
            Dictionary with ad data or None if extraction failed
        """
        ad_data = {
            "ad_id": "",
            "platform": "",
            "advertiser_name": "",
            "advertiser_url": "",
            "ad_text": "",
            "headline": "",
            "cta": "",
            "landing_page": "",
            "first_seen": "",
            "last_seen": "",
            "engagement": {},
            "targeting": {},
            "image_urls": [],
            "video_urls": []
        }
        
        try:
            # Extract ad ID
            try:
                ad_id_element = ad_element.find_element(By.XPATH, ".//div[contains(@class, 'ad-id')]")
                if ad_id_element:
                    ad_data["ad_id"] = ad_id_element.text.strip()
            except:
                # Try to extract from element attributes
                ad_id = ad_element.get_attribute('data-id') or ad_element.get_attribute('id')
                if ad_id:
                    ad_data["ad_id"] = ad_id
            
            # Extract platform
            platform_indicators = {
                'facebook': ["facebook-icon", "fb-icon"],
                'instagram': ["instagram-icon", "ig-icon"],
                'twitter': ["twitter-icon"],
                'linkedin': ["linkedin-icon"],
                'youtube': ["youtube-icon"]
            }
            
            for platform, indicators in platform_indicators.items():
                for indicator in indicators:
                    platform_elements = ad_element.find_elements(
                        By.XPATH, 
                        f".//div[contains(@class, '{indicator}')]"
                    )
                    if platform_elements:
                        ad_data["platform"] = platform
                        break
                if ad_data["platform"]:
                    break
            
            # Extract advertiser details
            try:
                advertiser_element = ad_element.find_element(
                    By.XPATH, 
                    ".//div[contains(@class, 'advertiser-name')]"
                )
                if advertiser_element:
                    ad_data["advertiser_name"] = advertiser_element.text.strip()
                    
                    # Try to get advertiser URL
                    advertiser_link = advertiser_element.find_element(By.XPATH, ".//a")
                    if advertiser_link:
                        ad_data["advertiser_url"] = advertiser_link.get_attribute('href')
            except:
                pass
            
            # Extract ad text
            try:
                text_elements = ad_element.find_elements(
                    By.XPATH,
                    ".//div[contains(@class, 'ad-text')]"
                )
                
                if text_elements:
                    ad_data["ad_text"] = text_elements[0].text.strip()
            except:
                pass
            
            # Extract headline
            try:
                headline_elements = ad_element.find_elements(
                    By.XPATH,
                    ".//div[contains(@class, 'ad-headline')]"
                )
                
                if headline_elements:
                    ad_data["headline"] = headline_elements[0].text.strip()
            except:
                pass
            
            # Extract CTA (Call to Action)
            try:
                cta_elements = ad_element.find_elements(
                    By.XPATH,
                    ".//div[contains(@class, 'ad-cta')]//button"
                )
                
                if cta_elements:
                    ad_data["cta"] = cta_elements[0].text.strip()
            except:
                pass
            
            # Extract landing page
            try:
                landing_page_elements = ad_element.find_elements(
                    By.XPATH,
                    ".//div[contains(@class, 'landing-page')]//a"
                )
                
                if landing_page_elements:
                    ad_data["landing_page"] = landing_page_elements[0].get_attribute('href')
            except:
                pass
            
            # Extract dates
            try:
                date_elements = ad_element.find_elements(
                    By.XPATH,
                    ".//div[contains(@class, 'ad-dates')]"
                )
                
                if date_elements:
                    date_text = date_elements[0].text.strip()
                    
                    # Parse date information
                    if "First seen" in date_text:
                        first_seen_match = re.search(r'First seen: (.+?)(?:$|\n)', date_text)
                        if first_seen_match:
                            ad_data["first_seen"] = first_seen_match.group(1).strip()
                    
                    if "Last seen" in date_text:
                        last_seen_match = re.search(r'Last seen: (.+?)(?:$|\n)', date_text)
                        if last_seen_match:
                            ad_data["last_seen"] = last_seen_match.group(1).strip()
            except:
                pass
            
            # Extract engagement metrics
            try:
                engagement_elements = ad_element.find_elements(
                    By.XPATH,
                    ".//div[contains(@class, 'engagement-metrics')]"
                )
                
                if engagement_elements:
                    # Extract common metrics
                    metrics = {
                        'likes': r'(\d+)\s*likes',
                        'comments': r'(\d+)\s*comments',
                        'shares': r'(\d+)\s*shares',
                        'reactions': r'(\d+)\s*reactions'
                    }
                    
                    engagement_text = engagement_elements[0].text.strip()
                    
                    for metric, pattern in metrics.items():
                        match = re.search(pattern, engagement_text, re.IGNORECASE)
                        if match:
                            ad_data["engagement"][metric] = int(match.group(1))
            except:
                pass
            
            # Extract targeting information
            try:
                targeting_elements = ad_element.find_elements(
                    By.XPATH,
                    ".//div[contains(@class, 'targeting-info')]"
                )
                
                if targeting_elements:
                    targeting_text = targeting_elements[0].text.strip()
                    
                    # Parse targeting categories
                    categories = {
                        'gender': r'Gender: (.+?)(?:$|\n)',
                        'age': r'Age: (.+?)(?:$|\n)',
                        'location': r'Location: (.+?)(?:$|\n)',
                        'interests': r'Interests: (.+?)(?:$|\n)',
                        'placements': r'Placements: (.+?)(?:$|\n)'
                    }
                    
                    for category, pattern in categories.items():
                        match = re.search(pattern, targeting_text, re.IGNORECASE)
                        if match:
                            ad_data["targeting"][category] = match.group(1).strip()
            except:
                pass
            
            # Extract images
            try:
                image_elements = ad_element.find_elements(
                    By.XPATH,
                    ".//div[contains(@class, 'ad-media')]//img"
                )
                
                for img in image_elements:
                    img_src = img.get_attribute('src')
                    if img_src and img_src.startswith('http') and img_src not in ad_data["image_urls"]:
                        ad_data["image_urls"].append(img_src)
            except:
                pass
            
            # Extract videos
            try:
                video_elements = ad_element.find_elements(
                    By.XPATH,
                    ".//div[contains(@class, 'ad-media')]//video"
                )
                
                for video in video_elements:
                    video_src = video.get_attribute('src')
                    if video_src and video_src.startswith('http'):
                        ad_data["video_urls"].append(video_src)
            except:
                pass
            
            # Return ad data only if we have essential fields
            if ad_data["ad_id"] or ad_data["advertiser_name"]:
                return ad_data
            else:
                return None
            
        except Exception as e:
            self.logger.warning(f"Error parsing ad element: {str(e)}")
            return None
    
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
                            "ads_count": len(ads)
                        },
                        "ads": ads
                    },
                    f,
                    indent=2
                )
            
            self.logger.info(f"Saved {len(ads)} ads to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving ads: {str(e)}")
    
    def extract_ad_insights(self, ads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract insights from collected ads.
        
        Args:
            ads: List of ad dictionaries
            
        Returns:
            List of insights dictionaries
        """
        if not ads:
            self.logger.warning("No ads to analyze")
            return []
        
        insights = []
        
        try:
            # Group ads by advertiser
            advertisers = {}
            for ad in ads:
                advertiser = ad.get('advertiser_name', 'Unknown')
                if advertiser not in advertisers:
                    advertisers[advertiser] = []
                advertisers[advertiser].append(ad)
            
            # Process each advertiser's ads
            for advertiser, advertiser_ads in advertisers.items():
                # Skip advertisers with too few ads
                if len(advertiser_ads) < 2:
                    continue
                
                # Analyze ad formats
                formats = self._analyze_ad_formats(advertiser_ads)
                
                # Analyze ad copy
                copy_insights = self._analyze_ad_copy(advertiser_ads)
                
                # Analyze targeting
                targeting_insights = self._analyze_targeting(advertiser_ads)
                
                # Analyze engagement
                engagement_insights = self._analyze_engagement(advertiser_ads)
                
                # Compile insights
                advertiser_insights = {
                    "advertiser": advertiser,
                    "ad_count": len(advertiser_ads),
                    "platforms": list(set(ad.get('platform', '') for ad in advertiser_ads if ad.get('platform'))),
                    "formats": formats,
                    "copy_insights": copy_insights,
                    "targeting_insights": targeting_insights,
                    "engagement_insights": engagement_insights,
                    "top_performing_ads": self._get_top_performing_ads(advertiser_ads, 3)
                }
                
                insights.append(advertiser_insights)
            
            # Save insights to file
            self._save_insights(insights)
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error extracting ad insights: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []
    
    def _analyze_ad_formats(self, ads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze ad formats used by the advertiser.
        
        Args:
            ads: List of ad dictionaries
            
        Returns:
            Dictionary with format analysis
        """
        formats = {
            "image_only": 0,
            "video_only": 0,
            "carousel": 0,
            "image_and_text": 0,
            "video_and_text": 0,
            "text_only": 0
        }
        
        for ad in ads:
            has_images = len(ad.get('image_urls', [])) > 0
            has_videos = len(ad.get('video_urls', [])) > 0
            has_text = bool(ad.get('ad_text', '').strip())
            
            # Determine the format based on content
            if has_images and has_videos:
                formats["carousel"] += 1
            elif has_images and not has_videos:
                if has_text:
                    formats["image_and_text"] += 1
                else:
                    formats["image_only"] += 1
            elif has_videos and not has_images:
                if has_text:
                    formats["video_and_text"] += 1
                else:
                    formats["video_only"] += 1
            elif has_text:
                formats["text_only"] += 1
        
        # Calculate percentages
        total = sum(formats.values())
        if total > 0:
            format_percentages = {
                format_type: (count / total) * 100
                for format_type, count in formats.items()
            }
        else:
            format_percentages = {format_type: 0 for format_type in formats}
        
        # Get dominant format
        dominant_format = max(formats.items(), key=lambda x: x[1])[0] if total > 0 else "unknown"
        
        return {
            "counts": formats,
            "percentages": format_percentages,
            "dominant_format": dominant_format
        }
    
    def _analyze_ad_copy(self, ads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze ad copy patterns.
        
        Args:
            ads: List of ad dictionaries
            
        Returns:
            Dictionary with copy analysis
        """
        # Collect all ad text
        all_text = ""
        headlines = []
        cta_buttons = []
        
        for ad in ads:
            if ad.get('ad_text'):
                all_text += " " + ad.get('ad_text', '')
            
            if ad.get('headline'):
                headlines.append(ad.get('headline', ''))
            
            if ad.get('cta'):
                cta_buttons.append(ad.get('cta', ''))
        
        # Analyze word count
        words = all_text.split()
        avg_word_count = len(words) / len(ads) if ads else 0
        
        # Extract most common phrases (2-3 words)
        phrases = []
        words = all_text.lower().split()
        
        # Extract 2-word phrases
        for i in range(len(words) - 1):
            phrases.append(f"{words[i]} {words[i+1]}")
        
        # Extract 3-word phrases
        for i in range(len(words) - 2):
            phrases.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        # Count phrase frequencies
        from collections import Counter
        phrase_counter = Counter(phrases)
        top_phrases = phrase_counter.most_common(5)
        
        # Analyze CTA buttons
        cta_counter = Counter(cta_buttons)
        top_ctas = cta_counter.most_common(3)
        
        # Analyze headline patterns
        headline_patterns = {
            "question": 0,
            "number": 0,
            "how_to": 0,
            "benefit": 0,
            "offer": 0
        }
        
        for headline in headlines:
            headline_lower = headline.lower()
            
            if "?" in headline:
                headline_patterns["question"] += 1
            
            if re.search(r'\d+', headline):
                headline_patterns["number"] += 1
            
            if "how to" in headline_lower or "how-to" in headline_lower:
                headline_patterns["how_to"] += 1
            
            benefit_keywords = ["improve", "better", "best", "free", "save", "boost", "increase"]
            if any(keyword in headline_lower for keyword in benefit_keywords):
                headline_patterns["benefit"] += 1
            
            offer_keywords = ["discount", "sale", "off", "limited", "exclusive", "today", "now"]
            if any(keyword in headline_lower for keyword in offer_keywords):
                headline_patterns["offer"] += 1
        
        return {
            "avg_word_count": avg_word_count,
            "top_phrases": [{"phrase": phrase, "count": count} for phrase, count in top_phrases],
            "top_ctas": [{"cta": cta, "count": count} for cta, count in top_ctas],
            "headline_patterns": headline_patterns
        }
    
    def _analyze_targeting(self, ads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze targeting patterns.
        
        Args:
            ads: List of ad dictionaries
            
        Returns:
            Dictionary with targeting analysis
        """
        targeting_data = {
            "gender": [],
            "age": [],
            "location": [],
            "interests": []
        }
        
        # Collect targeting information from all ads
        for ad in ads:
            targeting = ad.get('targeting', {})
            
            if targeting.get('gender'):
                targeting_data["gender"].append(targeting.get('gender'))
            
            if targeting.get('age'):
                targeting_data["age"].append(targeting.get('age'))
            
            if targeting.get('location'):
                targeting_data["location"].append(targeting.get('location'))
            
            if targeting.get('interests'):
                # Split multiple interests
                interests = targeting.get('interests', '').split(',')
                targeting_data["interests"].extend([i.strip() for i in interests])
        
        # Count frequencies
        from collections import Counter
        gender_counter = Counter(targeting_data["gender"])
        age_counter = Counter(targeting_data["age"])
        location_counter = Counter(targeting_data["location"])
        interest_counter = Counter(targeting_data["interests"])
        
        # Get most common values
        primary_gender = gender_counter.most_common(1)[0][0] if gender_counter else "Unknown"
        primary_age = age_counter.most_common(1)[0][0] if age_counter else "Unknown"
        top_locations = [loc for loc, count in location_counter.most_common(3)]
        top_interests = [interest for interest, count in interest_counter.most_common(5)]
        
        return {
            "primary_gender": primary_gender,
            "primary_age_range": primary_age,
            "top_locations": top_locations,
            "top_interests": top_interests,
            "detailed": {
                "gender": dict(gender_counter),
                "age": dict(age_counter),
                "location": dict(location_counter),
                "interests": dict(interest_counter)
            }
        }
    
    def _analyze_engagement(self, ads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze engagement patterns.
        
        Args:
            ads: List of ad dictionaries
            
        Returns:
            Dictionary with engagement analysis
        """
        # Calculate average engagement metrics
        likes = []
        comments = []
        shares = []
        reactions = []
        
        for ad in ads:
            engagement = ad.get('engagement', {})
            
            if 'likes' in engagement:
                likes.append(engagement['likes'])
            
            if 'comments' in engagement:
                comments.append(engagement['comments'])
            
            if 'shares' in engagement:
                shares.append(engagement['shares'])
            
            if 'reactions' in engagement:
                reactions.append(engagement['reactions'])
        
        # Calculate averages
        avg_likes = sum(likes) / len(likes) if likes else 0
        avg_comments = sum(comments) / len(comments) if comments else 0
        avg_shares = sum(shares) / len(shares) if shares else 0
        avg_reactions = sum(reactions) / len(reactions) if reactions else 0
        
        # Identify top performing ad types
        image_ads = [ad for ad in ads if len(ad.get('image_urls', [])) > 0 and len(ad.get('video_urls', [])) == 0]
        video_ads = [ad for ad in ads if len(ad.get('video_urls', [])) > 0]
        
        # Calculate engagement for different types
        image_engagement = self._calculate_avg_engagement(image_ads)
        video_engagement = self._calculate_avg_engagement(video_ads)
        
        # Determine which performs better
        top_format = "video" if video_engagement > image_engagement else "image"
        
        return {
            "average_metrics": {
                "likes": avg_likes,
                "comments": avg_comments,
                "shares": avg_shares,
                "reactions": avg_reactions
            },
            "format_performance": {
                "image": image_engagement,
                "video": video_engagement,
                "top_performing": top_format
            }
        }
    
    def _calculate_avg_engagement(self, ads: List[Dict[str, Any]]) -> float:
        """
        Calculate average engagement score for a set of ads.
        
        Args:
            ads: List of ad dictionaries
            
        Returns:
            Average engagement score
        """
        if not ads:
            return 0
        
        total_engagement = 0
        
        for ad in ads:
            engagement = ad.get('engagement', {})
            
            # Calculate a simple engagement score (can be customized)
            score = (
                engagement.get('likes', 0) * 1 +
                engagement.get('comments', 0) * 3 +
                engagement.get('shares', 0) * 5 +
                engagement.get('reactions', 0) * 1
            )
            
            total_engagement += score
        
        return total_engagement / len(ads)
    
    def _get_top_performing_ads(
        self, 
        ads: List[Dict[str, Any]], 
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get the top performing ads based on engagement.
        
        Args:
            ads: List of ad dictionaries
            limit: Maximum number of top ads to return
            
        Returns:
            List of top performing ads
        """
        # Calculate engagement score for each ad
        scored_ads = []
        
        for ad in ads:
            engagement = ad.get('engagement', {})
            
            # Calculate a simple engagement score
            score = (
                engagement.get('likes', 0) * 1 +
                engagement.get('comments', 0) * 3 +
                engagement.get('shares', 0) * 5 +
                engagement.get('reactions', 0) * 1
            )
            
            scored_ads.append((ad, score))
        
        # Sort by score and get top ads
        top_ads = [ad for ad, score in sorted(scored_ads, key=lambda x: x[1], reverse=True)[:limit]]
        
        return top_ads
    
    def _save_insights(self, insights: List[Dict[str, Any]]) -> None:
        """
        Save extracted insights to a JSON file.
        
        Args:
            insights: List of insight dictionaries
        """
        try:
            if not insights:
                return
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"adspy_insights_{timestamp}.json"
            filepath = os.path.join(self.output_dir, 'processed', filename)
            
            # Save to JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(
                    {
                        "metadata": {
                            "timestamp": datetime.now().isoformat(),
                            "advertisers_count": len(insights)
                        },
                        "insights": insights
                    },
                    f,
                    indent=2
                )
            
            self.logger.info(f"Saved insights for {len(insights)} advertisers to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving insights: {str(e)}")
    
    def format_for_training(self, ads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format ads data for LLM training.
        
        Args:
            ads: List of ad dictionaries
            
        Returns:
            List of training examples
        """
        if not ads:
            self.logger.warning("No ads to format for training")
            return []
        
        training_examples = []
        
        try:
            # Process each ad into a training example
            for ad in ads:
                # Skip ads without sufficient content
                if not ad.get('ad_text') and not ad.get('headline'):
                    continue
                
                # Create a descriptive prompt
                prompt = f"Create a {ad.get('platform', 'social media')} ad"
                
                if ad.get('advertiser_name'):
                    prompt += f" for {ad.get('advertiser_name')}"
                
                # Extract media type
                media_type = "image"
                if ad.get('video_urls'):
                    media_type = "video"
                elif len(ad.get('image_urls', [])) > 1:
                    media_type = "carousel"
                
                prompt += f" using {media_type} format"
                
                # Create the training example
                example = {
                    "input": prompt,
                    "output": {
                        "platform": ad.get('platform', 'facebook'),
                        "headline": ad.get('headline', ''),
                        "body_text": ad.get('ad_text', ''),
                        "cta": ad.get('cta', ''),
                        "media_type": media_type,
                        "landing_page": ad.get('landing_page', ''),
                        "targeting": ad.get('targeting', {})
                    }
                }
                
                training_examples.append(example)
            
            # Save training examples to file
            self._save_training_examples(training_examples)
            
            return training_examples
            
        except Exception as e:
            self.logger.error(f"Error formatting ads for training: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []
    
    def _save_training_examples(self, examples: List[Dict[str, Any]]) -> None:
        """
        Save training examples to a JSON file.
        
        Args:
            examples: List of training examples
        """
        try:
            if not examples:
                return
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"adspy_training_{timestamp}.json"
            filepath = os.path.join(self.output_dir, 'processed', filename)
            
            # Save to JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(examples, f, indent=2)
            
            self.logger.info(f"Saved {len(examples)} training examples to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving training examples: {str(e)}")
    
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

if __name__ == "__main__":
    # Example usage
    scraper = AdSpyScraper(use_proxies=False, headless=False)
    
    try:
        # Scrape ads for specific keywords
        ads = scraper.scrape_ads(
            keywords=["fitness", "workout", "health"],
            platforms=["facebook", "instagram"],
            limit=50
        )
        
        print(f"Collected {len(ads)} ads from AdSpy")
        
        # Extract insights from the collected ads
        insights = scraper.extract_ad_insights(ads)
        print(f"Generated insights for {len(insights)} advertisers")
        
        # Format ads for training
        training_examples = scraper.format_for_training(ads)
        print(f"Created {len(training_examples)} training examples")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always close the browser
        scraper.quit()