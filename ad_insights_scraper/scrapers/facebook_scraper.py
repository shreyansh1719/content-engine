"""
Advanced Facebook Ads Library Scraper with anti-detection measures
"""
import os
import re
import time
import random
import json
import logging
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

class FacebookAdsScraper:
    """
    Advanced Facebook Ads Library scraper with multiple layers of anti-detection.
    
    Features:
    - Uses undetected-chromedriver to evade bot detection
    - Rotates proxies, user-agents, and browser fingerprints
    - Implements humanlike browsing patterns
    - Handles CAPTCHAs when encountered
    - Extracts ad content, engagement metrics, and targeting info
    """
    
    def __init__(
        self,
        output_dir: str = 'data',
        use_proxies: bool = True,
        headless: bool = False,
        log_level: int = logging.INFO
    ):
        """
        Initialize the Facebook Ads Library scraper.
        
        Args:
            output_dir: Directory to save scraped data
            use_proxies: Whether to use proxy rotation
            headless: Run browser in headless mode
            log_level: Logging level
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
        self.max_ads_per_session = 200  # Limit per browser session to avoid detection
        self.scrape_attempts = 0
        self.max_scrape_attempts = 3
        
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
            
            # Create a new driver instance with minimal detectable automation
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
    
    def _check_for_login_block(self) -> bool:
        """
        Check if Facebook is requesting login and handle it.
        
        Returns:
            True if page is accessible, False if blocked by login
        """
        if not self.driver:
            return False
        
        try:
            # Common login block indicators
            login_indicators = [
                "//div[contains(text(), 'Log in to continue')]",
                "//div[contains(text(), 'You must log in')]",
                "//form[@id='login_form']",
                "//button[contains(text(), 'Log In')]",
                "//div[contains(@class, 'login')]//input[@name='email']"
            ]
            
            for indicator in login_indicators:
                login_elements = self.driver.find_elements(By.XPATH, indicator)
                if login_elements and login_elements[0].is_displayed():
                    self.logger.warning("Login block detected!")
                    
                    # Strategies to bypass login requirement:
                    # 1. Try clearing cookies and refreshing
                    self.driver.delete_all_cookies()
                    self._human_like_wait(1.0, 2.0)
                    self.driver.refresh()
                    self._human_like_wait(2.0, 4.0)
                    
                    # Check if login is still required
                    for indicator in login_indicators:
                        login_elements = self.driver.find_elements(By.XPATH, indicator)
                        if login_elements and login_elements[0].is_displayed():
                            self.logger.error("Login block persists, cannot continue")
                            return False
                    
                    # Login no longer required
                    return True
            
            # No login block detected
            return True
            
        except Exception as e:
            self.logger.warning(f"Login block check error: {str(e)}")
            return True  # Assume no login block if check fails
    
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
        
        for keyword in keywords:
            for country in countries:
                for ad_type in ad_types:
                    try:
                        ads = self._scrape_single_search(
                            keyword=keyword,
                            country=country,
                            ad_type=ad_type,
                            max_ads=max_ads_per_keyword
                        )
                        
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
                            f"fb_ads_{keyword}_{country}_{ad_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        )
                        
                        # Reset browser if needed
                        if len(all_ads) >= self.max_ads_per_session:
                            self.logger.info(f"Maximum ads per session reached ({self.max_ads_per_session}), restarting browser")
                            self._reset_session()
                    
                    except Exception as e:
                        self.logger.error(f"Error scraping {keyword} in {country} for {ad_type} ads: {str(e)}")
        
        # Save final results
        self.scraped_ads = all_ads
        self._save_ads_batch(
            all_ads,
            f"fb_ads_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        return all_ads
    
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
    
    def _scrape_single_search(
        self,
        keyword: str,
        country: str = 'US',
        ad_type: str = 'all',
        max_ads: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Scrape ads for a single keyword, country, and ad type.
        
        Args:
            keyword: Search keyword or brand name
            country: Country code
            ad_type: Type of ads to search for
            max_ads: Maximum number of ads to collect
            
        Returns:
            List of ad dictionaries
        """
        collected_ads = []
        
        # Attempt scraping with retries
        self.scrape_attempts = 0
        while self.scrape_attempts < self.max_scrape_attempts and len(collected_ads) < max_ads:
            try:
                # Launch browser if needed
                if not self.driver:
                    if not self._launch_browser():
                        self.logger.error("Failed to launch browser, aborting scrape")
                        break
                
                # Construct search URL
                encoded_keyword = quote(keyword)
                search_url = (
                    f"https://www.facebook.com/ads/library/?"
                    f"active_status=all&ad_type={ad_type}&country={country}&"
                    f"q={encoded_keyword}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped"
                )
                
                # Navigate to ads library
                self.logger.info(f"Searching for '{keyword}' ads in {country}")
                self.driver.get(search_url)
                self.page_load_count += 1
                
                # Initial wait
                self._human_like_wait(2.0, 4.0)
                
                # Check for CAPTCHA and login blocks
                if not self._check_for_captcha() or not self._check_for_login_block():
                    self.logger.warning("Access issues detected, retrying with new session")
                    self._reset_session()
                    self.scrape_attempts += 1
                    continue
                
                # Wait for ads to load
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'AdLibraryResult')]"))
                    )
                except TimeoutException:
                    # Check if "No ads found" is present
                    no_ads_elements = self.driver.find_elements(
                        By.XPATH, 
                        "//div[contains(text(), 'No ads found') or contains(text(), 'No ads matched')]"
                    )
                    
                    if no_ads_elements:
                        self.logger.info(f"No ads found for '{keyword}' in {country}")
                        break
                    else:
                        self.logger.warning("Ads not loading, retrying")
                        self.scrape_attempts += 1
                        continue
                
                # Scroll and collect ads
                prev_ad_count = 0
                scroll_count = 0
                max_scrolls = 50  # Limit to prevent infinite loops
                
                while len(collected_ads) < max_ads and scroll_count < max_scrolls:
                    # Extract ads from current view
                    new_ads = self._extract_ads_from_page()
                    
                    # Add new unique ads to collection
                    existing_ids = {ad['ad_id'] for ad in collected_ads if 'ad_id' in ad}
                    for ad in new_ads:
                        if 'ad_id' in ad and ad['ad_id'] not in existing_ids:
                            collected_ads.append(ad)
                            existing_ids.add(ad['ad_id'])
                    
                    # Log progress
                    if len(collected_ads) > prev_ad_count:
                        self.logger.info(f"Collected {len(collected_ads)} ads for '{keyword}' in {country}")
                        prev_ad_count = len(collected_ads)
                    
                    # Check if we've reached the target number of ads
                    if len(collected_ads) >= max_ads:
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
                        "//div[contains(@class, 'LoadingIndicator')] | //span[contains(text(), 'Load more')]"
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
                    if scroll_count > 5 and prev_ad_count == len(collected_ads):
                        no_more_content = scroll_count % 5 == 0
                        end_of_results_elements = self.driver.find_elements(
                            By.XPATH,
                            "//div[contains(text(), 'End of results') or contains(text(), 'No more ads')]"
                        )
                        
                        if end_of_results_elements or no_more_content:
                            self.logger.info("Reached end of results")
                            break
                
                # Scrape successful, reset attempt counter
                self.scrape_attempts = 0
                
            except Exception as e:
                self.logger.error(f"Error during scraping: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # Increment attempt counter and reset session
                self.scrape_attempts += 1
                self._reset_session()
        
        # Return the collected ads
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
                "//div[contains(@class, 'AdLibraryResult')]"
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
            "page_name": "",
            "page_id": "",
            "ad_text": "",
            "ad_creative": {},
            "ad_format": "",
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
            # Extract ad ID from element attributes or URL
            try:
                # Look for "See Ad Details" or similar buttons
                details_links = ad_element.find_elements(
                    By.XPATH,
                    ".//a[contains(@href, 'ad_id=')]"
                )
                
                if details_links:
                    link_href = details_links[0].get_attribute('href')
                    ad_id_match = re.search(r'ad_id=([0-9]+)', link_href)
                    if ad_id_match:
                        ad_data["ad_id"] = ad_id_match.group(1)
            except:
                pass
            
            # Extract page name and ID
            try:
                page_elements = ad_element.find_elements(
                    By.XPATH, 
                    ".//div[contains(@class, 'AdLibraryPageName')]//a"
                )
                
                if page_elements:
                    ad_data["page_name"] = page_elements[0].text.strip()
                    page_link = page_elements[0].get_attribute('href')
                    page_id_match = re.search(r'facebook\.com/(?:profile\.php\?id=)?([^/?&]+)', page_link)
                    if page_id_match:
                        ad_data["page_id"] = page_id_match.group(1)
            except:
                pass
            
            # Extract ad text
            try:
                text_elements = ad_element.find_elements(
                    By.XPATH,
                    ".//div[contains(@class, 'AdLibraryAdText')]"
                )
                
                if text_elements:
                    ad_data["ad_text"] = text_elements[0].text.strip()
            except:
                pass
            
            # Extract CTA (Call to Action)
            try:
                cta_elements = ad_element.find_elements(
                    By.XPATH,
                    ".//div[contains(@class, 'AdLibraryButtonSection')]//button"
                )
                
                if cta_elements:
                    ad_data["cta_text"] = cta_elements[0].text.strip()
            except:
                pass
            
            # Extract linked URL
            try:
                link_elements = ad_element.find_elements(
                    By.XPATH,
                    ".//div[contains(@class, 'AdLibraryLinkSection')]//a"
                )
                
                if link_elements:
                    ad_data["link_url"] = link_elements[0].get_attribute('href')
            except:
                pass
            
            # Extract platform information
            try:
                platform_elements = ad_element.find_elements(
                    By.XPATH,
                    ".//div[contains(text(), 'Platforms')]//following-sibling::div"
                )
                
                if platform_elements:
                    platforms_text = platform_elements[0].text.strip()
                    ad_data["platform"] = [p.strip() for p in platforms_text.split(',')]
            except:
                pass
            
            # Extract date information
            try:
                date_elements = ad_element.find_elements(
                    By.XPATH,
                    ".//div[contains(text(), 'Active date')]/following-sibling::div"
                )
                
                if date_elements:
                    date_text = date_elements[0].text.strip()
                    
                    # Handle different date formats
                    if "Started running on" in date_text:
                        start_date_match = re.search(r'Started running on (.+?)(?:$|\n)', date_text)
                        if start_date_match:
                            ad_data["start_date"] = start_date_match.group(1).strip()
                            ad_data["status"] = "active"
                    elif " to " in date_text:
                        date_parts = date_text.split(" to ")
                        if len(date_parts) == 2:
                            ad_data["start_date"] = date_parts[0].strip()
                            ad_data["end_date"] = date_parts[1].strip()
                            ad_data["status"] = "inactive" if date_parts[1].strip() else "active"
            except:
                pass
            
            # Extract images
            try:
                image_elements = ad_element.find_elements(
                    By.XPATH,
                    ".//img[not(contains(@src, 'icon')) and not(contains(@src, 'profile'))]"
                )
                
                for img in image_elements:
                    img_src = img.get_attribute('src')
                    if img_src and img_src.startswith('http') and img_src not in ad_data["image_urls"]:
                        ad_data["image_urls"].append(img_src)
                
                if image_elements:
                    ad_data["ad_format"] = "image"
            except:
                pass
            
            # Extract videos
            try:
                video_elements = ad_element.find_elements(
                    By.XPATH,
                    ".//video"
                )
                
                for video in video_elements:
                    video_src = video.get_attribute('src')
                    if video_src and video_src.startswith('http'):
                        ad_data["video_urls"].append(video_src)
                
                if video_elements:
                    ad_data["ad_format"] = "video"
            except:
                pass
            
            # Check if ad has a carousel format
            try:
                carousel_indicators = ad_element.find_elements(
                    By.XPATH,
                    ".//div[contains(@class, 'carousel')]"
                )
                
                if carousel_indicators:
                    ad_data["ad_format"] = "carousel"
            except:
                pass
            
            # Determine ad format if not already set
            if not ad_data["ad_format"]:
                if ad_data["video_urls"]:
                    ad_data["ad_format"] = "video"
                elif ad_data["image_urls"]:
                    ad_data["ad_format"] = "image"
                else:
                    ad_data["ad_format"] = "text"
            
            # Return ad data only if we have essential fields
            if ad_data["ad_id"] or (ad_data["page_name"] and ad_data["ad_text"]):
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
    
    def process_ads_for_training(self) -> List[Dict[str, Any]]:
        """
        Process collected ads into a format suitable for LLM training.
        
        Returns:
            List of processed ad examples
        """
        processed_data = []
        
        try:
            if not self.scraped_ads:
                self.logger.warning("No ads to process")
                return []
            
            for ad in self.scraped_ads:
                # Skip ads without essential content
                if not ad.get('ad_text') or not ad.get('page_name'):
                    continue
                
                # Create training example
                example = {
                    "input": f"Create a {ad.get('ad_format', 'standard')} ad for {ad.get('page_name')} that would be shown on {', '.join(ad.get('platform', ['Facebook']))}",
                    "output": {
                        "headline": ad.get('page_name', ''),
                        "description": ad.get('ad_text', ''),
                        "cta": ad.get('cta_text', ''),
                        "format": ad.get('ad_format', 'standard'),
                        "platforms": ad.get('platform', ['Facebook']),
                        "link_url": ad.get('link_url', ''),
                        "creative_elements": []
                    }
                }
                
                # Add creative elements description
                if ad.get('image_urls'):
                    example["output"]["creative_elements"].append("image")
                if ad.get('video_urls'):
                    example["output"]["creative_elements"].append("video")
                if ad.get('ad_format') == 'carousel':
                    example["output"]["creative_elements"].append("carousel")
                
                processed_data.append(example)
            
            # Save processed data
            processed_filepath = os.path.join(
                self.output_dir, 
                'processed', 
                f"fb_ads_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(processed_filepath, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2)
            
            self.logger.info(f"Saved {len(processed_data)} processed examples to {processed_filepath}")
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error processing ads for training: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
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
    scraper = FacebookAdsScraper(use_proxies=False, headless=False)
    
    try:
        # Scrape ads for specific keywords
        ads = scraper.scrape_ads_library(
            keywords=["fitness", "iphone", "fashion"],
            countries=["US"],
            max_ads_per_keyword=20
        )
        
        print(f"Collected {len(ads)} Facebook ads")
        
        # Process ads for training
        training_examples = scraper.process_ads_for_training()
        print(f"Created {len(training_examples)} training examples")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always close the browser
        scraper.quit()