"""
Responsive Text Scaling for Professional Ad Typography
Calculates optimal text sizes based on image dimensions and content
"""
import logging
import math
from typing import Dict, List, Tuple, Any, Optional, Union

class ResponsiveTextScaling:
    """
    Calculates optimal text sizes based on image dimensions and content.
    Ensures text is properly scaled for different display contexts.
    """
    
    def __init__(self):
        """Initialize the responsive text scaling engine."""
        self.logger = logging.getLogger(__name__)
        
        # Set baseline reference size
        self.reference_width = 1200  # Reference width for base scaling
        self.reference_height = 1200  # Reference height for base scaling
        
        # Set minimum and maximum font sizes
        self.min_sizes = {
            'headline': 28,
            'subheadline': 18,
            'body': 14,
            'cta': 16,
            'brand': 22
        }
        
        self.max_sizes = {
            'headline': 72,
            'subheadline': 42,
            'body': 32,
            'cta': 36,
            'brand': 48
        }
        
        # Initialize style-specific size ratios
        self.style_size_ratios = self._initialize_style_size_ratios()
        
        # Initialize industry-specific size adjustments
        self.industry_size_adjustments = self._initialize_industry_size_adjustments()
    
    def _initialize_style_size_ratios(self) -> Dict[str, Dict[str, float]]:
        """
        Initialize size ratios for different typography styles.
        
        Returns:
            Dictionary of style-specific size ratios
        """
        return {
            "modern": {
                "headline": 0.08,  # Relative to image height
                "subheadline": 0.04,
                "body": 0.032,
                "cta": 0.038,
                "brand": 0.05
            },
            
            "luxury": {
                "headline": 0.07,
                "subheadline": 0.035,
                "body": 0.03,
                "cta": 0.035,
                "brand": 0.045
            },
            
            "minimal": {
                "headline": 0.06,
                "subheadline": 0.035,
                "body": 0.03,
                "cta": 0.035,
                "brand": 0.04
            },
            
            "bold": {
                "headline": 0.09,
                "subheadline": 0.045,
                "body": 0.035,
                "cta": 0.04,
                "brand": 0.05
            },
            
            "elegant": {
                "headline": 0.065,
                "subheadline": 0.035,
                "body": 0.03,
                "cta": 0.035,
                "brand": 0.045
            },
            
            "playful": {
                "headline": 0.08,
                "subheadline": 0.04,
                "body": 0.035,
                "cta": 0.04,
                "brand": 0.05
            },
            
            "technical": {
                "headline": 0.075,
                "subheadline": 0.04,
                "body": 0.032,
                "cta": 0.038,
                "brand": 0.05
            },
            
            "dramatic": {
                "headline": 0.09,
                "subheadline": 0.04,
                "body": 0.032,
                "cta": 0.038,
                "brand": 0.05
            }
        }
    
    def _initialize_industry_size_adjustments(self) -> Dict[str, Dict[str, float]]:
        """
        Initialize industry-specific size adjustments.
        
        Returns:
            Dictionary of industry-specific size adjustments
        """
        return {
            "technology": {
                "headline": 1.0,  # Multiplier for the base size
                "subheadline": 1.0,
                "body": 1.0,
                "cta": 1.0,
                "brand": 1.0
            },
            
            "fashion": {
                "headline": 0.9,  # Fashion tends to use more elegant, slightly smaller type
                "subheadline": 0.95,
                "body": 0.9,
                "cta": 0.95,
                "brand": 1.1  # Bigger brand emphasis
            },
            
            "luxury": {
                "headline": 0.9,  # Luxury favors understated elegance
                "subheadline": 0.9,
                "body": 0.9,
                "cta": 0.9,
                "brand": 1.1  # Bigger brand emphasis
            },
            
            "food": {
                "headline": 1.1,  # Food ads often use bigger, more appetizing text
                "subheadline": 1.05,
                "body": 1.0,
                "cta": 1.05,
                "brand": 1.0
            },
            
            "automotive": {
                "headline": 1.1,  # Automotive tends toward bold headlines
                "subheadline": 1.0,
                "body": 0.95,
                "cta": 1.0,
                "brand": 1.0
            },
            
            "beauty": {
                "headline": 0.9,  # Beauty favors elegance and refinement
                "subheadline": 0.95,
                "body": 0.9,
                "cta": 0.95,
                "brand": 1.0
            },
            
            "finance": {
                "headline": 1.0,
                "subheadline": 1.0,
                "body": 1.1,  # Finance often has more detailed text
                "cta": 1.0,
                "brand": 1.0
            }
        }
    
    def calculate_text_sizes(self,
                            image_size: Tuple[int, int],
                            text_elements: Dict[str, str],
                            typography_style: Dict[str, Any]) -> Dict[str, int]:
        """
        Calculate optimal text sizes based on image dimensions and content.
        
        Args:
            image_size: (width, height) tuple of image dimensions
            text_elements: Dictionary with text content for each element
            typography_style: Typography style dictionary
            
        Returns:
            Dictionary with calculated sizes for each text element
        """
        try:
            # Extract image dimensions
            width, height = image_size
            
            # Get style name from typography style
            style = typography_style.get('style', 'modern')
            industry = typography_style.get('industry', None)
            brand_level = typography_style.get('brand_level', None)
            
            # Get size ratios for style
            size_ratios = self._get_size_ratios(style)
            
            # Get industry adjustments
            industry_adjustments = self._get_industry_adjustments(industry)
            
            # Calculate base sizes based on height
            base_sizes = {}
            for element in ['headline', 'subheadline', 'body', 'cta', 'brand']:
                # Apply style ratio
                ratio = size_ratios.get(element, 0.05)
                base_size = int(height * ratio)
                
                # Apply industry adjustment
                adjustment = industry_adjustments.get(element, 1.0)
                adjusted_size = int(base_size * adjustment)
                
                # Apply brand level adjustment
                level_adjustment = self._get_brand_level_adjustment(element, brand_level)
                adjusted_size = int(adjusted_size * level_adjustment)
                
                # Apply content-based adjustment
                element_key = element
                if element == 'body':
                    element_key = 'body_text'
                elif element == 'cta':
                    element_key = 'call_to_action'
                
                if element_key in text_elements:
                    content_adjustment = self._get_content_based_adjustment(
                        element, 
                        text_elements[element_key], 
                        width
                    )
                    adjusted_size = int(adjusted_size * content_adjustment)
                
                # Ensure size is within bounds
                final_size = max(self.min_sizes[element], min(adjusted_size, self.max_sizes[element]))
                
                # Store final size
                base_sizes[element] = final_size
            
            # Apply custom proportions if specified in typography style
            if 'text_proportions' in typography_style:
                custom_proportions = typography_style['text_proportions']
                
                # Get headline size as base
                headline_size = base_sizes['headline']
                
                # Adjust other sizes relative to headline
                for element, proportion in custom_proportions.items():
                    if element.endswith('_size') and element[:-5] in base_sizes:
                        elem = element[:-5]  # Remove '_size' suffix
                        base_sizes[elem] = int(headline_size * proportion / size_ratios['headline'])
                        
                        # Ensure size is within bounds
                        base_sizes[elem] = max(self.min_sizes[elem], min(base_sizes[elem], self.max_sizes[elem]))
            
            # Apply responsive scaling based on image size ratio
            reference_ratio = self.reference_width / self.reference_height
            image_ratio = width / height
            
            # Adjust sizes for extreme aspect ratios
            if abs(image_ratio - reference_ratio) > 0.3:
                # For wide images, reduce sizes
                if image_ratio > reference_ratio:
                    reduction_factor = 0.9 if image_ratio < 2 else 0.8
                    for element in base_sizes:
                        base_sizes[element] = int(base_sizes[element] * reduction_factor)
                
                # For tall images, increase headline but decrease others
                else:
                    base_sizes['headline'] = int(base_sizes['headline'] * 1.1)
                    for element in ['subheadline', 'body', 'cta']:
                        base_sizes[element] = int(base_sizes[element] * 0.9)
            
            return base_sizes
            
        except Exception as e:
            self.logger.error(f"Error calculating text sizes: {str(e)}")
            
            # Return default sizes
            return {
                'headline': 36,
                'subheadline': 24,
                'body': 18,
                'cta': 22,
                'brand': 28
            }
    
    def _get_size_ratios(self, style: str) -> Dict[str, float]:
        """
        Get size ratios for the specified style.
        
        Args:
            style: Typography style name
            
        Returns:
            Dictionary with size ratios for each element
        """
        style_lower = style.lower()
        
        # Direct match
        if style_lower in self.style_size_ratios:
            return self.style_size_ratios[style_lower]
        
        # Partial match
        for style_name, ratios in self.style_size_ratios.items():
            if style_name in style_lower or style_lower in style_name:
                return ratios
        
        # Map common style descriptors to styles
        style_mappings = {
            "sans": "modern",
            "sans-serif": "modern",
            "clean": "modern",
            "professional": "modern",
            
            "serif": "luxury",
            "high-end": "luxury",
            "premium": "luxury",
            "upscale": "luxury",
            
            "simple": "minimal",
            "minimalist": "minimal",
            "light": "minimal",
            
            "strong": "bold",
            "heavy": "bold",
            "powerful": "bold",
            "impactful": "bold",
            
            "classic": "elegant",
            "classy": "elegant",
            "refined": "elegant",
            "sophisticated": "elegant",
            
            "fun": "playful",
            "friendly": "playful",
            "casual": "playful",
            
            "tech": "technical",
            "functional": "technical",
            "efficient": "technical",
            "digital": "technical"
        }
        
        for descriptor, mapped_style in style_mappings.items():
            if descriptor in style_lower and mapped_style in self.style_size_ratios:
                return self.style_size_ratios[mapped_style]
        
        # Default to modern
        return self.style_size_ratios["modern"]
    
    def _get_industry_adjustments(self, industry: Optional[str]) -> Dict[str, float]:
        """
        Get industry-specific size adjustments.
        
        Args:
            industry: Industry name
            
        Returns:
            Dictionary with adjustment factors for each element
        """
        if not industry:
            return {element: 1.0 for element in ['headline', 'subheadline', 'body', 'cta', 'brand']}
            
        industry_lower = industry.lower()
        
        # Direct match
        if industry_lower in self.industry_size_adjustments:
            return self.industry_size_adjustments[industry_lower]
        
        # Partial match
        for industry_name, adjustments in self.industry_size_adjustments.items():
            if industry_name in industry_lower or industry_lower in industry_name:
                return adjustments
        
        # Map common industry descriptors to industries
        industry_mappings = {
            "tech": "technology",
            "software": "technology",
            "computer": "technology",
            "smartphone": "technology",
            "electronics": "technology",
            "digital": "technology",
            
            "clothes": "fashion",
            "apparel": "fashion",
            "clothing": "fashion",
            "shoes": "fashion",
            "wear": "fashion",
            "dress": "fashion",
            
            "high-end": "luxury",
            "premium": "luxury",
            "exclusive": "luxury",
            "watches": "luxury",
            "jewelry": "luxury",
            
            "restaurant": "food",
            "dining": "food",
            "cuisine": "food",
            "beverage": "food",
            "drink": "food",
            
            "car": "automotive",
            "vehicle": "automotive",
            "cars": "automotive",
            "auto": "automotive",
            
            "cosmetics": "beauty",
            "skincare": "beauty",
            "makeup": "beauty",
            "haircare": "beauty",
            "perfume": "beauty",
            
            "banking": "finance",
            "investment": "finance",
            "insurance": "finance"
        }
        
        for descriptor, mapped_industry in industry_mappings.items():
            if descriptor in industry_lower and mapped_industry in self.industry_size_adjustments:
                return self.industry_size_adjustments[mapped_industry]
        
        # Default to no adjustment
        return {element: 1.0 for element in ['headline', 'subheadline', 'body', 'cta', 'brand']}
    
    def _get_brand_level_adjustment(self, element: str, brand_level: Optional[str]) -> float:
        """
        Get adjustment factor based on brand level.
        
        Args:
            element: Element name
            brand_level: Brand level/positioning
            
        Returns:
            Adjustment factor
        """
        if not brand_level:
            return 1.0
            
        brand_level_lower = brand_level.lower()
        
        if 'luxury' in brand_level_lower or 'premium' in brand_level_lower or 'high-end' in brand_level_lower:
            # Luxury brands typically use more restrained typography
            if element == 'headline':
                return 0.9
            elif element == 'brand':
                return 1.1  # Bigger brand emphasis
            else:
                return 0.95
                
        elif 'budget' in brand_level_lower or 'affordable' in brand_level_lower or 'value' in brand_level_lower:
            # Value brands often use bigger, bolder typography
            if element == 'headline':
                return 1.1
            elif element == 'cta':
                return 1.1  # Stronger CTA
            else:
                return 1.0
                
        elif 'mid' in brand_level_lower or 'mainstream' in brand_level_lower:
            # Default for mid-level brands
            return 1.0
            
        # Default no adjustment
        return 1.0
    
    def _get_content_based_adjustment(self, element: str, text: str, width: int) -> float:
        """
        Get adjustment factor based on content length and target width.
        
        Args:
            element: Element name
            text: Element text content
            width: Image width
            
        Returns:
            Adjustment factor
        """
        # Calculate approximate chars that will fit at base size
        chars_per_line = width / 10  # Very rough approximation
        
        # Get content length
        content_length = len(text)
        
        # Different handling for each element type
        if element == 'headline':
            # Headlines should ideally be 1-2 lines
            words = text.split()
            word_count = len(words)
            
            if word_count <= 3:
                return 1.1  # Shorter headlines can be bigger
            elif word_count <= 6:
                return 1.0  # Standard size
            elif word_count <= 10:
                return 0.9  # Reduce size slightly
            else:
                return 0.8  # Reduce size more for longer headlines
                
        elif element == 'subheadline':
            # Subheadlines should ideally be 1-3 lines
            if content_length < chars_per_line * 0.7:
                return 1.05  # Very short can be slightly bigger
            elif content_length < chars_per_line * 1.5:
                return 1.0  # Standard size
            elif content_length < chars_per_line * 2.5:
                return 0.95  # Reduce size slightly
            else:
                return 0.9  # Reduce size more for longer subheadlines
                
        elif element == 'body':
            # Body text may need to be resized more aggressively
            if content_length < chars_per_line:
                return 1.0  # Standard size for short body
            elif content_length < chars_per_line * 2:
                return 0.95  # Slight reduction
            elif content_length < chars_per_line * 4:
                return 0.9  # More reduction
            else:
                return 0.85  # Significant reduction for long body text
                
        elif element == 'cta':
            # CTAs are typically short
            if content_length < 15:
                return 1.05  # Can be slightly bigger
            elif content_length < 25:
                return 1.0  # Standard size
            else:
                return 0.95  # Reduce for longer CTAs
                
        elif element == 'brand':
            # Brands are typically short
            if content_length < 10:
                return 1.05  # Can be slightly bigger
            else:
                return 1.0  # Standard size
        
        # Default no adjustment
        return 1.0
    
    def calculate_optimal_line_length(self,
                                    text: str,
                                    font_size: int,
                                    width: int,
                                    style: str = "modern") -> int:
        """
        Calculate optimal number of characters per line.
        
        Args:
            text: Text content
            font_size: Font size in pixels
            width: Available width in pixels
            style: Typography style
            
        Returns:
            Optimal characters per line
        """
        # Estimate average character width (in pixels) based on font size
        # This is a rough estimation and should be refined based on actual font metrics
        avg_char_width = font_size * 0.6
        
        # Calculate maximum characters that would fit in width
        max_chars = int(width / avg_char_width)
        
        # Apply style-specific adjustments
        style_adjustments = {
            "modern": 1.0,
            "luxury": 0.9,  # Luxury tends to use more whitespace
            "minimal": 0.85,  # Minimal uses lots of whitespace
            "bold": 1.1,  # Bold can be more compact
            "elegant": 0.9,
            "playful": 1.0,
            "technical": 1.0
        }
        
        adjustment = style_adjustments.get(style.lower(), 1.0)
        
        # Adjust max chars
        adjusted_max_chars = int(max_chars * adjustment)
        
        # Ensure reasonable limits (readability)
        min_chars = 30
        max_allowed_chars = 80
        
        return max(min_chars, min(adjusted_max_chars, max_allowed_chars))
    
    def calculate_text_wrap(self,
                          text: str,
                          font_size: int,
                          width: int,
                          element: str = "body",
                          style: str = "modern") -> List[str]:
        """
        Calculate text wrapping for optimal readability.
        
        Args:
            text: Text to wrap
            font_size: Font size in pixels
            width: Available width in pixels
            element: Element type (headline, subheadline, body, cta)
            style: Typography style
            
        Returns:
            List of wrapped text lines
        """
        # Different wrapping strategies for different elements
        if element == "headline":
            # Headlines should be as few lines as possible, preferring line breaks at natural points
            return self._wrap_headline(text, font_size, width, style)
            
        elif element == "subheadline":
            # Subheadlines can be a bit longer but still concise
            return self._wrap_subheadline(text, font_size, width, style)
            
        elif element == "body":
            # Body text needs to be wrapped for optimal reading
            return self._wrap_body_text(text, font_size, width, style)
            
        elif element == "cta":
            # CTAs should ideally be a single line
            return [text]
            
        else:
            # Default wrapping for other elements
            return self._simple_wrap(text, font_size, width)
    
    def _wrap_headline(self, text: str, font_size: int, width: int, style: str) -> List[str]:
        """
        Wrap headline text for optimal impact.
        
        Args:
            text: Headline text
            font_size: Font size in pixels
            width: Available width in pixels
            style: Typography style
            
        Returns:
            List of wrapped headline lines
        """
        # Calculate optimal line length
        optimal_chars = self.calculate_optimal_line_length(text, font_size, width, style)
        
        words = text.split()
        
        # For very short headlines, don't wrap
        if len(text) < optimal_chars * 0.8:
            return [text]
        
        # For longer headlines, try to create balanced lines
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            # Length of word plus space
            word_length = len(word) + 1
            
            # Check if adding this word would exceed optimal length
            if current_length + word_length > optimal_chars and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
            else:
                current_line.append(word)
                current_length += word_length
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
        
        # Cap headline at 3 lines maximum
        if len(lines) > 3:
            # Recombine and re-wrap to fewer lines
            rejoined = ' '.join(lines)
            words = rejoined.split()
            chars_per_line = len(rejoined) / 3
            
            lines = []
            current_line = []
            current_length = 0
            
            for word in words:
                word_length = len(word) + 1
                
                if current_length + word_length > chars_per_line and current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = word_length
                else:
                    current_line.append(word)
                    current_length += word_length
            
            # Add the last line
            if current_line:
                lines.append(' '.join(current_line))
        
        return lines
    
    def _wrap_subheadline(self, text: str, font_size: int, width: int, style: str) -> List[str]:
        """
        Wrap subheadline text for optimal readability.
        
        Args:
            text: Subheadline text
            font_size: Font size in pixels
            width: Available width in pixels
            style: Typography style
            
        Returns:
            List of wrapped subheadline lines
        """
        # Similar to headline but can be slightly longer
        optimal_chars = self.calculate_optimal_line_length(text, font_size, width, style)
        
        words = text.split()
        
        # For very short subheadlines, don't wrap
        if len(text) < optimal_chars:
            return [text]
        
        # For longer subheadlines, wrap normally
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1
            
            if current_length + word_length > optimal_chars and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
            else:
                current_line.append(word)
                current_length += word_length
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _wrap_body_text(self, text: str, font_size: int, width: int, style: str) -> List[str]:
        """
        Wrap body text for optimal readability.
        
        Args:
            text: Body text
            font_size: Font size in pixels
            width: Available width in pixels
            style: Typography style
            
        Returns:
            List of wrapped body text lines
        """
        # Body text should be wrapped for optimal reading width
        optimal_chars = self.calculate_optimal_line_length(text, font_size, width, style)
        
        # Split into paragraphs first
        paragraphs = text.split('\n')
        result = []
        
        for paragraph in paragraphs:
            # Further wrap each paragraph
            if not paragraph.strip():
                # Preserve empty lines
                result.append('')
                continue
                
            words = paragraph.split()
            current_line = []
            current_length = 0
            
            for word in words:
                word_length = len(word) + 1
                
                if current_length + word_length > optimal_chars and current_line:
                    result.append(' '.join(current_line))
                    current_line = [word]
                    current_length = word_length
                else:
                    current_line.append(word)
                    current_length += word_length
            
            # Add the last line of the paragraph
            if current_line:
                result.append(' '.join(current_line))
        
        return result
    
    def _simple_wrap(self, text: str, font_size: int, width: int) -> List[str]:
        """
        Apply simple text wrapping.
        
        Args:
            text: Text to wrap
            font_size: Font size in pixels
            width: Available width in pixels
            
        Returns:
            List of wrapped text lines
        """
        # Estimate characters per line
        chars_per_line = int(width / (font_size * 0.6))
        
        # Simple wrap by characters
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1
            
            if current_length + word_length > chars_per_line and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
            else:
                current_line.append(word)
                current_length += word_length
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines 
