import os
import sys
import json
import logging
import time
import random
import subprocess
from typing import List, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

class AdSpyScraper:
    def __init__(self, username: str, password: str, headless: bool = False):
        """
        Initialize AdSpy scraper with login credentials.
        
        Args:
            username: AdSpy login username
            password: AdSpy login password
            headless: Run browser in headless mode (default: False)
        """
        # Setup logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('adspy_scraper.log', encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load environment variables
        load_dotenv()
        
        # Setup Chrome options
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        
        # More robust browser configuration
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--disable-software-rasterizer')
        
        # User agents to rotate
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        # Initialize webdriver
        self.driver = None
        
        # Login credentials
        self.username = username
        self.password = password
        
        # Scraped ads storage
        self.scraped_ads: List[Dict[Any, Any]] = []
    
    def _get_chrome_version(self):
        """
        Detect Chrome version cross-platform
        """
        try:
            # Windows
            if sys.platform.startswith('win'):
                try:
                    import winreg
                    key = winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER, 
                        r"Software\Google\Chrome\BLBeacon"
                    )
                    version, _ = winreg.QueryValueEx(key, "version")
                    return version.split('.')[0]
                except ImportError:
                    # Fallback for Windows
                    result = subprocess.run(['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'], 
                                            capture_output=True, text=True)
                    if result.returncode == 0:
                        return result.stdout.split()[-1].split('.')[0]
            
            # macOS
            elif sys.platform == 'darwin':
                result = subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], 
                                        capture_output=True, text=True)
                return result.stdout.split()[2].split('.')[0]
            
            # Linux
            elif sys.platform.startswith('linux'):
                result = subprocess.run(['google-chrome', '--version'], 
                                        capture_output=True, text=True)
                return result.stdout.split()[2].split('.')[0]
        
        except Exception as e:
            self.logger.error(f"Could not detect Chrome version: {e}")
        
        return None
    
    def _get_chromedriver_path(self):
        """
        Attempt to find or download appropriate ChromeDriver
        """
        # Check if ChromeDriver is already in PATH
        try:
            from shutil import which
            chromedriver_path = which('chromedriver')
            if chromedriver_path:
                return chromedriver_path
        except:
            pass
        
        # Custom download directory
        driver_dir = os.path.join(os.path.expanduser('~'), '.chromedriver')
        os.makedirs(driver_dir, exist_ok=True)
        
        # Get Chrome version
        chrome_version = self._get_chrome_version()
        
        if chrome_version:
            # Construct download URL
            download_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{chrome_version}.0.0.0/win64/chromedriver-win64.zip"
            
            try:
                import requests
                import zipfile
                
                # Download driver
                driver_zip_path = os.path.join(driver_dir, 'chromedriver.zip')
                response = requests.get(download_url)
                
                if response.status_code == 200:
                    with open(driver_zip_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Unzip the file
                    with zipfile.ZipFile(driver_zip_path, 'r') as zip_ref:
                        zip_ref.extractall(driver_dir)
                    
                    # Find the executable
                    for root, dirs, files in os.walk(driver_dir):
                        for file in files:
                            if file == 'chromedriver.exe':
                                return os.path.join(root, file)
            
            except Exception as e:
                self.logger.error(f"ChromeDriver download error: {e}")
        
        # Fallback to WebDriverManager
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            return ChromeDriverManager().install()
        except Exception as e:
            self.logger.error(f"WebDriverManager fallback failed: {e}")
        
        return None
    
    def _setup_driver(self):
        """
        Set up Chrome WebDriver with multiple fallback mechanisms
        """
        try:
            # Close existing driver if open
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            
            # Randomize user agent
            self.options.add_argument(f'user-agent={random.choice(self.user_agents)}')
            
            # Get ChromeDriver path
            driver_path = self._get_chromedriver_path()
            
            if not driver_path:
                raise ValueError("Could not locate ChromeDriver")
            
            # Initialize WebDriver
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=self.options)
            
            # Set page load and script timeouts
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            self.logger.info("WebDriver initialized successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"WebDriver setup error: {e}")
            return False
    
    def login(self) -> bool:
        """
        Log in to AdSpy using provided credentials.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            # Setup driver
            if not self._setup_driver():
                self.logger.error("Failed to set up WebDriver")
                return False
            
            # Navigate to login page
            self.driver.get("https://app.adspy.com/login")
            
            # Wait for login form to load
            email_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            
            # Find password input
            password_input = self.driver.find_element(By.NAME, "password")
            
            # Clear and fill credentials
            email_input.clear()
            email_input.send_keys(self.username)
            
            password_input.clear()
            password_input.send_keys(self.password)
            
            # Find and click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            
            # Click login button
            login_button.click()
            
            # Wait for dashboard or successful login indicator
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "dashboard-element")) or
                EC.url_contains("/dashboard")
            )
            
            self.logger.info("Login successful")
            return True
        
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def search_ads(self, 
                   keyword: str, 
                   platform: str = "facebook", 
                   min_engagement: int = 500) -> None:
        """
        Search for ads with specified filters.
        """
        try:
            # Construct search URL
            search_url = f"https://app.adspy.com/search?query={keyword}&platform={platform}"
            self.driver.get(search_url)
            
            # Wait for search results
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ad-result"))
            )
            
            # Find ad elements
            ad_elements = self.driver.find_elements(By.CLASS_NAME, "ad-result")
            
            # Process each ad
            for ad_element in ad_elements:
                try:
                    ad_data = self._extract_ad_details(ad_element)
                    
                    # Filter by engagement
                    total_engagement = (
                        ad_data.get('engagement', {}).get('likes', 0) +
                        ad_data.get('engagement', {}).get('comments', 0) +
                        ad_data.get('engagement', {}).get('shares', 0)
                    )
                    
                    if total_engagement >= min_engagement:
                        self.scraped_ads.append(ad_data)
                
                except Exception as ad_error:
                    self.logger.warning(f"Error processing ad: {str(ad_error)}")
            
            self.logger.info(f"Scraped {len(self.scraped_ads)} high-performing ads")
        
        except Exception as e:
            self.logger.error(f"Ad search failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _extract_ad_details(self, ad_element) -> Dict[str, Any]:
        """
        Extract details from a single ad element.
        """
        ad_data = {
            'title': '',
            'description': '',
            'engagement': {
                'likes': 0,
                'comments': 0,
                'shares': 0
            },
            'image_url': '',
            'ad_link': ''
        }
        
        try:
            # Extract title
            title_elements = ad_element.find_elements(By.XPATH, ".//h3")
            if title_elements:
                ad_data['title'] = title_elements[0].text.strip()
            
            # Extract description
            desc_elements = ad_element.find_elements(By.XPATH, ".//div[contains(@class, 'ad-text')]")
            if desc_elements:
                ad_data['description'] = desc_elements[0].text.strip()
            
            # Extract image
            img_elements = ad_element.find_elements(By.XPATH, ".//img")
            if img_elements:
                ad_data['image_url'] = img_elements[0].get_attribute('src')
            
            # Extract engagement
            engagement_elements = ad_element.find_elements(By.XPATH, ".//div[contains(@class, 'engagement')]")
            if engagement_elements:
                engagement_text = engagement_elements[0].text
                # Parse engagement metrics
                try:
                    metrics = engagement_text.split('\n')
                    for metric in metrics:
                        if 'Like' in metric:
                            ad_data['engagement']['likes'] = int(metric.split()[0].replace(',', ''))
                        elif 'Comment' in metric:
                            ad_data['engagement']['comments'] = int(metric.split()[0].replace(',', ''))
                        elif 'Share' in metric:
                            ad_data['engagement']['shares'] = int(metric.split()[0].replace(',', ''))
                except Exception:
                    pass
            
            # Extract ad link
            link_elements = ad_element.find_elements(By.XPATH, ".//a[contains(@href, 'facebook.com')]")
            if link_elements:
                ad_data['ad_link'] = link_elements[0].get_attribute('href')
        
        except Exception as e:
            self.logger.warning(f"Error extracting ad details: {str(e)}")
        
        return ad_data
    
    def paginate_and_scrape(self, 
                             keyword: str, 
                             max_pages: int = 5, 
                             platform: str = "facebook",
                             min_engagement: int = 500) -> None:
        """
        Scrape multiple pages of search results.
        """
        for page in range(max_pages):
            try:
                # Search ads for current page
                self.search_ads(
                    keyword=keyword, 
                    platform=platform, 
                    min_engagement=min_engagement
                )
                
                # Try to navigate to next page
                next_button = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Next')]")
                if not next_button:
                    break
                
                next_button[0].click()
                
                # Wait for next page to load
                time.sleep(2)
            
            except Exception as e:
                self.logger.error(f"Error during pagination: {str(e)}")
                break
    
    def quit(self) -> None:
        """Close the browser and end the session."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.warning(f"Error closing driver: {e}")

def main():
    """
    Main function to demonstrate AdSpy scraper usage.
    """
    # Load credentials from environment variables
    username = os.getenv('ADSPY_USERNAME')
    password = os.getenv('ADSPY_PASSWORD')
    
    if not username or not password:
        print("Please set ADSPY_USERNAME and ADSPY_PASSWORD in .env file")
        return
    
    # Initialize scraper
    scraper = AdSpyScraper(username, password, headless=False)
    
    try:
        # Login to AdSpy
        if not scraper.login():
            print("Login failed. Check credentials.")# Example search keywords
        keywords = ['fitness', 'technology', 'ecommerce']
        
        # Scrape ads for each keyword
        for keyword in keywords:
            scraper.paginate_and_scrape(
                keyword=keyword, 
                max_pages=3, 
                platform='facebook', 
                min_engagement=500
            )
        
        # Print collected ads
        print(f"Total ads collected: {len(scraper.scraped_ads)}")
    
    except Exception as e:
        print(f"Scraping error: {e}")
    
    finally:
        # Always close the browser
        scraper.quit()

if __name__ == "__main__":
    main()