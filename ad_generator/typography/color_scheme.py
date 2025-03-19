"""
Color Scheme Generator for ad generation system.
Creates professional color schemes for typography and accents.
"""
import logging
from typing import Dict, Tuple, List, Any
from PIL import Image, ImageColor
import re

class ColorSchemeGenerator:
    """Generates professional color schemes for advertising typography."""
    
    def __init__(self):
        """Initialize the color scheme generator."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize industry-specific color palettes
        self.industry_palettes = self._setup_industry_palettes()
    
    def _setup_industry_palettes(self) -> Dict[str, Dict[str, List[Tuple[int, int, int, int]]]]:
        """Setup default color palettes by industry."""
        return {
            "technology": {
                "primary": [(41, 128, 185, 255), (52, 152, 219, 255)],  # Blue tones
                "accent": [(46, 204, 113, 255), (26, 188, 156, 255)],  # Green/teal accents
                "text": [(255, 255, 255, 255), (52, 73, 94, 255)]  # White and dark blue
            },
            "luxury": {
                "primary": [(44, 62, 80, 255), (52, 73, 94, 255)],  # Dark blue/gray
                "accent": [(212, 172, 13, 255), (250, 219, 20, 255)],  # Gold accents
                "text": [(255, 255, 255, 255), (30, 30, 30, 255)]  # White and black
            },
            "beauty": {
                "primary": [(155, 89, 182, 255), (142, 68, 173, 255)],  # Purple tones
                "accent": [(241, 196, 15, 255), (243, 156, 18, 255)],  # Gold/yellow accents
                "text": [(255, 255, 255, 255), (52, 73, 94, 255)]  # White and dark blue
            },
            "fashion": {
                "primary": [(52, 73, 94, 255), (44, 62, 80, 255)],  # Dark blue/gray
                "accent": [(231, 76, 60, 255), (192, 57, 43, 255)],  # Red accents
                "text": [(255, 255, 255, 255), (30, 30, 30, 255)]  # White and black
            },
            "food": {
                "primary": [(211, 84, 0, 255), (243, 156, 18, 255)],  # Orange/yellow
                "accent": [(46, 204, 113, 255), (39, 174, 96, 255)],  # Green accents
                "text": [(255, 255, 255, 255), (44, 62, 80, 255)]  # White and dark
            }
        }
    
    def extract_dominant_colors(self, image: Image.Image, num_colors: int = 5) -> List[Tuple[int, int, int]]:
        """
        Extract dominant colors from image for color scheme coordination.
        
        Args:
            image: PIL Image object
            num_colors: Number of dominant colors to extract
            
        Returns:
            List of RGB color tuples
        """
        # Resize image for faster processing
        img_small = image.resize((100, 100), Image.Resampling.LANCZOS)
        
        # Convert to RGB if needed
        if img_small.mode != 'RGB':
            img_small = img_small.convert('RGB')
        
        # Get colors
        pixels = list(img_small.getdata())
        
        # Count occurrences of each color
        color_counts = {}
        for pixel in pixels:
            if pixel in color_counts:
                color_counts[pixel] += 1
            else:
                color_counts[pixel] = 1
        
        # Sort by frequency
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Return top colors
        return [color for color, count in sorted_colors[:num_colors]]
    
    def generate_color_scheme(self, image: Image.Image, scheme_type: str = None, 
                             industry: str = None) -> Dict[str, Any]:
        """
        Generate a professional color scheme based on image analysis.
        
        Args:
            image: PIL Image object
            scheme_type: Type of color scheme (e.g., "complementary", "monochromatic")
            industry: Industry category for specialized color schemes
            
        Returns:
            Dictionary with color scheme data
        """
        # Extract dominant colors
        dominant_colors = self.extract_dominant_colors(image)
        
        # Calculate average brightness
        brightness = self._calculate_image_brightness(image)
        
        # Default colors
        default_text = (255, 255, 255, 255)  # White text
        default_dark_text = (30, 30, 30, 255)  # Near black text
        default_accent = (41, 128, 185, 230)  # Professional blue
        
        # Determine text color based on image brightness
        if brightness > 0.5:
            text_color = default_dark_text
        else:
            text_color = default_text
        
        # Get industry-specific palette if available
        industry_palette = None
        if industry:
            industry_lower = industry.lower()
            for key, palette in self.industry_palettes.items():
                if key in industry_lower:
                    industry_palette = palette
                    break
        
        # Process scheme type
        if scheme_type:
            scheme_type_lower = scheme_type.lower()
            
            # Handle specific color scheme types
            if "blue" in scheme_type_lower:
                accent_color = (41, 128, 185, 230)  # Professional blue
            elif "red" in scheme_type_lower:
                accent_color = (192, 57, 43, 230)  # Professional red
            elif "green" in scheme_type_lower:
                accent_color = (39, 174, 96, 230)  # Professional green
            elif "purple" in scheme_type_lower:
                accent_color = (142, 68, 173, 230)  # Purple
            elif "gold" in scheme_type_lower or "yellow" in scheme_type_lower:
                accent_color = (241, 196, 15, 230)  # Gold
            elif "black" in scheme_type_lower:
                accent_color = (30, 30, 30, 230)  # Black
            elif "white" in scheme_type_lower:
                accent_color = (240, 240, 240, 230)  # White
            elif "monochromatic" in scheme_type_lower and dominant_colors:
                # Use first dominant color as base
                base_color = dominant_colors[0]
                accent_color = (*base_color, 230)
                # Adjust text color to ensure contrast
                text_color = self._ensure_text_contrast(base_color)
            elif "complementary" in scheme_type_lower and dominant_colors:
                # Generate complementary color from first dominant color
                base_color = dominant_colors[0]
                complementary = self._get_complementary_color(base_color)
                accent_color = (*complementary, 230)
                # Use dominant color to determine text color
                text_color = self._ensure_text_contrast(base_color)
            elif "#" in scheme_type_lower:
                # Extract hex color
                hex_match = re.search(r'#(?:[0-9a-fA-F]{3}){1,2}', scheme_type_lower)
                if hex_match:
                    hex_color = hex_match.group(0)
                    try:
                        rgb = ImageColor.getrgb(hex_color)
                        accent_color = (*rgb, 230)
                        # Adjust text color to ensure contrast
                        text_color = self._ensure_text_contrast(rgb)
                    except:
                        # Invalid hex, use default
                        accent_color = default_accent
                else:
                    accent_color = default_accent
            else:
                # Default to first dominant color or blue if no dominants
                if dominant_colors:
                    accent_color = (*dominant_colors[0], 230)
                else:
                    accent_color = default_accent
        elif industry_palette:
            # Use industry palette
            accent_color = industry_palette["accent"][0]
            # Only override text color if not already set based on brightness
            if industry_palette["text"]:
                text_override = industry_palette["text"][0] if brightness < 0.5 else industry_palette["text"][1]
                # Check if there's enough contrast with dominant colors
                if dominant_colors:
                    for color in dominant_colors[:2]:
                        if not self._has_sufficient_contrast(color, text_override[:3]):
                            # Keep the brightness-based text color
                            break
                    else:
                        # All checks passed, use the industry text color
                        text_color = text_override
        else:
            # Use dominant color with sufficient contrast
            if dominant_colors:
                for color in dominant_colors:
                    # Check if dominant color has enough contrast with brightness-based text color
                    if self._has_sufficient_contrast(color, text_color[:3]):
                        accent_color = (*color, 230)
                        break
                else:
                    # No dominant color with good contrast, use default
                    accent_color = default_accent
            else:
                accent_color = default_accent
        
        # Return the generated color scheme
        return {
            "text_color": text_color,
            "accent_color": accent_color,
            "dominant_colors": dominant_colors[:3] if dominant_colors else None,
            "brightness": brightness,
            "scheme_type": scheme_type or "auto-generated",
            "industry": industry
        }
    
    def _calculate_image_brightness(self, image: Image.Image) -> float:
        """
        Calculate the overall brightness of an image.
        
        Args:
            image: PIL Image object
            
        Returns:
            Float from 0 (darkest) to 1 (brightest)
        """
        # Convert to grayscale
        gray = image.convert('L')
        # Calculate average pixel value and normalize to 0-1
        return sum(list(gray.getdata())) / (gray.width * gray.height * 255)
    
    def _get_complementary_color(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        Get complementary color for a given RGB color.
        
        Args:
            color: RGB color tuple
            
        Returns:
            Complementary RGB color tuple
        """
        r, g, b = color
        return (255 - r, 255 - g, 255 - b)
    
    def _ensure_text_contrast(self, background_color: Tuple[int, int, int]) -> Tuple[int, int, int, int]:
        """
        Ensure text has sufficient contrast with background.
        
        Args:
            background_color: RGB background color
            
        Returns:
            RGBA text color with good contrast
        """
        r, g, b = background_color
        
        # Calculate relative luminance (simplified)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        
        # Use white text on dark backgrounds, black text on light backgrounds
        if luminance < 0.5:
            return (255, 255, 255, 255)  # White text
        else:
            return (30, 30, 30, 255)  # Near black text
    
    def _has_sufficient_contrast(self, color1: Tuple[int, int, int], 
                               color2: Tuple[int, int, int]) -> bool:
        """
        Check if two colors have sufficient contrast for text readability.
        
        Args:
            color1: First RGB color
            color2: Second RGB color
            
        Returns:
            True if contrast is sufficient, False otherwise
        """
        # Calculate relative luminance (simplified)
        l1 = (0.299 * color1[0] + 0.587 * color1[1] + 0.114 * color1[2]) / 255
        l2 = (0.299 * color2[0] + 0.587 * color2[1] + 0.114 * color2[2]) / 255
        
        # Calculate contrast ratio (simplified)
        if l1 > l2:
            ratio = (l1 + 0.05) / (l2 + 0.05)
        else:
            ratio = (l2 + 0.05) / (l1 + 0.05)
        
        # WCAG recommends a ratio of at least 4.5:1 for normal text
        return ratio >= 4.5