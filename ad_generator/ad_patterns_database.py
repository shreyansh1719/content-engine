"""
Ad Patterns Database - Stores and retrieves advertising patterns with engagement metrics

This module provides access to a comprehensive database of advertising patterns
across multiple industries, including engagement metrics, visual approaches,
and copywriting techniques that have proven effective.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

class AdPatternsDatabase:
    """Database of advertising patterns with engagement metrics for AI ad generation."""
    
    def __init__(self, data_path: str = None):
        """
        Initialize the ad patterns database.
        
        Args:
            data_path: Path to the directory containing pattern database files
        """
        # Set up logger
        self.logger = logging.getLogger(__name__)
        
        # Set data path
        self.data_path = data_path or os.path.join('data', 'processed')
        os.makedirs(self.data_path, exist_ok=True)
        
        # Initialize database containers
        self.industries = {}
        self.universal_patterns = {}
        
        # Load database
        self.load_database()
    
    def load_database(self):
        """Load the ad patterns database from disk."""
        try:
            # Check for main database file
            db_file = os.path.join(self.data_path, 'ad_patterns_database.json')
            if os.path.exists(db_file):
                with open(db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.industries = data.get('industries', {})
                    self.universal_patterns = data.get('universal_patterns', {})
                self.logger.info(f"Loaded ad patterns database from {db_file}")
            else:
                # Load individual industry files if main file doesn't exist
                self._load_individual_files()
                
                # Load default database if no files found
                if not self.industries and not self.universal_patterns:
                    self._load_default_database()
        
        except Exception as e:
            self.logger.error(f"Error loading ad patterns database: {str(e)}")
            # Load default database as fallback
            self._load_default_database()
    
    def _load_individual_files(self):
        """Load patterns from individual industry files."""
        # Check for industry-specific files
        for filename in os.listdir(self.data_path):
            if filename.startswith('industry_') and filename.endswith('.json'):
                industry_name = filename[9:-5]  # Extract industry name from filename
                try:
                    with open(os.path.join(self.data_path, filename), 'r', encoding='utf-8') as f:
                        self.industries[industry_name] = json.load(f)
                    self.logger.info(f"Loaded patterns for {industry_name} industry")
                except Exception as e:
                    self.logger.error(f"Error loading {filename}: {str(e)}")
        
        # Check for universal patterns file
        universal_file = os.path.join(self.data_path, 'universal_patterns.json')
        if os.path.exists(universal_file):
            try:
                with open(universal_file, 'r', encoding='utf-8') as f:
                    self.universal_patterns = json.load(f)
                self.logger.info("Loaded universal ad patterns")
            except Exception as e:
                self.logger.error(f"Error loading universal patterns: {str(e)}")
    
    def _load_default_database(self):
        """Load default embedded database if no files found."""
        self.logger.info("Loading default embedded ad patterns database")
        from .default_patterns import DEFAULT_AD_PATTERNS
        
        self.industries = DEFAULT_AD_PATTERNS.get('industries', {})
        self.universal_patterns = DEFAULT_AD_PATTERNS.get('universal_patterns', {})
    
    def save_database(self):
        """Save the current database to disk."""
        try:
            # Save complete database
            db_file = os.path.join(self.data_path, 'ad_patterns_database.json')
            with open(db_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'industries': self.industries,
                    'universal_patterns': self.universal_patterns,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved ad patterns database to {db_file}")
            
            # Also save individual industry files for easier updates
            for industry, data in self.industries.items():
                industry_file = os.path.join(self.data_path, f'industry_{industry}.json')
                with open(industry_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Save universal patterns
            universal_file = os.path.join(self.data_path, 'universal_patterns.json')
            with open(universal_file, 'w', encoding='utf-8') as f:
                json.dump(self.universal_patterns, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Error saving ad patterns database: {str(e)}")
    
    def get_industry_patterns(self, industry: str) -> Dict:
        """
        Get patterns for a specific industry.
        
        Args:
            industry: Industry name or category
            
        Returns:
            Dictionary of patterns for the industry
        """
        # Handle case insensitivity and common variations
        industry_lower = industry.lower().strip()
        
        # Try exact match first
        for industry_key, data in self.industries.items():
            if industry_key.lower() == industry_lower:
                return data
        
        # Try partial match
        for industry_key, data in self.industries.items():
            if industry_lower in industry_key.lower() or industry_key.lower() in industry_lower:
                return data
        
        # Check industry aliases and categories
        industry_map = {
            'tech': 'technology',
            'software': 'technology',
            'electronics': 'technology',
            'gadgets': 'technology',
            'clothing': 'fashion',
            'apparel': 'fashion',
            'wear': 'fashion',
            'restaurant': 'food',
            'dining': 'food',
            'grocery': 'food',
            'music': 'entertainment',
            'streaming': 'entertainment',
            'movie': 'entertainment',
            'automotive': 'auto',
            'vehicle': 'auto',
            'car': 'auto'
        }
        
        if industry_lower in industry_map:
            mapped_industry = industry_map[industry_lower]
            for industry_key, data in self.industries.items():
                if mapped_industry in industry_key.lower():
                    return data
        
        # If no match found, return technology as default
        self.logger.warning(f"No specific patterns found for '{industry}', using technology as default")
        return self.industries.get('technology', {})
    
    def get_universal_patterns(self) -> Dict:
        """Get universal ad patterns that work across industries."""
        return self.universal_patterns
    
    def get_headline_patterns(self, industry: str) -> List[Dict]:
        """
        Get headline patterns for a specific industry.
        
        Args:
            industry: Industry name
            
        Returns:
            List of headline patterns with engagement metrics
        """
        industry_data = self.get_industry_patterns(industry)
        return industry_data.get('headline_patterns', [])
    
    def get_visual_approaches(self, industry: str) -> List[Dict]:
        """
        Get visual approaches for a specific industry.
        
        Args:
            industry: Industry name
            
        Returns:
            List of visual approaches with engagement metrics
        """
        industry_data = self.get_industry_patterns(industry)
        return industry_data.get('visual_approaches', [])
    
    def get_copy_structures(self, industry: str) -> List[Dict]:
        """
        Get copy structures for a specific industry.
        
        Args:
            industry: Industry name
            
        Returns:
            List of copy structures with engagement metrics
        """
        industry_data = self.get_industry_patterns(industry)
        return industry_data.get('copy_structures', [])
    
    def get_color_schemes(self, industry: str) -> List[Dict]:
        """
        Get color schemes for a specific industry.
        
        Args:
            industry: Industry name
            
        Returns:
            List of color schemes with engagement metrics
        """
        industry_data = self.get_industry_patterns(industry)
        return industry_data.get('color_schemes', [])
    
    def get_emotional_triggers(self, industry: str) -> List[Dict]:
        """
        Get emotional triggers for a specific industry.
        
        Args:
            industry: Industry name
            
        Returns:
            List of emotional triggers with engagement metrics
        """
        industry_data = self.get_industry_patterns(industry)
        return industry_data.get('emotional_triggers', [])
    
    def get_calls_to_action(self, industry: str = None) -> List[Dict]:
        """
        Get effective calls to action.
        
        Args:
            industry: Optional industry name for industry-specific CTAs
            
        Returns:
            List of CTA patterns with engagement metrics
        """
        if industry:
            industry_data = self.get_industry_patterns(industry)
            industry_ctas = industry_data.get('calls_to_action', [])
            if industry_ctas:
                return industry_ctas
                
        # Fall back to universal CTAs if industry-specific not found
        return self.universal_patterns.get('calls_to_action', [])
    
    def get_best_performing_pattern(self, pattern_type: str, industry: str,
                                   platform: str = None, demographic: str = None) -> Dict:
        """
        Get the best performing pattern of a specific type.
        
        Args:
            pattern_type: Type of pattern (headline, visual, copy, etc.)
            industry: Industry name
            platform: Optional platform (facebook, instagram, etc.)
            demographic: Optional demographic segment (e.g., "18-24")
            
        Returns:
            Highest performing pattern of the specified type
        """
        industry_data = self.get_industry_patterns(industry)
        patterns = industry_data.get(f"{pattern_type}_patterns", [])
        
        if not patterns:
            self.logger.warning(f"No {pattern_type} patterns found for {industry}")
            return {}
        
        # Filter by platform if specified
        if platform:
            platform_lower = platform.lower()
            platform_filtered = []
            
            for pattern in patterns:
                # Check if pattern has platform data
                engagement_metrics = pattern.get('engagement_metrics', {})
                platform_performance = engagement_metrics.get('platform_performance', {})
                
                if platform_lower in platform_performance:
                    # Create a copy with platform-specific score as the main score
                    pattern_copy = pattern.copy()
                    pattern_copy['performance_score'] = platform_performance[platform_lower]
                    platform_filtered.append(pattern_copy)
            
            if platform_filtered:
                patterns = platform_filtered
        
        # Filter by demographic if specified
        if demographic and not platform_filtered:  # Only if not already filtered by platform
            demo_filtered = []
            
            for pattern in patterns:
                demographic_performance = pattern.get('demographic_performance', {})
                
                if demographic in demographic_performance:
                    pattern_copy = pattern.copy()
                    pattern_copy['performance_score'] = demographic_performance[demographic]
                    demo_filtered.append(pattern_copy)
            
            if demo_filtered:
                patterns = demo_filtered
        
        # Sort by performance and return best pattern
        if patterns:
            # First try engagement_rate if available
            sorted_patterns = sorted(
                patterns,
                key=lambda x: (
                    x.get('engagement_metrics', {}).get('average_engagement_rate', 0) 
                    if isinstance(x.get('engagement_metrics'), dict) else 0
                ),
                reverse=True
            )
            
            # If no engagement rate, try performance_score
            if sorted_patterns[0].get('engagement_metrics', {}).get('average_engagement_rate', 0) == 0:
                sorted_patterns = sorted(
                    patterns,
                    key=lambda x: x.get('performance_score', 0),
                    reverse=True
                )
            
            return sorted_patterns[0]
        
        return {}
    
    def update_patterns_with_feedback(self, pattern_type: str, industry: str, 
                                     pattern_id: str, performance_data: Dict):
        """
        Update pattern performance based on feedback.
        
        Args:
            pattern_type: Type of pattern (headline, visual, copy, etc.)
            industry: Industry name
            pattern_id: Identifier for the specific pattern
            performance_data: New performance metrics
        """
        try:
            industry_data = self.get_industry_patterns(industry)
            patterns = industry_data.get(f"{pattern_type}_patterns", [])
            
            # Find the pattern to update
            for pattern in patterns:
                if pattern.get('id') == pattern_id:
                    # Update engagement metrics
                    metrics = pattern.get('engagement_metrics', {})
                    
                    # Update each metric with weighted average
                    for metric, value in performance_data.items():
                        if metric in metrics:
                            # 90% old value, 10% new value for stability
                            metrics[metric] = metrics[metric] * 0.9 + value * 0.1
                        else:
                            metrics[metric] = value
                    
                    pattern['engagement_metrics'] = metrics
                    
                    # Save updates
                    self.save_database()
                    self.logger.info(f"Updated performance data for {pattern_id} in {industry}")
                    return True
            
            self.logger.warning(f"Pattern {pattern_id} not found in {industry}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating pattern performance: {str(e)}")
            return False
    
    def add_new_pattern(self, pattern_type: str, industry: str, pattern_data: Dict):
        """
        Add a new pattern to the database.
        
        Args:
            pattern_type: Type of pattern (headline, visual, copy, etc.)
            industry: Industry name
            pattern_data: Complete pattern data including metrics
            
        Returns:
            Boolean indicating success
        """
        try:
            if industry not in self.industries:
                self.industries[industry] = {}
            
            patterns_key = f"{pattern_type}_patterns"
            if patterns_key not in self.industries[industry]:
                self.industries[industry][patterns_key] = []
            
            # Generate pattern ID if not provided
            if 'id' not in pattern_data:
                import uuid
                pattern_data['id'] = f"{pattern_type}_{str(uuid.uuid4())[:8]}"
            
            # Add timestamp
            pattern_data['added_on'] = datetime.now().isoformat()
            
            # Add to database
            self.industries[industry][patterns_key].append(pattern_data)
            
            # Save database
            self.save_database()
            
            self.logger.info(f"Added new {pattern_type} pattern to {industry}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding new pattern: {str(e)}")
            return False
    
    def get_midjourney_prompt(self, industry: str, product: str, visual_style: str = None):
        """
        Generate an optimized Midjourney prompt based on industry patterns.
        
        Args:
            industry: Industry name
            product: Product name
            visual_style: Optional specific visual style to use
            
        Returns:
            Optimized Midjourney prompt string
        """
        # Get visual approaches for the industry
        visual_approaches = self.get_visual_approaches(industry)
        
        if not visual_approaches:
            # Fall back to universal visual approaches
            visual_approaches = self.universal_patterns.get('visual_approaches', [])
        
        # Select the visual approach
        visual_approach = None
        
        if visual_style and visual_approaches:
            # Find matching style if specified
            for approach in visual_approaches:
                if visual_style.lower() in approach.get('pattern', '').lower():
                    visual_approach = approach
                    break
        
        # If no match or no style specified, use highest performing
        if not visual_approach and visual_approaches:
            visual_approach = max(
                visual_approaches,
                key=lambda x: x.get('engagement_metrics', {}).get('average_engagement_rate', 0)
                if isinstance(x.get('engagement_metrics'), dict) else 0
            )
        
        # Get color schemes
        color_schemes = self.get_color_schemes(industry)
        color_scheme = color_schemes[0] if color_schemes else {'description': 'vibrant, professional'}
        
        # Construct prompt
        if visual_approach:
            prompt_template = visual_approach.get('ideal_prompt', '')
            if prompt_template:
                # Replace placeholders
                prompt = prompt_template.replace('[product]', product)
                prompt = prompt.replace('[industry]', industry)
                prompt = prompt.replace('[color]', color_scheme.get('description', 'professional'))
                return prompt
        
        # Fallback generic prompt if no matching approach found
        return f"Professional advertisement for {product} in {industry} industry. High-quality product photography, professional lighting, clean composition, magazine-quality, 8k resolution. --aspect 4:3 --quality 2 --style raw"

# Example usage if run directly
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize database
    db = AdPatternsDatabase()
    
    # Test retrieving patterns for technology industry
    tech_headlines = db.get_headline_patterns('technology')
    print(f"Found {len(tech_headlines)} technology headline patterns")
    
    # Test getting best performing pattern
    best_headline = db.get_best_performing_pattern('headline', 'technology', 'instagram')
    if best_headline:
        print(f"Best headline pattern: {best_headline.get('template')}")
        print(f"Engagement rate: {best_headline.get('engagement_metrics', {}).get('average_engagement_rate')}%")
    
    # Generate a Midjourney prompt
    prompt = db.get_midjourney_prompt('technology', 'smartphone')
    print(f"Midjourney prompt: {prompt}")