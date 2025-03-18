# marketplace_scraper/scraper.py - Simplified version
import os
import logging
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class MarketplaceScraper:
    def __init__(self, username=None, password=None, output_dir='marketplace_data', headless=False):
        self.username = username
        self.password = password
        self.output_dir = output_dir
        self.headless = headless
        self.driver = None
        self.setup_logger()
        self.setup_dirs()
        
    def setup_logger(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def setup_dirs(self):
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'processed'), exist_ok=True)
    
    def setup_browser(self):
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-notifications')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.logger.info("Browser initialized")
    
    def login(self):
        if not self.username or not self.password:
            raise ValueError("Facebook username and password required")
        
        if not self.driver:
            self.setup_browser()
            
        try:
            self.driver.get("https://www.facebook.com/login")
            time.sleep(2)
            
            # Find username field
            username_field = self.driver.find_element(By.ID, "email")
            username_field.send_keys(self.username)
            
            # Find password field
            password_field = self.driver.find_element(By.ID, "pass")
            password_field.send_keys(self.password)
            
            # Click login
            login_button = self.driver.find_element(By.NAME, "login")
            login_button.click()
            
            # Wait for login
            WebDriverWait(self.driver, 20).until(
                EC.url_contains("facebook.com/")
            )
            
            # Check for security verification
            if "login" in self.driver.current_url:
                self.logger.error("Login failed, please check credentials")
                return False
                
            self.logger.info("Login successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Login error: {str(e)}")
            return False
    
    def navigate_to_marketplace(self, category=None):
        base_url = "https://www.facebook.com/marketplace/"
        url = base_url + (category if category else "")
        
        self.driver.get(url)
        time.sleep(3)
        
        if "marketplace" not in self.driver.current_url:
            self.logger.warning("Failed to navigate to marketplace")
            return False
        
        self.logger.info(f"Navigated to marketplace category: {category if category else 'all'}")
        return True
    
    def extract_ad_details(self, ad_element):
        try:
            ad_data = {
                "extraction_time": datetime.now().isoformat()
            }
            
            # Get href
            href = ad_element.get_attribute("href")
            if href:
                ad_data["url"] = href
            
            # Get title
            try:
                title_elements = ad_element.find_elements(By.TAG_NAME, "span")
                for span in title_elements:
                    text = span.text
                    if text and len(text) > 5 and len(text) < 100:
                        ad_data["title"] = text
                        break
            except:
                pass
            
            # Get price
            try:
                price_elements = ad_element.find_elements(By.XPATH, ".//span[contains(text(), '$')]")
                if price_elements:
                    ad_data["price"] = price_elements[0].text
            except:
                pass
            
            return ad_data if "title" in ad_data or "price" in ad_data else None
        except:
            return None
    
    def scroll_and_collect_ads(self, max_ads=100, category=None):
        if not self.driver:
            return []
            
        collected_ads = []
        
        try:
            self.navigate_to_marketplace(category)
            
            # Set up variables
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            seen_hrefs = set()
            
            while len(collected_ads) < max_ads:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Find ad elements
                ad_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/marketplace/item/')]")
                
                # Process new ads
                for ad_element in ad_elements:
                    href = ad_element.get_attribute("href")
                    if href and href not in seen_hrefs:
                        seen_hrefs.add(href)
                        
                        # Extract details
                        ad_details = self.extract_ad_details(ad_element)
                        if ad_details:
                            collected_ads.append(ad_details)
                            
                            if len(collected_ads) % 10 == 0:
                                self.logger.info(f"Collected {len(collected_ads)} ads")
                                
                            if len(collected_ads) >= max_ads:
                                break
                
                # Check if we've reached the bottom
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
        except Exception as e:
            self.logger.error(f"Error collecting ads: {str(e)}")
            
        return collected_ads
    
    def save_collected_data(self, ads):
        if not ads:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.output_dir, 'processed', f'marketplace_ads_{timestamp}.json')
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(ads, f, indent=4)
            self.logger.info(f"Saved {len(ads)} ads to {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}")
    
    def run_comprehensive_scraping_session(self, max_ads=100, categories=None):
        if not categories:
            categories = ['']  # Default to all
            
        collected_ads = []
        
        try:
            # Login
            success = self.login()
            if not success:
                return []
                
            # Collect ads from each category
            for category in categories:
                self.logger.info(f"Collecting ads from category: {category if category else 'all'}")
                ads = self.scroll_and_collect_ads(max_ads=max_ads, category=category)
                collected_ads.extend(ads)
                
            # Save data
            self.save_collected_data(collected_ads)
            
        except Exception as e:
            self.logger.error(f"Error in scraping session: {str(e)}")
        finally:
            # Close browser
            if self.driver:
                self.driver.quit()
                
        return collected_ads
    
    def extract_trends_from_marketplace_data(self, data_folder):
        """Extract trends from collected marketplace data"""
        try:
            # Find all JSON files
            json_files = [f for f in os.listdir(data_folder) if f.endswith('.json')]
            
            if not json_files:
                self.logger.warning(f"No JSON files found in {data_folder}")
                return {}
                
            # Process files
            all_ads = []
            for file in json_files:
                try:
                    with open(os.path.join(data_folder, file), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        all_ads.extend(data)
                    elif isinstance(data, dict) and 'ads' in data:
                        all_ads.extend(data['ads'])
                except:
                    pass
            
            # Calculate trends
            trends = {
                "extraction_date": datetime.now().isoformat(),
                "total_ads_analyzed": len(all_ads),
                "industries": {}
            }
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error extracting trends: {str(e)}")
            return {}

# Example usage
if __name__ == "__main__":
    scraper = MarketplaceScraper(username="your_username", password="your_password")
    ads = scraper.run_comprehensive_scraping_session(max_ads=50)
    print(f"Collected {len(ads)} ads")