"""
Browser fingerprint randomization to evade detection systems
"""
import random
import logging
from typing import Dict, List, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

class FingerprintRandomizer:
    """
    Advanced browser fingerprint randomization to evade detection.
    
    Features:
    - Randomizes various browser fingerprinting parameters
    - Customizes browser features and capabilities
    - Masks automation indicators
    - Simulates realistic user environments
    - Works with Chrome and Firefox browsers
    """
    
    def __init__(self):
        """Initialize the fingerprint randomizer."""
        # Setup logging
        self.logger = logging.getLogger('FingerprintRandomizer')
        
        # Common screen resolutions (width, height)
        self.screen_resolutions = [
            (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
            (1280, 720), (1600, 900), (1280, 800), (1920, 1200)
        ]
        
        # Common color depths
        self.color_depths = [24, 30, 32]
        
        # Common hardware concurrency (CPU threads)
        self.hardware_concurrency = [2, 4, 6, 8, 12, 16]
        
        # Common device memory values (GB)
        self.device_memory = [2, 4, 8, 16]
        
        # Common platform values
        self.platforms = {
            'windows': [
                'Win32', 'Win64', 'Windows NT 10.0; Win64; x64',
                'Windows NT 10.0; WOW64', 'Windows NT 10.0'
            ],
            'mac': [
                'MacIntel', 'Macintosh; Intel Mac OS X 10_15_7',
                'Macintosh; Intel Mac OS X 11_6_0',
                'Macintosh; Intel Mac OS X 12_0_1',
                'Macintosh; Intel Mac OS X 13_3_1'
            ],
            'linux': [
                'Linux x86_64', 'X11; Linux x86_64', 'X11; Ubuntu; Linux x86_64'
            ]
        }
        
        # Common language lists
        self.languages = [
            ['en-US', 'en', 'es-ES', 'es', 'fr-FR'],
            ['en-US', 'en'],
            ['en-US', 'en', 'fr-FR', 'fr'],
            ['en-GB', 'en', 'de-DE', 'de'],
            ['en-US', 'en', 'zh-CN', 'zh']
        ]
        
        # Common timezone offsets in minutes
        self.timezone_offsets = [-480, -420, -360, -300, -240, -180, -120, -60, 0, 60, 120, 180, 240, 300, 360, 480, 540, 600]
        
        # Common browser plugins (limited, as plugins are being phased out)
        self.plugins = [
            ['Chrome PDF Plugin', 'Chrome PDF Viewer', 'Native Client'],
            ['Chrome PDF Viewer', 'Native Client'],
            ['PDF Viewer', 'WebKit built-in PDF']
        ]
        
        # Common touch points for touch devices
        self.max_touch_points = [0, 2, 5, 10]
        
        # WebGL vendor and renderer info
        self.webgl_vendors = ['Google Inc.', 'Intel Inc.', 'NVIDIA Corporation', 'AMD', 'Apple Inc.']
        self.webgl_renderers = [
            'ANGLE (Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0)',
            'ANGLE (NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0)',
            'ANGLE (NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0)',
            'ANGLE (AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0)',
            'Apple M1',
            'Apple M1 Pro',
            'Apple M2',
            'Intel Iris OpenGL Engine',
            'AMD Radeon Pro 5500M OpenGL Engine'
        ]
        
        # WebRTC settings
        self.enable_webrtc_probability = 0.7  # 70% chance of enabling WebRTC
    
    def get_random_fingerprint_profile(self) -> Dict[str, Any]:
        """
        Generate a random fingerprint profile with consistent values.
        
        Returns:
            Dictionary with fingerprinting parameters
        """
        # Choose a platform (Windows, Mac, Linux)
        platform_type = random.choice(['windows', 'mac', 'linux'])
        platform = random.choice(self.platforms[platform_type])
        
        # Choose a resolution based on platform
        if platform_type == 'windows':
            resolution = random.choice(self.screen_resolutions)
        elif platform_type == 'mac':
            resolution = random.choice([(1440, 900), (1680, 1050), (2560, 1600), (2880, 1800)])
        else:  # Linux
            resolution = random.choice([(1920, 1080), (1366, 768), (1280, 800), (3840, 2160)])
        
        # Generate consistent profile
        profile = {
            'platform': platform,
            'screen_resolution': resolution,
            'color_depth': random.choice(self.color_depths),
            'hardware_concurrency': random.choice(self.hardware_concurrency),
            'device_memory': random.choice(self.device_memory),
            'languages': random.choice(self.languages),
            'timezone_offset': random.choice(self.timezone_offsets),
            'plugins': random.choice(self.plugins),
            'max_touch_points': random.choice(self.max_touch_points),
            'webgl_vendor': random.choice(self.webgl_vendors),
            'webgl_renderer': random.choice(self.webgl_renderers),
            'enable_webrtc': random.random() < self.enable_webrtc_probability
        }
        
        return profile
    
    def apply_to_options(self, options: Any) -> Any:
        """
        Apply fingerprint randomization to browser options.
        
        Args:
            options: Browser options object (Chrome or Firefox)
            
        Returns:
            Modified options object
        """
        # Generate random profile
        profile = self.get_random_fingerprint_profile()
        
        # Apply common modifications for both browsers
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Apply browser-specific modifications
        if isinstance(options, ChromeOptions):
            return self._apply_to_chrome_options(options, profile)
        elif isinstance(options, FirefoxOptions):
            return self._apply_to_firefox_options(options, profile)
        else:
            self.logger.warning(f"Unsupported options type: {type(options)}")
            return options
    
    def _apply_to_chrome_options(self, options: ChromeOptions, profile: Dict[str, Any]) -> ChromeOptions:
        """
        Apply fingerprint randomization to Chrome options.
        
        Args:
            options: Chrome options object
            profile: Fingerprint profile
            
        Returns:
            Modified Chrome options
        """
        # Apply window size based on profile
        width, height = profile['screen_resolution']
        options.add_argument(f'--window-size={width},{height}')
        
        # Set platform
        options.add_argument(f'--platform={profile["platform"]}')
        
        # Disable automation flags
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add language preferences
        options.add_argument(f'--lang={profile["languages"][0]}')
        
        # Set hardware concurrency
        options.add_argument(f'--js-flags=--cpu-count={profile["hardware_concurrency"]}')
        
        # WebRTC settings
        if not profile['enable_webrtc']:
            options.add_argument('--disable-webrtc')
        
        # Set color profile
        options.add_argument(f'--color-profile={profile["color_depth"]}')
        
        # Timezone emulation for consistent geolocation
        if profile['timezone_offset'] != 0:
            tz_sign = '+' if profile['timezone_offset'] > 0 else '-'
            tz_hour = abs(profile['timezone_offset']) // 60
            tz_minute = abs(profile['timezone_offset']) % 60
            options.add_argument(f'--timezone={tz_sign}{tz_hour:02d}:{tz_minute:02d}')
        
        # Add GPU info for WebGL fingerprinting
        options.add_argument(f'--gpu-vendor={profile["webgl_vendor"]}')
        options.add_argument(f'--gpu-device={profile["webgl_renderer"]}')
        
        # Disable various features that can leak fingerprinting info
        options.add_argument('--disable-features=HardwareMediaKeyHandling,MediaSessionService')
        
        # Add CDP flags to modify client properties
        options.add_experimental_option('prefs', {
            'profile.managed_default_content_settings.javascript': 1,
            'profile.default_content_setting_values.notifications': 2,
            'profile.managed_default_content_settings.images': 1,
            'profile.default_content_setting_values.cookies': 1
        })
        
        return options
    
    def _apply_to_firefox_options(self, options: FirefoxOptions, profile: Dict[str, Any]) -> FirefoxOptions:
        """
        Apply fingerprint randomization to Firefox options.
        
        Args:
            options: Firefox options object
            profile: Fingerprint profile
            
        Returns:
            Modified Firefox options
        """
        # Apply window size based on profile
        width, height = profile['screen_resolution']
        options.add_argument(f'--width={width}')
        options.add_argument(f'--height={height}')
        
        # Set language preferences
        options.set_preference('intl.accept_languages', ','.join(profile['languages']))
        
        # Disable WebRTC if needed
        if not profile['enable_webrtc']:
            options.set_preference('media.peerconnection.enabled', False)
        
        # Timezone preferences
        options.set_preference('privacy.resistFingerprinting.reduceTimerPrecision', False)
        
        # Disable various automation flags
        options.set_preference('dom.webdriver.enabled', False)
        options.set_preference('useAutomationExtension', False)
        
        # Disable animation for more consistent rendering
        options.set_preference('toolkit.cosmeticAnimations.enabled', False)
        
        # Normalize fingerprinting settings
        options.set_preference('privacy.resistFingerprinting', False)  # We're doing our own fingerprinting
        
        # Set plugin behavior
        options.set_preference('plugin.state.flash', 0)  # Disabled
        
        # Set resolution and color depth
        options.set_preference('layout.css.devPixelsPerPx', '1.0')
        
        return options
    
    def inject_fingerprint_js(self, driver: webdriver.Chrome) -> None:
        """
        Inject JavaScript to modify browser fingerprinting properties.
        
        Args:
            driver: WebDriver instance
        """
        # Generate fingerprint profile
        profile = self.get_random_fingerprint_profile()
        
        # Craft JavaScript to modify navigator and screen properties
        js_script = """
        // Store original functions
        const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
        
        // Override WebGL fingerprinting
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            // UNMASKED_VENDOR_WEBGL
            if (parameter === 37445) {
                return "%s";
            }
            // UNMASKED_RENDERER_WEBGL
            if (parameter === 37446) {
                return "%s";
            }
            return originalGetParameter.call(this, parameter);
        };
        
        // Override platform
        Object.defineProperty(navigator, 'platform', {
            get: function() { return "%s"; }
        });
        
        // Override hardware concurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: function() { return %d; }
        });
        
        // Override device memory
        Object.defineProperty(navigator, 'deviceMemory', {
            get: function() { return %d; }
        });
        
        // Override screen properties
        Object.defineProperty(screen, 'width', {
            get: function() { return %d; }
        });
        Object.defineProperty(screen, 'height', {
            get: function() { return %d; }
        });
        Object.defineProperty(screen, 'colorDepth', {
            get: function() { return %d; }
        });
        Object.defineProperty(screen, 'pixelDepth', {
            get: function() { return %d; }
        });
        
        // Override language
        Object.defineProperty(navigator, 'language', {
            get: function() { return "%s"; }
        });
        
        // Override languages
        Object.defineProperty(navigator, 'languages', {
            get: function() { return %s; }
        });
        
        // Override maxTouchPoints
        Object.defineProperty(navigator, 'maxTouchPoints', {
            get: function() { return %d; }
        });
        
        // Make detection of automated browser harder
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false
        });
        
        // Timezone override
        Date.prototype.getTimezoneOffset = function() { return %d; };
        """ % (
            profile['webgl_vendor'],
            profile['webgl_renderer'],
            profile['platform'],
            profile['hardware_concurrency'],
            profile['device_memory'],
            profile['screen_resolution'][0],
            profile['screen_resolution'][1],
            profile['color_depth'],
            profile['color_depth'],
            profile['languages'][0],
            json.dumps(profile['languages']),
            profile['max_touch_points'],
            profile['timezone_offset']
        )
        
        try:
            # Execute the script
            driver.execute_script(js_script)
            self.logger.debug("Injected fingerprint overrides")
        except Exception as e:
            self.logger.warning(f"Failed to inject fingerprint JS: {str(e)}")

# Example usage
if __name__ == "__main__":
    import json
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create fingerprint randomizer
    fingerprint_randomizer = FingerprintRandomizer()
    
    # Generate and print a random profile
    profile = fingerprint_randomizer.get_random_fingerprint_profile()
    print("Random Fingerprint Profile:")
    print(json.dumps(profile, indent=2))
    
    # Show how to use with Chrome
    chrome_options = ChromeOptions()
    chrome_options = fingerprint_randomizer.apply_to_options(chrome_options)
    
    # List Chrome arguments
    print("\nChrome Arguments:")
    for arg in chrome_options.arguments:
        print(f"  {arg}")