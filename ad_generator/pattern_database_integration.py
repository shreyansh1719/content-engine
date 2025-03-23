"""
Pattern Database Integration - Integrates ad pattern database with ad generation process

This module connects the ad patterns database with the ad generation process,
applying insights from the database to optimize ad creation through enhanced
prompts and templates.
"""

import logging
from typing import Dict, List, Any, Optional, Union
import random
import re

# Import from your existing code structure
from ad_generator.ad_patterns_database import AdPatternsDatabase
from ad_generator.patterns_analyzer import AdPatternsAnalyzer

class PatternDatabaseIntegration:
    """Integrates ad pattern database with ad generation process."""
    
    def __init__(self, data_path: str = None):
        """
        Initialize the pattern database integration.
        
        Args:
            data_path: Path to the database and analysis files
        """
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize databases
        self.patterns_db = AdPatternsDatabase(data_path)
        self.analyzer = AdPatternsAnalyzer(data_path)
        
        # Status tracking
        self.initialized = True
    
    def enhance_ad_prompt(self, original_prompt: str, industry: str, 
                         target_platform: str = None, 
                         target_demographic: str = None) -> Dict:
        """
        Enhance an ad generation prompt with insights from the patterns database.
        
        Args:
            original_prompt: Original user prompt
            industry: Industry category
            target_platform: Target platform (facebook, instagram, etc.)
            target_demographic: Target demographic (e.g., "18-24")
            
        Returns:
            Dictionary with enhanced prompt and context
        """
        try:
            # Get industry-specific patterns
            industry_patterns = self.patterns_db.get_industry_patterns(industry)
            
            # Get universal patterns
            universal_patterns = self.patterns_db.get_universal_patterns()
            
            # Get best performing headline pattern
            headline_pattern = self.patterns_db.get_best_performing_pattern(
                'headline', industry, platform=target_platform, demographic=target_demographic
            )
            
            # Get best performing visual approach
            visual_approach = self.patterns_db.get_best_performing_pattern(
                'visual', industry, platform=target_platform, demographic=target_demographic
            )
            
            # Get best performing copy structure
            copy_structure = self.patterns_db.get_best_performing_pattern(
                'copy', industry, platform=target_platform, demographic=target_demographic
            )
            
            # Get best performing CTA
            cta = self.patterns_db.get_best_performing_pattern(
                'calls_to_action', industry, platform=target_platform, demographic=target_demographic
            )
            
            # Create enhanced prompt
            enhanced_prompt = f"""Create a high-converting advertisement for {original_prompt} in the {industry} industry.

Based on pattern analysis of top-performing ads, use these specific elements:

1. HEADLINE PATTERN: {headline_pattern.get('template', 'Compelling headline for [Product]')}
   - This pattern has {headline_pattern.get('engagement_metrics', {}).get('average_engagement_rate', 0)}% engagement rate
   - Best for: {', '.join(headline_pattern.get('best_for', ['']))}

2. VISUAL APPROACH: {visual_approach.get('description', 'Professional product photography')}
   - {visual_approach.get('engagement_metrics', {}).get('average_engagement_rate', 0)}% engagement rate
   - {visual_approach.get('platform_performance', {}).get(target_platform, '')}% on {target_platform if target_platform else 'primary platforms'}

3. COPY STRUCTURE: {copy_structure.get('description', 'Clear feature-benefit structure')}
   - Optimal length: {copy_structure.get('average_word_count', 50)} words
   - Include {copy_structure.get('feature_benefit_percentage', 0)}% feature-benefit statements

4. CALL TO ACTION: "{cta.get('text', 'Shop Now')}"
   - Optimal placement: {cta.get('optimal_position', 'end')} of ad
   - {cta.get('engagement_metrics', {}).get('average_engagement_rate', 0)}% engagement rate

Generate a complete ad including:
1. Headline following the pattern
2. Subheadline
3. Body copy following the structure
4. Call to action
5. Detailed image description following the visual approach

Format your response as a structured JSON object.
"""
            
            # Create context for pattern-based generation
            context = {
                "industry": industry,
                "headline_pattern": headline_pattern,
                "visual_approach": visual_approach,
                "copy_structure": copy_structure,
                "cta": cta,
                "platform": target_platform,
                "demographic": target_demographic
            }
            
            return {
                "enhanced_prompt": enhanced_prompt,
                "context": context
            }
            
        except Exception as e:
            self.logger.error(f"Error enhancing prompt: {str(e)}")
            # Return original prompt if enhancement fails
            return {
                "enhanced_prompt": original_prompt,
                "context": {"industry": industry}
            }
    
    def enhance_image_prompt(self, original_prompt: str, industry: str,
                           visual_style: str = None, platform: str = None) -> str:
        """
        Enhance an image generation prompt with insights from the patterns database.
        
        Args:
            original_prompt: Original image prompt
            industry: Industry category
            visual_style: Optional specific visual style
            platform: Target platform (instagram, facebook, etc.)
            
        Returns:
            Enhanced image prompt
        """
        try:
            # Get optimal visual approach for this industry
            if not visual_style:
                visual_approaches = self.patterns_db.get_visual_approaches(industry)
                
                if visual_approaches:
                    # Sort by engagement rate for the specified platform if available
                    if platform:
                        platform_approaches = []
                        for approach in visual_approaches:
                            engagement_metrics = approach.get('engagement_metrics', {})
                            platform_performance = engagement_metrics.get('platform_performance', {})
                            
                            if platform in platform_performance:
                                approach_copy = approach.copy()
                                approach_copy['platform_score'] = platform_performance[platform]
                                platform_approaches.append(approach_copy)
                        
                        if platform_approaches:
                            visual_approaches = sorted(
                                platform_approaches,
                                key=lambda x: x.get('platform_score', 0),
                                reverse=True
                            )
                    
                    # Get the highest performing approach
                    best_approach = visual_approaches[0]
                    visual_style = best_approach.get('pattern', '')
            
            # Get the optimal color scheme
            color_schemes = self.patterns_db.get_color_schemes(industry)
            color_scheme = color_schemes[0] if color_schemes else None
            
            # Check if there's an ideal prompt template in the database
            ideal_prompt = ""
            visual_approaches = self.patterns_db.get_visual_approaches(industry)
            for approach in visual_approaches:
                if approach.get('pattern', '') == visual_style:
                    ideal_prompt = approach.get('ideal_prompt', '')
                    break
            
            if ideal_prompt:
                # Replace placeholders in ideal prompt
                enhanced_prompt = ideal_prompt.replace('[product]', original_prompt)
                
                # Add color scheme if available
                if color_scheme:
                    color_description = color_scheme.get('description', '')
                    enhanced_prompt = enhanced_prompt.replace('[color]', color_description)
                
                # Add specific platform optimizations
                if platform:
                    if platform.lower() == 'instagram':
                        enhanced_prompt += ", instagram aesthetic, square format, lifestyle"
                    elif platform.lower() == 'facebook':
                        enhanced_prompt += ", facebook ad style, rectangular format, clear messaging"
                    elif platform.lower() == 'pinterest':
                        enhanced_prompt += ", pinterest style, vertical format, inspirational"
                
                return enhanced_prompt
            
            # If no ideal prompt found, enhance the original prompt
            midjourney_prompt = self.patterns_db.get_midjourney_prompt(industry, original_prompt, visual_style)
            return midjourney_prompt
            
        except Exception as e:
            self.logger.error(f"Error enhancing image prompt: {str(e)}")
            # Return a basic enhanced version of the original prompt
            return f"Professional advertisement for {original_prompt} in {industry} industry. High-quality product photography, magazine quality, perfect lighting, clean composition."
    
    def optimize_ad_copy(self, headline: str, body_text: str, industry: str) -> Dict:
        """
        Optimize ad copy based on patterns database insights.
        
        Args:
            headline: Ad headline
            body_text: Ad body text
            industry: Industry category
            
        Returns:
            Dictionary with optimized headline and body text
        """
        try:
            # Get best performing headline patterns
            headline_patterns = self.patterns_db.get_headline_patterns(industry)
            
            # Get best performing copy structures
            copy_structures = self.patterns_db.get_copy_structures(industry)
            
            # Check if the existing headline matches any high-performing patterns
            headline_score = 0
            headline_improvements = []
            
            for pattern in headline_patterns:
                pattern_type = pattern.get('pattern', '')
                
                # Score the headline against this pattern
                pattern_score = self._score_text_against_pattern(headline, pattern_type)
                if pattern_score > headline_score:
                    headline_score = pattern_score
                
                # Suggest improvements
                if pattern_score < 0.7:  # If headline doesn't match pattern well
                    template = pattern.get('template', '')
                    if template:
                        headline_improvements.append({
                            'pattern': pattern_type,
                            'template': template,
                            'engagement_rate': pattern.get('engagement_metrics', {}).get('average_engagement_rate', 0)
                        })
            
            # Check if body text follows optimal structure
            body_score = 0
            body_improvements = []
            
            if copy_structures:
                best_structure = copy_structures[0]
                structure_type = best_structure.get('pattern', '')
                
                # Score the body text against this structure
                body_score = self._score_text_against_structure(body_text, structure_type)
                
                # Suggest improvements
                if body_score < 0.7:  # If body doesn't match structure well
                    optimal_sentence_count = best_structure.get('average_sentence_count', 3)
                    optimal_word_count = best_structure.get('average_word_count', 50)
                    feature_benefit = best_structure.get('feature_benefit_percentage', 0) > 50
                    
                    current_sentences = len(re.split(r'[.!?]+', body_text))
                    current_words = len(body_text.split())
                    
                    if current_sentences != optimal_sentence_count:
                        body_improvements.append(f"Adjust to {optimal_sentence_count} sentences for +{best_structure.get('engagement_metrics', {}).get('average_engagement_rate', 0)}% engagement")
                    
                    if abs(current_words - optimal_word_count) > 10:
                        direction = "Extend" if current_words < optimal_word_count else "Shorten"
                        body_improvements.append(f"{direction} to {optimal_word_count} words for optimal engagement")
                    
                    if feature_benefit and 'so' not in body_text.lower() and 'which means' not in body_text.lower():
                        body_improvements.append("Add clear feature-benefit statements (X, which means Y)")
            
            return {
                "headline_score": headline_score,
                "headline_improvements": headline_improvements,
                "body_score": body_score,
                "body_improvements": body_improvements
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing ad copy: {str(e)}")
            return {
                "headline_score": 0.5,
                "headline_improvements": [],
                "body_score": 0.5,
                "body_improvements": []
            }
    
    def generate_a_b_variants(self, base_ad: Dict, industry: str, variant_count: int = 2) -> List[Dict]:
        """
        Generate A/B test variants based on patterns database insights.
        
        Args:
            base_ad: Base ad content
            industry: Industry category
            variant_count: Number of variants to generate
            
        Returns:
            List of variant ads
        """
        try:
            variants = []
            
            # Get industry patterns
            headline_patterns = self.patterns_db.get_headline_patterns(industry)
            copy_structures = self.patterns_db.get_copy_structures(industry)
            ctas = self.patterns_db.get_calls_to_action(industry)
            
            # Skip the highest performing pattern (used in base ad)
            alt_headline_patterns = headline_patterns[1:] if len(headline_patterns) > 1 else headline_patterns
            alt_copy_structures = copy_structures[1:] if len(copy_structures) > 1 else copy_structures
            alt_ctas = ctas[1:] if len(ctas) > 1 else ctas
            
            # Create variants with alternative patterns
            for i in range(variant_count):
                variant = base_ad.copy()
                variant['variant_id'] = f"variant_{i+1}"
                
                # Vary one major element in each variant
                variation_type = random.choice(['headline', 'copy', 'cta'])
                
                if variation_type == 'headline' and alt_headline_patterns:
                    pattern = random.choice(alt_headline_patterns)
                    variant['headline_pattern'] = pattern.get('pattern', '')
                    variant['headline_template'] = pattern.get('template', '')
                    variant['variation_description'] = f"Alternative headline pattern: {pattern.get('pattern', '')}"
                
                elif variation_type == 'copy' and alt_copy_structures:
                    pattern = random.choice(alt_copy_structures)
                    variant['copy_structure'] = pattern.get('pattern', '')
                    variant['variation_description'] = f"Alternative copy structure: {pattern.get('pattern', '')}"
                
                elif variation_type == 'cta' and alt_ctas:
                    pattern = random.choice(alt_ctas)
                    variant['cta_text'] = pattern.get('text', '')
                    variant['cta_position'] = pattern.get('optimal_position', 'end')
                    variant['variation_description'] = f"Alternative CTA: {pattern.get('text', '')}"
                
                variants.append(variant)
            
            return variants
            
        except Exception as e:
            self.logger.error(f"Error generating A/B variants: {str(e)}")
            return []
    
    def update_database_with_feedback(self, ad_data: Dict, performance_metrics: Dict, industry: str) -> bool:
        """
        Update the patterns database with feedback from ad performance.
        
        Args:
            ad_data: Ad content that was used
            performance_metrics: Actual performance metrics
            industry: Industry category
            
        Returns:
            Boolean indicating success
        """
        try:
            # Extract patterns from the ad
            headline_pattern = None
            if 'headline' in ad_data:
                headline_text = ad_data['headline']
                headline_pattern = self._categorize_headline_pattern(headline_text)
            
            copy_structure = None
            if 'body_text' in ad_data:
                body_text = ad_data['body_text']
                copy_structure = self._categorize_copy_structure(body_text)
            
            # Extract engagement metrics
            engagement_rate = performance_metrics.get('engagement_rate', 0)
            ctr = performance_metrics.get('ctr', 0)
            conversion_rate = performance_metrics.get('conversion_rate', 0)
            
            # Create pattern performance data
            headline_performance = {
                'average_engagement_rate': engagement_rate,
                'click_through_rate': ctr,
                'conversion_rate': conversion_rate
            }
            
            # Update the database if we have valid pattern and metrics
            if headline_pattern and engagement_rate > 0:
                pattern_id = f"{industry}_{headline_pattern}"
                self.patterns_db.update_patterns_with_feedback(
                    'headline', 
                    industry, 
                    pattern_id, 
                    headline_performance
                )
            
            if copy_structure and engagement_rate > 0:
                pattern_id = f"{industry}_{copy_structure}"
                self.patterns_db.update_patterns_with_feedback(
                    'copy', 
                    industry, 
                    pattern_id, 
                    headline_performance
                )
            
            # Save database updates
            self.patterns_db.save_database()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating database with feedback: {str(e)}")
            return False
    
    def _score_text_against_pattern(self, text: str, pattern_type: str) -> float:
        """Score how well a text matches a pattern type."""
        text_lower = text.lower()
        
        if pattern_type == 'question':
            return 1.0 if '?' in text else 0.0
            
        elif pattern_type == 'numbered_list':
            return 1.0 if re.match(r'^\d+\s+', text) else 0.0
            
        elif pattern_type == 'how_to':
            return 1.0 if text_lower.startswith('how to') else 0.0
            
        elif pattern_type == 'problem_solution':
            problem_indicators = ['tired of', 'sick of', 'frustrated with', 'problem']
            solution_indicators = ['solution', 'solves', 'fix', 'resolve']
            
            problem_score = any(indicator in text_lower for indicator in problem_indicators)
            solution_score = any(indicator in text_lower for indicator in solution_indicators)
            
            return 1.0 if problem_score and solution_score else 0.5 if problem_score or solution_score else 0.0
            
        elif pattern_type == 'announcement':
            announcement_indicators = ['introducing', 'new', 'announcing', 'finally']
            return 1.0 if any(indicator in text_lower for indicator in announcement_indicators) else 0.0
            
        # Default score for unknown patterns
        return 0.5
    
    def _score_text_against_structure(self, text: str, structure_type: str) -> float:
        """Score how well a text matches a copy structure type."""
        if structure_type == 'paragraph':
            sentences = re.split(r'[.!?]+', text)
            return 1.0 if len(sentences) > 1 and '•' not in text else 0.0
            
        elif structure_type == 'bullet_list':
            return 1.0 if '•' in text or '*' in text else 0.0
            
        elif structure_type == 'feature_benefit':
            feature_benefit_indicators = [' so ', ' which means ', ' that means ']
            return 1.0 if any(indicator in text.lower() for indicator in feature_benefit_indicators) else 0.0
            
        # Default score for unknown structures
        return 0.5
    
    def _categorize_headline_pattern(self, headline: str) -> str:
        """Categorize headline into a pattern type."""
        headline_lower = headline.lower()
        
        if '?' in headline:
            return 'question'
            
        elif re.match(r'^\d+\s+', headline):
            return 'numbered_list'
            
        elif headline_lower.startswith('how to'):
            return 'how_to'
            
        elif any(word in headline_lower for word in ['tired of', 'sick of', 'frustrated with', 'problem']):
            return 'problem_solution'
            
        elif any(word in headline_lower for word in ['introducing', 'new', 'announcing', 'finally']):
            return 'announcement'
            
        elif re.match(r'^[A-Z][a-z]+\s', headline) and ' your ' in headline_lower:
            return 'command'
            
        return 'undefined'
    
    def _categorize_copy_structure(self, copy_text: str) -> str:
        """Categorize copy text into a structure type."""
        if '•' in copy_text or '*' in copy_text:
            return 'bullet_list'
            
        sentences = re.split(r'[.!?]+', copy_text)
        if len(sentences) > 1:
            return 'paragraph'
            
        return 'short_form'

# Example usage if run directly
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize integration
    integration = PatternDatabaseIntegration()
    
    # Test prompt enhancement
    enhanced = integration.enhance_ad_prompt(
        "luxury watch with automatic movement", 
        "luxury", 
        "instagram", 
        "25-34"
    )
    
    print("ENHANCED PROMPT:")
    print(enhanced['enhanced_prompt'])
    
    # Test image prompt enhancement
    enhanced_image_prompt = integration.enhance_image_prompt(
        "luxury watch with leather strap",
        "luxury",
        "editorial_style",
        "instagram"
    )
    
    print("\nENHANCED IMAGE PROMPT:")
    print(enhanced_image_prompt)