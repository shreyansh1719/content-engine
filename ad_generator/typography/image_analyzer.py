"""
Image Analyzer for ad generation system.
Analyzes images for optimal text placement and treatment.
"""
import logging
from typing import Dict, Tuple, List, Any
from PIL import Image
import numpy as np

class ImageAnalyzer:
    """Analyzes images for optimal text placement and styling."""
    
    def __init__(self):
        """Initialize the image analyzer."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_brightness_map(self, image: Image.Image) -> Dict[str, float]:
        """
        Analyze image to create a brightness map for optimal text placement.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with brightness values for different regions
        """
        # Convert to grayscale
        gray = image.convert('L')
        width, height = gray.size
        
        # Divide the image into a 3x3 grid (Rule of Thirds)
        cell_width = width // 3
        cell_height = height // 3
        
        brightness_map = {}
        
        # Analyze each cell
        for row in range(3):
            for col in range(3):
                # Define cell boundaries
                left = col * cell_width
                upper = row * cell_height
                right = left + cell_width
                lower = upper + cell_height
                
                # Crop and calculate brightness
                cell = gray.crop((left, upper, right, lower))
                brightness = sum(list(cell.getdata())) / (cell_width * cell_height * 255)
                
                # Store in map
                position = f"{['top', 'middle', 'bottom'][row]}_{['left', 'center', 'right'][col]}"
                brightness_map[position] = brightness
        
        # Calculate overall brightness
        brightness_map['overall'] = sum(list(gray.getdata())) / (width * height * 255)
        
        return brightness_map
    
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
    
    def analyze_composition(self, image: Image.Image) -> Dict[str, Any]:
        """
        Analyze image composition for text placement.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with composition analysis
        """
        width, height = image.size
        
        # Calculate rule of thirds points
        third_h, third_w = height // 3, width // 3
        roi_points = [
            (third_w, third_h),
            (third_w * 2, third_h),
            (third_w, third_h * 2),
            (third_w * 2, third_h * 2)
        ]
        
        # Analyze brightness in key areas
        brightness_map = self.analyze_brightness_map(image)
        
        # Find best areas for text (where contrast would be highest)
        dark_areas = []
        light_areas = []
        
        for region, brightness in brightness_map.items():
            if region == 'overall':
                continue
                
            if brightness < 0.3:  # Dark area
                dark_areas.append(region)
            elif brightness > 0.7:  # Light area
                light_areas.append(region)
        
        # Determine if image has clear focal point
        # In a real system, this would use more sophisticated image analysis
        # For now, we'll make a simplified assumption based on brightness patterns
        has_clear_subject = len(dark_areas) > 0 and len(light_areas) > 0
        
        # Determine if image has high contrast areas
        brightness_values = [v for k, v in brightness_map.items() if k != 'overall']
        brightness_range = max(brightness_values) - min(brightness_values) if brightness_values else 0
        high_contrast = brightness_range > 0.5
        
        return {
            "brightness_map": brightness_map,
            "dark_areas": dark_areas,
            "light_areas": light_areas,
            "rule_of_thirds_points": roi_points,
            "has_clear_subject": has_clear_subject,
            "high_contrast": high_contrast,
            "composition_suggestion": self._suggest_text_placement(brightness_map, has_clear_subject)
        }
    
    def _suggest_text_placement(self, brightness_map: Dict[str, float], has_clear_subject: bool) -> str:
        """
        Suggest optimal text placement based on image analysis.
        
        Args:
            brightness_map: Brightness map of the image
            has_clear_subject: Whether image has a clear subject
            
        Returns:
            Suggested text placement style
        """
        overall = brightness_map.get('overall', 0.5)
        
        # For very bright images, suggest top or bottom overlay
        if overall > 0.8:
            # Find darkest region
            darkest = min([(k, v) for k, v in brightness_map.items() if k != 'overall'], key=lambda x: x[1])
            
            if 'top' in darkest[0]:
                return 'top_heavy'
            elif 'bottom' in darkest[0]:
                return 'bottom_heavy'
            else:
                return 'centered'
        
        # For very dark images, suggest lighter text in a standard layout
        elif overall < 0.2:
            return 'centered'
        
        # For images with moderate brightness
        else:
            if has_clear_subject:
                # If there's a clear subject, place text away from it
                # This is a simplified approach - real systems would use object detection
                return 'bottom_heavy'
            else:
                return 'centered'