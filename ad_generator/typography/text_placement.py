"""
Text Placement System - Advanced positioning engine for professional ads
Handles smart layout, dynamic positioning, and brand-specific text arrangements
"""
import os
import logging
import math
from typing import Dict, List, Any, Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class TextPlacementEngine:
    """Advanced engine for optimal text placement in advertisements."""
    
    def __init__(self):
        """Initialize text placement engine."""
        self.logger = logging.getLogger(__name__)
        
        # Layout templates for different advertisement styles
        self.layout_templates = self._setup_layout_templates()
        
        # Brand-specific templates
        self.brand_templates = self._setup_brand_templates()
    
    def _setup_layout_templates(self) -> Dict[str, Dict[str, Any]]:
        """Set up layout templates for different ad styles."""
        return {
            'centered': {
                'description': 'Centered text with balanced spacing',
                'headline': {'x_rel': 0.5, 'y_rel': 0.25, 'alignment': 'center'},
                'subheadline': {'x_rel': 0.5, 'y_rel': 0.35, 'alignment': 'center'},
                'body': {'x_rel': 0.5, 'y_rel': 0.5, 'alignment': 'center'},
                'cta': {'x_rel': 0.5, 'y_rel': 0.8, 'alignment': 'center'},
                'brand': {'x_rel': 0.5, 'y_rel': 0.1, 'alignment': 'center'},
                'spacing': {
                    'headline_to_subheadline': 0.06,  # Relative to image height
                    'subheadline_to_body': 0.05,
                    'body_to_cta': 0.08
                }
            },
            'left_aligned': {
                'description': 'Left-aligned text with margin',
                'headline': {'x_rel': 0.1, 'y_rel': 0.25, 'alignment': 'left'},
                'subheadline': {'x_rel': 0.1, 'y_rel': 0.35, 'alignment': 'left'},
                'body': {'x_rel': 0.1, 'y_rel': 0.5, 'alignment': 'left'},
                'cta': {'x_rel': 0.1, 'y_rel': 0.8, 'alignment': 'left'},
                'brand': {'x_rel': 0.1, 'y_rel': 0.1, 'alignment': 'left'},
                'spacing': {
                    'headline_to_subheadline': 0.06,
                    'subheadline_to_body': 0.05,
                    'body_to_cta': 0.08
                }
            },
            'right_aligned': {
                'description': 'Right-aligned text with margin',
                'headline': {'x_rel': 0.9, 'y_rel': 0.25, 'alignment': 'right'},
                'subheadline': {'x_rel': 0.9, 'y_rel': 0.35, 'alignment': 'right'},
                'body': {'x_rel': 0.9, 'y_rel': 0.5, 'alignment': 'right'},
                'cta': {'x_rel': 0.9, 'y_rel': 0.8, 'alignment': 'right'},
                'brand': {'x_rel': 0.9, 'y_rel': 0.1, 'alignment': 'right'},
                'spacing': {
                    'headline_to_subheadline': 0.06,
                    'subheadline_to_body': 0.05,
                    'body_to_cta': 0.08
                }
            },
            'top_centered': {
                'description': 'Text centered at the top of the image',
                'headline': {'x_rel': 0.5, 'y_rel': 0.15, 'alignment': 'center'},
                'subheadline': {'x_rel': 0.5, 'y_rel': 0.22, 'alignment': 'center'},
                'body': {'x_rel': 0.5, 'y_rel': 0.3, 'alignment': 'center'},
                'cta': {'x_rel': 0.5, 'y_rel': 0.45, 'alignment': 'center'},
                'brand': {'x_rel': 0.5, 'y_rel': 0.07, 'alignment': 'center'},
                'spacing': {
                    'headline_to_subheadline': 0.05,
                    'subheadline_to_body': 0.04,
                    'body_to_cta': 0.06
                }
            },
            'bottom_centered': {
                'description': 'Text centered at the bottom of the image',
                'headline': {'x_rel': 0.5, 'y_rel': 0.65, 'alignment': 'center'},
                'subheadline': {'x_rel': 0.5, 'y_rel': 0.72, 'alignment': 'center'},
                'body': {'x_rel': 0.5, 'y_rel': 0.8, 'alignment': 'center'},
                'cta': {'x_rel': 0.5, 'y_rel': 0.9, 'alignment': 'center'},
                'brand': {'x_rel': 0.5, 'y_rel': 0.55, 'alignment': 'center'},
                'spacing': {
                    'headline_to_subheadline': 0.05,
                    'subheadline_to_body': 0.04,
                    'body_to_cta': 0.06
                }
            },
            'bottom_left': {
                'description': 'Text positioned in the bottom left corner',
                'headline': {'x_rel': 0.1, 'y_rel': 0.65, 'alignment': 'left'},
                'subheadline': {'x_rel': 0.1, 'y_rel': 0.72, 'alignment': 'left'},
                'body': {'x_rel': 0.1, 'y_rel': 0.8, 'alignment': 'left'},
                'cta': {'x_rel': 0.1, 'y_rel': 0.9, 'alignment': 'left'},
                'brand': {'x_rel': 0.1, 'y_rel': 0.55, 'alignment': 'left'},
                'spacing': {
                    'headline_to_subheadline': 0.05,
                    'subheadline_to_body': 0.04,
                    'body_to_cta': 0.06
                }
            },
            'bottom_right': {
                'description': 'Text positioned in the bottom right corner',
                'headline': {'x_rel': 0.9, 'y_rel': 0.65, 'alignment': 'right'},
                'subheadline': {'x_rel': 0.9, 'y_rel': 0.72, 'alignment': 'right'},
                'body': {'x_rel': 0.9, 'y_rel': 0.8, 'alignment': 'right'},
                'cta': {'x_rel': 0.9, 'y_rel': 0.9, 'alignment': 'right'},
                'brand': {'x_rel': 0.9, 'y_rel': 0.55, 'alignment': 'right'},
                'spacing': {
                    'headline_to_subheadline': 0.05,
                    'subheadline_to_body': 0.04,
                    'body_to_cta': 0.06
                }
            },
            'split_layout': {
                'description': 'Text split between top and bottom',
                'headline': {'x_rel': 0.5, 'y_rel': 0.15, 'alignment': 'center'},
                'subheadline': {'x_rel': 0.5, 'y_rel': 0.22, 'alignment': 'center'},
                'body': {'x_rel': 0.5, 'y_rel': 0.8, 'alignment': 'center'},
                'cta': {'x_rel': 0.5, 'y_rel': 0.9, 'alignment': 'center'},
                'brand': {'x_rel': 0.5, 'y_rel': 0.07, 'alignment': 'center'},
                'spacing': {
                    'headline_to_subheadline': 0.05,
                    'subheadline_to_body': 0.5,  # Large gap intentionally
                    'body_to_cta': 0.06
                }
            },
            'text_overlay': {
                'description': 'Text overlays center of image with semi-transparent background',
                'headline': {'x_rel': 0.5, 'y_rel': 0.45, 'alignment': 'center'},
                'subheadline': {'x_rel': 0.5, 'y_rel': 0.52, 'alignment': 'center'},
                'body': {'x_rel': 0.5, 'y_rel': 0.6, 'alignment': 'center'},
                'cta': {'x_rel': 0.5, 'y_rel': 0.7, 'alignment': 'center'},
                'brand': {'x_rel': 0.5, 'y_rel': 0.37, 'alignment': 'center'},
                'background': {
                    'enabled': True,
                    'color': (0, 0, 0, 150),
                    'padding': 0.1,  # Percent of height
                    'y_start': 0.35,
                    'y_end': 0.75
                },
                'spacing': {
                    'headline_to_subheadline': 0.05,
                    'subheadline_to_body': 0.04,
                    'body_to_cta': 0.06
                }
            },
            'dynamic': {
                'description': 'Dynamic placement based on image content',
                # Default positions will be overridden by analysis
                'headline': {'x_rel': 0.5, 'y_rel': 0.25, 'alignment': 'center'},
                'subheadline': {'x_rel': 0.5, 'y_rel': 0.35, 'alignment': 'center'},
                'body': {'x_rel': 0.5, 'y_rel': 0.5, 'alignment': 'center'},
                'cta': {'x_rel': 0.5, 'y_rel': 0.8, 'alignment': 'center'},
                'brand': {'x_rel': 0.5, 'y_rel': 0.1, 'alignment': 'center'},
                'spacing': {
                    'headline_to_subheadline': 0.06,
                    'subheadline_to_body': 0.05,
                    'body_to_cta': 0.08
                }
            }
        }
    
    def _setup_brand_templates(self) -> Dict[str, Dict[str, Any]]:
        """Set up brand-specific templates for text placement."""
        return {
            'apple': {
                'description': 'Apple-style minimalist layout',
                'headline': {'x_rel': 0.5, 'y_rel': 0.25, 'alignment': 'center'},
                'subheadline': {'x_rel': 0.5, 'y_rel': 0.33, 'alignment': 'center'},
                'body': {'x_rel': 0.5, 'y_rel': 0.45, 'alignment': 'center'},
                'cta': {'x_rel': 0.5, 'y_rel': 0.65, 'alignment': 'center'},
                'brand': {'x_rel': 0.5, 'y_rel': 0.15, 'alignment': 'center'},
                'spacing': {
                    'headline_to_subheadline': 0.05,
                    'subheadline_to_body': 0.05,
                    'body_to_cta': 0.1
                },
                'weights': {
                    'headline': 'thin',  # Apple often uses ultra-light fonts for headlines
                    'subheadline': 'regular',
                    'body': 'light',
                    'cta': 'regular'
                }
            },
            'nike': {
                'description': 'Nike-style bold, asymmetric layout',
                'headline': {'x_rel': 0.1, 'y_rel': 0.25, 'alignment': 'left'},
                'subheadline': {'x_rel': 0.1, 'y_rel': 0.35, 'alignment': 'left'},
                'body': {'x_rel': 0.1, 'y_rel': 0.45, 'alignment': 'left'},
                'cta': {'x_rel': 0.1, 'y_rel': 0.6, 'alignment': 'left'},
                'brand': {'x_rel': 0.1, 'y_rel': 0.8, 'alignment': 'left', 'large': True},
                'spacing': {
                    'headline_to_subheadline': 0.06,
                    'subheadline_to_body': 0.04,
                    'body_to_cta': 0.08
                },
                'weights': {
                    'headline': 'black',  # Nike uses very bold, condensed typography
                    'subheadline': 'bold',
                    'body': 'regular',
                    'cta': 'bold'
                }
            },
            'bmw': {
                'description': 'BMW-style precision layout',
                'headline': {'x_rel': 0.1, 'y_rel': 0.7, 'alignment': 'left'},
                'subheadline': {'x_rel': 0.1, 'y_rel': 0.77, 'alignment': 'left'},
                'body': {'x_rel': 0.1, 'y_rel': 0.85, 'alignment': 'left'},
                'cta': {'x_rel': 0.1, 'y_rel': 0.92, 'alignment': 'left'},
                'brand': {'x_rel': 0.1, 'y_rel': 0.03, 'alignment': 'left'},
                'spacing': {
                    'headline_to_subheadline': 0.04,
                    'subheadline_to_body': 0.04,
                    'body_to_cta': 0.03
                },
                'weights': {
                    'headline': 'light',  # BMW often uses light, elegant typography
                    'subheadline': 'regular',
                    'body': 'light',
                    'cta': 'regular'
                }
            },
            'rolex': {
                'description': 'Rolex-style elegant, centered layout',
                'headline': {'x_rel': 0.5, 'y_rel': 0.3, 'alignment': 'center'},
                'subheadline': {'x_rel': 0.5, 'y_rel': 0.38, 'alignment': 'center'},
                'body': {'x_rel': 0.5, 'y_rel': 0.48, 'alignment': 'center'},
                'cta': {'x_rel': 0.5, 'y_rel': 0.6, 'alignment': 'center'},
                'brand': {'x_rel': 0.5, 'y_rel': 0.15, 'alignment': 'center', 'large': True},
                'spacing': {
                    'headline_to_subheadline': 0.05,
                    'subheadline_to_body': 0.05,
                    'body_to_cta': 0.08
                },
                'weights': {
                    'headline': 'regular',  # Rolex uses elegant serif typography
                    'subheadline': 'light',
                    'body': 'light',
                    'cta': 'regular'
                }
            },
            'samsung': {
                'description': 'Samsung-style tech-focused layout',
                'headline': {'x_rel': 0.5, 'y_rel': 0.75, 'alignment': 'center'},
                'subheadline': {'x_rel': 0.5, 'y_rel': 0.82, 'alignment': 'center'},
                'body': {'x_rel': 0.5, 'y_rel': 0.87, 'alignment': 'center'},
                'cta': {'x_rel': 0.5, 'y_rel': 0.93, 'alignment': 'center'},
                'brand': {'x_rel': 0.1, 'y_rel': 0.05, 'alignment': 'left'},
                'spacing': {
                    'headline_to_subheadline': 0.04,
                    'subheadline_to_body': 0.03,
                    'body_to_cta': 0.03
                },
                'weights': {
                    'headline': 'bold',
                    'subheadline': 'regular',
                    'body': 'light',
                    'cta': 'medium'
                }
            }
        }
    
    def calculate_text_positions(self, 
                                image: Image.Image, 
                                text_elements: Dict[str, Any],
                                text_placement_style: str = 'centered',
                                brand_name: str = None,
                                font_dimensions: Dict[str, Dict[str, int]] = None,
                                analyze_image: bool = True) -> Dict[str, Dict[str, Any]]:
        """
        Calculate optimal text positions based on layout template.
        
        Args:
            image: PIL Image
            text_elements: Dictionary with text elements (headline, subheadline, etc.)
            text_placement_style: Layout style name
            brand_name: Optional brand name for brand-specific template
            font_dimensions: Dictionary with text dimensions for each element
            analyze_image: Whether to analyze image for dynamic placement
            
        Returns:
            Dictionary with calculated positions and properties for each text element
        """
        width, height = image.size
        
        # Check if we have a brand-specific template
        template = None
        if brand_name:
            brand_lower = brand_name.lower()
            for brand, brand_template in self.brand_templates.items():
                if brand in brand_lower:
                    template = brand_template
                    break
        
        # If no brand template, use the specified style
        if not template:
            template = self.layout_templates.get(text_placement_style, self.layout_templates['centered'])
        
        # For dynamic placement, analyze image
        if text_placement_style == 'dynamic' and analyze_image:
            template = self._calculate_dynamic_placement(image, template, text_elements)
        
        # Calculate positions for each text element
        positions = {}
        
        # Get text content and dimensions
        for element_name, element_data in {
            'headline': {'text': text_elements.get('headline', '')},
            'subheadline': {'text': text_elements.get('subheadline', '')},
            'body': {'text': text_elements.get('body', '')},
            'cta': {'text': text_elements.get('call_to_action', '')},
            'brand': {'text': text_elements.get('brand_name', '')}
        }.items():
            text = element_data['text']
            
            if text:
                # Get element template
                element_template = template.get(element_name, {
                    'x_rel': 0.5,
                    'y_rel': 0.5,
                    'alignment': 'center'
                })
                
                # Calculate position
                x = int(element_template['x_rel'] * width)
                y = int(element_template['y_rel'] * height)
                
                # Calculate dimensions if provided
                dimensions = {}
                if font_dimensions and element_name in font_dimensions:
                    dimensions = font_dimensions[element_name]
                
                # Add to positions
                positions[element_name] = {
                    'position': (x, y),
                    'alignment': element_template.get('alignment', 'center'),
                    'dimensions': dimensions,
                    'weight': template.get('weights', {}).get(element_name, 'regular'),
                    'text': text
                }
                
                # Add special properties if specified
                if element_template.get('large'):
                    positions[element_name]['large'] = True
        
        # Adjust positions based on spacing if multiple elements are present
        self._adjust_positions_for_spacing(positions, template.get('spacing', {}), height)
        
        # Add background information if applicable
        if template.get('background', {}).get('enabled'):
            positions['background'] = template['background']
        
        return positions
    
    def _calculate_dynamic_placement(self, 
                                    image: Image.Image, 
                                    template: Dict[str, Any],
                                    text_elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate dynamic text placement based on image content.
        
        Args:
            image: PIL Image
            template: Base template to modify
            text_elements: Text elements
            
        Returns:
            Modified template with dynamic placements
        """
        # Create a copy of template to modify
        dynamic_template = template.copy()
        
        # Analyze image for subject position and brightness
        subject_position = self._find_subject_position(image)
        brightness_map = self._analyze_image_brightness(image)
        
        # Adjust text placement based on subject position
        if subject_position:
            # Place text in the opposite area from the main subject
            # If subject is in top half, place text in bottom half
            if subject_position['y'] < 0.5:
                # Move text to bottom
                dynamic_template['headline']['y_rel'] = 0.7
                dynamic_template['subheadline']['y_rel'] = 0.77
                dynamic_template['body']['y_rel'] = 0.84
                dynamic_template['cta']['y_rel'] = 0.9
                dynamic_template['brand']['y_rel'] = 0.6
            else:
                # Move text to top
                dynamic_template['headline']['y_rel'] = 0.2
                dynamic_template['subheadline']['y_rel'] = 0.27
                dynamic_template['body']['y_rel'] = 0.34
                dynamic_template['cta']['y_rel'] = 0.45
                dynamic_template['brand']['y_rel'] = 0.1
            
            # If subject is in left half, place text in right half
            if subject_position['x'] < 0.5:
                # Right alignment
                for element in ['headline', 'subheadline', 'body', 'cta', 'brand']:
                    dynamic_template[element]['x_rel'] = 0.85
                    dynamic_template[element]['alignment'] = 'right'
            else:
                # Left alignment
                for element in ['headline', 'subheadline', 'body', 'cta', 'brand']:
                    dynamic_template[element]['x_rel'] = 0.15
                    dynamic_template[element]['alignment'] = 'left'
        
        # For very bright or dark images, adjust text placement to ensure readability
        if brightness_map:
            overall_brightness = brightness_map.get('overall', 0.5)
            
            # For very bright images, prefer darker areas
            if overall_brightness > 0.8:
                # Find darkest region
                darkest_region = min(brightness_map.items(), key=lambda x: x[1] if x[0] != 'overall' else 1.0)
                
                # Get region coordinates
                region_name = darkest_region[0]
                if '_' in region_name:
                    vert, horiz = region_name.split('_')
                    
                    # Map region to relative coordinates
                    y_map = {'top': 0.2, 'middle': 0.5, 'bottom': 0.8}
                    x_map = {'left': 0.15, 'center': 0.5, 'right': 0.85}
                    
                    # Adjust text placement
                    for element in ['headline', 'subheadline', 'body', 'cta']:
                        dynamic_template[element]['y_rel'] = y_map.get(vert, 0.5)
                        dynamic_template[element]['x_rel'] = x_map.get(horiz, 0.5)
                        dynamic_template[element]['alignment'] = horiz
            
            # For very dark images, prefer lighter areas or add background
            elif overall_brightness < 0.2:
                # Add semi-transparent background for text
                dynamic_template['background'] = {
                    'enabled': True,
                    'color': (0, 0, 0, 180),
                    'padding': 0.05,
                    'y_start': 0.6,
                    'y_end': 0.95
                }
                
                # Position text within the background area
                dynamic_template['headline']['y_rel'] = 0.68
                dynamic_template['subheadline']['y_rel'] = 0.75
                dynamic_template['body']['y_rel'] = 0.82
                dynamic_template['cta']['y_rel'] = 0.89
                
                # Center horizontally
                for element in ['headline', 'subheadline', 'body', 'cta']:
                    dynamic_template[element]['x_rel'] = 0.5
                    dynamic_template[element]['alignment'] = 'center'
        
        return dynamic_template
    
    def _find_subject_position(self, image: Image.Image) -> Optional[Dict[str, float]]:
        """
        Find the main subject position in the image.
        
        Args:
            image: PIL Image
            
        Returns:
            Dictionary with subject position information or None
        """
        try:
            # Basic image analysis using edge detection
            # Convert to grayscale
            gray = image.convert('L')
            width, height = gray.size
            
            # Apply edge detection
            edges = gray.filter(ImageFilter.FIND_EDGES)
            
            # Convert to numpy array for processing
            edges_array = np.array(edges)
            
            # Find strongest edges
            threshold = np.percentile(edges_array, 90)  # Top 10% of edges
            strong_edges = edges_array > threshold
            
            # Find contours in strong edges
            y_indices, x_indices = np.where(strong_edges)
            
            if len(y_indices) > 0 and len(x_indices) > 0:
                # Calculate weighted center of strong edges
                center_x = np.mean(x_indices)
                center_y = np.mean(y_indices)
                
                # Normalize to 0-1 range
                normalized_x = center_x / width
                normalized_y = center_y / height
                
                return {
                    'x': normalized_x,
                    'y': normalized_y
                }
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error finding subject position: {str(e)}")
            return None
    
    def _analyze_image_brightness(self, image: Image.Image) -> Optional[Dict[str, float]]:
        """
        Analyze image brightness across different regions.
        
        Args:
            image: PIL Image
            
        Returns:
            Dictionary with brightness values or None
        """
        try:
            # Convert to grayscale
            gray = image.convert('L')
            width, height = gray.size
            
            # Divide the image into a 3x3 grid
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
            
        except Exception as e:
            self.logger.warning(f"Error analyzing image brightness: {str(e)}")
            return None
    
    def _adjust_positions_for_spacing(self, 
                                     positions: Dict[str, Dict[str, Any]], 
                                     spacing: Dict[str, float],
                                     height: int) -> None:
        """
        Adjust text positions based on specified spacing.
        
        Args:
            positions: Dictionary with current positions
            spacing: Spacing specifications
            height: Image height
        """
        # Get positions that need adjustment
        headline_pos = positions.get('headline', {}).get('position', None)
        subheadline_pos = positions.get('subheadline', {}).get('position', None)
        body_pos = positions.get('body', {}).get('position', None)
        cta_pos = positions.get('cta', {}).get('position', None)
        
        # Calculate dimensions
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
    
    def get_text_bounding_boxes(self, 
                               positions: Dict[str, Dict[str, Any]], 
                               fonts: Dict[str, ImageFont.FreeTypeFont],
                               image_size: Tuple[int, int]) -> Dict[str, Tuple[int, int, int, int]]:
        """
        Calculate the bounding boxes for each text element.
        
        Args:
            positions: Text positions dictionary
            fonts: Dictionary of fonts for each element
            image_size: (width, height) of the image
            
        Returns:
            Dictionary with bounding box for each element
        """
        width, height = image_size
        bounding_boxes = {}
        
        for element_name, element_data in positions.items():
            if element_name == 'background':
                continue
                
            text = element_data.get('text', '')
            if not text or element_name not in fonts:
                continue
            
            font = fonts[element_name]
            position = element_data['position']
            alignment = element_data.get('alignment', 'center')
            
            # Get text dimensions
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate text position based on alignment
            x, y = position
            if alignment == 'center':
                x = x - text_width // 2
            elif alignment == 'right':
                x = x - text_width
            
            # Calculate bounding box
            bbox = (x, y, x + text_width, y + text_height)
            bounding_boxes[element_name] = bbox
        
        return bounding_boxes
    
    def check_text_overlaps(self, bounding_boxes: Dict[str, Tuple[int, int, int, int]]) -> List[Tuple[str, str]]:
        """
        Check for overlaps between text elements.
        
        Args:
            bounding_boxes: Dictionary with bounding box for each element
            
        Returns:
            List of overlapping element pairs
        """
        overlaps = []
        
        # Check each pair of elements
        elements = list(bounding_boxes.keys())
        
        for i in range(len(elements)):
            for j in range(i + 1, len(elements)):
                element1 = elements[i]
                element2 = elements[j]
                
                box1 = bounding_boxes[element1]
                box2 = bounding_boxes[element2]
                
                # Check for overlap
                if (box1[0] < box2[2] and box1[2] > box2[0] and
                    box1[1] < box2[3] and box1[3] > box2[1]):
                    overlaps.append((element1, element2))
        
        return overlaps
    
    def resolve_text_overlaps(self, 
                             positions: Dict[str, Dict[str, Any]], 
                             bounding_boxes: Dict[str, Tuple[int, int, int, int]],
                             overlaps: List[Tuple[str, str]],
                             image_height: int) -> Dict[str, Dict[str, Any]]:
        """
        Resolve overlaps between text elements.
        
        Args:
            positions: Text positions dictionary
            bounding_boxes: Dictionary with bounding box for each element
            overlaps: List of overlapping element pairs
            image_height: Height of the image
            
        Returns:
            Updated positions dictionary
        """
        resolved_positions = positions.copy()
        
        # Process each overlap
        for element1, element2 in overlaps:
            # Get element priorities (lower elements have higher priority)
            element_priority = {
                'brand': 1,
                'headline': 2,
                'subheadline': 3,
                'body': 4,
                'cta': 5
            }
            
            # Determine which element to move
            if element_priority.get(element1, 10) < element_priority.get(element2, 10):
                element_to_move = element2
                fixed_element = element1
            else:
                element_to_move = element1
                fixed_element = element2
            
            # Get bounding boxes
            box_move = bounding_boxes[element_to_move]
            box_fixed = bounding_boxes[fixed_element]
            
            # Calculate overlap
            overlap_y = min(box_move[3], box_fixed[3]) - max(box_move[1], box_fixed[1])
            
            # Add padding
            padding = int(0.02 * image_height)  # 2% of image height
            
            # Move the element vertically to resolve overlap
            x, y = resolved_positions[element_to_move]['position']
            
            if box_move[1] < box_fixed[1]:
                # Move up
                new_y = box_move[1] - overlap_y - padding
            else:
                # Move down
                new_y = y + overlap_y + padding
            
            # Update position
            resolved_positions[element_to_move]['position'] = (x, new_y)
            
            # Update bounding box
            height = box_move[3] - box_move[1]
            bounding_boxes[element_to_move] = (box_move[0], new_y, box_move[2], new_y + height)
        
        return resolved_positions
    
    def optimize_text_placement(self, 
                              image: Image.Image, 
                              text_elements: Dict[str, Any],
                              fonts: Dict[str, ImageFont.FreeTypeFont],
                              text_placement_style: str = 'centered',
                              brand_name: str = None) -> Dict[str, Dict[str, Any]]:
        """
        Optimize text placement with overlap detection and resolution.
        
        Args:
            image: PIL Image
            text_elements: Dictionary with text elements
            fonts: Dictionary of fonts for each element
            text_placement_style: Layout style name
            brand_name: Optional brand name for brand-specific template
            
        Returns:
            Optimized text positions dictionary
        """
        width, height = image.size
        
        # Calculate font dimensions
        font_dimensions = {}
        for element_name, font in fonts.items():
            text = None
            if element_name == 'headline':
                text = text_elements.get('headline')
            elif element_name == 'subheadline':
                text = text_elements.get('subheadline')
            elif element_name == 'body':
                text = text_elements.get('body')
            elif element_name == 'cta':
                text = text_elements.get('call_to_action')
            elif element_name == 'brand':
                text = text_elements.get('brand_name')
            
            if text:
                # Get text dimensions
                bbox = font.getbbox(text)
                font_dimensions[element_name] = {
                    'width': bbox[2] - bbox[0],
                    'height': bbox[3] - bbox[1],
                    'descent': getattr(font, 'getmetrics', lambda: (0, 0))()[1]
                }
        
        # Calculate initial positions
        positions = self.calculate_text_positions(
            image,
            text_elements,
            text_placement_style,
            brand_name,
            font_dimensions,
            analyze_image=True
        )
        
        # Calculate bounding boxes
        bounding_boxes = self.get_text_bounding_boxes(positions, fonts, (width, height))
        
        # Check for overlaps
        overlaps = self.check_text_overlaps(bounding_boxes)
        
        # Resolve overlaps if any
        if overlaps:
            positions = self.resolve_text_overlaps(positions, bounding_boxes, overlaps, height)
        
        return positions

# Import ImageFilter for edge detection if not imported already
try:
    from PIL import ImageFilter
except ImportError:
    pass


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize text placement engine
    engine = TextPlacementEngine()
    
    # Print available layout templates
    print("Available layout templates:")
    for name, template in engine.layout_templates.items():
        print(f"- {name}: {template['description']}")
    
    print("\nAvailable brand templates:")
    for name, template in engine.brand_templates.items():
        print(f"- {name}: {template['description']}")