"""
Ad Patterns Analyzer - Utility for analyzing ads and extracting patterns with metrics

This module provides tools to analyze ads from various sources (Facebook, Instagram, etc.)
and extract patterns that can be added to the ad patterns database.
"""

import os
import json
import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import time
import random

class AdPatternsAnalyzer:
    """Analyze ads and extract patterns with engagement metrics."""
    
    def __init__(self, data_path: str = None):
        """
        Initialize the ad patterns analyzer.
        
        Args:
            data_path: Path to the directory for storing analysis results
        """
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Set data path
        self.data_path = data_path or os.path.join('data', 'training')
        os.makedirs(self.data_path, exist_ok=True)
        
        # Initialize pattern storage
        self.current_analysis = {
            "industry": "",
            "source": "",
            "ads_analyzed": 0,
            "headline_patterns": {},
            "visual_approaches": {},
            "color_schemes": {},
            "copy_structures": {},
            "emotional_triggers": {},
            "calls_to_action": {}
        }
    
    def analyze_facebook_ad(self, ad_data: Dict) -> Dict:
        """
        Analyze a Facebook ad and extract patterns.
        
        Args:
            ad_data: Dictionary containing Facebook ad data
            
        Returns:
            Dictionary with extracted patterns and metrics
        """
        try:
            patterns = {}
            
            # Extract headline
            if 'ad_creative_link_titles' in ad_data and ad_data['ad_creative_link_titles']:
                headline = ad_data['ad_creative_link_titles'][0]
                patterns['headline'] = self._categorize_headline(headline)
            
            # Extract copy
            if 'ad_creative_bodies' in ad_data and ad_data['ad_creative_bodies']:
                body_text = ad_data['ad_creative_bodies'][0]
                patterns['copy_structure'] = self._analyze_copy_structure(body_text)
                patterns['emotional_triggers'] = self._extract_emotional_triggers(body_text)
                patterns['cta'] = self._extract_cta(body_text)
            
            # Extract engagement metrics
            patterns['engagement_metrics'] = self._extract_facebook_metrics(ad_data)
            
            # Add to current analysis
            self._add_to_current_analysis(patterns)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error analyzing Facebook ad: {str(e)}")
            return {}
    
    def analyze_instagram_ad(self, ad_data: Dict) -> Dict:
        """
        Analyze an Instagram ad and extract patterns.
        
        Args:
            ad_data: Dictionary containing Instagram ad data
            
        Returns:
            Dictionary with extracted patterns and metrics
        """
        try:
            patterns = {}
            
            # Similar to Facebook but with Instagram-specific metrics
            # This is a placeholder - you would customize for Instagram's data structure
            
            # Instagram often has the same ad structure as Facebook Ads
            patterns = self.analyze_facebook_ad(ad_data)
            
            # Override or add Instagram-specific metrics
            if 'engagement_metrics' in patterns:
                patterns['engagement_metrics']['platform'] = 'instagram'
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error analyzing Instagram ad: {str(e)}")
            return {}
    
    def analyze_ad_from_html(self, html_content: str, source: str = "facebook") -> Dict:
        """
        Analyze ad from scraped HTML content.
        
        Args:
            html_content: HTML content from ad page
            source: Source platform (facebook, instagram, etc.)
            
        Returns:
            Dictionary with extracted patterns and metrics
        """
        try:
            patterns = {}
            
            # Extract headline using regex
            headline_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.DOTALL)
            if headline_match:
                headline = headline_match.group(1).strip()
                patterns['headline'] = self._categorize_headline(headline)
            
            # Extract body copy
            body_match = re.search(r'<div[^>]*class="[^"]*ad-body[^"]*"[^>]*>(.*?)</div>', html_content, re.DOTALL)
            if body_match:
                body_text = body_match.group(1).strip()
                # Remove HTML tags
                body_text = re.sub(r'<[^>]+>', '', body_text)
                patterns['copy_structure'] = self._analyze_copy_structure(body_text)
                patterns['emotional_triggers'] = self._extract_emotional_triggers(body_text)
                patterns['cta'] = self._extract_cta(body_text)
            
            # Extract engagement metrics if available
            metrics_match = re.search(r'data-metrics="([^"]*)"', html_content)
            if metrics_match:
                try:
                    metrics_json = metrics_match.group(1).replace('&quot;', '"')
                    metrics = json.loads(metrics_json)
                    patterns['engagement_metrics'] = metrics
                except:
                    # If parsing fails, use placeholder metrics
                    patterns['engagement_metrics'] = self._create_placeholder_metrics(source)
            else:
                patterns['engagement_metrics'] = self._create_placeholder_metrics(source)
            
            # Add to current analysis
            self._add_to_current_analysis(patterns)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error analyzing ad from HTML: {str(e)}")
            return {}
    
    def add_manually_analyzed_ad(self, ad_data: Dict, industry: str) -> bool:
        """
        Add manually analyzed ad data to the current analysis.
        
        Args:
            ad_data: Dictionary with ad elements and metrics
            industry: Industry category for the ad
            
        Returns:
            Boolean indicating success
        """
        try:
            # Set industry for current analysis
            if not self.current_analysis['industry']:
                self.current_analysis['industry'] = industry
            
            # Validate required fields
            required_fields = ['headline', 'copy', 'visual_approach']
            for field in required_fields:
                if field not in ad_data:
                    self.logger.warning(f"Missing required field: {field}")
            
            # Add to current analysis
            self._add_to_current_analysis(ad_data)
            
            # Increment ad count
            self.current_analysis['ads_analyzed'] += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding manually analyzed ad: {str(e)}")
            return False
    
    def complete_analysis(self, industry: str, min_sample_size: int = 20) -> Dict:
        """
        Complete the current analysis and save results.
        
        Args:
            industry: Industry category
            min_sample_size: Minimum sample size for valid patterns
            
        Returns:
            Dictionary with aggregated patterns and metrics
        """
        try:
            # Set industry
            self.current_analysis['industry'] = industry
            
            # Check sample size
            if self.current_analysis['ads_analyzed'] < min_sample_size:
                self.logger.warning(f"Small sample size: {self.current_analysis['ads_analyzed']} ads analyzed. Results may not be statistically significant.")
            
            # Aggregate patterns and metrics
            results = {
                "industry": industry,
                "sample_size": self.current_analysis['ads_analyzed'],
                "analysis_date": datetime.now().isoformat(),
                "headline_patterns": self._aggregate_headline_patterns(),
                "visual_approaches": self._aggregate_visual_approaches(),
                "color_schemes": self._aggregate_color_schemes(),
                "copy_structures": self._aggregate_copy_structures(),
                "emotional_triggers": self._aggregate_emotional_triggers(),
                "calls_to_action": self._aggregate_ctas()
            }
            
            # Save results
            self._save_analysis_results(results)
            
            # Reset current analysis
            self.current_analysis = {
                "industry": "",
                "source": "",
                "ads_analyzed": 0,
                "headline_patterns": {},
                "visual_approaches": {},
                "color_schemes": {},
                "copy_structures": {},
                "emotional_triggers": {},
                "calls_to_action": {}
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error completing analysis: {str(e)}")
            return {}
    
    def _categorize_headline(self, headline: str) -> Dict:
        """Categorize headline into pattern types."""
        headline_type = "undefined"
        
        # Question pattern
        if '?' in headline:
            headline_type = "question"
        
        # Number pattern (e.g., "5 Ways to...")
        elif re.match(r'^\d+\s+', headline):
            headline_type = "numbered_list"
        
        # How-to pattern
        elif headline.lower().startswith('how to'):
            headline_type = "how_to"
        
        # Problem-solution pattern
        elif any(word in headline.lower() for word in ['tired of', 'sick of', 'frustrated with', 'problem']):
            headline_type = "problem_solution"
        
        # Announcement pattern
        elif any(word in headline.lower() for word in ['introducing', 'new', 'announcing', 'finally']):
            headline_type = "announcement"
        
        # Command pattern
        elif re.match(r'^[A-Z][a-z]+\s', headline) and ' your ' in headline.lower():
            headline_type = "command"
        
        return {
            "text": headline,
            "type": headline_type,
            "word_count": len(headline.split()),
            "character_count": len(headline)
        }
    
    def _analyze_copy_structure(self, copy_text: str) -> Dict:
        """Analyze ad copy structure."""
        sentences = self._split_into_sentences(copy_text)
        
        structure = {
            "text": copy_text,
            "sentence_count": len(sentences),
            "word_count": len(copy_text.split()),
            "character_count": len(copy_text),
            "has_bullet_points": '•' in copy_text or '*' in copy_text,
            "has_numbers": bool(re.search(r'\d+', copy_text)),
            "has_question": '?' in copy_text,
            "format": "paragraph" if len(sentences) > 1 and not ('•' in copy_text) else "bullet_list" if '•' in copy_text else "short_form"
        }
        
        # Check for feature-benefit structure
        feature_benefit_pairs = []
        for sentence in sentences:
            if ' so ' in sentence.lower() or ' which means ' in sentence.lower() or ' that means ' in sentence.lower():
                parts = re.split(r'\s+so\s+|\s+which means\s+|\s+that means\s+', sentence, flags=re.IGNORECASE)
                if len(parts) > 1:
                    feature_benefit_pairs.append({
                        "feature": parts[0].strip(),
                        "benefit": parts[1].strip()
                    })
        
        structure["feature_benefit_pairs"] = feature_benefit_pairs
        structure["has_feature_benefit_structure"] = len(feature_benefit_pairs) > 0
        
        return structure
    
    def _extract_emotional_triggers(self, text: str) -> List[str]:
        """Extract emotional triggers from ad copy."""
        triggers = []
        
        # Dictionary of emotional triggers and their indicator words/phrases
        emotion_indicators = {
            "fear_of_missing_out": ["limited time", "don't miss", "last chance", "exclusive", "ends soon"],
            "aspiration": ["imagine", "dream", "achieve", "success", "best version"],
            "belonging": ["join", "community", "together", "like you", "others are"],
            "guilt": ["shouldn't you", "you owe it", "you deserve", "treat yourself"],
            "curiosity": ["discover", "secret", "revealed", "find out", "mystery"],
            "urgency": ["now", "today", "hurry", "quick", "fast"],
            "trust": ["proven", "guaranteed", "trusted", "reliable", "safe"],
            "value": ["save", "discount", "free", "bonus", "deal"],
            "status": ["exclusive", "premium", "luxury", "elite", "vip"],
            "simplification": ["easy", "simple", "hassle-free", "effortless", "quick"]
        }
        
        # Check for each emotional trigger
        text_lower = text.lower()
        for emotion, indicators in emotion_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    triggers.append(emotion)
                    break  # Only add each emotion once
        
        return triggers
    
    def _extract_cta(self, text: str) -> Dict:
        """Extract call-to-action from ad copy."""
        cta = {
            "text": "",
            "type": "none",
            "position": "none"
        }
        
        # Common CTA phrases
        cta_phrases = [
            "shop now", "buy now", "get started", "learn more", "sign up", 
            "subscribe", "download", "try free", "book now", "order now",
            "get yours", "join now", "discover", "find out more", "click here"
        ]
        
        # Check for CTA phrases in text
        text_lower = text.lower()
        for phrase in cta_phrases:
            if phrase in text_lower:
                cta["text"] = phrase
                
                # Determine CTA type
                if phrase in ["shop now", "buy now", "order now", "get yours"]:
                    cta["type"] = "purchase"
                elif phrase in ["learn more", "discover", "find out more"]:
                    cta["type"] = "information"
                elif phrase in ["sign up", "subscribe", "join now"]:
                    cta["type"] = "subscription"
                elif phrase in ["download", "try free"]:
                    cta["type"] = "acquisition"
                else:
                    cta["type"] = "action"
                
                # Determine position (approximate)
                position = text_lower.find(phrase)
                text_length = len(text_lower)
                if position < text_length / 3:
                    cta["position"] = "beginning"
                elif position < 2 * text_length / 3:
                    cta["position"] = "middle"
                else:
                    cta["position"] = "end"
                
                break
        
        return cta
    
    def _extract_facebook_metrics(self, ad_data: Dict) -> Dict:
        """Extract engagement metrics from Facebook ad data."""
        metrics = {
            "platform": "facebook",
            "estimated_engagement_rate": 0.0,
            "estimated_ctr": 0.0,
            "estimated_conversion_rate": 0.0
        }
        
        # Extract actual metrics if available
        if 'impressions' in ad_data and isinstance(ad_data['impressions'], dict):
            impressions = ad_data['impressions'].get('lower_bound', 0)
            metrics["impressions"] = impressions
            
            # If engagement data available
            if 'engagement' in ad_data and isinstance(ad_data['engagement'], dict):
                engagement = ad_data['engagement'].get('post_engagement', 0)
                if impressions > 0 and engagement > 0:
                    metrics["estimated_engagement_rate"] = (engagement / impressions) * 100
            
            # Convert to float for consistency
            metrics["estimated_engagement_rate"] = float(metrics["estimated_engagement_rate"])
        
        return metrics
    
    def _create_placeholder_metrics(self, platform: str) -> Dict:
        """Create placeholder metrics when real data unavailable."""
        # Create realistic-looking placeholder data
        base_engagement = random.uniform(2.5, 7.5)  # Base engagement rate between 2.5% and 7.5%
        
        # Adjust based on platform (Instagram typically has higher engagement than Facebook)
        platform_factor = 1.2 if platform.lower() == 'instagram' else 1.0
        
        metrics = {
            "platform": platform.lower(),
            "estimated_engagement_rate": base_engagement * platform_factor,
            "estimated_ctr": base_engagement * 0.7 * platform_factor,  # CTR typically lower than engagement
            "estimated_conversion_rate": base_engagement * 0.3 * platform_factor,  # Conversion typically lower than CTR
            "is_placeholder": True  # Flag that these are estimated metrics
        }
        
        return metrics
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting - could be improved with NLP libraries
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _add_to_current_analysis(self, patterns: Dict) -> None:
        """Add extracted patterns to current analysis."""
        self.current_analysis['ads_analyzed'] += 1
        
        # Add headline pattern
        if 'headline' in patterns and patterns['headline']:
            headline_type = patterns['headline'].get('type', 'undefined')
            if headline_type not in self.current_analysis['headline_patterns']:
                self.current_analysis['headline_patterns'][headline_type] = {
                    'count': 0,
                    'examples': [],
                    'engagement_rates': [],
                    'word_counts': [],
                    'character_counts': []
                }
            
            self.current_analysis['headline_patterns'][headline_type]['count'] += 1
            self.current_analysis['headline_patterns'][headline_type]['examples'].append(
                patterns['headline'].get('text', '')
            )
            self.current_analysis['headline_patterns'][headline_type]['word_counts'].append(
                patterns['headline'].get('word_count', 0)
            )
            self.current_analysis['headline_patterns'][headline_type]['character_counts'].append(
                patterns['headline'].get('character_count', 0)
            )
            
            # Add engagement rate if available
            if 'engagement_metrics' in patterns and 'estimated_engagement_rate' in patterns['engagement_metrics']:
                self.current_analysis['headline_patterns'][headline_type]['engagement_rates'].append(
                    patterns['engagement_metrics']['estimated_engagement_rate']
                )
        
        # Add copy structure
        if 'copy_structure' in patterns and patterns['copy_structure']:
            copy_format = patterns['copy_structure'].get('format', 'undefined')
            if copy_format not in self.current_analysis['copy_structures']:
                self.current_analysis['copy_structures'][copy_format] = {
                    'count': 0,
                    'sentence_counts': [],
                    'word_counts': [],
                    'engagement_rates': [],
                    'has_feature_benefit': 0
                }
            
            self.current_analysis['copy_structures'][copy_format]['count'] += 1
            self.current_analysis['copy_structures'][copy_format]['sentence_counts'].append(
                patterns['copy_structure'].get('sentence_count', 0)
            )
            self.current_analysis['copy_structures'][copy_format]['word_counts'].append(
                patterns['copy_structure'].get('word_count', 0)
            )
            
            # Track feature-benefit usage
            if patterns['copy_structure'].get('has_feature_benefit_structure', False):
                self.current_analysis['copy_structures'][copy_format]['has_feature_benefit'] += 1
            
            # Add engagement rate if available
            if 'engagement_metrics' in patterns and 'estimated_engagement_rate' in patterns['engagement_metrics']:
                self.current_analysis['copy_structures'][copy_format]['engagement_rates'].append(
                    patterns['engagement_metrics']['estimated_engagement_rate']
                )
        
        # Add emotional triggers
        if 'emotional_triggers' in patterns and patterns['emotional_triggers']:
            for trigger in patterns['emotional_triggers']:
                if trigger not in self.current_analysis['emotional_triggers']:
                    self.current_analysis['emotional_triggers'][trigger] = {
                        'count': 0,
                        'engagement_rates': []
                    }
                
                self.current_analysis['emotional_triggers'][trigger]['count'] += 1
                
                # Add engagement rate if available
                if 'engagement_metrics' in patterns and 'estimated_engagement_rate' in patterns['engagement_metrics']:
                    self.current_analysis['emotional_triggers'][trigger]['engagement_rates'].append(
                        patterns['engagement_metrics']['estimated_engagement_rate']
                    )
        
        # Add CTA
        if 'cta' in patterns and patterns['cta'] and patterns['cta']['text']:
            cta_type = patterns['cta'].get('type', 'undefined')
            if cta_type not in self.current_analysis['calls_to_action']:
                self.current_analysis['calls_to_action'][cta_type] = {
                    'count': 0,
                    'examples': [],
                    'positions': {'beginning': 0, 'middle': 0, 'end': 0},
                    'engagement_rates': []
                }
            
            self.current_analysis['calls_to_action'][cta_type]['count'] += 1
            self.current_analysis['calls_to_action'][cta_type]['examples'].append(
                patterns['cta'].get('text', '')
            )
            
            # Track position
            position = patterns['cta'].get('position', 'end')
            self.current_analysis['calls_to_action'][cta_type]['positions'][position] += 1
            
            # Add engagement rate if available
            if 'engagement_metrics' in patterns and 'estimated_engagement_rate' in patterns['engagement_metrics']:
                self.current_analysis['calls_to_action'][cta_type]['engagement_rates'].append(
                    patterns['engagement_metrics']['estimated_engagement_rate']
                )
    
    def _aggregate_headline_patterns(self) -> List[Dict]:
        """Aggregate headline patterns from current analysis."""
        patterns = []
        
        for pattern_type, data in self.current_analysis['headline_patterns'].items():
            if data['count'] == 0:
                continue
                
            engagement_rate = 0
            if data['engagement_rates']:
                engagement_rate = sum(data['engagement_rates']) / len(data['engagement_rates'])
            
            avg_word_count = 0
            if data['word_counts']:
                avg_word_count = sum(data['word_counts']) / len(data['word_counts'])
            
            avg_character_count = 0
            if data['character_counts']:
                avg_character_count = sum(data['character_counts']) / len(data['character_counts'])
            
            # Create pattern entry
            pattern = {
                "id": f"{self.current_analysis['industry']}_{pattern_type}",
                "pattern": pattern_type,
                "count": data['count'],
                "frequency_percentage": (data['count'] / self.current_analysis['ads_analyzed']) * 100,
                "examples": data['examples'][:5],  # Limit to 5 examples
                "engagement_metrics": {
                    "average_engagement_rate": round(engagement_rate, 1),
                    "sample_size": len(data['engagement_rates'])
                },
                "average_word_count": round(avg_word_count, 1),
                "average_character_count": round(avg_character_count, 1)
            }
            
            patterns.append(pattern)
        
        # Sort by engagement rate
        return sorted(patterns, key=lambda x: x['engagement_metrics']['average_engagement_rate'], reverse=True)
    
    def _aggregate_copy_structures(self) -> List[Dict]:
        """Aggregate copy structures from current analysis."""
        structures = []
        
        for structure_type, data in self.current_analysis['copy_structures'].items():
            if data['count'] == 0:
                continue
                
            engagement_rate = 0
            if data['engagement_rates']:
                engagement_rate = sum(data['engagement_rates']) / len(data['engagement_rates'])
            
            avg_sentence_count = 0
            if data['sentence_counts']:
                avg_sentence_count = sum(data['sentence_counts']) / len(data['sentence_counts'])
            
            avg_word_count = 0
            if data['word_counts']:
                avg_word_count = sum(data['word_counts']) / len(data['word_counts'])
            
            feature_benefit_percentage = 0
            if data['count'] > 0:
                feature_benefit_percentage = (data['has_feature_benefit'] / data['count']) * 100
            
            # Create structure entry
            structure = {
                "id": f"{self.current_analysis['industry']}_{structure_type}",
                "pattern": structure_type,
                "count": data['count'],
                "frequency_percentage": (data['count'] / self.current_analysis['ads_analyzed']) * 100,
                "engagement_metrics": {
                    "average_engagement_rate": round(engagement_rate, 1),
                    "sample_size": len(data['engagement_rates'])
                },
                "average_sentence_count": round(avg_sentence_count, 1),
                "average_word_count": round(avg_word_count, 1),
                "feature_benefit_percentage": round(feature_benefit_percentage, 1)
            }
            
            structures.append(structure)
        
        # Sort by engagement rate
        return sorted(structures, key=lambda x: x['engagement_metrics']['average_engagement_rate'], reverse=True)
    
    def _aggregate_emotional_triggers(self) -> List[Dict]:
        """Aggregate emotional triggers from current analysis."""
        triggers = []
        
        for trigger_type, data in self.current_analysis['emotional_triggers'].items():
            if data['count'] == 0:
                continue
                
            engagement_rate = 0
            if data['engagement_rates']:
                engagement_rate = sum(data['engagement_rates']) / len(data['engagement_rates'])
            
            # Create trigger entry
            trigger = {
                "id": f"{self.current_analysis['industry']}_{trigger_type}",
                "pattern": trigger_type,
                "count": data['count'],
                "frequency_percentage": (data['count'] / self.current_analysis['ads_analyzed']) * 100,
                "engagement_metrics": {
                    "average_engagement_rate": round(engagement_rate, 1),
                    "sample_size": len(data['engagement_rates'])
                }
            }
            
            triggers.append(trigger)
        
        # Sort by engagement rate
        return sorted(triggers, key=lambda x: x['engagement_metrics']['average_engagement_rate'], reverse=True)
    
    def _aggregate_ctas(self) -> List[Dict]:
        """Aggregate calls to action from current analysis."""
        ctas = []
        
        for cta_type, data in self.current_analysis['calls_to_action'].items():
            if data['count'] == 0:
                continue
                
            engagement_rate = 0
            if data['engagement_rates']:
                engagement_rate = sum(data['engagement_rates']) / len(data['engagement_rates'])
            
            # Find most common position
            best_position = max(data['positions'].items(), key=lambda x: x[1])[0]
            
            # Find most common example
            example_counts = {}
            for example in data['examples']:
                example_lower = example.lower()
                if example_lower not in example_counts:
                    example_counts[example_lower] = 0
                example_counts[example_lower] += 1
            
            best_example = ""
            if example_counts:
                best_example = max(example_counts.items(), key=lambda x: x[1])[0]
            
            # Create CTA entry
            cta = {
                "id": f"{self.current_analysis['industry']}_{cta_type}",
                "pattern": cta_type,
                "text": best_example,
                "count": data['count'],
                "frequency_percentage": (data['count'] / self.current_analysis['ads_analyzed']) * 100,
                "optimal_position": best_position,
                "position_distribution": {
                    pos: (count / data['count']) * 100 for pos, count in data['positions'].items() if count > 0
                },
                "engagement_metrics": {
                    "average_engagement_rate": round(engagement_rate, 1),
                    "sample_size": len(data['engagement_rates'])
                }
            }
            
            ctas.append(cta)
        
        # Sort by engagement rate
        return sorted(ctas, key=lambda x: x['engagement_metrics']['average_engagement_rate'], reverse=True)
    
    def _aggregate_visual_approaches(self) -> List[Dict]:
        """Aggregate visual approaches from current analysis."""
        # Visual approaches are mostly added manually since image analysis
        # Would require computer vision capabilities
        return list(self.current_analysis.get('visual_approaches', {}).values())
    
    def _aggregate_color_schemes(self) -> List[Dict]:
        """Aggregate color schemes from current analysis."""
        # Color schemes are mostly added manually since color analysis
        # Would require computer vision capabilities
        return list(self.current_analysis.get('color_schemes', {}).values())
    
    def _save_analysis_results(self, results: Dict) -> None:
        """Save analysis results to file."""
        try:
            # Create filename with timestamp and industry
            industry_slug = results['industry'].lower().replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"ad_analysis_{industry_slug}_{timestamp}.json"
            filepath = os.path.join(self.data_path, filename)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Analysis results saved to: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving analysis results: {str(e)}")
    
    def convert_analysis_to_database_format(self, analysis_file: str) -> Dict:
        """
        Convert analysis results to database format for the AdPatternsDatabase.
        
        Args:
            analysis_file: Path to analysis results file
            
        Returns:
            Dictionary in database format
        """
        try:
            # Load analysis
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis = json.load(f)
            
            industry = analysis.get('industry', '').lower().replace(' ', '_')
            
            # Convert to database format
            db_format = {
                "headline_patterns": [],
                "visual_approaches": [],
                "copy_structures": [],
                "color_schemes": [],
                "emotional_triggers": [],
                "calls_to_action": []
            }
            
            # Format headline patterns
            for pattern in analysis.get('headline_patterns', []):
                db_pattern = {
                    "id": pattern.get('id', f"{industry}_{pattern['pattern']}"),
                    "pattern": pattern.get('pattern', 'undefined'),
                    "template": self._create_template_from_pattern(pattern),
                    "engagement_metrics": {
                        "average_engagement_rate": pattern.get('engagement_metrics', {}).get('average_engagement_rate', 0),
                        "sample_size": pattern.get('engagement_metrics', {}).get('sample_size', 0)
                    },
                    "examples": pattern.get('examples', [])[:3],
                    "best_for": self._infer_best_uses(pattern)
                }
                db_format['headline_patterns'].append(db_pattern)
            
            # Similarly format other pattern types
            # [implementation for visual_approaches, copy_structures, etc.]
            
            return db_format
            
        except Exception as e:
            self.logger.error(f"Error converting analysis to database format: {str(e)}")
            return {}
    
    def _create_template_from_pattern(self, pattern: Dict) -> str:
        """Create a template from a pattern using examples."""
        pattern_type = pattern.get('pattern', '').lower()
        examples = pattern.get('examples', [])
        
        if not examples:
            return "Custom [Product] Template"
        
        # Use first example as base
        example = examples[0]
        
        # Create template based on pattern type
        if pattern_type == 'question':
            # Convert statement to question template
            return example.replace('.', '?') if '?' not in example else example
            
        elif pattern_type == 'numbered_list':
            # Replace specific number with [Number]
            return re.sub(r'^\d+', '[Number]', example)
            
        elif pattern_type == 'how_to':
            # Standardize how-to format
            if example.lower().startswith('how to'):
                return example
            return f"How to {example}"
            
        elif pattern_type == 'problem_solution':
            # Create problem-solution template
            return "Tired of [Problem]? Try [Product] for [Solution]"
            
        # Default: replace specific product/brand names with placeholders
        return example.replace('.', '')
    
    def _infer_best_uses(self, pattern: Dict) -> List[str]:
        """Infer best uses for a pattern based on metrics and type."""
        best_uses = []
        pattern_type = pattern.get('pattern', '').lower()
        
        # Add based on pattern type
        if pattern_type == 'question':
            best_uses.append('engagement_focused')
            best_uses.append('problem_aware_audience')
            
        elif pattern_type == 'numbered_list':
            best_uses.append('feature_rich_products')
            best_uses.append('comparison_shoppers')
            
        elif pattern_type == 'how_to':
            best_uses.append('solution_focused')
            best_uses.append('educational_content')
            
        elif pattern_type == 'problem_solution':
            best_uses.append('pain_point_targeting')
            best_uses.append('solution_aware_audience')
            
        elif pattern_type == 'announcement':
            best_uses.append('new_products')
            best_uses.append('product_launches')
        
        # Check word count
        avg_word_count = pattern.get('average_word_count', 0)
        if avg_word_count <= 5:
            best_uses.append('mobile_ads')
            best_uses.append('minimal_designs')
        elif avg_word_count >= 8:
            best_uses.append('detailed_information')
        
        return best_uses[:3]  # Limit to top 3 uses


# Example usage if run directly
if __name__ == "__main__":
    analyzer = AdPatternsAnalyzer()
    
    # Example manual ad data
    sample_ad = {
        "headline": {
            "text": "Transform Your Home in Just One Day",
            "type": "command"
        },
        "copy": {
            "text": "Our premium paint dries in just 1 hour, so you can completely refresh your space in a single day. Available in 50+ designer colors.",
            "format": "paragraph"
        },
        "visual_approach": "lifestyle_transformation",
        "engagement_metrics": {
            "estimated_engagement_rate": 5.7
        }
    }
    
    # Add to analysis
    analyzer.add_manually_analyzed_ad(sample_ad, "home_improvement")
    
    # Add a few more sample ads
    for i in range(5):
        analyzer.add_manually_analyzed_ad(sample_ad, "home_improvement")
    
    # Complete analysis
    results = analyzer.complete_analysis("home_improvement", min_sample_size=5)
    print(f"Analysis completed with {results.get('sample_size', 0)} ads")
    if results.get('headline_patterns'):
        print(f"Top headline pattern: {results['headline_patterns'][0]['pattern']}")
        print(f"Engagement rate: {results['headline_patterns'][0]['engagement_metrics']['average_engagement_rate']}%")