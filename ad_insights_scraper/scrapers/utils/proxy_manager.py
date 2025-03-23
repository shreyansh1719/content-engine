"""
Advanced proxy management system to avoid IP blocks
"""
import os
import time
import json
import logging
import random
import threading
import requests
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta

class ProxyManager:
    """
    Advanced proxy manager for web scraping with anti-detection features.
    
    Features:
    - Loads proxies from multiple sources
    - Rotates proxies based on usage patterns
    - Tests proxies for anonymity and functionality
    - Tracks proxy health and success rates
    - Supports multiple proxy protocols (HTTP, SOCKS4, SOCKS5)
    - Auto-bans failing proxies for configurable time periods
    """
    
    def __init__(
        self,
        proxy_list_path: Optional[str] = None,
        proxy_api_key: Optional[str] = None,
        test_url: str = 'https://httpbin.org/ip',
        min_proxies: int = 10,
        max_consecutive_failures: int = 3,
        ban_duration_minutes: int = 30,
        health_check_interval_seconds: int = 300
    ):
        """
        Initialize proxy manager with configuration options.
        
        Args:
            proxy_list_path: Path to JSON file with proxy list
            proxy_api_key: API key for proxy provider service
            test_url: URL to test proxy anonymity and functionality
            min_proxies: Minimum number of working proxies required
            max_consecutive_failures: Max failures before banning a proxy
            ban_duration_minutes: How long to ban a failing proxy
            health_check_interval_seconds: Interval between health checks
        """
        # Setup logging
        self.logger = logging.getLogger('ProxyManager')
        
        # Configuration
        self.test_url = test_url
        self.min_proxies = min_proxies
        self.max_consecutive_failures = max_consecutive_failures
        self.ban_duration_minutes = ban_duration_minutes
        self.health_check_interval_seconds = health_check_interval_seconds
        
        # Proxy sources
        self.proxy_list_path = proxy_list_path or 'proxies.json'
        self.proxy_api_key = proxy_api_key or os.getenv('PROXY_API_KEY')
        
        # Proxy storage and tracking
        self.proxies: List[Dict[str, Any]] = []
        self.banned_proxies: Dict[str, datetime] = {}
        self.current_index = 0
        self.last_rotation_time = datetime.now()
        
        # Thread lock for thread safety
        self.lock = threading.RLock()
        
        # Initialize proxy list
        self._initialize_proxies()
        
        # Start health check thread if interval is set
        if self.health_check_interval_seconds > 0:
            self._start_health_check_thread()
    
    def _initialize_proxies(self) -> None:
        """
        Initialize proxy list from configured sources.
        """
        with self.lock:
            # Try loading from file first
            self._load_proxies_from_file()
            
            # If we don't have enough proxies, try API sources
            if len(self.proxies) < self.min_proxies and self.proxy_api_key:
                self._load_proxies_from_api()
            
            # If we still don't have enough proxies, try free public sources
            if len(self.proxies) < self.min_proxies:
                self._load_free_public_proxies()
            
            # Test and filter proxies
            self._test_and_filter_proxies()
            
            # Check if we have enough proxies
            if len(self.proxies) < self.min_proxies:
                self.logger.warning(
                    f"Only {len(self.proxies)} working proxies available, "
                    f"which is less than the minimum required ({self.min_proxies})"
                )
            else:
                self.logger.info(f"Initialized with {len(self.proxies)} working proxies")
    
    def _load_proxies_from_file(self) -> None:
        """
        Load proxies from the specified JSON file.
        """
        try:
            if os.path.exists(self.proxy_list_path):
                with open(self.proxy_list_path, 'r') as f:
                    loaded_proxies = json.load(f)
                
                # Extract proxies based on file format
                if isinstance(loaded_proxies, list):
                    for proxy_data in loaded_proxies:
                        if isinstance(proxy_data, dict) and 'host' in proxy_data and 'port' in proxy_data:
                            self.proxies.append(self._normalize_proxy(proxy_data))
                        elif isinstance(proxy_data, str):
                            # Handle string format like "host:port"
                            parts = proxy_data.split(':')
                            if len(parts) >= 2:
                                self.proxies.append(self._normalize_proxy({
                                    'host': parts[0],
                                    'port': int(parts[1]),
                                    'protocol': parts[2] if len(parts) > 2 else 'http'
                                }))
                
                self.logger.info(f"Loaded {len(self.proxies)} proxies from file")
        except Exception as e:
            self.logger.error(f"Error loading proxies from file: {str(e)}")
    
    def _load_proxies_from_api(self) -> None:
        """
        Load proxies from paid API provider.
        """
        try:
            # Example implementation for proxy API provider
            # Replace with your actual proxy provider's API
            if not self.proxy_api_key:
                return
            
            # Example API endpoints for different proxy providers
            api_endpoints = [
                f"https://proxy-provider1.com/api?key={self.proxy_api_key}&limit=20",
                f"https://proxy-provider2.com/api?apikey={self.proxy_api_key}&count=20"
            ]
            
            for endpoint in api_endpoints:
                try:
                    response = requests.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Handle different API response formats
                        if isinstance(data, list):
                            for proxy_data in data:
                                if isinstance(proxy_data, dict) and 'host' in proxy_data and 'port' in proxy_data:
                                    self.proxies.append(self._normalize_proxy(proxy_data))
                        elif isinstance(data, dict) and 'proxies' in data:
                            for proxy_data in data['proxies']:
                                if isinstance(proxy_data, dict) and 'host' in proxy_data and 'port' in proxy_data:
                                    self.proxies.append(self._normalize_proxy(proxy_data))
                                elif isinstance(proxy_data, str):
                                    parts = proxy_data.split(':')
                                    if len(parts) >= 2:
                                        self.proxies.append(self._normalize_proxy({
                                            'host': parts[0],
                                            'port': int(parts[1]),
                                            'protocol': parts[2] if len(parts) > 2 else 'http'
                                        }))
                        
                        self.logger.info(f"Loaded {len(self.proxies)} proxies from API")
                        break
                except Exception as api_error:
                    self.logger.warning(f"Error with API endpoint {endpoint}: {str(api_error)}")
        
        except Exception as e:
            self.logger.error(f"Error loading proxies from API: {str(e)}")
    
    def _load_free_public_proxies(self) -> None:
        """
        Load free public proxies from various sources.
        """
        try:
            # Free proxy sources
            free_proxy_sources = [
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
                "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
                "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
            ]
            
            for source in free_proxy_sources:
                try:
                    response = requests.get(source, timeout=10)
                    if response.status_code == 200:
                        proxy_lines = response.text.strip().split('\n')
                        
                        for line in proxy_lines:
                            parts = line.strip().split(':')
                            if len(parts) >= 2:
                                # Determine protocol based on source URL
                                protocol = 'socks5' if 'socks5' in source else 'http'
                                
                                # Add to proxy list
                                self.proxies.append(self._normalize_proxy({
                                    'host': parts[0],
                                    'port': int(parts[1]),
                                    'protocol': protocol,
                                    'username': parts[2] if len(parts) > 3 else None,
                                    'password': parts[3] if len(parts) > 3 else None,
                                    'source': 'free',
                                    'last_used': None,
                                    'success_count': 0,
                                    'failure_count': 0,
                                    'consecutive_failures': 0,
                                    'total_requests': 0,
                                    'success_rate': 0
                                }))
                        
                        self.logger.info(f"Loaded {len(proxy_lines)} proxies from {source}")
                        
                        # If we have enough proxies, stop loading more
                        if len(self.proxies) >= self.min_proxies * 3:  # Get extras for testing
                            break
                
                except Exception as source_error:
                    self.logger.warning(f"Error loading from {source}: {str(source_error)}")
        
        except Exception as e:
            self.logger.error(f"Error loading free public proxies: {str(e)}")
    
    def _normalize_proxy(self, proxy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize proxy data to a standard format.
        
        Args:
            proxy_data: Raw proxy data
            
        Returns:
            Normalized proxy dictionary
        """
        # Ensure all required fields are present
        normalized = {
            'host': proxy_data.get('host', proxy_data.get('ip', '')),
            'port': int(proxy_data.get('port', 0)),
            'protocol': proxy_data.get('protocol', proxy_data.get('type', 'http')).lower(),
            'username': proxy_data.get('username', None),
            'password': proxy_data.get('password', None),
            'source': proxy_data.get('source', 'file'),
            'country': proxy_data.get('country', 'unknown'),
            'last_used': proxy_data.get('last_used', None),
            'success_count': proxy_data.get('success_count', 0),
            'failure_count': proxy_data.get('failure_count', 0),
            'consecutive_failures': proxy_data.get('consecutive_failures', 0),
            'total_requests': proxy_data.get('total_requests', 0),
            'success_rate': proxy_data.get('success_rate', 0)
        }
        
        # Calculate success rate if needed
        if normalized['total_requests'] > 0:
            normalized['success_rate'] = (normalized['success_count'] / normalized['total_requests']) * 100
        
        return normalized
    
    def _get_proxy_key(self, proxy: Dict[str, Any]) -> str:
        """
        Get a unique key for a proxy.
        
        Args:
            proxy: Proxy dictionary
            
        Returns:
            Unique proxy identifier string
        """
        return f"{proxy['host']}:{proxy['port']}"
    
    def _test_proxy(self, proxy: Dict[str, Any]) -> bool:
        """
        Test if a proxy is working and anonymous.
        
        Args:
            proxy: Proxy dictionary
            
        Returns:
            True if proxy is working, False otherwise
        """
        proxy_url = self._format_proxy_url(proxy)
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        try:
            # Set a short timeout for testing
            response = requests.get(
                self.test_url,
                proxies=proxies,
                timeout=10
            )
            
            # Check if request was successful
            if response.status_code == 200:
                # Check if response contains proxy IP (not our real IP)
                response_data = response.json()
                if 'origin' in response_data:
                    # Verify this is the proxy's IP, not our real IP
                    if proxy['host'] in response_data['origin']:
                        return True
                else:
                    # If no origin in response, assume it's working
                    return True
        
        except Exception:
            # Any error means proxy is not working
            pass
        
        return False
    
    def _format_proxy_url(self, proxy: Dict[str, Any]) -> str:
        """
        Format proxy information as a URL.
        
        Args:
            proxy: Proxy dictionary
            
        Returns:
            Formatted proxy URL string
        """
        protocol = proxy['protocol'].lower()
        
        # Format with authentication if provided
        if proxy['username'] and proxy['password']:
            return f"{protocol}://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
        
        # Format without authentication
        return f"{protocol}://{proxy['host']}:{proxy['port']}"
    
    def _test_and_filter_proxies(self) -> None:
        """
        Test all proxies and keep only the working ones.
        """
        working_proxies = []
        
        # If we have many proxies, select a random subset to test
        test_proxies = self.proxies
        if len(test_proxies) > 50:  # Limit testing to 50 proxies
            test_proxies = random.sample(test_proxies, 50)
        
        for proxy in test_proxies:
            # Skip testing if proxy is banned
            proxy_key = self._get_proxy_key(proxy)
            if proxy_key in self.banned_proxies:
                ban_time = self.banned_proxies[proxy_key]
                if datetime.now() < ban_time:
                    self.logger.debug(f"Skipping banned proxy {proxy_key}")
                    continue
                else:
                    # Ban period has expired, remove from banned list
                    del self.banned_proxies[proxy_key]
            
            # Test proxy
            if self._test_proxy(proxy):
                working_proxies.append(proxy)
                
                # Reset failure count for working proxies
                proxy['consecutive_failures'] = 0
                proxy['success_count'] += 1
                proxy['total_requests'] += 1
                
                # Update success rate
                if proxy['total_requests'] > 0:
                    proxy['success_rate'] = (proxy['success_count'] / proxy['total_requests']) * 100
            else:
                # Increment failure count
                proxy['failure_count'] += 1
                proxy['consecutive_failures'] += 1
                proxy['total_requests'] += 1
                
                # Update success rate
                if proxy['total_requests'] > 0:
                    proxy['success_rate'] = (proxy['success_count'] / proxy['total_requests']) * 100
                
                # Ban proxy if too many consecutive failures
                if proxy['consecutive_failures'] >= self.max_consecutive_failures:
                    self.logger.debug(f"Banning proxy {proxy_key} for {self.ban_duration_minutes} minutes due to failures")
                    self.banned_proxies[proxy_key] = datetime.now() + timedelta(minutes=self.ban_duration_minutes)
                else:
                    # Still include proxies that haven't reached failure threshold
                    working_proxies.append(proxy)
        
        with self.lock:
            # Update proxy list with working proxies
            self.proxies = working_proxies
    
    def _get_best_proxy(self) -> Optional[Dict[str, Any]]:
        """
        Get the best available proxy based on success rate.
        
        Returns:
            Best proxy or None if no proxies available
        """
        with self.lock:
            if not self.proxies:
                return None
            
            # Filter out banned proxies
            available_proxies = []
            for proxy in self.proxies:
                proxy_key = self._get_proxy_key(proxy)
                if proxy_key not in self.banned_proxies:
                    available_proxies.append(proxy)
            
            if not available_proxies:
                return None
            
            # Sort by success rate (highest first)
            available_proxies.sort(key=lambda p: p['success_rate'], reverse=True)
            
            # Choose randomly from top performers to distribute load
            top_performers = available_proxies[:max(3, len(available_proxies) // 3)]
            return random.choice(top_performers)
    
    def _get_next_proxy(self) -> Optional[Dict[str, Any]]:
        """
        Get the next proxy in rotation.
        
        Returns:
            Next proxy dictionary or None if no proxies available
        """
        with self.lock:
            if not self.proxies:
                return None
            
            # Get current time
            now = datetime.now()
            
            # Check if we need to rotate proxies based on time
            minutes_since_rotation = (now - self.last_rotation_time).total_seconds() / 60
            if minutes_since_rotation >= 15:  # Rotate proxy list every 15 minutes
                random.shuffle(self.proxies)
                self.current_index = 0
                self.last_rotation_time = now
            
            # Find the next non-banned proxy
            attempts = 0
            max_attempts = len(self.proxies)
            
            while attempts < max_attempts:
                # Get proxy at current index
                index = self.current_index % len(self.proxies)
                proxy = self.proxies[index]
                
                # Move to next index for next call
                self.current_index = (self.current_index + 1) % len(self.proxies)
                
                # Check if proxy is banned
                proxy_key = self._get_proxy_key(proxy)
                if proxy_key in self.banned_proxies:
                    ban_time = self.banned_proxies[proxy_key]
                    if now < ban_time:
                        # Proxy is still banned, try next one
                        attempts += 1
                        continue
                    else:
                        # Ban period has expired, remove from banned list
                        del self.banned_proxies[proxy_key]
                
                # Return valid proxy
                return proxy
                
                attempts += 1
            
            # No valid proxies found
            return None
    
    def _start_health_check_thread(self) -> None:
        """
        Start a background thread for periodic proxy health checks.
        """
        def health_check_worker():
            while True:
                try:
                    # Sleep for the specified interval
                    time.sleep(self.health_check_interval_seconds)
                    
                    # Test and filter proxies
                    self._test_and_filter_proxies()
                    
                    # Save current proxy list to file
                    self._save_proxies_to_file()
                    
                except Exception as e:
                    self.logger.error(f"Health check error: {str(e)}")
        
        # Start the thread
        health_thread = threading.Thread(target=health_check_worker, daemon=True)
        health_thread.start()
    
    def _save_proxies_to_file(self) -> None:
        """
        Save the current list of proxies to file.
        """
        try:
            with self.lock:
                with open(self.proxy_list_path, 'w') as f:
                    json.dump(self.proxies, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Error saving proxies to file: {str(e)}")
    
    def get_next_proxy(self) -> Optional[Dict[str, Any]]:
        """
        Get the next proxy for use in rotation.
        
        Returns:
            Proxy dictionary with host, port, etc.
        """
        # Decide whether to use best proxy or next in rotation (80% chance for best)
        use_best = random.random() < 0.8
        
        proxy = self._get_best_proxy() if use_best else self._get_next_proxy()
        
        if proxy:
            # Update usage tracking
            proxy['last_used'] = datetime.now().isoformat()
        
        return proxy
    
    def report_success(self, proxy: Dict[str, Any]) -> None:
        """
        Report successful use of a proxy.
        
        Args:
            proxy: The proxy that was used successfully
        """
        with self.lock:
            # Find the proxy in our list
            proxy_key = self._get_proxy_key(proxy)
            
            for idx, p in enumerate(self.proxies):
                if self._get_proxy_key(p) == proxy_key:
                    # Update success stats
                    p['success_count'] += 1
                    p['total_requests'] += 1
                    p['consecutive_failures'] = 0
                    
                    # Update success rate
                    if p['total_requests'] > 0:
                        p['success_rate'] = (p['success_count'] / p['total_requests']) * 100
                    
                    # Remove from banned list if present
                    if proxy_key in self.banned_proxies:
                        del self.banned_proxies[proxy_key]
                    
                    break
    
    def report_failure(self, proxy: Dict[str, Any]) -> None:
        """
        Report failed use of a proxy.
        
        Args:
            proxy: The proxy that failed
        """
        with self.lock:
            # Find the proxy in our list
            proxy_key = self._get_proxy_key(proxy)
            
            for idx, p in enumerate(self.proxies):
                if self._get_proxy_key(p) == proxy_key:
                    # Update failure stats
                    p['failure_count'] += 1
                    p['consecutive_failures'] += 1
                    p['total_requests'] += 1
                    
                    # Update success rate
                    if p['total_requests'] > 0:
                        p['success_rate'] = (p['success_count'] / p['total_requests']) * 100
                    
                    # Ban proxy if too many consecutive failures
                    if p['consecutive_failures'] >= self.max_consecutive_failures:
                        self.logger.debug(f"Banning proxy {proxy_key} for {self.ban_duration_minutes} minutes due to failures")
                        self.banned_proxies[proxy_key] = datetime.now() + timedelta(minutes=self.ban_duration_minutes)
                    
                    break
    
    def format_for_requests(self, proxy: Dict[str, Any]) -> Dict[str, str]:
        """
        Format proxy for use with requests library.
        
        Args:
            proxy: Proxy dictionary
            
        Returns:
            Dictionary with http/https proxy URLs
        """
        proxy_url = self._format_proxy_url(proxy)
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def format_for_selenium(self, proxy: Dict[str, Any]) -> Dict[str, str]:
        """
        Format proxy for use with Selenium WebDriver.
        
        Args:
            proxy: Proxy dictionary
            
        Returns:
            Dictionary with proxy settings for Selenium
        """
        return {
            'proxyType': proxy['protocol'],
            'httpProxy': f"{proxy['host']}:{proxy['port']}",
            'sslProxy': f"{proxy['host']}:{proxy['port']}",
            'socksProxy': f"{proxy['host']}:{proxy['port']}" if proxy['protocol'].startswith('socks') else '',
            'socksVersion': 5 if proxy['protocol'] == 'socks5' else 4 if proxy['protocol'] == 'socks4' else 0,
            'socksUsername': proxy['username'] or '',
            'socksPassword': proxy['password'] or '',
            'noProxy': ''
        }
    
    def get_proxy_stats(self) -> Dict[str, Any]:
        """
        Get statistics about proxy usage and health.
        
        Returns:
            Dictionary with proxy statistics
        """
        with self.lock:
            # Count banned proxies
            banned_count = len(self.banned_proxies)
            
            # Count proxies by protocol
            protocol_counts = {}
            for proxy in self.proxies:
                protocol = proxy['protocol']
                protocol_counts[protocol] = protocol_counts.get(protocol, 0) + 1
            
            # Calculate average success rate
            total_success_rate = sum(proxy['success_rate'] for proxy in self.proxies)
            avg_success_rate = total_success_rate / len(self.proxies) if self.proxies else 0
            
            return {
                'total_proxies': len(self.proxies),
                'banned_proxies': banned_count,
                'protocol_distribution': protocol_counts,
                'average_success_rate': avg_success_rate
            }

# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create proxy manager
    proxy_manager = ProxyManager(min_proxies=5)
    
    # Get proxy stats
    stats = proxy_manager.get_proxy_stats()
    print(f"Proxy Stats: {stats}")
    
    # Get a proxy for use
    proxy = proxy_manager.get_next_proxy()
    if proxy:
        print(f"Using proxy: {proxy['host']}:{proxy['port']} ({proxy['protocol']})")
        
        # Example of reporting success/failure
        proxy_manager.report_success(proxy)
        
        # Format for requests
        requests_proxy = proxy_manager.format_for_requests(proxy)
        print(f"Requests format: {requests_proxy}")
        
        # Format for Selenium
        selenium_proxy = proxy_manager.format_for_selenium(proxy)
        print(f"Selenium format: {selenium_proxy}")