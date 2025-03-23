"""
User-Agent generator and rotator for browser fingerprinting protection
"""
import os
import json
import random
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

class UserAgentRotator:
    """
    Advanced User-Agent rotation system for web scraping with anti-detection features.
    
    Features:
    - Maintains extensive, up-to-date collection of realistic user agents
    - Groups user agents by browser, OS, and device type
    - Supports weighted selection based on browser market share
    - Offers consistent user-agent selection for session persistence
    - Provides special browser-specific user agents for targeted scraping
    """
    
    def __init__(self, user_agents_path: Optional[str] = None):
        """
        Initialize user agent rotator with custom data file.
        
        Args:
            user_agents_path: Path to JSON file with user agents data
        """
        # Setup logging
        self.logger = logging.getLogger('UserAgentRotator')
        
        # User agents storage
        self.user_agents: Dict[str, List[str]] = {
            'chrome': [],
            'firefox': [],
            'safari': [],
            'edge': [],
            'opera': [],
            'mobile': [],
            'tablet': [],
            'desktop': []
        }
        
        # Load user agents from file or use default collection
        self.user_agents_path = user_agents_path
        self._load_user_agents()
        
        # Maintain last used for consistent sessions
        self.last_used: Dict[str, str] = {}
        
        # Track market share for weighted selection
        self.browser_weights = {
            'chrome': 65,    # ~65% market share
            'safari': 18,    # ~18% market share
            'firefox': 4,    # ~4% market share
            'edge': 4,       # ~4% market share
            'opera': 2,      # ~2% market share
            'other': 7       # ~7% market share
        }
    
    def _load_user_agents(self) -> None:
        """
        Load user agents from file or initialize with default collection.
        """
        # First try to load from user-provided file
        if self.user_agents_path and os.path.exists(self.user_agents_path):
            try:
                with open(self.user_agents_path, 'r', encoding='utf-8') as f:
                    user_agent_data = json.load(f)
                
                # Extract user agents by category
                for category, agents in user_agent_data.items():
                    if category in self.user_agents and isinstance(agents, list):
                        self.user_agents[category] = agents
                
                self.logger.info(f"Loaded user agents from {self.user_agents_path}")
                return
            except Exception as e:
                self.logger.warning(f"Failed to load user agents from file: {e}")
        
        # If unable to load from file, use default collection
        self._initialize_default_user_agents()
    
    def _initialize_default_user_agents(self) -> None:
        """
        Initialize with a comprehensive default collection of user agents.
        """
        # Chrome user agents (desktop)
        self.user_agents['chrome'] = [
            # Windows Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            
            # MacOS Chrome
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            
            # Linux Chrome
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        ]
        
        # Firefox user agents
        self.user_agents['firefox'] = [
            # Windows Firefox
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:111.0) Gecko/20100101 Firefox/111.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
            
            # MacOS Firefox
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.3; rv:112.0) Gecko/20100101 Firefox/112.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.2; rv:111.0) Gecko/20100101 Firefox/111.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.1; rv:110.0) Gecko/20100101 Firefox/110.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.0; rv:109.0) Gecko/20100101 Firefox/109.0",
            
            # Linux Firefox
            "Mozilla/5.0 (X11; Linux x86_64; rv:112.0) Gecko/20100101 Firefox/112.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:111.0) Gecko/20100101 Firefox/111.0",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:110.0) Gecko/20100101 Firefox/110.0",
            "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
        ]
        
        # Safari user agents
        self.user_agents['safari'] = [
            # MacOS Safari
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
            
            # iOS Safari
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1",
        ]
        
        # Edge user agents
        self.user_agents['edge'] = [
            # Windows Edge
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.39",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78",
            
            # MacOS Edge
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.39",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62",
        ]
        
        # Opera user agents
        self.user_agents['opera'] = [
            # Windows Opera
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 OPR/98.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 OPR/97.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 OPR/96.0.0.0",
            
            # MacOS Opera
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 OPR/98.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 OPR/97.0.0.0",
        ]
        
        # Mobile user agents
        self.user_agents['mobile'] = [
            # Android Chrome
            "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; Pixel 6a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36",
            
            # iOS Safari
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1",
            
            # Android Firefox
            "Mozilla/5.0 (Android 13; Mobile; rv:112.0) Gecko/112.0 Firefox/112.0",
            "Mozilla/5.0 (Android 13; Mobile; rv:111.0) Gecko/111.0 Firefox/111.0",
        ]
        
        # Tablet user agents
        self.user_agents['tablet'] = [
            # iPadOS Safari
            "Mozilla/5.0 (iPad; CPU OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1",
            
            # Android Tablet Chrome
            "Mozilla/5.0 (Linux; Android 13; SM-X906C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; SM-T970) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            
            # Android Tablet Firefox
            "Mozilla/5.0 (Android 13; Tablet; rv:112.0) Gecko/112.0 Firefox/112.0",
        ]
        
        # Desktop user agents (combination of desktop browsers)
        self.user_agents['desktop'] = (
            self.user_agents['chrome'][:8] +
            self.user_agents['firefox'][:6] +
            self.user_agents['safari'][:4] +
            self.user_agents['edge'][:4] +
            self.user_agents['opera'][:3]
        )
        
        self.logger.info("Initialized with default user agents")
    
    def get_random_user_agent(self, browser_type: Optional[str] = None, device_type: Optional[str] = None) -> str:
        """
        Get a random user agent, optionally filtered by browser and device type.
        
        Args:
            browser_type: Browser type ('chrome', 'firefox', 'safari', etc.)
            device_type: Device type ('desktop', 'mobile', 'tablet')
            
        Returns:
            Random user agent string
        """
        # Determine which collection to use
        if browser_type and browser_type.lower() in self.user_agents:
            collection = self.user_agents[browser_type.lower()]
        elif device_type and device_type.lower() in self.user_agents:
            collection = self.user_agents[device_type.lower()]
        else:
            # Use weighted selection based on market share
            browser = self._weighted_browser_selection()
            collection = self.user_agents.get(browser, self.user_agents['chrome'])
        
        # Default to chrome if collection is empty
        if not collection:
            collection = self.user_agents['chrome']
        
        # Return random user agent from the collection
        return random.choice(collection)
    
    def _weighted_browser_selection(self) -> str:
        """
        Select a browser based on market share weights.
        
        Returns:
            Browser name string
        """
        # Create list of browsers with their weights
        browsers = []
        weights = []
        
        for browser, weight in self.browser_weights.items():
            # Only include browsers with user agents
            if browser in self.user_agents and self.user_agents[browser]:
                browsers.append(browser)
                weights.append(weight)
        
        # Default to chrome if no valid browsers
        if not browsers:
            return 'chrome'
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Weighted random selection
        return random.choices(browsers, weights=normalized_weights, k=1)[0]
    
    def get_consistent_user_agent(self, session_id: str, browser_type: Optional[str] = None) -> str:
        """
        Get a consistent user agent for a session.
        
        Args:
            session_id: Unique session identifier
            browser_type: Browser type (optional)
            
        Returns:
            User agent string
        """
        # Check if we already have a user agent for this session
        if session_id in self.last_used:
            return self.last_used[session_id]
        
        # Generate a new user agent and store it
        user_agent = self.get_random_user_agent(browser_type)
        self.last_used[session_id] = user_agent
        return user_agent
    
    def get_modern_user_agent(self, browser_type: Optional[str] = None) -> str:
        """
        Get a modern user agent from the newest browser versions.
        
        Args:
            browser_type: Browser type (optional)
            
        Returns:
            Modern user agent string
        """
        # Default to chrome if no browser specified
        if not browser_type:
            browser_type = self._weighted_browser_selection()
        
        # Get collection for the browser
        collection = self.user_agents.get(browser_type.lower(), self.user_agents['chrome'])
        
        # Sort by browser version (higher is more modern)
        # This is a simple heuristic that works for most user agent strings
        sorted_agents = sorted(collection, key=self._extract_version_number, reverse=True)
        
        # Return one of the top 3 most modern user agents
        return random.choice(sorted_agents[:min(3, len(sorted_agents))])
    
    def _extract_version_number(self, user_agent: str) -> float:
        """
        Extract numeric version from a user agent string.
        
        Args:
            user_agent: User agent string
            
        Returns:
            Version number as float
        """
        try:
            # Extract Chrome version
            if "Chrome/" in user_agent:
                chrome_version = user_agent.split("Chrome/")[1].split(" ")[0]
                return float(chrome_version.split('.')[0])
            
            # Extract Firefox version
            if "Firefox/" in user_agent:
                firefox_version = user_agent.split("Firefox/")[1].split(" ")[0]
                return float(firefox_version.split('.')[0])
            
            # Extract Safari version
            if "Version/" in user_agent and "Safari/" in user_agent:
                safari_version = user_agent.split("Version/")[1].split(" ")[0]
                return float(safari_version.split('.')[0])
            
            # Extract Edge version
            if "Edg/" in user_agent:
                edge_version = user_agent.split("Edg/")[1].split(" ")[0]
                return float(edge_version.split('.')[0])
            
            # Extract Opera version
            if "OPR/" in user_agent:
                opera_version = user_agent.split("OPR/")[1].split(" ")[0]
                return float(opera_version.split('.')[0])
        
        except (IndexError, ValueError):
            pass
        
        # Default to 0 if version can't be extracted
        return 0.0
    
    def generate_chrome_windows_user_agent(self) -> str:
        """
        Generate a Chrome on Windows user agent with current versions.
        
        Returns:
            Chrome Windows user agent string
        """
        # Current Chrome major versions (range)
        chrome_versions = list(range(110, 113))
        chrome_version = random.choice(chrome_versions)
        
        # Minor version components
        minor_version = random.randint(0, 5000)
        build_version = random.randint(0, 200)
        
        return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.{minor_version}.{build_version} Safari/537.36"
    
    def generate_chrome_mac_user_agent(self) -> str:
        """
        Generate a Chrome on Mac user agent with current versions.
        
        Returns:
            Chrome Mac user agent string
        """
        # Current Chrome major versions (range)
        chrome_versions = list(range(110, 113))
        chrome_version = random.choice(chrome_versions)
        
        # Mac OS versions
        mac_versions = ["10_15_7", "11_6_8", "12_6_3", "13_0", "13_1", "13_2_1", "13_3_1"]
        mac_version = random.choice(mac_versions)
        
        # Minor version components
        minor_version = random.randint(0, 5000)
        build_version = random.randint(0, 200)
        
        return f"Mozilla/5.0 (Macintosh; Intel Mac OS X {mac_version}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.{minor_version}.{build_version} Safari/537.36"
    
    def get_latest_user_agents(self) -> Dict[str, str]:
        """
        Get the latest user agent for each major browser.
        
        Returns:
            Dictionary with latest user agent for each browser
        """
        latest_agents = {}
        
        for browser in ['chrome', 'firefox', 'safari', 'edge', 'opera']:
            # Skip if no user agents for this browser
            if not self.user_agents.get(browser, []):
                continue
            
            # Sort by version number
            sorted_agents = sorted(self.user_agents[browser], key=self._extract_version_number, reverse=True)
            
            # Get the latest one
            if sorted_agents:
                latest_agents[browser] = sorted_agents[0]
        
        return latest_agents
    
    def get_matching_user_agent(self, pattern: str) -> str:
        """
        Get a user agent that matches the given pattern.
        
        Args:
            pattern: String to match in user agent
            
        Returns:
            Matching user agent or random one if none match
        """
        # Look in all collections
        matching_agents = []
        
        for collection in self.user_agents.values():
            for agent in collection:
                if pattern.lower() in agent.lower():
                    matching_agents.append(agent)
        
        # Return a matching agent or random one
        if matching_agents:
            return random.choice(matching_agents)
        else:
            return self.get_random_user_agent()
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save user agents collection to a file.
        
        Args:
            filepath: Path to save the user agents JSON
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.user_agents, f, indent=2)
            
            self.logger.info(f"Saved user agents to {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving user agents to file: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create user agent rotator
    ua_rotator = UserAgentRotator()
    
    # Get a random user agent
    print(f"Random user agent: {ua_rotator.get_random_user_agent()}")
    
    # Get browser-specific user agents
    print(f"Chrome user agent: {ua_rotator.get_random_user_agent('chrome')}")
    print(f"Firefox user agent: {ua_rotator.get_random_user_agent('firefox')}")
    
    # Get device-specific user agents
    print(f"Mobile user agent: {ua_rotator.get_random_user_agent(device_type='mobile')}")
    print(f"Tablet user agent: {ua_rotator.get_random_user_agent(device_type='tablet')}")
    
    # Get consistent user agent for a session
    session_id = "test_session_123"
    print(f"Session user agent: {ua_rotator.get_consistent_user_agent(session_id)}")
    print(f"Same session again: {ua_rotator.get_consistent_user_agent(session_id)}")
    
    # Get modern Chrome user agent
    print(f"Modern Chrome user agent: {ua_rotator.get_modern_user_agent('chrome')}")
    
    # Generate specific browser user agents
    print(f"Generated Chrome Windows: {ua_rotator.generate_chrome_windows_user_agent()}")
    print(f"Generated Chrome Mac: {ua_rotator.generate_chrome_mac_user_agent()}")