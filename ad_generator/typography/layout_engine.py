"""
Text Layout Engine for Professional Ad Typography
Provides advanced layout algorithms for ideal text placement
"""
import logging
import math
from typing import Dict, List, Tuple, Any, Optional, Union
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

class TextLayoutEngine:
    """
    Engine for calculating optimal text placement in advertisements.
    Uses image analysis to determine ideal text placement.
    """
    
    def __init__(self):
        """Initialize the text layout engine."""
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize layout strategies
        self.layout_strategies = self._initialize_layout_strategies()
    
    def _initialize_layout_strategies(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize layout strategies for different design approaches.
        
        Returns:
            Dictionary of layout strategies
        """
        return {
            "centered": {
                "description": "Centered text with balanced spacing",
                "elements": {
                    "headline": {"x_rel": 0.5, "y_rel": 0.3, "alignment": "center"},
                    "subheadline": {"x_rel": 0.5, "y_rel": 0.4, "alignment": "center"},
                    "body": {"x_rel": 0.5, "y_rel": 0.55, "alignment": "center"},
                    "cta": {"x_rel": 0.5, "y_rel": 0.75, "alignment": "center"},
                    "brand": {"x_rel": 0.5, "y_rel": 0.15, "alignment": "center"}
                },
                "spacing": {
                    "headline_to_subheadline": 0.03,  # % of image height
                    "subheadline_to_body": 0.05,
                    "body_to_cta": 0.08
                }
            },
            
            "left_aligned": {
                "description": "Left-aligned text with margin",
                "elements": {
                    "headline": {"x_rel": 0.1, "y_rel": 0.3, "alignment": "left"},
                    "subheadline": {"x_rel": 0.1, "y_rel": 0.4, "alignment": "left"},
                    "body": {"x_rel": 0.1, "y_rel": 0.55, "alignment": "left"},
                    "cta": {"x_rel": 0.1, "y_rel": 0.75, "alignment": "left"},
                    "brand": {"x_rel": 0.1, "y_rel": 0.15, "alignment": "left"}
                },
                "spacing": {
                    "headline_to_subheadline": 0.03,
                    "subheadline_to_body": 0.05,
                    "body_to_cta": 0.08
                }
            },
            
            "right_aligned": {
                "description": "Right-aligned text with margin",
                "elements": {
                    "headline": {"x_rel": 0.9, "y_rel": 0.3, "alignment": "right"},
                    "subheadline": {"x_rel": 0.9, "y_rel": 0.4, "alignment": "right"},
                    "body": {"x_rel": 0.9, "y_rel": 0.55, "alignment": "right"},
                    "cta": {"x_rel": 0.9, "y_rel": 0.75, "alignment": "right"},
                    "brand": {"x_rel": 0.9, "y_rel": 0.15, "alignment": "right"}
                },
                "spacing": {
                    "headline_to_subheadline": 0.03,
                    "subheadline_to_body": 0.05,
                    "body_to_cta": 0.08
                }
            },
            
            "top_centered": {
                "description": "Text centered at the top of the image",
                "elements": {
                    "headline": {"x_rel": 0.5, "y_rel": 0.15, "alignment": "center"},
                    "subheadline": {"x_rel": 0.5, "y_rel": 0.22, "alignment": "center"},
                    "body": {"x_rel": 0.5, "y_rel": 0.32, "alignment": "center"},
                    "cta": {"x_rel": 0.5, "y_rel": 0.45, "alignment": "center"},
                    "brand": {"x_rel": 0.5, "y_rel": 0.07, "alignment": "center"}
                },
                "spacing": {
                    "headline_to_subheadline": 0.03,
                    "subheadline_to_body": 0.04,
                    "body_to_cta": 0.05
                }
            },
            
            "bottom_centered": {
                "description": "Text centered at the bottom of the image",
                "elements": {
                    "headline": {"x_rel": 0.5, "y_rel": 0.65, "alignment": "center"},
                    "subheadline": {"x_rel": 0.5, "y_rel": 0.72, "alignment": "center"},
                    "body": {"x_rel": 0.5, "y_rel": 0.8, "alignment": "center"},
                    "cta": {"x_rel": 0.5, "y_rel": 0.9, "alignment": "center"},
                    "brand": {"x_rel": 0.5, "y_rel": 0.55, "alignment": "center"}
                },
                "spacing": {
                    "headline_to_subheadline": 0.03,
                    "subheadline_to_body": 0.03,
                    "body_to_cta": 0.04
                }
            },
            
            "bottom_left": {
                "description": "Text positioned in the bottom left corner",
                "elements": {
                    "headline": {"x_rel": 0.1, "y_rel": 0.65, "alignment": "left"},
                    "subheadline": {"x_rel": 0.1, "y_rel": 0.72, "alignment": "left"},
                    "body": {"x_rel": 0.1, "y_rel": 0.8, "alignment": "left"},
                    "cta": {"x_rel": 0.1, "y_rel": 0.9, "alignment": "left"},
                    "brand": {"x_rel": 0.1, "y_rel": 0.55, "alignment": "left"}
                },
                "spacing": {
                    "headline_to_subheadline": 0.03,
                    "subheadline_to_body": 0.03,
                    "body_to_cta": 0.04
                }
            },
            
            "bottom_right": {
                "description": "Text positioned in the bottom right corner",
                "elements": {
                    "headline": {"x_rel": 0.9, "y_rel": 0.65, "alignment": "right"},
                    "subheadline": {"x_rel": 0.9, "y_rel": 0.72, "alignment": "right"},
                    "body": {"x_rel": 0.9, "y_rel": 0.8, "alignment": "right"},
                    "cta": {"x_rel": 0.9, "y_rel": 0.9, "alignment": "right"},
                    "brand": {"x_rel": 0.9, "y_rel": 0.55, "alignment": "right"}
                },
                "spacing": {
                    "headline_to_subheadline": 0.03,
                    "subheadline_to_body": 0.03,
                    "body_to_cta": 0.04
                }
            },
            
            "split_layout": {
                "description": "Text split between top and bottom",
                "elements": {
                    "headline": {"x_rel": 0.5, "y_rel": 0.15, "alignment": "center"},
                    "subheadline": {"x_rel": 0.5, "y_rel": 0.22, "alignment": "center"},
                    "body": {"x_rel": 0.5, "y_rel": 0.8, "alignment": "center"},
                    "cta": {"x_rel": 0.5, "y_rel": 0.9, "alignment": "center"},
                    "brand": {"x_rel": 0.5, "y_rel": 0.07, "alignment": "center"}
                },
                "spacing": {
                    "headline_to_subheadline": 0.03,
                    "subheadline_to_body": 0.5,  # Large gap intentionally
                    "body_to_cta": 0.04
                }
            },
            
            "text_overlay": {
                "description": "Text overlays center of image with semi-transparent background",
                "elements": {
                    "headline": {"x_rel": 0.5, "y_rel": 0.45, "alignment": "center"},
                    "subheadline": {"x_rel": 0.5, "y_rel": 0.52, "alignment": "center"},
                    "body": {"x_rel": 0.5, "y_rel": 0.6, "alignment": "center"},
                    "cta": {"x_rel": 0.5, "y_rel": 0.7, "alignment": "center"},
                    "brand": {"x_rel": 0.5, "y_rel": 0.37, "alignment": "center"}
                },
                "background": {
                    "enabled": True,
                    "color": (0, 0, 0, 150),
                    "padding": 0.1,  # Percent of height
                    "y_start": 0.35,
                    "y_end": 0.75
                },
                "spacing": {
                    "headline_to_subheadline": 0.03,
                    "subheadline_to_body": 0.03,
                    "body_to_cta": 0.04
                }
            },
            
            "dynamic": {
                "description": "Dynamic placement based on image content",
                # Default positions will be overridden by analysis
                "elements": {
                    "headline": {"x_rel": 0.5, "y_rel": 0.3, "alignment": "center"},
                    "subheadline": {"x_rel": 0.5, "y_rel": 0.4, "alignment": "center"},
                    "body": {"x_rel": 0.5, "y_rel": 0.55, "alignment": "center"},
                    "cta": {"x_rel": 0.5, "y_rel": 0.75, "alignment": "center"},
                    "brand": {"x_rel": 0.5, "y_rel": 0.15, "alignment": "center"}
                },
                "spacing": {
                    "headline_to_subheadline": 0.03,
                    "subheadline_to_body": 0.05,
                    "body_to_cta": 0.08
                }
            }
        }
    
    def analyze_image(self, image: Image.Image) -> Dict[str, Any]:
        """
        Analyze image to determine optimal text placement.
        
        Args:
            image: Image to analyze
            
        Returns:
            Analysis results
        """
        try:
            # Calculate brightness map
            brightness_map = self._calculate_brightness_map(image)
            
            # Find subject position
            subject_position = self._detect_subject_position(image)
            
            # Analyze edges for visual complexity
            edge_complexity = self._analyze_edge_complexity(image)
            
            # Determine rule of thirds points
            rule_of_thirds = self._calculate_rule_of_thirds(image.size)
            
            # Find ideal text areas
            ideal_text_areas = self._find_ideal_text_areas(brightness_map, subject_position, edge_complexity)
            
            # Return analysis results
            return {
                "brightness_map": brightness_map,
                "subject_position": subject_position,
                "edge_complexity": edge_complexity,
                "rule_of_thirds": rule_of_thirds,
                "ideal_text_areas": ideal_text_areas,
                "overall_brightness": brightness_map.get("overall", 0.5)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing image: {str(e)}")
            # Return default analysis
            return {
                "brightness_map": {"overall": 0.5},
                "subject_position": {"x": 0.5, "y": 0.5},
                "edge_complexity": 0.5,
                "rule_of_thirds": self._calculate_rule_of_thirds((1000, 1000)),
                "ideal_text_areas": ["center"],
                "overall_brightness": 0.5
            }
    
    def _calculate_brightness_map(self, image: Image.Image) -> Dict[str, float]:
        """
        Calculate brightness map for the image.
        
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
                brightness = float(np.array(cell).sum()) / (cell_width * cell_height * 255)
                
                # Store in map
                position = f"{['top', 'middle', 'bottom'][row]}_{['left', 'center', 'right'][col]}"
                brightness_map[position] = brightness
        
        # Calculate overall brightness
        brightness_map['overall'] = float(np.array(gray).sum()) / (width * height * 255)
        
        return brightness_map
    
    def _detect_subject_position(self, image: Image.Image) -> Dict[str, float]:
        """
        Detect the main subject position in the image.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with normalized subject position {x, y}
        """
        try:
            # Convert to grayscale
            gray = image.convert('L')
            width, height = gray.size
            
            # Apply edge detection
            edges = gray.filter(ImageFilter.FIND_EDGES)
            
            # Find strongest edges
            edge_data = list(np.array(edges).flatten())
            strongest_edges = []
            threshold = sum(edge_data) / len(edge_data) * 1.5  # Adjust threshold as needed
            
            for y in range(height):
                for x in range(width):
                    pixel_value = edges.getpixel((x, y))
                    if pixel_value > threshold:
                        strongest_edges.append((x, y))
            
            # Calculate center of strongest edges
            if strongest_edges:
                center_x = sum(x for x, y in strongest_edges) / len(strongest_edges)
                center_y = sum(y for x, y in strongest_edges) / len(strongest_edges)
                
                # Normalize to 0-1 range
                normalized_x = center_x / width
                normalized_y = center_y / height
                
                return {
                    "x": normalized_x,
                    "y": normalized_y
                }
            
            # Default to center if no strong edges
            return {"x": 0.5, "y": 0.5}
            
        except Exception as e:
            self.logger.error(f"Error detecting subject position: {str(e)}")
            return {"x": 0.5, "y": 0.5}
    
    def _analyze_edge_complexity(self, image: Image.Image) -> float:
        """
        Analyze edge complexity to determine visual complexity.
        
        Args:
            image: PIL Image object
            
        Returns:
            Complexity score from 0.0 (simple) to 1.0 (complex)
        """
        try:
            # Convert to grayscale
            gray = image.convert('L')
            
            # Apply edge detection
            edges = gray.filter(ImageFilter.FIND_EDGES)
            
            # Calculate edge density
            edge_data = list(np.array(edges).flatten())
            edge_sum = sum(edge_data)
            max_possible = 255 * len(edge_data)
            
            # Normalize to 0-1 range
            complexity = min(1.0, edge_sum / max_possible * 10)  # Scale for reasonable values
            
            return complexity
            
        except Exception as e:
            self.logger.error(f"Error analyzing edge complexity: {str(e)}")
            return 0.5
    
    def _calculate_rule_of_thirds(self, size: Tuple[int, int]) -> Dict[str, List[Tuple[int, int]]]:
        """
        Calculate rule of thirds points for the image.
        
        Args:
            size: Image size (width, height)
            
        Returns:
            Dictionary with rule of thirds points
        """
        width, height = size
        
        # Calculate third points
        horizontal = [width // 3, width * 2 // 3]
        vertical = [height // 3, height * 2 // 3]
        
        # Calculate intersections
        intersections = []
        for x in horizontal:
            for y in vertical:
                intersections.append((x, y))
        
        return {
            "horizontal": horizontal,
            "vertical": vertical,
            "intersections": intersections
        }
    
    def _find_ideal_text_areas(self, brightness_map: Dict[str, float],
                              subject_position: Dict[str, float],
                              edge_complexity: float) -> List[str]:
        """
        Find ideal areas for text placement based on image analysis.
        
        Args:
            brightness_map: Brightness map of the image
            subject_position: Position of the main subject
            edge_complexity: Edge complexity score
            
        Returns:
            List of areas suitable for text
        """
        ideal_areas = []
        
        # Determine if image is bright or dark overall
        overall_brightness = brightness_map.get("overall", 0.5)
        is_bright = overall_brightness > 0.5
        
        # Find areas with good contrast
        for position, brightness in brightness_map.items():
            if position == "overall":
                continue
                
            # Check for adequate contrast
            if (is_bright and brightness < 0.4) or (not is_bright and brightness > 0.6):
                ideal_areas.append(position)
        
        # If no ideal areas found, use areas away from subject
        if not ideal_areas:
            # Determine subject area
            x, y = subject_position["x"], subject_position["y"]
            
            # Determine subject's grid position
            subject_row = 0 if y < 0.33 else 1 if y < 0.66 else 2
            subject_col = 0 if x < 0.33 else 1 if x < 0.66 else 2
            
            # Find positions away from subject
            subject_pos = f"{['top', 'middle', 'bottom'][subject_row]}_{['left', 'center', 'right'][subject_col]}"
            
            # Add areas on opposite side
            opposite_row = 2 - subject_row
            opposite_col = 2 - subject_col
            
            opposite_pos = f"{['top', 'middle', 'bottom'][opposite_row]}_{['left', 'center', 'right'][opposite_col]}"
            ideal_areas.append(opposite_pos)
            
            # Add other positions not containing the subject
            for row in range(3):
                for col in range(3):
                    pos = f"{['top', 'middle', 'bottom'][row]}_{['left', 'center', 'right'][col]}"
                    if pos != subject_pos and pos != opposite_pos:
                        ideal_areas.append(pos)
        
        # Prioritize areas based on common ad layout patterns
        if edge_complexity > 0.7:
            # For complex images, prefer simpler areas
            if "top_center" in ideal_areas or "bottom_center" in ideal_areas:
                return ["top_center" if "top_center" in ideal_areas else "bottom_center"]
        
        return ideal_areas
    
    def calculate_text_positions(self,
                               image: Image.Image,
                               text_elements: Dict[str, str],
                               fonts: Dict[str, ImageFont.FreeTypeFont],
                               text_sizes: Dict[str, int],
                               image_analysis: Dict[str, Any],
                               typography_style: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Calculate optimal text positions based on image analysis and typography style.
        
        Args:
            image: Image to place text on
            text_elements: Dictionary with text content for each element
            fonts: Dictionary with fonts for each element
            text_sizes: Dictionary with text sizes for each element
            image_analysis: Image analysis results
            typography_style: Typography style dictionary
            
        Returns:
            Dictionary with positions and properties for each text element
        """
        try:
            # Get image dimensions
            width, height = image.size
            
            # Get layout strategy based on typography style
            layout_name = typography_style.get("text_placement", "centered")
            
            # Default to dynamic for high-complexity images
            if image_analysis.get("edge_complexity", 0) > 0.8:
                layout_name = "dynamic"
            
            # Get layout strategy
            layout = self.layout_strategies.get(layout_name, self.layout_strategies["centered"])
            
            # For dynamic layout, adjust based on image analysis
            if layout_name == "dynamic":
                layout = self._create_dynamic_layout(image_analysis, layout)
            
            # Calculate positions for all text elements
            positions = {}
            
            # Get text elements for positioning
            elements = {
                'headline': text_elements.get('headline', ''),
                'subheadline': text_elements.get('subheadline', ''),
                'body': text_elements.get('body_text', ''),
                'cta': text_elements.get('call_to_action', ''),
                'brand': text_elements.get('brand_name', '')
            }
            
            # Calculate initial positions based on layout strategy
            for element_name, text in elements.items():
                if not text:
                    continue
                    
                # Get element settings from layout
                element_settings = layout.get("elements", {}).get(element_name, {})
                
                if not element_settings:
                    continue
                
                # Calculate position
                x_rel = element_settings.get("x_rel", 0.5)
                y_rel = element_settings.get("y_rel", 0.5)
                alignment = element_settings.get("alignment", "center")
                
                # Convert to absolute position
                x = int(x_rel * width)
                y = int(y_rel * height)
                
                # Get text dimensions if font is available
                dimensions = {}
                if element_name in fonts:
                    font = fonts[element_name]
                    text_width, text_height = self._get_text_dimensions(text, font)
                    dimensions = {
                        "width": text_width,
                        "height": text_height
                    }
                
                # Add to positions
                positions[element_name] = {
                    "position": (x, y),
                    "alignment": alignment,
                    "dimensions": dimensions
                }
            
            # Adjust positions based on spacing settings
            positions = self._adjust_positions_for_spacing(
                positions, 
                layout.get("spacing", {}), 
                height
            )
            
            # Include background if specified
            if "background" in layout:
                positions["background"] = layout["background"]
            
            # Check for text overlaps and resolve
            positions = self._resolve_text_overlaps(positions, width, height)
            
            return positions
            
        except Exception as e:
            self.logger.error(f"Error calculating text positions: {str(e)}")
            # Return default positions
            return self._get_default_positions(width, height, text_elements)
    
    def _create_dynamic_layout(self, image_analysis: Dict[str, Any], base_layout: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create dynamic layout based on image analysis.
        
        Args:
            image_analysis: Image analysis results
            base_layout: Base layout to customize
            
        Returns:
            Custom layout dictionary
        """
        # Create copy of base layout
        layout = {
            "description": "Custom dynamic layout",
            "elements": base_layout.get("elements", {}).copy(),
            "spacing": base_layout.get("spacing", {}).copy()
        }
        
        # Get subject position
        subject_x = image_analysis.get("subject_position", {}).get("x", 0.5)
        subject_y = image_analysis.get("subject_position", {}).get("y", 0.5)
        
        # Get brightness map
        brightness_map = image_analysis.get("brightness_map", {})
        overall_brightness = brightness_map.get("overall", 0.5)
        
        # Get ideal text areas
        ideal_areas = image_analysis.get("ideal_text_areas", ["center"])
        
        # Adjust layout based on subject position
        if subject_y < 0.4:
            # Subject in top part, place text at bottom
            self._modify_layout_for_bottom(layout)
        elif subject_y > 0.6:
            # Subject in bottom part, place text at top
            self._modify_layout_for_top(layout)
        elif subject_x < 0.4:
            # Subject on left, place text on right
            self._modify_layout_for_right(layout)
        elif subject_x > 0.6:
            # Subject on right, place text on left
            self._modify_layout_for_left(layout)
        else:
            # Subject in center, use most contrasting area
            self._modify_layout_based_on_brightness(layout, brightness_map)
        
        # Check if we need a background panel for text
        if overall_brightness > 0.7 or overall_brightness < 0.3:
            # Add semi-transparent background for better readability
            layout["background"] = {
                "enabled": True,
                "color": (0, 0, 0, 180) if overall_brightness > 0.7 else (255, 255, 255, 180),
                "padding": 0.05,
                "y_start": layout["elements"]["headline"]["y_rel"] - 0.05,
                "y_end": layout["elements"]["cta"]["y_rel"] + 0.05
            }
        
        return layout
    
    def _modify_layout_for_bottom(self, layout: Dict[str, Any]) -> None:
        """
        Modify layout to place text at bottom.
        
        Args:
            layout: Layout to modify
        """
        elements = layout["elements"]
        
        # Update element positions
        elements["headline"]["y_rel"] = 0.65
        elements["subheadline"]["y_rel"] = 0.72
        elements["body"]["y_rel"] = 0.8
        elements["cta"]["y_rel"] = 0.9
        elements["brand"]["y_rel"] = 0.55
    
    def _modify_layout_for_top(self, layout: Dict[str, Any]) -> None:
        """
        Modify layout to place text at top.
        
        Args:
            layout: Layout to modify
        """
        elements = layout["elements"]
        
        # Update element positions
        elements["headline"]["y_rel"] = 0.15
        elements["subheadline"]["y_rel"] = 0.22
        elements["body"]["y_rel"] = 0.32
        elements["cta"]["y_rel"] = 0.45
        elements["brand"]["y_rel"] = 0.07
    
    def _modify_layout_for_left(self, layout: Dict[str, Any]) -> None:
        """
        Modify layout to place text on left.
        
        Args:
            layout: Layout to modify
        """
        elements = layout["elements"]
        
        # Update element positions and alignment
        for element in elements.values():
            element["x_rel"] = 0.1
            element["alignment"] = "left"
    
    def _modify_layout_for_right(self, layout: Dict[str, Any]) -> None:
        """
        Modify layout to place text on right.
        
        Args:
            layout: Layout to modify
        """
        elements = layout["elements"]
        
        # Update element positions and alignment
        for element in elements.values():
            element["x_rel"] = 0.9
            element["alignment"] = "right"
    
    def _modify_layout_based_on_brightness(self, layout: Dict[str, Any], brightness_map: Dict[str, float]) -> None:
        """
        Modify layout based on brightness map.
        
        Args:
            layout: Layout to modify
            brightness_map: Brightness map of the image
        """
        # Find darkest and brightest areas
        min_brightness = 1.0
        max_brightness = 0.0
        darkest_area = "bottom_center"
        brightest_area = "top_center"
        
        for area, brightness in brightness_map.items():
            if area == "overall":
                continue
                
            if brightness < min_brightness:
                min_brightness = brightness
                darkest_area = area
                
            if brightness > max_brightness:
                max_brightness = brightness
                brightest_area = area
        
        # Place text in area with good contrast
        overall_brightness = brightness_map.get("overall", 0.5)
        
        if overall_brightness > 0.7:
            # Bright image, place text in darkest area
            self._modify_layout_for_area(layout, darkest_area)
        elif overall_brightness < 0.3:
            # Dark image, place text in brightest area
            self._modify_layout_for_area(layout, brightest_area)
        else:
            # Medium brightness, use top or bottom based on brightness pattern
            top_avg = (brightness_map.get("top_left", 0.5) + 
                       brightness_map.get("top_center", 0.5) + 
                       brightness_map.get("top_right", 0.5)) / 3
                       
            bottom_avg = (brightness_map.get("bottom_left", 0.5) + 
                          brightness_map.get("bottom_center", 0.5) + 
                          brightness_map.get("bottom_right", 0.5)) / 3
                          
            if top_avg < bottom_avg:
                # Top is darker, place text there
                self._modify_layout_for_top(layout)
            else:
                # Bottom is darker, place text there
                self._modify_layout_for_bottom(layout)
    
    def _modify_layout_for_area(self, layout: Dict[str, Any], area: str) -> None:
        """
        Modify layout to place text in specified area.
        
        Args:
            layout: Layout to modify
            area: Area name (e.g., 'top_left', 'bottom_right')
        """
        # Parse area name
        parts = area.split('_')
        if len(parts) != 2:
            return
            
        vertical, horizontal = parts
        
        # Determine vertical position
        if vertical == "top":
            self._modify_layout_for_top(layout)
        elif vertical == "bottom":
            self._modify_layout_for_bottom(layout)
        
        # Determine horizontal position
        if horizontal == "left":
            self._modify_layout_for_left(layout)
        elif horizontal == "right":
            self._modify_layout_for_right(layout)
    
    def _adjust_positions_for_spacing(self,
                                    positions: Dict[str, Dict[str, Any]],
                                    spacing: Dict[str, float],
                                    height: int) -> Dict[str, Dict[str, Any]]:
        """
        Adjust text positions based on specified spacing.
        
        Args:
            positions: Text element positions
            spacing: Spacing settings
            height: Image height
            
        Returns:
            Adjusted positions
        """
        # Get positions that need adjustment
        headline_pos = positions.get('headline', {}).get('position', None)
        subheadline_pos = positions.get('subheadline', {}).get('position', None)
        body_pos = positions.get('body', {}).get('position', None)
        cta_pos = positions.get('cta', {}).get('position', None)
        
        # Get dimensions
        headline_dims = positions.get('headline', {}).get('dimensions', {})
        headline_height = headline_dims.get('height', 0)
        
        subheadline_dims = positions.get('subheadline', {}).get('dimensions', {})
        subheadline_height = subheadline_dims.get('height', 0)
        
        body_dims = positions.get('body', {}).get('dimensions', {})
        body_height = body_dims.get('height', 0)
        
        # Adjust positions based on dimensions and specified spacing
        # Only adjust if both elements are present
        
        # Adjust subheadline position based on headline
        if headline_pos and subheadline_pos and 'headline_to_subheadline' in spacing:
            headline_x, headline_y = headline_pos
            subheadline_x, _ = subheadline_pos
            
            spacing_px = int(spacing['headline_to_subheadline'] * height)
            new_y = headline_y + headline_height + spacing_px
            positions['subheadline']['position'] = (subheadline_x, new_y)
        
        # Adjust body position based on subheadline
        if subheadline_pos and body_pos and 'subheadline_to_body' in spacing:
            subheadline_x, subheadline_y = subheadline_pos
            body_x, _ = body_pos
            
            spacing_px = int(spacing['subheadline_to_body'] * height)
            new_y = subheadline_y + subheadline_height + spacing_px
            positions['body']['position'] = (body_x, new_y)
        
        # Adjust CTA position based on body
        if body_pos and cta_pos and 'body_to_cta' in spacing:
            body_x, body_y = body_pos
            cta_x, _ = cta_pos
            
            spacing_px = int(spacing['body_to_cta'] * height)
            new_y = body_y + body_height + spacing_px
            positions['cta']['position'] = (cta_x, new_y)
        
        return positions
    
    def _resolve_text_overlaps(self,
                             positions: Dict[str, Dict[str, Any]],
                             width: int,
                             height: int) -> Dict[str, Dict[str, Any]]:
        """
        Resolve overlaps between text elements.
        
        Args:
            positions: Text element positions
            width: Image width
            height: Image height
            
        Returns:
            Adjusted positions
        """
        # Calculate bounding boxes for all elements
        bounding_boxes = {}
        
        for element_name, element_data in positions.items():
            if element_name == "background":
                continue
                
            position = element_data.get('position')
            dimensions = element_data.get('dimensions', {})
            alignment = element_data.get('alignment', 'center')
            
            if not position or not dimensions:
                continue
                
            x, y = position
            element_width = dimensions.get('width', 0)
            element_height = dimensions.get('height', 0)
            
            # Calculate bounding box based on alignment
            if alignment == 'center':
                left = x - element_width // 2
                right = x + element_width // 2
            elif alignment == 'left':
                left = x
                right = x + element_width
            else:  # right
                left = x - element_width
                right = x
                
            top = y
            bottom = y + element_height
            
            bounding_boxes[element_name] = (left, top, right, bottom)
        
        # Check for overlaps
        overlaps = []
        elements = list(bounding_boxes.keys())
        
        for i in range(len(elements)):
            for j in range(i + 1, len(elements)):
                element1 = elements[i]
                element2 = elements[j]
                
                box1 = bounding_boxes[element1]
                box2 = bounding_boxes[element2]
                
                if (box1[0] < box2[2] and box1[2] > box2[0] and
                    box1[1] < box2[3] and box1[3] > box2[1]):
                    overlaps.append((element1, element2))
        
        # Resolve overlaps
        for element1, element2 in overlaps:
            # Determine which element to move (prefer moving the second element)
            element_to_move = element2
            fixed_element = element1
            
            # Special cases
            if element1 == 'cta' or (element1 == 'body' and element2 != 'cta'):
                element_to_move = element1
                fixed_element = element2
                
            # Calculate the overlap amount
            moving_box = bounding_boxes[element_to_move]
            fixed_box = bounding_boxes[fixed_element]
            
            # Calculate vertical overlap
            v_overlap = min(moving_box[3], fixed_box[3]) - max(moving_box[1], fixed_box[1])
            
            # Add padding
            padding = 10
            
            # Get current position and alignment
            moving_pos = positions[element_to_move]['position']
            moving_align = positions[element_to_move]['alignment']
            
            # Calculate new position
            x, y = moving_pos
            
            # Determine if we should move up or down
            if moving_box[1] > fixed_box[1]:
                # Move down
                new_y = y + v_overlap + padding
            else:
                # Move up
                new_y = y - v_overlap - padding
            
            # Update position
            positions[element_to_move]['position'] = (x, new_y)
            
            # Update bounding box for future overlap checks
            element_width = positions[element_to_move]['dimensions'].get('width', 0)
            element_height = positions[element_to_move]['dimensions'].get('height', 0)
            
            if moving_align == 'center':
                left = x - element_width // 2
                right = x + element_width // 2
            elif moving_align == 'left':
                left = x
                right = x + element_width
            else:  # right
                left = x - element_width
                right = x
                
            bounding_boxes[element_to_move] = (left, new_y, right, new_y + element_height)
        
        return positions
    
    def _get_default_positions(self, width: int, height: int, text_elements: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """
        Get default text positions if calculation fails.
        
        Args:
            width: Image width
            height: Image height
            text_elements: Text elements
            
        Returns:
            Default positions
        """
        # Create default positions using centered layout
        positions = {}
        
        elements = {
            'headline': text_elements.get('headline', ''),
            'subheadline': text_elements.get('subheadline', ''),
            'body': text_elements.get('body_text', ''),
            'cta': text_elements.get('call_to_action', ''),
            'brand': text_elements.get('brand_name', '')
        }
        
        # Default positions
        default_positions = {
            'headline': (width // 2, int(height * 0.3)),
            'subheadline': (width // 2, int(height * 0.4)),
            'body': (width // 2, int(height * 0.55)),
            'cta': (width // 2, int(height * 0.75)),
            'brand': (width // 2, int(height * 0.15))
        }
        
        # Create position entries
        for element_name, text in elements.items():
            if not text:
                continue
                
            positions[element_name] = {
                "position": default_positions.get(element_name, (width // 2, height // 2)),
                "alignment": "center",
                "dimensions": {}
            }
        
        return positions
    
    def _get_text_dimensions(self, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
        """
        Get dimensions of text with the given font.
        
        Args:
            text: Text string
            font: Font to use
            
        Returns:
            (width, height) tuple
        """
        try:
            # Try getbbox method first (Pillow >= 8.0.0)
            bbox = font.getbbox(text)
            if bbox:
                return bbox[2] - bbox[0], bbox[3] - bbox[1]
        except (AttributeError, TypeError):
            try:
                # Try older PIL method
                return font.getsize(text)
            except:
                # Estimate based on character count
                size = getattr(font, 'size', 12)
                return int(len(text) * size * 0.6), int(size * 1.2) 
