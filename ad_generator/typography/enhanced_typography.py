"""
Professional Typography Integration System
Provides sophisticated typography with perfect background integration for advertising
"""
import os
import logging
import numpy as np
import cv2
from typing import Dict, List, Tuple, Any, Optional, Union
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops, ImageColor
import colorsys
import math
import random
from collections import defaultdict

class EnhancedTypographySystem:
    """
    Professional typography system for advertising with sophisticated
    background analysis and industry-standard text treatments.
    """
    
    def __init__(self, font_manager=None, text_effects=None, brand_typography=None):
        """Initialize the enhanced typography system."""
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Store references to other system components
        self.font_manager = font_manager
        self.text_effects = text_effects
        self.brand_typography = brand_typography
        
        # Initialize style databases
        self.industry_typography_styles = self._initialize_industry_styles()
        self.brand_level_typography = self._initialize_brand_level_styles()
        self.product_typography_styles = self._initialize_product_styles()
        
        # Font size ratios for responsive typography
        self.font_size_ratios = {
            "headline": 0.08,     # 8% of image height
            "subheadline": 0.035, # 3.5% of image height
            "body": 0.025,        # 2.5% of image height
            "cta": 0.035,         # 3.5% of image height
            "brand": 0.04         # 4% of image height
        }
        
        # Initialize text effect mapping
        self.effect_mapping = self._initialize_effect_mapping()
        
        # Templates for text zones based on composition styles
        self.text_zone_templates = self._initialize_text_zone_templates()
        
    def create_typography(self, 
                         image: Image.Image, 
                         text_elements: Dict[str, str],
                         brand_name: str = None,
                         industry: str = None,
                         brand_level: str = None,
                         style_profile: Dict[str, Any] = None) -> Image.Image:
        """
        Create professional typography integrated perfectly with the image.
        
        Args:
            image: Base image
            text_elements: Dictionary of text elements (headline, subheadline, etc.)
            brand_name: Brand name (optional)
            industry: Industry type (optional)
            brand_level: Brand positioning level (optional)
            style_profile: Style overrides (optional)
        
        Returns:
            Image with integrated typography
        """
        self.logger.info(f"Creating typography for {brand_name} in {industry} industry")
        
        # Perform advanced image analysis
        analysis = self.analyze_image_deeply(image)
        
        # Get typography style based on industry, brand level, and overrides
        typography_style = self.get_typography_style(
            brand_name=brand_name,
            industry=industry,
            brand_level=brand_level,
            style_profile=style_profile
        )
        
        # Apply style overrides if provided
        if style_profile:
            typography_style = self._apply_style_overrides(typography_style, style_profile)
            self.logger.info(f"Applied style overrides: {style_profile}")
        
        # Select font pairings
        self.logger.info("Selecting font pairings")
        fonts = self._select_fonts(typography_style, text_elements, image.size[1])
        font_selection_results = {k: v is not None for k, v in fonts.items()}
        self.logger.info(f"Font selection results: {font_selection_results}")
        
        # Calculate optimal text sizes
        self.logger.info("Calculating optimal text sizes")
        sized_fonts = self._calculate_font_sizes(
            fonts, 
            text_elements, 
            image.size, 
            typography_style
        )
        
        # Calculate optimal text positions
        self.logger.info("Calculating text positions")
        text_positions = self._calculate_text_positions(
            sized_fonts,
            text_elements,
            image.size,
            analysis,
            typography_style
        )
        
        # Generate color scheme
        self.logger.info("Generating color scheme")
        colors = self._generate_text_colors(
            image, 
            analysis, 
            text_positions, 
            typography_style
        )
        
        # Create overlay for text
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Apply text elements with proper effects
        self.logger.info("Applying text elements with effects")
        self._apply_text_elements(
            draw, 
            overlay,
            text_elements,
            sized_fonts,
            text_positions,
            colors,
            typography_style,
            analysis,
            image
        )
        
        # Composite text overlay with original image
        self.logger.info("Compositing text overlay with original image")
        result = self._composite_with_blending(image, overlay, analysis)
        
        return result
        
    def analyze_image_deeply(self, image: Image.Image) -> Dict[str, Any]:
        """
        Perform deep image analysis for optimal text placement.
        
        Args:
            image: Image to analyze
            
        Returns:
            Dictionary with detailed image analysis
        """
        # Convert to numpy array for advanced analysis
        img_array = np.array(image.convert('RGB'))
        
        # Calculate edge density map to find areas with low detail (good for text)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = self._calculate_edge_density_map(edges, 20)
        
        # Calculate brightness map
        brightness_map = self._calculate_brightness_map(gray)
        
        # Identify key focal points in the image
        focal_points = self._identify_focal_points(img_array)
        
        # Calculate saliency map to identify visually prominent regions
        saliency_map = self._calculate_saliency_map(img_array)
        
        # Combine edge density and saliency to find optimal text areas
        text_placement_map = self._calculate_text_placement_map(edge_density, brightness_map, saliency_map)
        
        # Find dominant colors
        dominant_colors = self._extract_dominant_colors(image)
        
        # Get color palette
        color_palette = self._extract_color_palette(dominant_colors, brightness_map['overall'])
        
        return {
            'edge_density': edge_density,
            'brightness_map': brightness_map,
            'focal_points': focal_points,
            'saliency_map': saliency_map,
            'text_placement_map': text_placement_map,
            'dominant_colors': dominant_colors,
            'color_palette': color_palette
        }
    
    def _calculate_edge_density_map(self, edges: np.ndarray, window_size: int) -> np.ndarray:
        """
        Calculate edge density map using sliding window approach.
        
        Args:
            edges: Edge image
            window_size: Size of sliding window
            
        Returns:
            Edge density map
        """
        height, width = edges.shape
        density_map = np.zeros((height, width), dtype=np.float32)
        
        # Pad edge image
        padded_edges = np.pad(edges, window_size//2, mode='constant')
        
        # Calculate density using convolution
        for y in range(height):
            for x in range(width):
                window = padded_edges[y:y+window_size, x:x+window_size]
                density_map[y, x] = np.sum(window) / (window_size * window_size * 255)
        
        # Normalize density map
        density_map = 1.0 - density_map  # Invert so higher values are better for text
        
        return density_map
    
    def _calculate_brightness_map(self, gray_img: np.ndarray) -> Dict[str, Any]:
        """
        Calculate brightness map for text contrast.
        
        Args:
            gray_img: Grayscale image
            
        Returns:
            Dictionary with brightness information
        """
        height, width = gray_img.shape
        
        # Calculate overall brightness
        overall = np.mean(gray_img) / 255.0
        
        # Calculate brightness in 3x3 grid
        grid = np.zeros((3, 3), dtype=np.float32)
        grid_names = {}
        
        cell_height = height // 3
        cell_width = width // 3
        
        for i in range(3):
            for j in range(3):
                y_start = i * cell_height
                y_end = (i + 1) * cell_height if i < 2 else height
                x_start = j * cell_width
                x_end = (j + 1) * cell_width if j < 2 else width
                
                cell = gray_img[y_start:y_end, x_start:x_end]
                grid[i, j] = np.mean(cell) / 255.0
                
                pos_names = ['top', 'middle', 'bottom']
                pos_names2 = ['left', 'center', 'right']
                grid_names[f"{pos_names[i]}_{pos_names2[j]}"] = grid[i, j]
        
        # Calculate variance for contrast
        contrast = np.std(gray_img) / 255.0
        
        # Calculate brightness histogram
        hist, bins = np.histogram(gray_img, bins=10, range=(0, 256))
        hist = hist / np.sum(hist)
        
        return {
            'overall': float(overall),
            'grid': grid_names,
            'contrast': float(contrast),
            'histogram': hist.tolist(),
            'is_dark': overall < 0.5,
            'is_high_contrast': contrast > 0.2
        }
    
    def _identify_focal_points(self, img_array: np.ndarray) -> List[Dict[str, Any]]:
        """
        Identify key focal points in the image.
        
        Args:
            img_array: Image as numpy array
            
        Returns:
            List of focal points with positions
        """
        # Convert to grayscale if it's not already
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
            
        # Detect corners
        corners = cv2.goodFeaturesToTrack(gray, maxCorners=10, qualityLevel=0.1, minDistance=50)
        
        focal_points = []
        if corners is not None:
            for corner in corners:
                x, y = corner.ravel()
                focal_points.append({
                    'position': (float(x), float(y)),
                    'type': 'corner'
                })
        
        # Get image dimensions
        height, width = gray.shape[:2]
        
        # Add center of image as a focal point
        focal_points.append({
            'position': (width / 2, height / 2),
            'type': 'center'
        })
        
        # Add rule of thirds points
        for x_ratio in [1/3, 2/3]:
            for y_ratio in [1/3, 2/3]:
                focal_points.append({
                    'position': (width * x_ratio, height * y_ratio),
                    'type': 'rule_of_thirds'
                })
        
        return focal_points
    
    # Apply these fixes to enhanced_typography.py
    def _calculate_saliency_map(self, img_array: np.ndarray) -> np.ndarray:
        """
    Calculate a simple saliency map to identify visually important regions.
    
    Args:
        img_array: Image as numpy array
        
    Returns:
        Saliency map as numpy array
    """
        try:
        # Uses a simplified saliency calculation
        # Convert to LAB color space
            lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        
        # Split channels
            l, a, b = cv2.split(lab)
        
        # Convert channels to float32 for consistent operations
            l = l.astype(np.float32)
            a = a.astype(np.float32)
            b = b.astype(np.float32)
        
        # Calculate mean of each channel
            l_mean = np.float32(np.mean(l))
            a_mean = np.float32(np.mean(a))
            b_mean = np.float32(np.mean(b))
        
        # Create mean arrays with matching type
            l_mean_arr = np.ones_like(l, dtype=np.float32) * l_mean
            a_mean_arr = np.ones_like(a, dtype=np.float32) * a_mean
            b_mean_arr = np.ones_like(b, dtype=np.float32) * b_mean
        
        # Calculate difference from mean with explicit types
            l_diff = cv2.absdiff(l, l_mean_arr)
            a_diff = cv2.absdiff(a, a_mean_arr)
            b_diff = cv2.absdiff(b, b_mean_arr)
        
        # Combine differences with explicit output type
            temp = cv2.add(l_diff, a_diff, dtype=cv2.CV_32F)
            saliency = cv2.add(temp, b_diff, dtype=cv2.CV_32F)
        
        # Normalize
            saliency = cv2.normalize(saliency, None, 0, 1, cv2.NORM_MINMAX, cv2.CV_32F)
        
            return saliency
        except Exception as e:
            self.logger.error(f"Error in saliency map calculation: {str(e)}")
        # Return fallback saliency map
            height, width = img_array.shape[:2]
            return np.zeros((height, width), dtype=np.float32)

    def _calculate_text_placement_map(self, edge_density: np.ndarray, 
                                brightness_map: Dict[str, Any],
                                saliency_map: np.ndarray) -> Dict[str, Any]:
        """
    Calculate optimal text placement map combining all factors.
    
    Args:
        edge_density: Edge density map
        brightness_map: Brightness information
        saliency_map: Saliency map
        
    Returns:
        Dictionary with text placement information
    """
        try:
        # Create weighted combination
            is_dark = brightness_map['is_dark']
        
        # Ensure consistent array types for arithmetic operations
            edge_density = edge_density.astype(np.float32)
            saliency_map = saliency_map.astype(np.float32)
            text_placement = edge_density.copy()
        
        # Avoid high saliency areas (subtract with 0.5 weight)
        # Use cv2.subtract with explicit dtype instead of numpy subtraction
            scaled_saliency = saliency_map * 0.5
            text_placement = cv2.subtract(text_placement, scaled_saliency, dtype=cv2.CV_32F)
        
        # Normalize - handle the case where min and max might be the same
            min_val = np.min(text_placement)
            max_val = np.max(text_placement)
            if max_val > min_val:
                text_placement = (text_placement - min_val) / (max_val - min_val)
            else:
                text_placement = np.zeros_like(text_placement)
        
        # Find best regions for each text element
            height, width = text_placement.shape
            regions = {}
        
        # Headline typically at top or middle
            headline_region = self._find_best_region(text_placement, 'top', width, height)
            regions['headline'] = headline_region
        
        # Subheadline below headline
            subheadline_y_min = headline_region['bounds'][1] + headline_region['bounds'][3]
            subheadline_region = self._find_best_region(
            text_placement, 
            'custom', 
            width, height,
            custom_bounds=(0, subheadline_y_min, width, height//3)
        )
            regions['subheadline'] = subheadline_region
        
        # CTA at bottom
            cta_region = self._find_best_region(text_placement, 'bottom', width, height)
            regions['cta'] = cta_region
        
        # Brand name at top corner
            brand_region = self._find_best_region(text_placement, 'top_corner', width, height)
            regions['brand'] = brand_region
        
            return {
            'map': text_placement,
            'regions': regions,
            'is_dark_background': is_dark
        }
        except Exception as e:
            self.logger.error(f"Error in text placement map calculation: {str(e)}")
        # Return fallback placement map
            height, width = edge_density.shape
            return {
            'map': np.zeros((height, width), dtype=np.float32),
            'regions': self._create_fallback_regions(width, height),
            'is_dark_background': brightness_map.get('is_dark', False)
        }

    def _create_fallback_regions(self, width: int, height: int) -> Dict[str, Dict[str, Any]]:
        """
    Create fallback placement regions when calculation fails.
    
    Args:
        width: Image width
        height: Image height
        
    Returns:
        Dictionary with default regions
    """
        return {
        'headline': {
            'score': 1.0,
            'position': (width // 2, height // 4),
            'bounds': (0, 0, width, height // 3),
            'region_type': 'top'
        },
        'subheadline': {
            'score': 1.0,
            'position': (width // 2, height // 3),
            'bounds': (0, height // 3, width, height // 3),
            'region_type': 'middle'
        },
        'cta': {
            'score': 1.0,
            'position': (width // 2, height * 3 // 4),
            'bounds': (0, height * 2 // 3, width, height // 3),
            'region_type': 'bottom'
        },
        'brand': {
            'score': 1.0,
            'position': (width // 4, height // 8),
            'bounds': (0, 0, width // 3, height // 3),
            'region_type': 'top_corner'
        }
    }

    def _calculate_edge_density_map(self, edges: np.ndarray, window_size: int) -> np.ndarray:
        """
    Calculate edge density map using sliding window approach.
    
    Args:
        edges: Edge image
        window_size: Size of sliding window
        
    Returns:
        Edge density map
    """
        try:
            height, width = edges.shape
            density_map = np.zeros((height, width), dtype=np.float32)
        
        # Pad edge image
            padded_edges = np.pad(edges, window_size//2, mode='constant')
            padded_edges = padded_edges.astype(np.float32)  # Ensure consistent type
        
        # Calculate density using convolution
            for y in range(height):
                for x in range(width):
                    window = padded_edges[y:y+window_size, x:x+window_size]
                    density_map[y, x] = np.sum(window) / (window_size * window_size * 255.0)
        
        # Normalize density map
            density_map = 1.0 - density_map  # Invert so higher values are better for text
        
            return density_map
        except Exception as e:
            self.logger.error(f"Error in edge density calculation: {str(e)}")
        # Return fallback density map
            return np.ones((height, width), dtype=np.float32) * 0.5

    def _find_best_region(self, placement_map: np.ndarray, region_type: str, 
                        width: int, height: int, custom_bounds=None) -> Dict[str, Any]:
        """
        Find the best placement region for a particular text element.
        
        Args:
            placement_map: Text placement score map
            region_type: Type of region ('top', 'bottom', 'middle', etc.)
            width: Image width
            height: Image height
            custom_bounds: Optional custom bounds
            
        Returns:
            Dictionary with region information
        """
        if custom_bounds:
            x, y, w, h = custom_bounds
            region = placement_map[y:y+h, x:x+w]
            bounds = (x, y, w, h)
        elif region_type == 'top':
            region = placement_map[:height//3, :]
            bounds = (0, 0, width, height//3)
        elif region_type == 'middle':
            region = placement_map[height//3:2*height//3, :]
            bounds = (0, height//3, width, height//3)
        elif region_type == 'bottom':
            region = placement_map[2*height//3:, :]
            bounds = (0, 2*height//3, width, height//3)
        elif region_type == 'top_corner':
            corner_size = min(width, height) // 5
            region = placement_map[:corner_size, :corner_size]
            bounds = (0, 0, corner_size, corner_size)
        else:
            region = placement_map
            bounds = (0, 0, width, height)
        
        # Find highest score position
        max_y, max_x = np.unravel_index(np.argmax(region), region.shape)
        max_score = region[max_y, max_x]
        
        # Adjust coordinates to global image
        global_x = max_x + bounds[0]
        global_y = max_y + bounds[1]
        
        return {
            'score': float(max_score),
            'position': (int(global_x), int(global_y)),
            'bounds': bounds,
            'region_type': region_type
        }
    
    def _extract_dominant_colors(self, image: Image.Image, n_colors: int = 8) -> List[Tuple[int, int, int]]:
        """
        Extract dominant colors using clustering.
        
        Args:
            image: PIL Image
            n_colors: Number of colors to extract
            
        Returns:
            List of RGB tuples representing dominant colors
        """
        # Resize image for faster processing
        img_small = image.resize((100, 100), Image.Resampling.LANCZOS)
        img_array = np.array(img_small.convert('RGB'))
        pixels = img_array.reshape(-1, 3)
        
        # Use k-means clustering to find dominant colors
        try:
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=n_colors, n_init=10)
            kmeans.fit(pixels)
            
            # Get the colors
            colors = kmeans.cluster_centers_.astype(int)
            
            # Count occurrences of each cluster
            labels = kmeans.labels_
            counts = np.bincount(labels)
            
            # Sort by frequency
            colors_with_counts = [(tuple(color), count) for color, count in zip(colors, counts)]
            sorted_colors = [color for color, _ in sorted(colors_with_counts, key=lambda x: x[1], reverse=True)]
            
            return sorted_colors
        except:
            # Fallback method if sklearn is not available
            return self._extract_colors_fallback(image, n_colors)
    
    def _extract_colors_fallback(self, image: Image.Image, n_colors: int = 8) -> List[Tuple[int, int, int]]:
        """
        Extract dominant colors using a simple binning approach (fallback).
        
        Args:
            image: PIL Image
            n_colors: Number of colors to extract
            
        Returns:
            List of RGB tuples representing dominant colors
        """
        # Resize image for faster processing
        img_small = image.resize((100, 100), Image.Resampling.LANCZOS)
        
        # Get colors
        colors = img_small.getcolors(maxcolors=10000)
        if not colors:
            return [(0, 0, 0), (255, 255, 255), (128, 128, 128)]
        
        # Sort by frequency
        sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)
        
        # Return top N colors
        return [color[1] for color in sorted_colors[:n_colors]]
    
    def _extract_color_palette(self, dominant_colors: List[Tuple[int, int, int]], 
                            brightness: float) -> Dict[str, Tuple[int, int, int]]:
        """
        Extract a professional color palette from dominant colors.
        
        Args:
            dominant_colors: List of dominant colors
            brightness: Overall image brightness
            
        Returns:
            Dictionary with color palette
        """
        if not dominant_colors:
            return {
                'primary': (0, 0, 0) if brightness > 0.5 else (255, 255, 255),
                'secondary': (128, 128, 128),
                'accent': (41, 128, 185),
                'background': (255, 255, 255) if brightness > 0.5 else (0, 0, 0),
                'text': (0, 0, 0) if brightness > 0.5 else (255, 255, 255)
            }
        
        # Get primary color as most dominant
        primary = dominant_colors[0]
        
        # Get secondary color which has good contrast with primary
        secondary = None
        for color in dominant_colors[1:]:
            contrast = self._calculate_contrast_ratio(primary, color)
            if contrast >= 2.0:
                secondary = color
                break
        
        if not secondary and len(dominant_colors) > 1:
            secondary = dominant_colors[1]
        elif not secondary:
            # Create a secondary color with good contrast
            secondary = self._generate_contrasting_color(primary)
        
        # Get accent color (vibrant color with sufficient contrast)
        accent = None
        for color in dominant_colors:
            if self._is_vibrant(color) and self._calculate_contrast_ratio(color, primary) >= 2.0:
                accent = color
                break
        
        if not accent:
            # Generate accent color
            accent = self._generate_accent_color(primary, secondary)
        
        # Determine text color based on brightness
        text = (0, 0, 0) if brightness > 0.5 else (255, 255, 255)
        
        # Determine background color
        background = (255, 255, 255) if brightness > 0.5 else (20, 20, 20)
        
        return {
            'primary': primary,
            'secondary': secondary,
            'accent': accent,
            'background': background,
            'text': text
        }
    
    def _generate_contrasting_color(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        Generate a color with good contrast to the input color.
        
        Args:
            color: Input color
            
        Returns:
            Contrasting color
        """
        r, g, b = color
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        
        if brightness > 128:
            # Input is light, return dark color
            return (max(0, r - 160), max(0, g - 160), max(0, b - 160))
        else:
            # Input is dark, return light color
            return (min(255, r + 160), min(255, g + 160), min(255, b + 160))
    
    def _generate_accent_color(self, primary: Tuple[int, int, int], 
                            secondary: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        Generate a vibrant accent color complementary to the palette.
        
        Args:
            primary: Primary color
            secondary: Secondary color
            
        Returns:
            Accent color
        """
        # Convert to HSV
        p_h, p_s, p_v = colorsys.rgb_to_hsv(primary[0]/255, primary[1]/255, primary[2]/255)
        
        # Create complementary color (180° away on color wheel)
        accent_h = (p_h + 0.5) % 1.0
        accent_s = min(1.0, p_s * 1.5)  # More saturated
        accent_v = max(0.7, p_v)  # Maintain good brightness
        
        # Convert back to RGB
        r, g, b = colorsys.hsv_to_rgb(accent_h, accent_s, accent_v)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def _is_vibrant(self, color: Tuple[int, int, int]) -> bool:
        """
        Check if a color is vibrant.
        
        Args:
            color: Color to check
            
        Returns:
            True if color is vibrant
        """
        r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        # Vibrant colors have high saturation and value
        return s > 0.5 and v > 0.5
    
    def _calculate_contrast_ratio(self, color1: Tuple[int, int, int], 
                               color2: Tuple[int, int, int]) -> float:
        """
        Calculate WCAG contrast ratio between two colors.
        
        Args:
            color1: First color
            color2: Second color
            
        Returns:
            Contrast ratio
        """
        # Calculate relative luminance
        def relative_luminance(color):
            r, g, b = [c/255.0 for c in color]
            
            def adjust(value):
                if value <= 0.03928:
                    return value / 12.92
                else:
                    return ((value + 0.055) / 1.055) ** 2.4
            
            r_adj = adjust(r)
            g_adj = adjust(g)
            b_adj = adjust(b)
            
            return 0.2126 * r_adj + 0.7152 * g_adj + 0.0722 * b_adj
        
        # Calculate luminance for both colors
        l1 = relative_luminance(color1)
        l2 = relative_luminance(color2)
        
        # Calculate contrast ratio
        if l1 > l2:
            return (l1 + 0.05) / (l2 + 0.05)
        else:
            return (l2 + 0.05) / (l1 + 0.05)
    
    def get_typography_style(self, brand_name: str, industry: str, 
                           brand_level: str, style_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get typography style based on industry and brand level.
        
        Args:
            brand_name: Brand name
            industry: Industry type
            brand_level: Brand positioning level
            style_profile: Style overrides (optional)
            
        Returns:
            Typography style dictionary
        """
        self.logger.info(f"Getting typography style for {brand_name}, {industry}, {brand_level}")
        
        # Initialize default style
        style = {
            "style": "modern",
            "font_family": "sans",
            "headline_weight": "bold",
            "headline_size_factor": 0.08,
            "subheadline_size_factor": 0.035,
            "cta_style": "rounded",
            "text_effects": {
                "headline": "clean_gradient",
                "subheadline": "subtle_shadow",
                "body": "simple",
                "cta": "glass_effect",
                "brand": "minimal_elegant"
            },
            "text_colors": {
                "headline": (255, 255, 255, 255),
                "subheadline": (230, 230, 230, 255),
                "body": (200, 200, 200, 255),
                "cta": (255, 255, 255, 255),
                "brand": (255, 255, 255, 255)
            },
            "color_scheme": "monochromatic",
            "text_placement": "centered"
        }
        
        # Apply industry-specific style
        industry_style = self._get_industry_style(industry)
        if industry_style:
            style.update(industry_style)
        
        # Apply brand level-specific style
        brand_style = self._get_brand_level_style(brand_level)
        if brand_style:
            style.update(brand_style)
        
        # Apply style profile overrides if provided
        if style_profile:
            style = self._apply_style_overrides(style, style_profile)
        
        return style
    
    def _get_industry_style(self, industry: str) -> Dict[str, Any]:
        """
        Get typography style for a specific industry.
        
        Args:
            industry: Industry name
            
        Returns:
            Industry-specific style dictionary
        """
        if not industry:
            return {}
            
        industry_lower = industry.lower()
        
        # Try direct match
        for key, style in self.industry_typography_styles.items():
            if key.lower() == industry_lower:
                return style
                
        # Try keyword match
        for key, style in self.industry_typography_styles.items():
            if key.lower() in industry_lower or any(kw in industry_lower for kw in style.get('keywords', [])):
                return style
                
        # No match
        return {}
    
    def _get_brand_level_style(self, brand_level: str) -> Dict[str, Any]:
        """
        Get typography style for a specific brand level.
        
        Args:
            brand_level: Brand level name
            
        Returns:
            Brand level-specific style dictionary
        """
        if not brand_level:
            return {}
            
        level_lower = brand_level.lower()
        
        # Try direct match
        for key, style in self.brand_level_typography.items():
            if key.lower() == level_lower:
                return style
                
        # Try keyword match
        level_keywords = {
            'luxury': ['premium', 'high-end', 'exclusive', 'upscale'],
            'premium': ['quality', 'upper', 'professional'],
            'mid-range': ['standard', 'mid-tier', 'moderate'],
            'budget': ['affordable', 'value', 'economical', 'low-cost']
        }
        
        for level, keywords in level_keywords.items():
            if any(kw in level_lower for kw in keywords):
                return self.brand_level_typography.get(level, {})
                
        # No match
        return {}
    
    def _apply_style_overrides(self, base_style: Dict[str, Any], 
                             overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply style overrides to base style.
        
        Args:
            base_style: Base style dictionary
            overrides: Style overrides
            
        Returns:
            Updated style dictionary
        """
        # Make a deep copy of the base style
        result = base_style.copy()
        
        # Apply overrides
        for key, value in overrides.items():
            if key == 'color_overrides' and isinstance(value, dict):
                # Special handling for color overrides
                if 'text_colors' not in result:
                    result['text_colors'] = {}
                
                # Map color_overrides keys to text_colors
                mapping = {
                    'headline_color': 'headline',
                    'subheadline_color': 'subheadline',
                    'body_color': 'body',
                    'cta_text_color': 'cta',
                    'brand_color': 'brand',
                    'accent_color': 'accent'
                }
                
                for override_key, override_value in value.items():
                    if override_key in mapping:
                        result['text_colors'][mapping[override_key]] = override_value
                    else:
                        result['text_colors'][override_key] = override_value
            else:
                # Direct override
                result[key] = value
        
        return result
    
    def _select_fonts(self, typography_style: Dict[str, Any], 
                    text_elements: Dict[str, str], 
                    image_height: int) -> Dict[str, Any]:
        """
        Select appropriate fonts for each text element.
        
        Args:
            typography_style: Typography style
            text_elements: Text elements
            image_height: Image height for size calculations
            
        Returns:
            Dictionary of selected fonts
        """
        fonts = {}
        
        # Get style and font family
        style = typography_style.get('style', 'modern')
        font_family = typography_style.get('font_family', 'sans')
        
        # Get fonts using font manager
        if self.font_manager and hasattr(self.font_manager, 'get_font_pairing'):
            font_pair = self.font_manager.get_font_pairing(
                style=style,
                brand_name=None,
                industry=None,
                text_elements=text_elements
            )
            
            # Convert to proper font objects
            for element, font in font_pair.items():
                if element in ['headline', 'subheadline', 'body', 'cta', 'brand']:
                    fonts[element] = font
        else:
            # Fallback to basic font loading
            try:
                # Calculate base sizes
                headline_size = int(image_height * typography_style.get('headline_size_factor', 0.08))
                subheadline_size = int(image_height * typography_style.get('subheadline_size_factor', 0.035))
                body_size = int(image_height * 0.025)
                cta_size = int(image_height * 0.035)
                brand_size = int(image_height * 0.04)
                
                # Determine font weights
                headline_weight = typography_style.get('headline_weight', 'bold')
                subheadline_weight = typography_style.get('subheadline_weight', 'regular')
                
                # Load fonts
                if font_family == 'serif':
                    fonts['headline'] = self._load_font("Times-Bold" if headline_weight == 'bold' else "Times", headline_size)
                    fonts['subheadline'] = self._load_font("Times", subheadline_size)
                    fonts['body'] = self._load_font("Times", body_size)
                    fonts['cta'] = self._load_font("Times-Bold", cta_size)
                    fonts['brand'] = self._load_font("Times-Bold", brand_size)
                else:
                    fonts['headline'] = self._load_font("Arial-Bold" if headline_weight == 'bold' else "Arial", headline_size)
                    fonts['subheadline'] = self._load_font("Arial", subheadline_size)
                    fonts['body'] = self._load_font("Arial", body_size)
                    fonts['cta'] = self._load_font("Arial-Bold", cta_size)
                    fonts['brand'] = self._load_font("Arial-Bold", brand_size)
            except Exception as e:
                self.logger.error(f"Error loading fonts: {str(e)}")
                # Further fallback to most basic fonts
                try:
                    from PIL import ImageFont
                    default_font = ImageFont.load_default()
                    fonts = {
                        'headline': default_font,
                        'subheadline': default_font,
                        'body': default_font,
                        'cta': default_font,
                        'brand': default_font
                    }
                except:
                    self.logger.error("Critical error loading any fonts")
                    fonts = {
                        'headline': None,
                        'subheadline': None,
                        'body': None,
                        'cta': None,
                        'brand': None
                    }
        
        return fonts
    
    def _load_font(self, font_name: str, size: int) -> ImageFont.FreeTypeFont:
        """
        Load a font with intelligent fallback.
        
        Args:
            font_name: Font name
            size: Font size
            
        Returns:
            Font object
        """
        # Try using font manager if available
        if self.font_manager and hasattr(self.font_manager, '_load_font'):
            return self.font_manager._load_font(font_name, size)
            
        # Otherwise fallback to standard fonts
        try:
            from PIL import ImageFont
            
            # Common system font locations
            font_paths = [
                f"/usr/share/fonts/truetype/{font_name}.ttf",
                f"/usr/share/fonts/TTF/{font_name}.ttf",
                f"/Library/Fonts/{font_name}.ttf",
                f"C:\\Windows\\Fonts\\{font_name}.ttf",
                f"{font_name}.ttf"
            ]
            
            # Try standard fonts by name
            common_fonts = {
                "Arial": ["arial.ttf", "Arial.ttf", "ARIAL.TTF"],
                "Arial-Bold": ["arialbd.ttf", "Arial Bold.ttf", "Arial-Bold.ttf"],
                "Times": ["times.ttf", "Times.ttf", "Times New Roman.ttf"],
                "Times-Bold": ["timesbd.ttf", "Times Bold.ttf", "Times-Bold.ttf"],
                "Helvetica": ["Helvetica.ttf", "helvetica.ttf"],
                "Helvetica-Bold": ["Helvetica-Bold.ttf", "helvetica-bold.ttf"]
            }
            
            # Try to load the requested font
            if font_name in common_fonts:
                for font_file in common_fonts[font_name]:
                    for prefix in ["", "/usr/share/fonts/truetype/", "/Library/Fonts/", "C:\\Windows\\Fonts\\"]:
                        try:
                            return ImageFont.truetype(f"{prefix}{font_file}", size)
                        except:
                            continue
            
            # Try all the paths
            for path in font_paths:
                try:
                    return ImageFont.truetype(path, size)
                except:
                    continue
            
            # Last resort - use default font
            return ImageFont.load_default()
            
        except Exception as e:
            self.logger.error(f"Font loading error: {str(e)}")
            # Absolute last resort
            from PIL import ImageFont
            return ImageFont.load_default()
    
    def _calculate_font_sizes(self, fonts: Dict[str, Any], 
                           text_elements: Dict[str, str],
                           image_size: Tuple[int, int],
                           typography_style: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate optimal font sizes based on text length and image size.
        
        Args:
            fonts: Dictionary of font objects
            text_elements: Text elements
            image_size: Image size
            typography_style: Typography style
            
        Returns:
            Dictionary of sized fonts
        """
        width, height = image_size
        sized_fonts = {}
        
        # Get size factors from style or use defaults
        headline_factor = typography_style.get('headline_size_factor', self.font_size_ratios['headline'])
        subheadline_factor = typography_style.get('subheadline_size_factor', self.font_size_ratios['subheadline'])
        body_factor = typography_style.get('body_size_factor', self.font_size_ratios['body'])
        cta_factor = typography_style.get('cta_size_factor', self.font_size_ratios['cta'])
        brand_factor = typography_style.get('brand_size_factor', self.font_size_ratios['brand'])
        
        # Adjust factors based on text length to prevent overflow
        text_factors = {
            'headline': self._adjust_size_factor(headline_factor, text_elements.get('headline', ''), width),
            'subheadline': self._adjust_size_factor(subheadline_factor, text_elements.get('subheadline', ''), width),
            'body': self._adjust_size_factor(body_factor, text_elements.get('body', ''), width),
            'cta': self._adjust_size_factor(cta_factor, text_elements.get('call_to_action', ''), width),
            'brand': self._adjust_size_factor(brand_factor, text_elements.get('brand_name', ''), width)
        }
        
        # Calculate font sizes based on image height and adjusted factors
        for element, factor in text_factors.items():
            base_font = fonts.get(element)
            if base_font:
                # Calculate size
                size = int(height * factor)
                
                try:
                    # Try to load font with adjusted size
                    if hasattr(self.font_manager, '_load_font'):
                        sized_font = self.font_manager._load_font(
                            base_font.path if hasattr(base_font, 'path') else base_font,
                            size
                        )
                    else:
                        # Fallback to PIL font loading
                        from PIL import ImageFont
                        if hasattr(base_font, 'path'):
                            sized_font = ImageFont.truetype(base_font.path, size)
                        else:
                            # Use a system font with appropriate size
                            font_name = "Arial" if element != 'headline' else "Arial-Bold"
                            sized_font = self._load_font(font_name, size)
                except Exception as e:
                    self.logger.error(f"Error sizing font for {element}: {str(e)}")
                    sized_font = base_font  # Use original font if sizing fails
                
                sized_fonts[element] = sized_font
        
        return sized_fonts
    
    def _adjust_size_factor(self, base_factor: float, text: str, width: int) -> float:
        """
        Adjust size factor based on text length to prevent overflow.
        
        Args:
            base_factor: Base size factor
            text: Text string
            width: Available width
            
        Returns:
            Adjusted size factor
        """
        if not text:
            return base_factor
            
        # Calculate approximate width factor based on text length
        # Longer text needs smaller font
        text_length = len(text)
        
        # Adjust factor based on text length and available width
        if text_length > 50:
            factor = base_factor * 0.7
        elif text_length > 30:
            factor = base_factor * 0.8
        elif text_length > 15:
            factor = base_factor * 0.9
        else:
            factor = base_factor
            
        # Make sure factor doesn't get too small
        return max(factor, base_factor * 0.5)
    
    def _calculate_text_positions(self, fonts: Dict[str, Any],
                               text_elements: Dict[str, str],
                               image_size: Tuple[int, int],
                               analysis: Dict[str, Any],
                               typography_style: Dict[str, Any]) -> Dict[str, Tuple[int, int]]:
        """
        Calculate optimal positions for text elements.
        
        Args:
            fonts: Dictionary of fonts
            text_elements: Text elements
            image_size: Image size
            analysis: Image analysis
            typography_style: Typography style
            
        Returns:
            Dictionary of positions for each text element
        """
        width, height = image_size
        positions = {}
        
        # Get text placement style
        placement_style = typography_style.get('text_placement', 'centered')
        
        # Get text placement recommendations from analysis
        text_placement = analysis.get('text_placement_map', {})
        
        # Find appropriate text zone template
        template = self._get_text_zone_template(placement_style)
        
        # Calculate positions based on template and analysis
        for element, text in text_elements.items():
            if not text:
                continue
                
            # Map element name to standard name if needed
            std_element = element
            if element == 'call_to_action':
                std_element = 'cta'
            elif element == 'brand_name':
                std_element = 'brand'
                
            # Get font for this element
            font = fonts.get(std_element)
            if not font:
                continue
                
            # Get text dimensions
            text_width, text_height = self._get_text_dimensions(text, font)
            
            # Get zone for this element from template
            zone = template.get(std_element, {})
            
            # Calculate position based on zone and analysis
            position = self._calculate_element_position(
                std_element, 
                text, 
                text_width, 
                text_height, 
                width, 
                height, 
                zone, 
                text_placement,
                analysis
            )
            
            positions[element] = position
        
        return positions
    
    def _get_text_zone_template(self, placement_style: str) -> Dict[str, Dict[str, Any]]:
        """
        Get text zone template based on placement style.
        
        Args:
            placement_style: Text placement style
            
        Returns:
            Text zone template
        """
        return self.text_zone_templates.get(placement_style, self.text_zone_templates['centered'])
    
    def _calculate_element_position(self, element: str, text: str, text_width: int, text_height: int,
                                 width: int, height: int, zone: Dict[str, Any],
                                 text_placement: Dict[str, Any], analysis: Dict[str, Any]) -> Tuple[int, int]:
        """
        Calculate position for a specific text element.
        
        Args:
            element: Element name
            text: Text content
            text_width: Text width
            text_height: Text height
            width: Image width
            height: Image height
            zone: Zone information
            text_placement: Text placement analysis
            analysis: Overall image analysis
            
        Returns:
            (x, y) position for the text
        """
        # Get horizontal and vertical position information from zone
        h_pos = zone.get('h_pos', 'center')
        v_pos = zone.get('v_pos', 'middle')
        v_offset = zone.get('v_offset', 0.0)
        h_offset = zone.get('h_offset', 0.0)
        
        # Try to use optimized position from analysis
        regions = text_placement.get('regions', {})
        if element in regions:
            region = regions[element]
            opt_x, opt_y = region['position']
            
            # Apply adjustments based on zone
            if h_pos == 'left':
                opt_x = int(width * 0.1)
            elif h_pos == 'right':
                opt_x = int(width * 0.9)
            elif h_pos == 'center':
                opt_x = width // 2
                
            return (opt_x, opt_y)
        
        # Calculate position based on zone
        if h_pos == 'left':
            x = int(width * (0.1 + h_offset))
        elif h_pos == 'right':
            x = int(width * (0.9 + h_offset))
        else:  # center
            x = int(width * (0.5 + h_offset))
            
        if v_pos == 'top':
            y = int(height * (0.1 + v_offset))
        elif v_pos == 'bottom':
            y = int(height * (0.9 + v_offset))
        else:  # middle
            y = int(height * (0.5 + v_offset))
            
        # Special adjustments for each element type
        if element == 'headline':
            # Headlines typically at top or middle
            y = min(y, int(height * 0.3))
        elif element == 'subheadline':
            # Subheadlines below headlines
            headline_pos = regions.get('headline', {}).get('position', (width//2, height//4))
            y = headline_pos[1] + text_height + 20
        elif element == 'cta':
            # CTAs typically at bottom
            y = max(y, int(height * 0.85))
        elif element == 'brand':
            # Brand typically at top
            y = min(y, int(height * 0.15))
            
        return (x, y)
    
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
            # Try new Pillow method first
            bbox = font.getbbox(text)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            try:
                # Fall back to older method
                return font.getsize(text)
            except:
                # Rough estimate if all else fails
                size = getattr(font, 'size', 12)
                return int(len(text) * size * 0.6), int(size * 1.2)
    
    def _generate_text_colors(self, image: Image.Image, analysis: Dict[str, Any],
                           text_positions: Dict[str, Tuple[int, int]], 
                           typography_style: Dict[str, Any]) -> Dict[str, Tuple[int, int, int, int]]:
        """
    Generate optimized text colors for each element.
    
    Args:
        image: Original image
        analysis: Image analysis
        text_positions: Positions of text elements
        typography_style: Typography style
        
    Returns:
        Dictionary of colors for each text element
    """
    # Get predefined colors from typography style
        style_colors = typography_style.get('text_colors', {})
    
    # Get overall brightness from analysis
        is_dark = analysis.get('brightness_map', {}).get('is_dark', False)
        overall_brightness = analysis.get('brightness_map', {}).get('overall', 0.5)
    
    # Get dominant colors
        dominant_colors = analysis.get('dominant_colors', [])
    
    # Get color palette
        color_palette = analysis.get('color_palette', {})
    
    # Default colors based on image brightness
        default_text_color = (255, 255, 255, 255) if is_dark else (0, 0, 0, 255)
        accent_color = color_palette.get('accent', (41, 128, 185))
        if len(accent_color) == 3:
            accent_color = accent_color + (255,)
        
    # Generate colors for each text element
        colors = {}
    
        for element, position in text_positions.items():
            std_element = element
            if element == 'call_to_action':
                std_element = 'cta'
            elif element == 'brand_name':
                std_element = 'brand'
            
        # Use style color if available
            if std_element in style_colors:
                color = style_colors[std_element]
                if len(color) == 3:
                    color = color + (255,)
                colors[element] = color
                continue
            
        # Otherwise calculate optimal color based on local brightness
            x, y = position
            local_brightness = self._calculate_local_brightness(image, x, y, 50)
        
            if std_element == 'headline':
            # Headlines need maximum contrast
                colors[element] = (255, 255, 255, 255) if local_brightness < 0.5 else (0, 0, 0, 255)
            elif std_element == 'brand':
            # Brand often uses accent color
                if accent_color:
                # Check if accent has enough contrast
                    if self._has_sufficient_contrast(accent_color[:3], local_brightness):
                        colors[element] = accent_color
                    else:
                    # Use default high-contrast color
                        colors[element] = (255, 255, 255, 255) if local_brightness < 0.5 else (0, 0, 0, 255)
                else:
                    colors[element] = (255, 255, 255, 255) if local_brightness < 0.5 else (0, 0, 0, 255)
            elif std_element == 'cta':
            # CTA needs to stand out
                colors[element] = (255, 255, 255, 255)  # Text color for CTA button
            else:
            # Other elements use default colors with good contrast
                colors[element] = (230, 230, 230, 255) if local_brightness < 0.5 else (50, 50, 50, 255)
    
    # Store button color specifically for CTA
        if 'call_to_action' in colors:
            button_color = accent_color if accent_color else (41, 128, 185, 230)
        
        # Get the text color
            cta_text_color = colors['call_to_action'][:3]
        
        # Calculate background brightness for button
            button_brightness = (button_color[0] * 299 + button_color[1] * 587 + button_color[2] * 114) / 1000 / 255
        
        # Ensure contrast between button and text
            if not self._has_sufficient_contrast(cta_text_color, button_brightness):
            # Adjust button color to ensure contrast with text
                if button_brightness < 0.5:
                # Button is dark, lighten it
                    button_color = (min(255, button_color[0] + 50), 
                              min(255, button_color[1] + 50), 
                              min(255, button_color[2] + 50), 
                              button_color[3])
                else:
                # Button is light, darken it
                    button_color = (max(0, button_color[0] - 50), 
                              max(0, button_color[1] - 50), 
                              max(0, button_color[2] - 50), 
                              button_color[3])
        
            colors['cta_button'] = button_color
    
        return colors
    
    def _calculate_local_brightness(self, image: Image.Image, x: int, y: int, radius: int) -> float:
        """
        Calculate local brightness around a point.
        
        Args:
            image: Image
            x: X coordinate
            y: Y coordinate
            radius: Radius to consider
            
        Returns:
            Brightness value (0-1)
        """
        # Ensure point is within image bounds
        width, height = image.size
        if x < 0 or y < 0 or x >= width or y >= height:
            return 0.5  # Default for out-of-bounds
            
        # Calculate region bounds
        left = max(0, x - radius)
        upper = max(0, y - radius)
        right = min(width, x + radius)
        lower = min(height, y + radius)
        
        # Extract region
        region = image.crop((left, upper, right, lower))
        
        # Convert to grayscale and calculate average brightness
        gray_region = region.convert('L')
        brightness = sum(gray_region.getdata()) / (len(gray_region.getdata()) * 255)
        
        return brightness
    
    def _has_sufficient_contrast(self, color: Tuple[int, int, int], 
                          background_brightness: float) -> bool:
        """
    Check if a color has sufficient contrast with the background.
    
    Args:
        color: Color to check (RGB tuple)
        background_brightness: Background brightness value (0-1)
        
    Returns:
        True if contrast is sufficient
    """
        try:
        # Calculate relative luminance of the color
            r, g, b = [c/255.0 for c in color]
            luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        # Check contrast with background
            if background_brightness < 0.5:
            # Dark background
                return luminance > 0.5
            else:
            # Light background
                return luminance < 0.5
        except Exception as e:
            self.logger.error(f"Error checking contrast: {str(e)}")
        # Default to True to allow operation to continue
            return True
    
    def _apply_text_elements(self, draw: ImageDraw.Draw, overlay: Image.Image,
                          text_elements: Dict[str, str], fonts: Dict[str, Any],
                          positions: Dict[str, Tuple[int, int]], colors: Dict[str, Tuple[int, int, int, int]],
                          typography_style: Dict[str, Any], analysis: Dict[str, Any],
                          original_image: Image.Image) -> None:
        """
        Apply all text elements with appropriate effects.
        
        Args:
            draw: ImageDraw object
            overlay: Text overlay image
            text_elements: Text elements
            fonts: Font objects
            positions: Text positions
            colors: Text colors
            typography_style: Typography style
            analysis: Image analysis
            original_image: Original image
        """
        # Get text effects from style
        effects = typography_style.get('text_effects', {})
        
        # Process each text element
        for element, text in text_elements.items():
            if not text:
                continue
                
            # Standardize element name
            std_element = element
            if element == 'call_to_action':
                std_element = 'cta'
            elif element == 'brand_name':
                std_element = 'brand'
                
            # Get font, position, color and effect
            font = fonts.get(std_element)
            if not font:
                continue
                
            position = positions.get(element)
            if not position:
                continue
                
            color = colors.get(element, (255, 255, 255, 255))
            
            effect_name = effects.get(std_element, 'simple')
            
            # Apply effect using text effects engine if available
            if self.text_effects and hasattr(self.text_effects, 'apply_text_effect'):
                self.logger.info(f"Applying effect '{effect_name}' to text: {text[:20]}{'...' if len(text) > 20 else ''}")
                
                # Special handling for CTA button
                if std_element == 'cta':
                    # Create button with specific style
                    button_style = typography_style.get('cta_style', 'rounded')
                    button_color = colors.get('cta_button', (41, 128, 185, 230))
                    
                    self.text_effects.create_button(
                        draw=draw,
                        text=text,
                        position=position,
                        font=font,
                        button_style=button_style,
                        text_color=color,
                        button_color=button_color
                    )
                else:
                    # Apply regular text effect
                    self.text_effects.apply_text_effect(
                        draw=draw,
                        text=text,
                        position=position,
                        font=font,
                        alignment="center",
                        effect=effect_name,
                        text_color=color,
                        accent_color=colors.get('accent', None),
                        typography_style=typography_style,
                        image=original_image
                    )
            else:
                # Fallback to simple text rendering
                self._apply_fallback_text_effect(
                    draw, 
                    text, 
                    position, 
                    font, 
                    color, 
                    effect_name, 
                    std_element,
                    colors.get('cta_button', (41, 128, 185, 230)) if std_element == 'cta' else None
                )
    
    def _apply_fallback_text_effect(self, draw: ImageDraw.Draw, text: str, 
                                 position: Tuple[int, int], font: ImageFont.FreeTypeFont,
                                 color: Tuple[int, int, int, int], effect: str,
                                 element: str, button_color: Optional[Tuple[int, int, int, int]] = None) -> None:
        """
        Apply fallback text effect when text effects engine is unavailable.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: Text position
            font: Font to use
            color: Text color
            effect: Effect name
            element: Element type
            button_color: Button color for CTA
        """
        x, y = position
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Center text
        if element != 'cta':
            # All elements except CTA are center-aligned at their position
            x = x - text_width // 2
            
            # Draw shadow for most elements
            draw.text(
                (x + 2, y + 2),
                text,
                font=font,
                fill=(0, 0, 0, 100)
            )
            
            # Draw main text
            draw.text(
                (x, y),
                text,
                font=font,
                fill=color
            )
        else:
            # Special handling for CTA button
            if button_color:
                # Create button
                padding_x = 20
                padding_y = 10
                
                button_width = text_width + padding_x * 2
                button_height = text_height + padding_y * 2
                
                # Button coordinates
                button_left = x - button_width // 2
                button_top = y - button_height // 2
                button_right = button_left + button_width
                button_bottom = button_top + button_height
                
                # Draw button shadow
                draw.rounded_rectangle(
                    [(button_left + 2, button_top + 2), (button_right + 2, button_bottom + 2)],
                    radius=8,
                    fill=(0, 0, 0, 100)
                )
                
                # Draw button
                draw.rounded_rectangle(
                    [(button_left, button_top), (button_right, button_bottom)],
                    radius=8,
                    fill=button_color
                )
                
                # Draw text
                text_x = x - text_width // 2
                text_y = y - text_height // 2
                
                draw.text(
                    (text_x, text_y),
                    text,
                    font=font,
                    fill=color
                )
            else:
                # Just draw text if no button color specified
                x = x - text_width // 2
                draw.text(
                    (x, y),
                    text,
                    font=font,
                    fill=color
                )
    
    def _composite_with_blending(self, image: Image.Image, overlay: Image.Image, 
                              analysis: Dict[str, Any]) -> Image.Image:
        """
        Composite overlay with original image using advanced blending.
        
        Args:
            image: Original image
            overlay: Text overlay
            analysis: Image analysis
            
        Returns:
            Composited image
        """
        # Ensure both images are RGBA
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
            
        # Simple alpha composite
        return Image.alpha_composite(image, overlay)
    
    def _initialize_industry_styles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize typography styles for different industries."""
        return {
            "luxury": {
                "style": "luxury",
                "font_family": "serif",
                "headline_weight": "light",
                "headline_size_factor": 0.07,
                "subheadline_size_factor": 0.035,
                "text_effects": {
                    "headline": "elegant_serif",
                    "subheadline": "minimal_elegant",
                    "body": "simple",
                    "cta": "minimal_line",
                    "brand": "luxury_metallic"
                },
                "cta_style": "minimal_line",
                "text_placement": "centered",
                "color_scheme": "monochromatic",
                "keywords": ["premium", "high-end", "exclusive", "upscale"]
            },
            "fashion": {
                "style": "minimal",
                "font_family": "sans",
                "headline_weight": "light",
                "headline_size_factor": 0.08,
                "subheadline_size_factor": 0.03,
                "text_effects": {
                    "headline": "minimal_elegant",
                    "subheadline": "simple",
                    "body": "simple",
                    "cta": "minimal_line",
                    "brand": "simple"
                },
                "cta_style": "minimal_line",
                "text_placement": "centered",
                "color_scheme": "monochromatic",
                "keywords": ["apparel", "clothing", "style", "design"]
            },
            "technology": {
                "style": "modern",
                "font_family": "sans",
                "headline_weight": "bold",
                "headline_size_factor": 0.075,
                "subheadline_size_factor": 0.035,
                "text_effects": {
                    "headline": "clean_gradient",
                    "subheadline": "subtle_shadow",
                    "body": "simple",
                    "cta": "rounded",
                    "brand": "clean_gradient"
                },
                "cta_style": "rounded",
                "text_placement": "dynamic",
                "color_scheme": "complementary",
                "keywords": ["tech", "software", "digital", "electronic"]
            },
            "beauty": {
                "style": "elegant",
                "font_family": "serif",
                "headline_weight": "light",
                "headline_size_factor": 0.07,
                "subheadline_size_factor": 0.03,
                "text_effects": {
                    "headline": "minimal_elegant",
                    "subheadline": "simple",
                    "body": "simple",
                    "cta": "rounded",
                    "brand": "subtle_glow"
                },
                "cta_style": "minimal_line",
                "text_placement": "centered",
                "color_scheme": "monochromatic",
                "keywords": ["cosmetics", "makeup", "skincare", "perfume"]
            },
            "automotive": {
                "style": "bold",
                "font_family": "sans",
                "headline_weight": "bold",
                "headline_size_factor": 0.08,
                "subheadline_size_factor": 0.035,
                "text_effects": {
                    "headline": "dynamic_bold",
                    "subheadline": "subtle_shadow",
                    "body": "simple",
                    "cta": "pill",
                    "brand": "clean_gradient"
                },
                "cta_style": "pill",
                "text_placement": "dynamic",
                "color_scheme": "complementary",
                "keywords": ["car", "vehicle", "automotive", "transport"]
            },
            "food_beverage": {
                "style": "playful",
                "font_family": "sans",
                "headline_weight": "bold",
                "headline_size_factor": 0.08,
                "subheadline_size_factor": 0.04,
                "text_effects": {
                    "headline": "shadow",
                    "subheadline": "subtle_bg",
                    "body": "simple",
                    "cta": "rounded",
                    "brand": "clean_gradient"
                },
                "cta_style": "rounded",
                "text_placement": "dynamic",
                "color_scheme": "analogous",
                "keywords": ["food", "beverage", "drink", "restaurant"]
            },
            "perfumery": {
                "style": "elegant",
                "font_family": "serif",
                "headline_weight": "light",
                "headline_size_factor": 0.07,
                "subheadline_size_factor": 0.035,
                "text_effects": {
                    "headline": "elegant_serif",
                    "subheadline": "minimal_elegant",
                    "body": "simple",
                    "cta": "minimal_line",
                    "brand": "subtle_glow"
                },
                "cta_style": "minimal_line",
                "text_placement": "centered",
                "color_scheme": "monochromatic",
                "keywords": ["fragrance", "scent", "cologne", "perfume"]
            }
        }
    # Add these utility methods to your EnhancedTypographySystem class

    def _ensure_float32(self, array: np.ndarray) -> np.ndarray:
        """
    Ensure array is float32 type for consistent OpenCV operations.
    
    Args:
        array: Input numpy array
        
    Returns:
        Array converted to float32 type
    """
        if array is None:
            return None
        return array.astype(np.float32) if array.dtype != np.float32 else array

    def _safe_cv_operation(self, operation_name: str, *args, **kwargs):
        """
    Safely execute OpenCV operations with proper error handling.
    
    Args:
        operation_name: Name of OpenCV operation (e.g., 'add', 'subtract')
        *args: Arguments for the operation
        **kwargs: Keyword arguments for the operation
        
    Returns:
        Result of the operation or fallback value
    """
        try:
        # Get the operation from OpenCV
            operation = getattr(cv2, operation_name)
        
        # Ensure all array arguments are float32
            new_args = []
            for arg in args:
                if isinstance(arg, np.ndarray):
                    new_args.append(self._ensure_float32(arg))
                else:
                    new_args.append(arg)
        
        # Add explicit dtype if not provided
            if 'dtype' not in kwargs and operation_name in ['add', 'subtract', 'multiply', 'divide']:
                kwargs['dtype'] = cv2.CV_32F
        
        # Execute operation
            return operation(*new_args, **kwargs)
        except Exception as e:
            self.logger.error(f"Error in OpenCV {operation_name}: {str(e)}")
        
        # Create appropriate fallback based on operation
            if len(args) > 0 and isinstance(args[0], np.ndarray):
                shape = args[0].shape
                if operation_name in ['add', 'subtract', 'multiply', 'divide', 'absdiff']:
                    return np.zeros(shape, dtype=np.float32)
                elif operation_name == 'normalize':
                    return args[0]  # Return input array unnormalized
        
        # Generic fallback
            return None
    
    def _initialize_brand_level_styles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize typography styles for different brand levels."""
        return {
            "luxury": {
                "font_family": "serif",
                "headline_weight": "light",
                "text_effects": {
                    "headline": "elegant_serif",
                    "subheadline": "minimal_elegant",
                    "body": "simple",
                    "cta": "minimal_line",
                    "brand": "elegant_serif"
                },
                "cta_style": "minimal_line"
            },
            "premium": {
                "font_family": "serif",
                "headline_weight": "light",
                "text_effects": {
                    "headline": "premium_gradient",
                    "subheadline": "minimal_elegant",
                    "body": "simple",
                    "cta": "rounded",
                    "brand": "clean_gradient"
                },
                "cta_style": "rounded"
            },
            "mid-range": {
                "font_family": "sans",
                "headline_weight": "bold",
                "text_effects": {
                    "headline": "clean_gradient",
                    "subheadline": "subtle_shadow",
                    "body": "simple",
                    "cta": "rounded",
                    "brand": "clean_gradient"
                },
                "cta_style": "rounded"
            },
            "budget": {
                "font_family": "sans",
                "headline_weight": "bold",
                "text_effects": {
                    "headline": "shadow",
                    "subheadline": "subtle_shadow",
                    "body": "simple",
                    "cta": "pill",
                    "brand": "simple"
                },
                "cta_style": "pill"
            }
        }
    
    def _initialize_product_styles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize typography styles for specific product types."""
        return {
            "perfume": {
                "font_family": "serif",
                "headline_weight": "light",
                "text_effects": {
                    "headline": "elegant_serif",
                    "subheadline": "minimal_elegant",
                    "body": "simple",
                    "cta": "minimal_line",
                    "brand": "subtle_glow"
                },
                "cta_style": "minimal_line",
                "text_placement": "centered"
            },
            "smartphone": {
                "font_family": "sans",
                "headline_weight": "bold",
                "text_effects": {
                    "headline": "clean_gradient",
                    "subheadline": "subtle_shadow",
                    "body": "simple",
                    "cta": "rounded",
                    "brand": "clean_gradient"
                },
                "cta_style": "rounded",
                "text_placement": "dynamic"
            },
            "car": {
                "font_family": "sans",
                "headline_weight": "bold",
                "text_effects": {
                    "headline": "dynamic_bold",
                    "subheadline": "subtle_shadow",
                    "body": "simple",
                    "cta": "pill",
                    "brand": "clean_gradient"
                },
                "cta_style": "pill",
                "text_placement": "dynamic"
            },
            "watch": {
                "font_family": "serif",
                "headline_weight": "light",
                "text_effects": {
                    "headline": "elegant_serif",
                    "subheadline": "minimal_elegant",
                    "body": "simple",
                    "cta": "minimal_line",
                    "brand": "luxury_metallic"
                },
                "cta_style": "minimal_line",
                "text_placement": "centered"
            }
        }
    
    def _initialize_effect_mapping(self) -> Dict[str, Dict[str, str]]:
        """Initialize mapping of industry/brand level to effect names."""
        return {
            "industry": {
                "luxury": {
                    "headline": "elegant_serif",
                    "subheadline": "minimal_elegant",
                    "body": "simple",
                    "cta": "minimal_line",
                    "brand": "elegant_serif"
                },
                "fashion": {
                    "headline": "minimal_elegant",
                    "subheadline": "simple",
                    "body": "simple",
                    "cta": "minimal_line",
                    "brand": "minimal_elegant"
                },
                "technology": {
                    "headline": "clean_gradient",
                    "subheadline": "subtle_shadow",
                    "body": "simple", 
                    "cta": "glass_effect",
                    "brand": "clean_gradient"
                },
                "automotive": {
                    "headline": "dynamic_bold",
                    "subheadline": "subtle_shadow",
                    "body": "simple",
                    "cta": "pill",
                    "brand": "clean_gradient"
                }
            },
            "brand_level": {
                "luxury": {
                    "headline": "elegant_serif",
                    "subheadline": "minimal_elegant",
                    "body": "simple",
                    "cta": "minimal_line",
                    "brand": "elegant_serif"
                },
                "premium": {
                    "headline": "premium_gradient",
                    "subheadline": "subtle_shadow",
                    "body": "simple",
                    "cta": "rounded",
                    "brand": "clean_gradient"
                },
                "mid-range": {
                    "headline": "clean_gradient",
                    "subheadline": "subtle_shadow",
                    "body": "simple",
                    "cta": "glass_effect",
                    "brand": "clean_gradient"
                },
                "budget": {
                    "headline": "shadow",
                    "subheadline": "subtle_shadow",
                    "body": "simple",
                    "cta": "pill",
                    "brand": "simple"
                }
            }
        }
    
    def _initialize_text_zone_templates(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Initialize templates for text zones in different layout styles."""
        return {
            "centered": {
                "headline": {
                    "h_pos": "center",
                    "v_pos": "top",
                    "v_offset": 0.2
                },
                "subheadline": {
                    "h_pos": "center",
                    "v_pos": "top",
                    "v_offset": 0.3
                },
                "body": {
                    "h_pos": "center",
                    "v_pos": "middle",
                    "v_offset": 0.1
                },
                "cta": {
                    "h_pos": "center",
                    "v_pos": "bottom",
                    "v_offset": -0.15
                },
                "brand": {
                    "h_pos": "center",
                    "v_pos": "top",
                    "v_offset": 0.1
                }
            },
            "dynamic": {
                "headline": {
                    "h_pos": "center",
                    "v_pos": "top",
                    "v_offset": 0.15
                },
                "subheadline": {
                    "h_pos": "center", 
                    "v_pos": "top",
                    "v_offset": 0.25
                },
                "body": {
                    "h_pos": "center",
                    "v_pos": "middle",
                    "v_offset": 0
                },
                "cta": {
                    "h_pos": "center",
                    "v_pos": "bottom",
                    "v_offset": -0.1
                },
                "brand": {
                    "h_pos": "right",
                    "v_pos": "top",
                    "v_offset": 0.05,
                    "h_offset": -0.05
                }
            },
            "split": {
                "headline": {
                    "h_pos": "left",
                    "v_pos": "middle",
                    "h_offset": 0.1,
                    "v_offset": -0.1
                },
                "subheadline": {
                    "h_pos": "left",
                    "v_pos": "middle",
                    "h_offset": 0.1,
                    "v_offset": 0
                },
                "body": {
                    "h_pos": "left",
                    "v_pos": "middle",
                    "h_offset": 0.1,
                    "v_offset": 0.1
                },
                "cta": {
                    "h_pos": "left",
                    "v_pos": "middle",
                    "h_offset": 0.1,
                    "v_offset": 0.2
                },
                "brand": {
                    "h_pos": "left",
                    "v_pos": "top",
                    "h_offset": 0.1,
                    "v_offset": 0.05
                }
            },
            "bottom": {
                "headline": {
                    "h_pos": "center",
                    "v_pos": "bottom",
                    "v_offset": -0.3
                },
                "subheadline": {
                    "h_pos": "center",
                    "v_pos": "bottom",
                    "v_offset": -0.2
                },
                "body": {
                    "h_pos": "center",
                    "v_pos": "bottom",
                    "v_offset": -0.15
                },
                "cta": {
                    "h_pos": "center",
                    "v_pos": "bottom",
                    "v_offset": -0.05
                },
                "brand": {
                    "h_pos": "right",
                    "v_pos": "top",
                    "h_offset": -0.05,
                    "v_offset": 0.05
                }
            }
        }