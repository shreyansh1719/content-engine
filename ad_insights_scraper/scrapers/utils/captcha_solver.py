"""
Advanced CAPTCHA solver utility with multiple solving methods
"""
import os
import time
import base64
import logging
import random
from io import BytesIO
from typing import Optional, Dict, Any, Union, Tuple

import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

class CaptchaSolver:
    """
    Advanced CAPTCHA solver with multiple solving strategies.
    
    Features:
    - Detects various CAPTCHA types (reCAPTCHA v2/v3, hCaptcha, image CAPTCHAs)
    - Supports integration with external solving services
    - Implements automated solving for simple CAPTCHAs
    - Includes heuristic delay tactics to appear more human-like
    - Fallback mechanisms for different CAPTCHA scenarios
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        service: str = 'auto',
        timeout: int = 120,
        delay_range: Tuple[float, float] = (1.0, 3.0)
    ):
        """
        Initialize CAPTCHA solver with API credentials.
        
        Args:
            api_key: API key for CAPTCHA solving service
            service: Service name ('2captcha', 'anticaptcha', 'capsolver', 'auto')
            timeout: Maximum time to wait for CAPTCHA solution (seconds)
            delay_range: Random delay range for human-like behavior (min, max seconds)
        """
        # Setup logging
        self.logger = logging.getLogger('CaptchaSolver')
        
        # Configuration
        self.api_key = api_key or os.getenv('CAPTCHA_API_KEY')
        self.service = service.lower()
        self.timeout = timeout
        self.delay_range = delay_range
        
        # Service API endpoints
        self.service_endpoints = {
            '2captcha': {
                'submit': 'https://2captcha.com/in.php',
                'retrieve': 'https://2captcha.com/res.php'
            },
            'anticaptcha': {
                'submit': 'https://api.anti-captcha.com/createTask',
                'retrieve': 'https://api.anti-captcha.com/getTaskResult'
            },
            'capsolver': {
                'submit': 'https://api.capsolver.com/createTask',
                'retrieve': 'https://api.capsolver.com/getTaskResult'
            }
        }
        
        # Track solving attempts
        self.solving_attempts = 0
        self.max_solving_attempts = 3
        
        # Success/failure tracking for service selection
        self.service_success_rates = {
            '2captcha': 0.0,
            'anticaptcha': 0.0,
            'capsolver': 0.0
        }
        self.service_attempts = {
            '2captcha': 0,
            'anticaptcha': 0,
            'capsolver': 0
        }
        self.service_successes = {
            '2captcha': 0,
            'anticaptcha': 0,
            'capsolver': 0
        }
    
    def solve_captcha(self, driver: webdriver.Chrome) -> bool:
        """
        Detect and solve CAPTCHA on the current page.
        
        Args:
            driver: WebDriver instance with page containing CAPTCHA
            
        Returns:
            True if CAPTCHA was solved successfully, False otherwise
        """
        self.solving_attempts += 1
        
        try:
            # First, detect what type of CAPTCHA we're dealing with
            captcha_type = self._detect_captcha_type(driver)
            
            if not captcha_type:
                self.logger.info("No CAPTCHA detected or unable to classify")
                return True  # No CAPTCHA, consider it "solved"
            
            self.logger.info(f"Detected CAPTCHA type: {captcha_type}")
            
            # Apply solving strategy based on CAPTCHA type
            if captcha_type == 'recaptcha_v2_checkbox':
                return self._solve_recaptcha_v2_checkbox(driver)
            elif captcha_type == 'recaptcha_v2_invisible':
                return self._solve_recaptcha_v2_invisible(driver)
            elif captcha_type == 'recaptcha_v3':
                return self._solve_recaptcha_v3(driver)
            elif captcha_type == 'hcaptcha':
                return self._solve_hcaptcha(driver)
            elif captcha_type == 'image_captcha':
                return self._solve_image_captcha(driver)
            elif captcha_type == 'text_captcha':
                return self._solve_text_captcha(driver)
            elif captcha_type == 'funcaptcha':
                return self._solve_funcaptcha(driver)
            elif captcha_type == 'custom_captcha':
                return self._solve_custom_captcha(driver)
            else:
                self.logger.warning(f"Unsupported CAPTCHA type: {captcha_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error solving CAPTCHA: {str(e)}")
            
            # Retry with a different approach if we have attempts left
            if self.solving_attempts < self.max_solving_attempts:
                self.logger.info(f"Retrying with attempt {self.solving_attempts + 1}/{self.max_solving_attempts}")
                time.sleep(random.uniform(2.0, 5.0))  # Wait before retrying
                return self.solve_captcha(driver)
            
            return False
    
    def _detect_captcha_type(self, driver: webdriver.Chrome) -> Optional[str]:
        """
        Detect the type of CAPTCHA present on the page.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            String identifying CAPTCHA type or None if not detected
        """
        try:
            # Check for reCAPTCHA v2 checkbox
            recaptcha_checkbox = driver.find_elements(
                By.CSS_SELECTOR, 
                'div.g-recaptcha, iframe[src*="google.com/recaptcha/api2/anchor"]'
            )
            if recaptcha_checkbox:
                return 'recaptcha_v2_checkbox'
            
            # Check for reCAPTCHA v2 invisible
            recaptcha_invisible = driver.find_elements(
                By.CSS_SELECTOR, 
                'div.g-recaptcha[data-size="invisible"], iframe[src*="google.com/recaptcha/api2/bframe"]'
            )
            if recaptcha_invisible:
                return 'recaptcha_v2_invisible'
            
            # Check for reCAPTCHA v3
            recaptcha_v3 = driver.find_elements(
                By.CSS_SELECTOR, 
                'script[src*="recaptcha/api.js?render="]'
            )
            if recaptcha_v3:
                return 'recaptcha_v3'
            
            # Check for hCaptcha
            hcaptcha = driver.find_elements(
                By.CSS_SELECTOR, 
                'div.h-captcha, iframe[src*="hcaptcha.com"]'
            )
            if hcaptcha:
                return 'hcaptcha'
            
            # Check for FunCaptcha (Arkose Labs)
            funcaptcha = driver.find_elements(
                By.CSS_SELECTOR, 
                'iframe[src*="arkoselabs"], iframe[src*="funcaptcha"]'
            )
            if funcaptcha:
                return 'funcaptcha'
            
            # Check for simple image CAPTCHA
            image_captcha = driver.find_elements(
                By.CSS_SELECTOR, 
                'img[alt*="captcha" i], img[src*="captcha" i], img[alt*="security" i]'
            )
            if image_captcha:
                return 'image_captcha'
            
            # Check for text input CAPTCHA
            text_captcha_inputs = driver.find_elements(
                By.CSS_SELECTOR, 
                'input[name*="captcha" i], input[id*="captcha" i], input[placeholder*="captcha" i]'
            )
            if text_captcha_inputs:
                return 'text_captcha'
            
            # Check for custom Facebook CAPTCHA
            facebook_captcha = driver.find_elements(
                By.CSS_SELECTOR,
                'div[id*="captcha"], div[class*="captcha"], div[class*="checkpoint"]'
            )
            if facebook_captcha:
                return 'custom_captcha'
            
            # Nothing detected
            return None
            
        except Exception as e:
            self.logger.warning(f"Error detecting CAPTCHA type: {str(e)}")
            return None
    
    def _solve_recaptcha_v2_checkbox(self, driver: webdriver.Chrome) -> bool:
        """
        Solve reCAPTCHA v2 checkbox type.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            True if solved successfully, False otherwise
        """
        try:
            # Try to locate the iframe containing the checkbox
            iframe = driver.find_element(
                By.CSS_SELECTOR, 
                'iframe[src*="google.com/recaptcha/api2/anchor"]'
            )
            
            # Switch to the iframe
            driver.switch_to.frame(iframe)
            
            # Find and click the checkbox
            checkbox = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'recaptcha-anchor'))
            )
            
            # Human-like delay before clicking
            self._human_like_delay()
            
            # Click the checkbox
            checkbox.click()
            
            # Switch back to the main content
            driver.switch_to.default_content()
            
            # Wait for CAPTCHA to be verified (checkbox turns green)
            # This might open an image challenge in another iframe, which requires external solving
            time.sleep(3)  # Wait for potential image challenge to appear
            
            # Check if image challenge appeared
            image_iframe = driver.find_elements(
                By.CSS_SELECTOR, 
                'iframe[src*="google.com/recaptcha/api2/bframe"]'
            )
            
            if image_iframe:
                self.logger.info("Image challenge detected, solving with external service")
                return self._solve_recaptcha_with_service(driver)
            
            # Check if the checkbox is checked
            driver.switch_to.frame(iframe)
            checked = driver.find_elements(
                By.CSS_SELECTOR,
                'span#recaptcha-anchor[aria-checked="true"]'
            )
            driver.switch_to.default_content()
            
            if checked:
                self.logger.info("reCAPTCHA checkbox has been successfully checked")
                return True
            else:
                self.logger.info("Failed to check reCAPTCHA checkbox, trying external service")
                return self._solve_recaptcha_with_service(driver)
                
        except Exception as e:
            self.logger.warning(f"Error solving reCAPTCHA v2 checkbox: {str(e)}")
            return self._solve_recaptcha_with_service(driver)
    
    def _solve_recaptcha_v2_invisible(self, driver: webdriver.Chrome) -> bool:
        """
        Solve invisible reCAPTCHA v2.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            True if solved successfully, False otherwise
        """
        # Invisible reCAPTCHA typically requires specialized solving methods
        # since there's no checkbox to click and it triggers on form submission
        return self._solve_recaptcha_with_service(driver)
    
    def _solve_recaptcha_v3(self, driver: webdriver.Chrome) -> bool:
        """
        Handle reCAPTCHA v3 tokens.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            True if handled successfully, False otherwise
        """
        try:
            # For v3, we can try to extract the site key from the script tag
            site_key = None
            recaptcha_script = driver.find_elements(
                By.CSS_SELECTOR, 
                'script[src*="recaptcha/api.js?render="]'
            )
            
            if recaptcha_script:
                src = recaptcha_script[0].get_attribute('src')
                # Extract site key from src attribute
                if 'render=' in src:
                    site_key = src.split('render=')[1].split('&')[0]
            
            if not site_key:
                # Try to find site key in the page source
                page_source = driver.page_source
                import re
                match = re.search(r'grecaptcha\.execute\([\'"]([^\'"]+)[\'"]', page_source)
                if match:
                    site_key = match.group(1)
            
            if not site_key:
                self.logger.warning("Could not find reCAPTCHA v3 site key")
                return False
            
            # Get page URL for the solving service
            page_url = driver.current_url
            
            # Solve using external service
            if self.api_key:
                token = self._solve_recaptcha_v3_with_service(site_key, page_url)
                if token:
                    # Inject the token into the page
                    js_code = f"""
                    document.dispatchEvent(new CustomEvent('recaptcha-token', {{
                        detail: {{
                            response: '{token}',
                            widgetId: 0
                        }}
                    }}));
                    
                    // Set in grecaptcha object directly if it exists
                    if (typeof grecaptcha !== 'undefined' && grecaptcha.enterprise) {{
                        grecaptcha.enterprise.callbacks.forEach(callback => {{
                            if (callback && typeof callback === 'function') {{
                                try {{
                                    callback('{token}');
                                }} catch (e) {{
                                    console.error('Error executing reCAPTCHA callback', e);
                                }}
                            }}
                        }});
                    }}
                    """
                    driver.execute_script(js_code)
                    
                    self.logger.info("Injected reCAPTCHA v3 token")
                    return True
            
            # If we can't solve it, we just continue, as v3 doesn't block the user interaction
            # It's up to the server to decide what to do with the score
            self.logger.info("Continuing without solving reCAPTCHA v3")
            return True
            
        except Exception as e:
            self.logger.warning(f"Error handling reCAPTCHA v3: {str(e)}")
            return False
    
    def _solve_hcaptcha(self, driver: webdriver.Chrome) -> bool:
        """
        Solve hCaptcha.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            True if solved successfully, False otherwise
        """
        try:
            # Try to locate the hCaptcha iframe
            iframe = driver.find_element(
                By.CSS_SELECTOR, 
                'iframe[src*="hcaptcha.com/captcha"]'
            )
            
            # Extract site key from iframe src
            site_key = None
            src = iframe.get_attribute('src')
            if 'sitekey=' in src:
                site_key = src.split('sitekey=')[1].split('&')[0]
            
            if not site_key:
                self.logger.warning("Could not find hCaptcha site key")
                return False
            
            # Get page URL for the solving service
            page_url = driver.current_url
            
            # Solve using external service
            if self.api_key:
                token = self._solve_hcaptcha_with_service(site_key, page_url)
                if token:
                    # Inject the token into the page
                    js_code = f"""
                    document.querySelector('textarea[name="h-captcha-response"]').innerText = '{token}';
                    document.querySelector('textarea[name="g-recaptcha-response"]').innerText = '{token}';
                    
                    // Trigger callback if defined
                    if (typeof hcaptcha !== 'undefined' && hcaptcha.callbacks) {{
                        for (let callback of Object.values(hcaptcha.callbacks)) {{
                            if (typeof callback === 'function') {{
                                try {{
                                    callback('{token}');
                                }} catch (e) {{
                                    console.error('Error executing hCaptcha callback', e);
                                }}
                            }}
                        }}
                    }}
                    """
                    driver.execute_script(js_code)
                    
                    self.logger.info("Injected hCaptcha token")
                    return True
            
            # Manual fallback - switch to iframe and click the checkbox
            driver.switch_to.frame(iframe)
            
            checkbox = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'checkbox'))
            )
            
            # Human-like delay before clicking
            self._human_like_delay()
            
            # Click the checkbox
            checkbox.click()
            
            # Switch back to the main content
            driver.switch_to.default_content()
            
            # Wait for potential image challenge
            time.sleep(3)
            
            return False  # Manual solving usually requires image challenges which we can't handle
            
        except Exception as e:
            self.logger.warning(f"Error solving hCaptcha: {str(e)}")
            return False
    
    def _solve_image_captcha(self, driver: webdriver.Chrome) -> bool:
        """
        Solve simple image CAPTCHA.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            True if solved successfully, False otherwise
        """
        try:
            # Find CAPTCHA image
            captcha_image = driver.find_element(
                By.CSS_SELECTOR, 
                'img[alt*="captcha" i], img[src*="captcha" i], img[alt*="security" i]'
            )
            
            # Find related input field
            captcha_input = driver.find_element(
                By.CSS_SELECTOR, 
                'input[name*="captcha" i], input[id*="captcha" i], input[placeholder*="captcha" i]'
            )
            
            if not captcha_image or not captcha_input:
                self.logger.warning("Could not find image CAPTCHA elements")
                return False
            
            # Get image source
            image_src = captcha_image.get_attribute('src')
            
            # Download the image
            image_data = None
            if image_src.startswith('data:image'):
                # Handle data URI
                image_data = image_src.split(',')[1]
                image_data = base64.b64decode(image_data)
            else:
                # Handle regular URL
                response = requests.get(image_src, timeout=10)
                response.raise_for_status()
                image_data = response.content
            
            if not image_data:
                self.logger.warning("Failed to download CAPTCHA image")
                return False
            
            # Solve the CAPTCHA
            captcha_text = self._solve_image_captcha_with_service(image_data)
            
            if not captcha_text:
                self.logger.warning("Failed to solve image CAPTCHA")
                return False
            
            # Enter the CAPTCHA text
            captcha_input.clear()
            
            # Human-like typing
            self._human_like_typing(captcha_input, captcha_text)
            
            # Find and click the submit button
            submit_button = driver.find_element(
                By.XPATH, 
                '//button[contains(text(), "Submit") or contains(text(), "Verify") or contains(text(), "Continue")]'
            )
            
            if submit_button:
                self._human_like_delay()
                submit_button.click()
                
                # Wait for page to process the CAPTCHA
                time.sleep(3)
                
                # Check if CAPTCHA is still present
                remaining_captchas = driver.find_elements(
                    By.CSS_SELECTOR, 
                    'img[alt*="captcha" i], img[src*="captcha" i], img[alt*="security" i]'
                )
                
                if not remaining_captchas:
                    self.logger.info("Image CAPTCHA solved successfully")
                    return True
            
            self.logger.warning("Failed to submit image CAPTCHA solution")
            return False
            
        except Exception as e:
            self.logger.warning(f"Error solving image CAPTCHA: {str(e)}")
            return False
    
    def _solve_text_captcha(self, driver: webdriver.Chrome) -> bool:
        """
        Solve simple text CAPTCHA.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            True if solved successfully, False otherwise
        """
        try:
            # Find CAPTCHA instructions
            captcha_instructions = driver.find_elements(
                By.XPATH, 
                '//label[contains(text(), "captcha" or contains(text(), "security") or contains(text(), "verification"))]'
            )
            
            # Find related input field
            captcha_input = driver.find_element(
                By.CSS_SELECTOR, 
                'input[name*="captcha" i], input[id*="captcha" i], input[placeholder*="captcha" i]'
            )
            
            if not captcha_input:
                self.logger.warning("Could not find text CAPTCHA input")
                return False
            
            # Extract CAPTCHA question or challenge
            captcha_question = ""
            if captcha_instructions:
                captcha_question = captcha_instructions[0].text
            else:
                # Try to find instructions near the input
                input_placeholder = captcha_input.get_attribute('placeholder')
                input_label = captcha_input.get_attribute('aria-label')
                
                if input_placeholder:
                    captcha_question = input_placeholder
                elif input_label:
                    captcha_question = input_label
            
            if not captcha_question:
                self.logger.warning("Could not find text CAPTCHA question")
                return False
            
            # Solve the text CAPTCHA
            captcha_answer = self._solve_text_captcha_with_service(captcha_question)
            
            if not captcha_answer:
                self.logger.warning("Failed to solve text CAPTCHA")
                return False
            
            # Enter the CAPTCHA answer
            captcha_input.clear()
            
            # Human-like typing
            self._human_like_typing(captcha_input, captcha_answer)
            
            # Find and click the submit button
            submit_button = driver.find_element(
                By.XPATH, 
                '//button[contains(text(), "Submit") or contains(text(), "Verify") or contains(text(), "Continue")]'
            )
            
            if submit_button:
                self._human_like_delay()
                submit_button.click()
                
                # Wait for page to process the CAPTCHA
                time.sleep(3)
                
                # Check if CAPTCHA is still present
                remaining_captchas = driver.find_elements(
                    By.CSS_SELECTOR, 
                    'input[name*="captcha" i], input[id*="captcha" i], input[placeholder*="captcha" i]'
                )
                
                if not remaining_captchas:
                    self.logger.info("Text CAPTCHA solved successfully")
                    return True
            
            self.logger.warning("Failed to submit text CAPTCHA solution")
            return False
            
        except Exception as e:
            self.logger.warning(f"Error solving text CAPTCHA: {str(e)}")
            return False
    
    def _solve_funcaptcha(self, driver: webdriver.Chrome) -> bool:
        """
        Solve FunCaptcha (Arkose Labs).
        
        Args:
            driver: WebDriver instance
            
        Returns:
            True if solved successfully, False otherwise
        """
        # FunCaptcha requires using an external service
        try:
            # Find the FunCaptcha iframe
            iframe = driver.find_element(
                By.CSS_SELECTOR, 
                'iframe[src*="arkoselabs"], iframe[src*="funcaptcha"]'
            )
            
            # Extract public key from iframe src
            src = iframe.get_attribute('src')
            public_key = None
            
            if 'pk=' in src:
                public_key = src.split('pk=')[1].split('&')[0]
            
            if not public_key:
                self.logger.warning("Could not find FunCaptcha public key")
                return False
            
            # Get page URL for the solving service
            page_url = driver.current_url
            
            # Get service token if present
            service_url = src.split('?')[0] if '?' in src else src
            
            # Solve using external service
            if self.api_key:
                token = self._solve_funcaptcha_with_service(public_key, page_url, service_url)
                if token:
                    # Inject the token into the page
                    js_code = f"""
                    document.querySelector('input[name="fc-token"]').value = '{token}';
                    
                    // Trigger completion callback if defined
                    if (typeof arkose !== 'undefined' && arkose.callbacks) {{
                        try {{
                            arkose.callbacks.complete('{token}');
                        }} catch (e) {{
                            console.error('Error executing Arkose callback', e);
                        }}
                    }}
                    """
                    driver.execute_script(js_code)
                    
                    self.logger.info("Injected FunCaptcha token")
                    return True
            
            # Manual solving isn't practical for FunCaptcha
            self.logger.warning("Manual solving of FunCaptcha not supported")
            return False
            
        except Exception as e:
            self.logger.warning(f"Error solving FunCaptcha: {str(e)}")
            return False
    
    def _solve_custom_captcha(self, driver: webdriver.Chrome) -> bool:
        """
        Solve custom or site-specific CAPTCHAs.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            True if solved successfully, False otherwise
        """
        try:
            # Facebook-specific checkpoint handling
            facebook_checkpoint = driver.find_elements(
                By.CSS_SELECTOR,
                'div#checkpoint_title, div.checkpoint_title'
            )
            
            if facebook_checkpoint:
                # Facebook security checkpoint - look for the continue button
                continue_button = driver.find_elements(
                    By.XPATH,
                    '//button[contains(text(), "Continue") or contains(text(), "Continue")]'
                )
                
                if continue_button:
                    self._human_like_delay()
                    continue_button[0].click()
                    
                    # Wait for page transition
                    time.sleep(3)
                    
                    # Check if we're past the checkpoint
                    remaining_checkpoint = driver.find_elements(
                        By.CSS_SELECTOR,
                        'div#checkpoint_title, div.checkpoint_title'
                    )
                    
                    if not remaining_checkpoint:
                        self.logger.info("Custom checkpoint bypassed successfully")
                        return True
            
            # Generic custom CAPTCHA handling
            # Try to find image and text input patterns
            captcha_image = driver.find_elements(
                By.CSS_SELECTOR, 
                'img[src*="captcha"], img[class*="captcha"], img[alt*="verification"]'
            )
            
            captcha_input = driver.find_elements(
                By.CSS_SELECTOR, 
                'input[id*="captcha"], input[name*="captcha"], input[class*="captcha"]'
            )
            
            if captcha_image and captcha_input:
                return self._solve_image_captcha(driver)
            
            self.logger.warning("Could not identify custom CAPTCHA pattern")
            return False
            
        except Exception as e:
            self.logger.warning(f"Error solving custom CAPTCHA: {str(e)}")
            return False
    
    def _solve_recaptcha_with_service(self, driver: webdriver.Chrome) -> bool:
        """
        Solve reCAPTCHA using an external solving service.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            True if solved successfully, False otherwise
        """
        try:
            if not self.api_key:
                self.logger.warning("No API key provided for CAPTCHA solving service")
                return False
            
            # Extract site key from page
            site_key = None
            
            # Try to find site key in data-sitekey attribute
            site_key_element = driver.find_elements(
                By.CSS_SELECTOR, 
                'div.g-recaptcha[data-sitekey]'
            )
            
            if site_key_element:
                site_key = site_key_element[0].get_attribute('data-sitekey')
            else:
                # Try to find site key in the page source
                page_source = driver.page_source
                import re
                match = re.search(r'data-sitekey=[\'"]([^\'"]+)[\'"]', page_source)
                if match:
                    site_key = match.group(1)
                else:
                    # Try to extract from reCAPTCHA API URL
                    recaptcha_frame = driver.find_elements(
                        By.CSS_SELECTOR, 
                        'iframe[src*="google.com/recaptcha/api2/anchor"]'
                    )
                    if recaptcha_frame:
                        src = recaptcha_frame[0].get_attribute('src')
                        if 'k=' in src:
                            site_key = src.split('k=')[1].split('&')[0]
            
            if not site_key:
                self.logger.warning("Could not find reCAPTCHA site key")
                return False
            
            # Get page URL for the solving service
            page_url = driver.current_url
            
            # Solve using the appropriate service
            token = self._solve_recaptcha_v2_with_service(site_key, page_url)
            
            if not token:
                self.logger.warning("Failed to get reCAPTCHA token from service")
                return False
            
            # Inject the token into the page
            js_code = f"""
            document.getElementById('g-recaptcha-response').innerHTML = '{token}';
            
            // Set on an alternative element if the standard one isn't found
            var elements = document.getElementsByName('g-recaptcha-response');
            for (var i = 0; i < elements.length; i++) {{
                elements[i].innerHTML = '{token}';
            }}
            
            // Attempt to trigger callback
            if (typeof ___grecaptcha_cfg !== 'undefined') {{
                // Find callback index
                for (var i in ___grecaptcha_cfg.clients) {{
                    var client = ___grecaptcha_cfg.clients[i];
                    for (var j in client) {{
                        if (typeof client[j].callback === 'function') {{
                            client[j].callback('{token}');
                            break;
                        }}
                    }}
                }}
            }}
            """
            driver.execute_script(js_code)
            
            self.logger.info("Injected reCAPTCHA token")
            
            # Submit the form if needed
            after_verification_button = driver.find_elements(
                By.XPATH, 
                '//button[contains(text(), "Submit") or contains(text(), "Verify") or contains(text(), "Continue")]'
            )
            
            if after_verification_button:
                self._human_like_delay()
                after_verification_button[0].click()
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Error solving reCAPTCHA with service: {str(e)}")
            return False
    
    def _select_best_service(self) -> str:
        """
        Select the best CAPTCHA solving service based on success rates.
        
        Returns:
            Service name to use
        """
        if self.service != 'auto':
            return self.service
        
        # Calculate current success rates
        for service in self.service_success_rates.keys():
            attempts = self.service_attempts.get(service, 0)
            if attempts > 0:
                success_rate = self.service_successes.get(service, 0) / attempts
                self.service_success_rates[service] = success_rate
        
        # Find service with highest success rate (with at least one attempt)
        best_service = None
        best_rate = -1
        
        for service, rate in self.service_success_rates.items():
            if self.service_attempts.get(service, 0) > 0 and rate > best_rate:
                best_rate = rate
                best_service = service
        
        # If no service has been used yet, use 2captcha as default
        if not best_service:
            return '2captcha'
        
        return best_service
    
    def _solve_recaptcha_v2_with_service(self, site_key: str, page_url: str) -> Optional[str]:
        """
        Solve reCAPTCHA v2 using external service.
        
        Args:
            site_key: reCAPTCHA site key
            page_url: URL of the page with CAPTCHA
            
        Returns:
            CAPTCHA solution token or None if failed
        """
        if not self.api_key:
            return None
        
        service = self._select_best_service()
        self.service_attempts[service] = self.service_attempts.get(service, 0) + 1
        
        try:
            if service == '2captcha':
                # 2captcha API
                params = {
                    'key': self.api_key,
                    'method': 'userrecaptcha',
                    'googlekey': site_key,
                    'pageurl': page_url,
                    'json': 1
                }
                
                # Submit the task
                response = requests.post(self.service_endpoints['2captcha']['submit'], params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data.get('status'):
                    self.logger.warning(f"2captcha task submission failed: {data.get('request')}")
                    return None
                
                # Get the task ID
                task_id = data.get('request')
                
                # Wait for the result
                start_time = time.time()
                while time.time() - start_time < self.timeout:
                    # Delay between checks
                    time.sleep(5)
                    
                    # Check task status
                    params = {
                        'key': self.api_key,
                        'action': 'get',
                        'id': task_id,
                        'json': 1
                    }
                    
                    response = requests.get(self.service_endpoints['2captcha']['retrieve'], params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('status') == 1:
                        # Task completed
                        self.service_successes[service] = self.service_successes.get(service, 0) + 1
                        return data.get('request')
                    
                    if data.get('request') == 'ERROR_CAPTCHA_UNSOLVABLE':
                        self.logger.warning("CAPTCHA reported as unsolvable")
                        return None
                
                self.logger.warning("Timeout waiting for CAPTCHA solution")
                return None
                
            elif service == 'anticaptcha':
                # Anti Captcha API
                task_payload = {
                    'clientKey': self.api_key,
                    'task': {
                        'type': 'NoCaptchaTaskProxyless',
                        'websiteURL': page_url,
                        'websiteKey': site_key
                    }
                }
                
                # Submit the task
                response = requests.post(self.service_endpoints['anticaptcha']['submit'], json=task_payload)
                response.raise_for_status()
                data = response.json()
                
                if data.get('errorId'):
                    self.logger.warning(f"Anti Captcha task submission failed: {data.get('errorDescription')}")
                    return None
                
                # Get the task ID
                task_id = data.get('taskId')
                
                # Wait for the result
                start_time = time.time()
                while time.time() - start_time < self.timeout:
                    # Delay between checks
                    time.sleep(5)
                    
                    # Check task status
                    status_payload = {
                        'clientKey': self.api_key,
                        'taskId': task_id
                    }
                    
                    response = requests.post(self.service_endpoints['anticaptcha']['retrieve'], json=status_payload)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('status') == 'ready':
                        # Task completed
                        self.service_successes[service] = self.service_successes.get(service, 0) + 1
                        return data.get('solution', {}).get('gRecaptchaResponse')
                    
                    if data.get('errorId'):
                        self.logger.warning(f"Anti Captcha error: {data.get('errorDescription')}")
                        return None
                
                self.logger.warning("Timeout waiting for CAPTCHA solution")
                return None
                
            elif service == 'capsolver':
                # CapSolver API
                task_payload = {
                    'clientKey': self.api_key,
                    'task': {
                        'type': 'ReCaptchaV2TaskProxyless',
                        'websiteURL': page_url,
                        'websiteKey': site_key
                    }
                }
                
                # Submit the task
                response = requests.post(self.service_endpoints['capsolver']['submit'], json=task_payload)
                response.raise_for_status()
                data = response.json()
                
                if not data.get('success'):
                    self.logger.warning(f"CapSolver task submission failed: {data.get('errorDescription')}")
                    return None
                
                # Get the task ID
                task_id = data.get('taskId')
                
                # Wait for the result
                start_time = time.time()
                while time.time() - start_time < self.timeout:
                    # Delay between checks
                    time.sleep(5)
                    
                    # Check task status
                    status_payload = {
                        'clientKey': self.api_key,
                        'taskId': task_id
                    }
                    
                    response = requests.post(self.service_endpoints['capsolver']['retrieve'], json=status_payload)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('status') == 'ready':
                        # Task completed
                        self.service_successes[service] = self.service_successes.get(service, 0) + 1
                        return data.get('solution', {}).get('gRecaptchaResponse')
                    
                    if not data.get('success'):
                        self.logger.warning(f"CapSolver error: {data.get('errorDescription')}")
                        return None
                
                self.logger.warning("Timeout waiting for CAPTCHA solution")
                return None
            
            else:
                self.logger.warning(f"Unsupported service: {service}")
                return None
                
        except Exception as e:
            self.logger.warning(f"Error using {service} service: {str(e)}")
            return None
    
    def _solve_recaptcha_v3_with_service(self, site_key: str, page_url: str, min_score: float = 0.7) -> Optional[str]:
        """
        Solve reCAPTCHA v3 using external service.
        
        Args:
            site_key: reCAPTCHA site key
            page_url: URL of the page with CAPTCHA
            min_score: Minimum score to target (0.0 to 1.0)
            
        Returns:
            CAPTCHA solution token or None if failed
        """
        # Similar to v2 solving but with v3-specific parameters
        service = self._select_best_service()
        self.service_attempts[service] = self.service_attempts.get(service, 0) + 1
        
        try:
            if service == '2captcha':
                # 2captcha API
                params = {
                    'key': self.api_key,
                    'method': 'userrecaptcha',
                    'version': 'v3',
                    'action': 'verify',
                    'min_score': min_score,
                    'googlekey': site_key,
                    'pageurl': page_url,
                    'json': 1
                }
                
                # Submit the task
                response = requests.post(self.service_endpoints['2captcha']['submit'], params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data.get('status'):
                    self.logger.warning(f"2captcha task submission failed: {data.get('request')}")
                    return None
                
                # Get the task ID
                task_id = data.get('request')
                
                # Wait for the result
                start_time = time.time()
                while time.time() - start_time < self.timeout:
                    # Delay between checks
                    time.sleep(5)
                    
                    # Check task status
                    params = {
                        'key': self.api_key,
                        'action': 'get',
                        'id': task_id,
                        'json': 1
                    }
                    
                    response = requests.get(self.service_endpoints['2captcha']['retrieve'], params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('status') == 1:
                        # Task completed
                        self.service_successes[service] = self.service_successes.get(service, 0) + 1
                        return data.get('request')
                    
                    if data.get('request') == 'ERROR_CAPTCHA_UNSOLVABLE':
                        self.logger.warning("CAPTCHA reported as unsolvable")
                        return None
                
                self.logger.warning("Timeout waiting for CAPTCHA solution")
                return None
            
            # Implement other services if needed
            
            else:
                self.logger.warning(f"Unsupported service for reCAPTCHA v3: {service}")
                return None
                
        except Exception as e:
            self.logger.warning(f"Error solving reCAPTCHA v3 with service: {str(e)}")
            return None
    
    def _solve_hcaptcha_with_service(self, site_key: str, page_url: str) -> Optional[str]:
        """
        Solve hCaptcha using external service.
        
        Args:
            site_key: hCaptcha site key
            page_url: URL of the page with CAPTCHA
            
        Returns:
            CAPTCHA solution token or None if failed
        """
        # Similar to reCAPTCHA solving but with hCaptcha-specific parameters
        service = self._select_best_service()
        self.service_attempts[service] = self.service_attempts.get(service, 0) + 1
        
        try:
            if service == '2captcha':
                # 2captcha API
                params = {
                    'key': self.api_key,
                    'method': 'hcaptcha',
                    'sitekey': site_key,
                    'pageurl': page_url,
                    'json': 1
                }
                
                # Submit the task
                response = requests.post(self.service_endpoints['2captcha']['submit'], params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data.get('status'):
                    self.logger.warning(f"2captcha task submission failed: {data.get('request')}")
                    return None
                
                # Get the task ID
                task_id = data.get('request')
                
                # Wait for the result
                start_time = time.time()
                while time.time() - start_time < self.timeout:
                    # Delay between checks
                    time.sleep(5)
                    
                    # Check task status
                    params = {
                        'key': self.api_key,
                        'action': 'get',
                        'id': task_id,
                        'json': 1
                    }
                    
                    response = requests.get(self.service_endpoints['2captcha']['retrieve'], params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('status') == 1:
                        # Task completed
                        self.service_successes[service] = self.service_successes.get(service, 0) + 1
                        return data.get('request')
                    
                    if data.get('request') == 'ERROR_CAPTCHA_UNSOLVABLE':
                        self.logger.warning("CAPTCHA reported as unsolvable")
                        return None
                
                self.logger.warning("Timeout waiting for CAPTCHA solution")
                return None
            
            # Implement other services if needed
            
            else:
                self.logger.warning(f"Unsupported service for hCaptcha: {service}")
                return None
                
        except Exception as e:
            self.logger.warning(f"Error solving hCaptcha with service: {str(e)}")
            return None
    
    def _solve_funcaptcha_with_service(self, public_key: str, page_url: str, service_url: str) -> Optional[str]:
        """
        Solve FunCaptcha using external service.
        
        Args:
            public_key: FunCaptcha public key
            page_url: URL of the page with CAPTCHA
            service_url: FunCaptcha service URL
            
        Returns:
            CAPTCHA solution token or None if failed
        """
        # Similar to other CAPTCHA types but with FunCaptcha-specific parameters
        service = self._select_best_service()
        self.service_attempts[service] = self.service_attempts.get(service, 0) + 1
        
        try:
            if service == '2captcha':
                # 2captcha API
                params = {
                    'key': self.api_key,
                    'method': 'funcaptcha',
                    'publickey': public_key,
                    'pageurl': page_url,
                    'surl': service_url,
                    'json': 1
                }
                
                # Submit the task
                response = requests.post(self.service_endpoints['2captcha']['submit'], params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data.get('status'):
                    self.logger.warning(f"2captcha task submission failed: {data.get('request')}")
                    return None
                
                # Get the task ID
                task_id = data.get('request')
                
                # Wait for the result
                start_time = time.time()
                while time.time() - start_time < self.timeout:
                    # Delay between checks
                    time.sleep(5)
                    
                    # Check task status
                    params = {
                        'key': self.api_key,
                        'action': 'get',
                        'id': task_id,
                        'json': 1
                    }
                    
                    response = requests.get(self.service_endpoints['2captcha']['retrieve'], params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('status') == 1:
                        # Task completed
                        self.service_successes[service] = self.service_successes.get(service, 0) + 1
                        return data.get('request')
                    
                    if data.get('request') == 'ERROR_CAPTCHA_UNSOLVABLE':
                        self.logger.warning("CAPTCHA reported as unsolvable")
                        return None
                
                self.logger.warning("Timeout waiting for CAPTCHA solution")
                return None
            
            # Implement other services if needed
            
            else:
                self.logger.warning(f"Unsupported service for FunCaptcha: {service}")
                return None
                
        except Exception as e:
            self.logger.warning(f"Error solving FunCaptcha with service: {str(e)}")
            return None
    
    def _solve_image_captcha_with_service(self, image_data: bytes) -> Optional[str]:
        """
        Solve image CAPTCHA using external service.
        
        Args:
            image_data: CAPTCHA image data
            
        Returns:
            CAPTCHA solution text or None if failed
        """
        service = self._select_best_service()
        self.service_attempts[service] = self.service_attempts.get(service, 0) + 1
        
        try:
            if service == '2captcha':
                # 2captcha API
                files = {
                    'file': ('captcha.png', image_data)
                }
                
                params = {
                    'key': self.api_key,
                    'method': 'post',
                    'json': 1
                }
                
                # Submit the task
                response = requests.post(self.service_endpoints['2captcha']['submit'], params=params, files=files)
                response.raise_for_status()
                data = response.json()
                
                if not data.get('status'):
                    self.logger.warning(f"2captcha task submission failed: {data.get('request')}")
                    return None
                
                # Get the task ID
                task_id = data.get('request')
                
                # Wait for the result
                start_time = time.time()
                while time.time() - start_time < self.timeout:
                    # Delay between checks
                    time.sleep(5)
                    
                    # Check task status
                    params = {
                        'key': self.api_key,
                        'action': 'get',
                        'id': task_id,
                        'json': 1
                    }
                    
                    response = requests.get(self.service_endpoints['2captcha']['retrieve'], params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('status') == 1:
                        # Task completed
                        self.service_successes[service] = self.service_successes.get(service, 0) + 1
                        return data.get('request')
                    
                    if data.get('request') == 'ERROR_CAPTCHA_UNSOLVABLE':
                        self.logger.warning("CAPTCHA reported as unsolvable")
                        return None
                
                self.logger.warning("Timeout waiting for CAPTCHA solution")
                return None
            
            # Implement other services if needed
            
            else:
                self.logger.warning(f"Unsupported service for image CAPTCHA: {service}")
                return None
                
        except Exception as e:
            self.logger.warning(f"Error solving image CAPTCHA with service: {str(e)}")
            return None
    
    def _solve_text_captcha_with_service(self, captcha_question: str) -> Optional[str]:
        """
        Solve text CAPTCHA using external service.
        
        Args:
            captcha_question: Text CAPTCHA question
            
        Returns:
            CAPTCHA solution text or None if failed
        """
        service = self._select_best_service()
        self.service_attempts[service] = self.service_attempts.get(service, 0) + 1
        
        try:
            if service == '2captcha':
                # 2captcha API
                params = {
                    'key': self.api_key,
                    'method': 'textcaptcha',
                    'textcaptcha': captcha_question,
                    'json': 1
                }
                
                # Submit the task
                response = requests.post(self.service_endpoints['2captcha']['submit'], params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data.get('status'):
                    self.logger.warning(f"2captcha task submission failed: {data.get('request')}")
                    return None
                
                # Get the task ID
                task_id = data.get('request')
                
                # Wait for the result
                start_time = time.time()
                while time.time() - start_time < self.timeout:
                    # Delay between checks
                    time.sleep(5)
                    
                    # Check task status
                    params = {
                        'key': self.api_key,
                        'action': 'get',
                        'id': task_id,
                        'json': 1
                    }
                    
                    response = requests.get(self.service_endpoints['2captcha']['retrieve'], params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('status') == 1:
                        # Task completed
                        self.service_successes[service] = self.service_successes.get(service, 0) + 1
                        return data.get('request')
                    
                    if data.get('request') == 'ERROR_CAPTCHA_UNSOLVABLE':
                        self.logger.warning("CAPTCHA reported as unsolvable")
                        return None
                
                self.logger.warning("Timeout waiting for CAPTCHA solution")
                return None
            
            # Implement other services if needed
            
            else:
                self.logger.warning(f"Unsupported service for text CAPTCHA: {service}")
                return None
                
        except Exception as e:
            self.logger.warning(f"Error solving text CAPTCHA with service: {str(e)}")
            return None
    
    def _human_like_delay(self) -> None:
        """
        Wait for a random amount of time to mimic human behavior.
        """
        min_delay, max_delay = self.delay_range
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
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

# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create CAPTCHA solver
    solver = CaptchaSolver(
        api_key=os.getenv('CAPTCHA_API_KEY'),
        service='2captcha'
    )
    
    print("CAPTCHA Solver initialized. It would normally be used within a scraping routine.")
    print("Example: solver.solve_captcha(driver)")