"""
Enhanced Product Image Integration
Improvements for professional ad generation with better background removal, 
image integration, and visual effects.
"""
import os
import numpy as np
import logging
import traceback
from typing import Dict, Optional, Tuple, List, Any
from datetime import datetime
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageChops, ImageOps,ImageFont
import requests
from io import BytesIO
import random
__all__ = ['ProductImageIntegrator', 'EnhancedProductIntegrator']

class EnhancedProductIntegrator:
    """
    Enhanced version of ProductImageIntegrator with improved background removal,
    image integration, and professional effects.
    """
    
    def __init__(self, openai_api_key=None):
        """Initialize enhanced product integrator."""
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.setup_logging()
        
        # Create output directories
        os.makedirs("output/images/products", exist_ok=True)
        os.makedirs("output/images/enhanced", exist_ok=True)
        os.makedirs("output/images/backgrounds", exist_ok=True)
        os.makedirs("output/images/composites", exist_ok=True)
        
        # Try to import OpenAI
        try:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            self.has_openai = True
            self.logger.info("OpenAI client initialized successfully")
        except ImportError:
            self.has_openai = False
            self.logger.warning("OpenAI package not installed. Some features may be limited.")
            self.openai_client = None
    
    def setup_logging(self):
        """Set up detailed logging configuration."""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_format)
        self.logger = logging.getLogger("EnhancedProductIntegrator")
        
        # Add file handler for persistent logs
        try:
            os.makedirs("logs", exist_ok=True)
            file_handler = logging.FileHandler(f"logs/product_integrator_{datetime.now().strftime('%Y%m%d')}.log")
            file_handler.setFormatter(logging.Formatter(log_format))
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not set up log file: {e}")
    def process_product_image(self, image_path: str, product_type: str, remove_background: bool = True) -> Dict[str, Any]:
        """
    Enhanced processing for product images with significantly improved background removal
    and quality preservation.
    
    Args:
        image_path: Path to the product image
        product_type: Type of product (helps with specialized processing)
        remove_background: Whether to remove the background
        
    Returns:
        Dictionary with processed image paths and metadata
    """
    # Validate image path upfront
        if not image_path or not isinstance(image_path, str):
            self.logger.error(f"Invalid image path: {image_path}")
            raise ValueError(f"Invalid image path provided: {image_path}")
        
        if not os.path.exists(image_path):
            self.logger.error(f"Image not found: {image_path}")
            raise FileNotFoundError(f"Product image not found: {image_path}")
    
        self.logger.info(f"Processing product image: {image_path}")
    
    # Load and validate image
        product_img = Image.open(image_path).convert("RGBA")
    
    # Analyze image quality and dimensions for better processing
        quality_score = self._analyze_image_quality(product_img)
        self.logger.info(f"Image quality score: {quality_score:.2f}/10")
    
    # Save original product image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_path = f"output/images/products/original_{timestamp}.png"
        product_img.save(original_path, "PNG", quality=100)
    
    # Step 1: Remove background with significantly improved methods
        if remove_background:
        # Use tiered background removal approach for best results
            product_img = self._enhanced_background_removal(product_img, product_type)
            background_removed_path = f"output/images/products/no_bg_{timestamp}.png"
            product_img.save(background_removed_path, "PNG", quality=100)
            self.logger.info(f"Background removed and saved to: {background_removed_path}")
        else:
            background_removed_path = original_path
    
    # Step 2: Advanced image enhancement for professional quality
        enhanced_img = self._professional_product_enhancement(product_img, product_type)
        enhanced_path = f"output/images/enhanced/enhanced_{timestamp}.png"
        enhanced_img.save(enhanced_path, "PNG", quality=100)
        self.logger.info(f"Enhanced product saved to: {enhanced_path}")
    
    # Analyze image for integration parameters
        analysis = self._analyze_product_image(enhanced_img, product_type)
    
        return {
        "original_path": original_path,
        "background_removed_path": background_removed_path,
        "enhanced_path": enhanced_path,
        "dimensions": enhanced_img.size,
        "transparent_bg": remove_background,
        "product_type": product_type,
        "analysis": analysis,
        "timestamp": timestamp,
        "quality_score": quality_score
    }

    def _analyze_background_composition(self, background: Image.Image) -> Dict[str, Any]:
        """
    Analyze background image for composition, focal points, and visual weight.
    
    Args:
        background: Background image
        
    Returns:
        Dictionary with background analysis
    """
        width, height = background.size
    
    # Convert to grayscale for analysis
        bg_gray = background.convert('L')
    
    # Sample in a grid to determine visual weight distribution
        grid_size = 10
        grid_w = width // grid_size
        grid_h = height // grid_size
    
        weight_left = 0
        weight_right = 0
        weight_top = 0
        weight_bottom = 0
        total_pixels = 0
    
        for y in range(0, height, grid_h):
            for x in range(0, width, grid_w):
            # Sample the brightness at this point
                try:
                    brightness = bg_gray.getpixel((x, y)) / 255.0
                
                # Contribute to the respective quadrant
                    if x < width // 2:
                        weight_left += 1 - brightness  # Darker = more weight
                    else:
                        weight_right += 1 - brightness
                    
                    if y < height // 2:
                        weight_top += 1 - brightness
                    else:
                        weight_bottom += 1 - brightness
                    
                    total_pixels += 1
                except IndexError:
                    continue
    
    # Normalize weights
        if total_pixels > 0:
            weight_left /= total_pixels / 2
            weight_right /= total_pixels / 2
            weight_top /= total_pixels / 2
            weight_bottom /= total_pixels / 2
    
    # Check if it's a minimalist background (low variance in brightness)
        brightness_values = []
        for y in range(0, height, grid_h):
            for x in range(0, width, grid_w):
                try:
                    brightness_values.append(bg_gray.getpixel((x, y)) / 255.0)
                except IndexError:
                    continue
                
        import numpy as np
        brightness_variance = np.var(brightness_values) if brightness_values else 0
        is_minimalist = brightness_variance < 0.05
    
    # Calculate negative space (areas with consistent brightness)
        negative_space = 0.5  # Default
        if brightness_values:
        # Count pixels with brightness close to the mode
            from collections import Counter
            rounded_values = [round(b * 10) / 10 for b in brightness_values]
            counts = Counter(rounded_values)
            most_common_brightness = counts.most_common(1)[0][0]
            similar_count = sum(counts[k] for k in counts if abs(k - most_common_brightness) <= 0.2)
            negative_space = similar_count / len(brightness_values)
    
    # Determine focal points (simplified)
        focal_points = []
    
    # 1. Add rule of thirds points
        for x_ratio in [1/3, 2/3]:
            for y_ratio in [1/3, 2/3]:
                focal_points.append((int(width * x_ratio), int(height * y_ratio)))
    
    # 2. Add center point
        focal_points.append((width // 2, height // 2))
    
        return {
        'weight_left': weight_left,
        'weight_right': weight_right,
        'weight_top': weight_top,
        'weight_bottom': weight_bottom,
        'is_minimalist': is_minimalist,
        'negative_space': negative_space,
        'focal_points': focal_points
    }
    
    def _analyze_image_quality(self, image: Image.Image) -> float:
        """
        Analyze the quality of an image using multiple metrics.
        
        Args:
            image: PIL Image to analyze
            
        Returns:
            Quality score from 0-10
        """
        # Check dimensions
        width, height = image.size
        dimension_score = min(10, max(1, min(width, height) / 100))
        
        # Check for transparency
        has_transparency = False
        if image.mode == 'RGBA':
            _, _, _, alpha = image.split()
            transparent_pixels = np.sum(np.array(alpha) < 250)
            has_transparency = transparent_pixels > 0
        
        # Calculate contrast and sharpness
        gray_img = image.convert('L')
        
        # Contrast score
        gray_array = np.array(gray_img)
        contrast = np.std(gray_array) / 128  # Normalize
        contrast_score = min(10, max(1, contrast * 10))
        
        # Sharpness approximation
        try:
            blurred = gray_img.filter(ImageFilter.GaussianBlur(radius=2))
            diff = ImageChops.difference(gray_img, blurred)
            sharpness = np.mean(np.array(diff)) / 40  # Normalize
            sharpness_score = min(10, max(1, sharpness * 10))
        except:
            sharpness_score = 5  # Default if calculation fails
        
        # Final weighted score
        quality_score = (
            dimension_score * 0.3 + 
            contrast_score * 0.3 + 
            sharpness_score * 0.4
        )
        
        return quality_score
    def _calculate_optimal_placement(self, product: Image.Image, background: Image.Image, brand_analysis: Dict[str, Any]) -> Dict[str, int]:
        """
    Calculate optimal placement for any product type on the background.
    
    Args:
        product: Product image
        background: Background image
        brand_analysis: Brand analysis information
        
    Returns:
        Dictionary with placement coordinates
    """
        self.logger.info("Calculating optimal product placement")
    
    # Get image dimensions
        product_width, product_height = product.size
        bg_width, bg_height = background.size
    
    # Calculate product aspect ratio
        product_ratio = product_width / product_height
    
    # Extract brand parameters (if available)
        industry = brand_analysis.get('industry', '').lower()
        brand_level = brand_analysis.get('brand_level', '').lower()
    
    # Analyze background for composition zones
        bg_analysis = self._analyze_background_composition(background)
    
    # Determine product orientation
        if product_height > product_width * 1.2:
            orientation = "portrait"
        elif product_width > product_height * 1.2:
            orientation = "landscape"
        else:
            orientation = "square"
    
    # Determine optimal scale factor based on negative space in background
        negative_space = bg_analysis.get('negative_space', 0.5)
        base_scale = 0.45 + (0.25 * (1 - negative_space))  # Scale between 45-70% based on negative space
    
    # Fine-tune scale based on brand level
        if 'luxury' in brand_level:
        # Luxury brands typically benefit from more negative space
            scale_factor = base_scale * 0.9
        elif 'premium' in brand_level:
            scale_factor = base_scale * 0.95
        elif 'budget' in brand_level:
        # Budget/value brands often use larger product imagery
            scale_factor = base_scale * 1.1
        else:
            scale_factor = base_scale
    
    # Cap maximum scale to ensure product doesn't overwhelm composition
        scale_factor = min(scale_factor, 0.75)
    
    # Calculate new dimensions while maintaining aspect ratio
        if orientation == "landscape":
            new_width = int(bg_width * scale_factor)
            new_height = int(new_width / product_ratio)
        else:  # portrait or square
            new_height = int(bg_height * scale_factor)
            new_width = int(new_height * product_ratio)
    
    # Ensure product fits within background with a margin
        margin = int(bg_width * 0.05)  # 5% margin
        new_width = min(new_width, bg_width - margin * 2)
        new_height = min(new_height, bg_height - margin * 2)
    
    # Use focal point or rule-of-thirds point based on brand level and background analysis
        focal_points = bg_analysis.get('focal_points', [(bg_width // 2, bg_height // 2)])
    
    # Select placement strategy based on background and brand
        if bg_analysis.get('is_minimalist', False) or 'luxury' in brand_level:
        # For minimalist backgrounds or luxury brands, use rule of thirds
            x_center = int(bg_width * (1/3 if bg_analysis.get('weight_right', 0) > 0.6 else 2/3))
            y_center = int(bg_height * 0.5)  # Center vertically
        elif focal_points and len(focal_points) > 0:
        # Use primary focal point for placement
            primary_focal = focal_points[0]
            x_center, y_center = primary_focal
        else:
        # Default to slightly off-center for visual interest
            x_center = int(bg_width * 0.52)
            y_center = int(bg_height * 0.48)
    
    # Adjust placement based on visual weight in background
        if bg_analysis.get('weight_left', 0) > 0.6:
        # If background is heavy on left, move product right
            x_center = int(bg_width * 0.6)
        elif bg_analysis.get('weight_right', 0) > 0.6:
        # If background is heavy on right, move product left
            x_center = int(bg_width * 0.4)
    
    # Calculate top-left coordinates for placement
        x = max(margin, x_center - new_width // 2)
        y = max(margin, y_center - new_height // 2)
    
    # Ensure product doesn't go off-edge
        if x + new_width > bg_width - margin:
            x = bg_width - new_width - margin
        if y + new_height > bg_height - margin:
            y = bg_height - new_height - margin
    
    # Log placement decision
        self.logger.info(f"Calculated placement: x={x}, y={y}, width={new_width}, height={new_height}")
    
        return {
        "x": x,
        "y": y,
        "width": new_width,
        "height": new_height,
        "center_x": x_center,
        "center_y": y_center,
        "scale_factor": scale_factor,
        "orientation": orientation
    }
    
    def _enhanced_background_removal(self, image: Image.Image, product_type: str) -> Image.Image:
        """
        Enhanced background removal using advanced algorithms and multi-tiered approach.
        Significantly improved from the original version.
        
        Args:
            image: PIL Image to process
            product_type: Type of product for specialized processing
            
        Returns:
            Image with transparent background
        """
        # Try to use OpenAI first for best results
        if self.has_openai and self.openai_client:
            try:
                self.logger.info("Attempting advanced background removal with OpenAI")
                result = self._remove_background_with_openai(image)
                
                # Verify quality of result
                quality = self._evaluate_transparency_quality(result)
                if quality > 6.0:  # Good quality threshold
                    self.logger.info(f"OpenAI background removal successful with quality score: {quality:.2f}")
                    return result
                else:
                    self.logger.info(f"OpenAI result below quality threshold ({quality:.2f}), trying alternative methods")
            except Exception as e:
                self.logger.warning(f"OpenAI background removal failed: {str(e)}. Trying advanced alternatives.")
        
        # Multi-method approach for best results
        results = []
        
        # Method 1: Advanced U2Net-inspired edge detection
        try:
            self.logger.info("Attempting advanced edge-based background removal")
            edge_result = self._advanced_edge_based_removal(image, product_type)
            if self._validate_transparency(edge_result):
                quality = self._evaluate_transparency_quality(edge_result)
                results.append(("edge", edge_result, quality))
                self.logger.info(f"Edge method quality: {quality:.2f}")
        except Exception as e:
            self.logger.warning(f"Advanced edge-based removal failed: {str(e)}")
        
        # Method 2: Improved color-based segmentation with clustering
        try:
            self.logger.info("Attempting improved color-based background removal")
            color_result = self._improved_color_based_removal(image, product_type)
            if self._validate_transparency(color_result):
                quality = self._evaluate_transparency_quality(color_result)
                results.append(("color", color_result, quality))
                self.logger.info(f"Color method quality: {quality:.2f}")
        except Exception as e:
            self.logger.warning(f"Improved color-based removal failed: {str(e)}")
        
        # Method 3: Machine learning inspired segmentation
        try:
            self.logger.info("Attempting ML-inspired background removal")
            ml_result = self._ml_inspired_removal(image, product_type)
            if self._validate_transparency(ml_result):
                quality = self._evaluate_transparency_quality(ml_result)
                results.append(("ml", ml_result, quality))
                self.logger.info(f"ML method quality: {quality:.2f}")
        except Exception as e:
            self.logger.warning(f"ML-inspired removal failed: {str(e)}")
        
        # If we have results, use the best one based on quality score
        if results:
            # Sort by quality score (higher is better)
            results.sort(key=lambda x: x[2], reverse=True)
            best_method, best_result, quality = results[0]
            self.logger.info(f"Using {best_method} background removal method with quality score: {quality:.2f}")
            
            # Apply final refinements to best result
            refined_result = self._refine_transparency_mask(best_result)
            return refined_result
        
        # If all methods failed, try one more simple approach as fallback
        self.logger.warning("All advanced methods failed. Using reliable fallback method.")
        return self._reliable_fallback_removal(image)
    
    def _advanced_edge_based_removal(self, image: Image.Image, product_type: str) -> Image.Image:
        """
        Advanced edge-based background removal inspired by U2Net techniques.
        
        Args:
            image: PIL Image
            product_type: Type of product
            
        Returns:
            Image with transparent background
        """
        # Convert to RGBA if not already
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Create numpy array for processing
        img_array = np.array(image)
        
        # Create grayscale image for edge detection
        gray = image.convert('L')
        
        # Apply multiple filter passes for better edge detection
        edges1 = gray.filter(ImageFilter.EDGE_ENHANCE_MORE)
        edges2 = edges1.filter(ImageFilter.FIND_EDGES)
        edges3 = edges2.filter(ImageFilter.EDGE_ENHANCE_MORE)
        
        # Combine multiple edge maps for better results
        edges_array1 = np.array(edges1)
        edges_array2 = np.array(edges2)
        edges_array3 = np.array(edges3)
        
        # Create a combined edge map with weighted contributions
        edge_map = (edges_array1 * 0.2 + edges_array2 * 0.5 + edges_array3 * 0.3)
        
        # Apply adaptive thresholding for better object detection
        threshold = np.percentile(edge_map, 75)  # Using 75th percentile for threshold
        edge_mask = edge_map > threshold
        
        # Fill holes in the mask using morphological operations
        from scipy import ndimage
        filled_mask = ndimage.binary_fill_holes(edge_mask)
        
        # Find connected components
        labeled, num_features = ndimage.label(filled_mask)
        
        # Product-specific adjustments based on product type
        if product_type.lower() in ["bottle", "perfume", "container"]:
            # For bottles, we expect a single large object
            # Keep only the largest component
            sizes = np.bincount(labeled.ravel())[1:]
            largest_label = np.argmax(sizes) + 1
            main_mask = labeled == largest_label
            
            # For bottles, sometimes we need to extend mask vertically
            # to capture the full height (common issue with bottle necks)
            extended_mask = self._extend_vertical_mask(main_mask)
            final_mask = extended_mask
            
        elif "electronics" in product_type.lower() or "device" in product_type.lower():
            # For electronics, we may have multiple components
            # Keep components of significant size
            sizes = np.bincount(labeled.ravel())[1:]
            largest_size = np.max(sizes)
            
            significant_mask = np.zeros_like(labeled, dtype=bool)
            for i, size in enumerate(sizes):
                if size > largest_size * 0.05:  # Keep components at least 5% of largest
                    significant_mask = np.logical_or(significant_mask, labeled == (i + 1))
            
            final_mask = significant_mask
            
        else:
            # For other products, use a balanced approach
            # Keep the largest component and any that are at least 10% of its size
            sizes = np.bincount(labeled.ravel())[1:]
            if len(sizes) > 0:
                largest_size = np.max(sizes)
                
                significant_mask = np.zeros_like(labeled, dtype=bool)
                for i, size in enumerate(sizes):
                    if size > largest_size * 0.1:
                        significant_mask = np.logical_or(significant_mask, labeled == (i + 1))
                
                final_mask = significant_mask
            else:
                final_mask = filled_mask
        
        # Clean up the mask with morphological operations
        final_mask = ndimage.binary_opening(final_mask, structure=np.ones((3, 3)))
        final_mask = ndimage.binary_closing(final_mask, structure=np.ones((5, 5)))
        
        # Smooth the mask edges for natural transparency
        mask_float = final_mask.astype(np.float32)
        smooth_mask = ndimage.gaussian_filter(mask_float, sigma=1.0)
        
        # Scale back to 0-255 range
        alpha_mask = (smooth_mask * 255).astype(np.uint8)
        
        # Create the final image with transparency
        result_array = img_array.copy()
        result_array[:, :, 3] = alpha_mask
        
        return Image.fromarray(result_array)
    
    def _improved_color_based_removal(self, image: Image.Image, product_type: str) -> Image.Image:
        """
        Improved color-based background removal using advanced clustering.
        
        Args:
            image: PIL Image
            product_type: Type of product
            
        Returns:
            Image with transparent background
        """
        # Convert to RGBA if not already
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Get image as numpy array
        img_array = np.array(image)
        height, width, _ = img_array.shape
        
        # Resize for faster processing if image is large
        scale_factor = 1.0
        if width > 500 or height > 500:
            scale_factor = 500 / max(width, height)
            resized_img = image.resize((int(width * scale_factor), int(height * scale_factor)), Image.LANCZOS)
            resized_array = np.array(resized_img)
        else:
            resized_img = image
            resized_array = img_array
        
        # Extract RGB channels for clustering
        rgb_data = resized_array[:, :, :3].reshape(-1, 3)
        
        # Sample from the edges to identify potential background colors
        resized_height, resized_width = resized_array.shape[:2]
        edge_indices = []
        
        # Add top and bottom rows
        edge_indices.extend([(0, j) for j in range(resized_width)])
        edge_indices.extend([(resized_height-1, j) for j in range(resized_width)])
        
        # Add left and right columns (excluding corners already added)
        edge_indices.extend([(i, 0) for i in range(1, resized_height-1)])
        edge_indices.extend([(i, resized_width-1) for i in range(1, resized_height-1)])
        
        # Convert indices to flat indices for the reshaped data
        edge_flat_indices = [i * resized_width + j for i, j in edge_indices]
        
        # Get edge colors
        edge_colors = rgb_data[edge_flat_indices]
        
        # Use clustering to find dominant background colors
        from sklearn.cluster import KMeans
        
        # Determine appropriate number of clusters based on color variance
        color_variance = np.var(edge_colors, axis=0).sum()
        n_clusters = min(max(2, int(color_variance / 1000)), 5)
        
        kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
        kmeans.fit(edge_colors)
        
        bg_colors = kmeans.cluster_centers_
        
        # Create foreground mask using distance from background colors
        mask = np.ones((resized_height, resized_width), dtype=bool)
        
        # Product-specific adjustment for color tolerance
        if "white" in product_type.lower() or "light" in product_type.lower():
            # More precise color matching for white or light products
            color_tolerance = 25
        elif "black" in product_type.lower() or "dark" in product_type.lower():
            # More precise for dark products
            color_tolerance = 25
        elif "colorful" in product_type.lower() or "multicolor" in product_type.lower():
            # More tolerance for multicolor products
            color_tolerance = 40
        else:
            # Default tolerance
            color_tolerance = 30
        
        # Calculate distances to each background color
        for bg_color in bg_colors:
            color_dist = np.sqrt(np.sum((resized_array[:, :, :3] - bg_color)**2, axis=2))
            
            # Adaptively adjust tolerance based on distance distribution
            # to better handle gradients in the background
            dist_threshold = color_tolerance
            
            # Add to mask (True = foreground, False = background)
            mask = np.logical_and(mask, color_dist > dist_threshold)
        
        # Clean up the mask with morphological operations
        from scipy import ndimage
        mask = ndimage.binary_opening(mask, structure=np.ones((3, 3)))
        mask = ndimage.binary_closing(mask, structure=np.ones((5, 5)))
        
        # Fill holes
        mask = ndimage.binary_fill_holes(mask)
        
        # Resize mask back to original size if needed
        if scale_factor < 1.0:
            mask_img = Image.fromarray((mask * 255).astype(np.uint8))
            mask_img = mask_img.resize((width, height), Image.LANCZOS)
            mask = np.array(mask_img) > 127
        
        # Smooth the mask edges
        mask_float = mask.astype(np.float32)
        smooth_mask = ndimage.gaussian_filter(mask_float, sigma=1.0)
        
        # Scale back to 0-255 range
        alpha_mask = (smooth_mask * 255).astype(np.uint8)
        
        # Create the final image with transparency
        result_array = img_array.copy()
        result_array[:, :, 3] = alpha_mask
        
        return Image.fromarray(result_array)
    
    def _ml_inspired_removal(self, image: Image.Image, product_type: str) -> Image.Image:
        """
        Machine learning inspired background removal using advanced image features.
        
        Args:
            image: PIL Image
            product_type: Type of product
            
        Returns:
            Image with transparent background
        """
        # Convert to RGBA if not already
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Create numpy array for processing
        img_array = np.array(image)
        height, width, _ = img_array.shape
        
        # Create feature maps (similar to what ML models would use)
        # 1. Color features
        rgb_norm = img_array[:, :, :3].astype(np.float32) / 255.0
        
        # 2. Gradient features
        gray = np.mean(rgb_norm, axis=2)
        from scipy import ndimage
        grad_x = ndimage.sobel(gray, axis=0, mode='reflect')
        grad_y = ndimage.sobel(gray, axis=1, mode='reflect')
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        gradient_magnitude = gradient_magnitude / np.max(gradient_magnitude)
        
        # 3. Position features - distance from center
        y_indices, x_indices = np.ogrid[:height, :width]
        center_y, center_x = height / 2, width / 2
        dist_from_center = np.sqrt(((x_indices - center_x) / width)**2 + 
                                   ((y_indices - center_y) / height)**2)
        
        # Create a composite feature space
        features = np.zeros((height, width, 5))
        features[:, :, :3] = rgb_norm
        features[:, :, 3] = gradient_magnitude
        features[:, :, 4] = dist_from_center
        
        # Reshape for clustering
        features_flat = features.reshape(-1, 5)
        
        # Use clustering to separate foreground and background
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=2, n_init=10, random_state=42)
        cluster_labels = kmeans.fit_predict(features_flat)
        
        # Reshape labels back to image dimensions
        clusters = cluster_labels.reshape(height, width)
        
        # Determine which cluster is foreground based on position and edge content
        # (Foreground objects tend to be centered and have more edges)
        cluster_0_center_dist = np.mean(dist_from_center[clusters == 0])
        cluster_1_center_dist = np.mean(dist_from_center[clusters == 1])
        
        cluster_0_edge_content = np.mean(gradient_magnitude[clusters == 0])
        cluster_1_edge_content = np.mean(gradient_magnitude[clusters == 1])
        
        # Score each cluster (lower is more likely to be foreground)
        cluster_0_score = cluster_0_center_dist - cluster_0_edge_content
        cluster_1_score = cluster_1_center_dist - cluster_1_edge_content
        
        # Determine foreground cluster
        if cluster_0_score < cluster_1_score:
            mask = clusters == 0
        else:
            mask = clusters == 1
        
        # Clean up the mask with morphological operations
        from scipy import ndimage
        mask = ndimage.binary_opening(mask, structure=np.ones((3, 3)))
        mask = ndimage.binary_closing(mask, structure=np.ones((7, 7)))
        
        # Fill holes
        mask = ndimage.binary_fill_holes(mask)
        
        # Smooth the mask edges
        mask_float = mask.astype(np.float32)
        smooth_mask = ndimage.gaussian_filter(mask_float, sigma=1.0)
        
        # Scale to 0-255 range
        alpha_mask = (smooth_mask * 255).astype(np.uint8)
        
        # Create the final image with transparency
        result_array = img_array.copy()
        result_array[:, :, 3] = alpha_mask
        
        return Image.fromarray(result_array)
    
    def _extend_vertical_mask(self, mask: np.ndarray) -> np.ndarray:
        """
        Extend mask vertically to better handle products like bottles.
        
        Args:
            mask: Binary mask array
            
        Returns:
            Extended mask
        """
        # Find the bounding box of the mask
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        
        if not np.any(rows) or not np.any(cols):
            return mask  # Empty mask
            
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        
        # For each column in the bounding box, extend the mask vertically
        extended_mask = mask.copy()
        for col in range(cmin, cmax + 1):
            col_indices = np.where(mask[:, col])[0]
            if len(col_indices) > 0:
                extended_mask[col_indices.min():col_indices.max() + 1, col] = True
        
        return extended_mask
    
    def _reliable_fallback_removal(self, image: Image.Image) -> Image.Image:
        """
        A highly reliable fallback method for background removal when others fail.
        
        Args:
            image: PIL Image
            
        Returns:
            Image with transparent background
        """
        # Convert to RGBA if not already
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Create numpy array for processing
        img_array = np.array(image)
        height, width, _ = img_array.shape
        
        # Focus on the center of the image
        center_y, center_x = height // 2, width // 2
        
        # Sample a center region to get foreground colors
        center_region_size = min(width, height) // 4
        center_region = img_array[
            max(0, center_y - center_region_size):min(height, center_y + center_region_size),
            max(0, center_x - center_region_size):min(width, center_x + center_region_size),
            :3
        ]
        
        # Sample edge regions to get background colors
        edge_pixels = np.vstack([
            img_array[0, :, :3],                  # Top edge
            img_array[height-1, :, :3],           # Bottom edge
            img_array[1:height-1, 0, :3],         # Left edge
            img_array[1:height-1, width-1, :3]    # Right edge
        ])
        
        # Find common background colors using clustering
        from sklearn.cluster import KMeans
        n_clusters = min(3, len(edge_pixels))
        if n_clusters < 1:
            n_clusters = 1
            
        kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
        kmeans.fit(edge_pixels)
        bg_colors = kmeans.cluster_centers_
        
        # Create mask based on color distance from background colors
        mask = np.ones((height, width), dtype=bool)
        
        # Adaptive color distance threshold
        from scipy.spatial.distance import cdist
        
        # Calculate distances between center region and background colors
        if center_region.size > 0:
            center_colors = center_region.reshape(-1, 3)
            distances = cdist(center_colors, bg_colors)
            min_distances = np.min(distances, axis=1)
            
            # Set color tolerance based on the distribution of distances
            color_tolerance = np.percentile(min_distances, 25)
            color_tolerance = max(30, min(color_tolerance, 60))
        else:
            color_tolerance = 40
        
        # Apply color-based masking
        for bg_color in bg_colors:
            color_dist = np.sqrt(np.sum((img_array[:, :, :3] - bg_color)**2, axis=2))
            mask = np.logical_and(mask, color_dist > color_tolerance)
        
        # Clean up the mask with morphological operations
        from scipy import ndimage
        mask = ndimage.binary_opening(mask, structure=np.ones((3, 3)))
        mask = ndimage.binary_closing(mask, structure=np.ones((7, 7)))
        
        # Fill holes
        mask = ndimage.binary_fill_holes(mask)
        
        # Smooth the mask edges
        mask_float = mask.astype(np.float32)
        smooth_mask = ndimage.gaussian_filter(mask_float, sigma=1.0)
        
        # Scale to 0-255 range
        alpha_mask = (smooth_mask * 255).astype(np.uint8)
        
        # Create the final image with transparency
        result_array = img_array.copy()
        result_array[:, :, 3] = alpha_mask
        
        return Image.fromarray(result_array)
    
    def _refine_transparency_mask(self, image: Image.Image) -> Image.Image:
        """
        Apply final refinements to transparency mask for professional edges.
        
        Args:
            image: PIL Image with transparency
            
        Returns:
            Image with refined transparency
        """
        if image.mode != 'RGBA':
            return image
        
        # Split into channels
        r, g, b, a = image.split()
        
        # Convert alpha to numpy array for processing
        alpha_array = np.array(a)
        
        # Apply guided filter to alpha channel for edge-aware smoothing
        from scipy import ndimage
        
        # Create guidance image from RGB channels
        rgb = Image.merge('RGB', (r, g, b))
        gray = rgb.convert('L')
        gray_array = np.array(gray)
        
        # Edge-preserving smoothing
        # First, find edges in the guidance image
        edges = ndimage.gaussian_gradient_magnitude(gray_array, sigma=2.0)
        edges_norm = edges / (np.max(edges) + 1e-8)
        
        # Use edge information to control smoothing strength
        smoothing_factor = 1.0 - edges_norm
        
        # Apply adaptive smoothing to alpha channel
        smoothed_alpha = ndimage.gaussian_filter(alpha_array.astype(float), sigma=1.0)
        
        # Blend original and smoothed alpha based on edge strength
        refined_alpha = alpha_array * edges_norm + smoothed_alpha * (1.0 - edges_norm)
        
        # Convert back to 8-bit
        refined_alpha = np.clip(refined_alpha, 0, 255).astype(np.uint8)
        
        # Create new alpha channel
        new_alpha = Image.fromarray(refined_alpha)
        
        # Merge back with RGB channels
        result = Image.merge('RGBA', (r, g, b, new_alpha))
        
        return result
    
    def _remove_background_with_openai(self, image: Image.Image) -> Image.Image:
        """
        Use OpenAI to remove background with optimized prompts.
        
        Args:
            image: PIL Image
            
        Returns:
            Image with transparent background
        """
        try:
            # Save image to buffer for API
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)
            
            # Call OpenAI API with very specific prompt for improved background removal
            response = self.openai_client.images.edit(
                image=buffer,
                prompt="Create a professional product image with complete background removal. Remove the background entirely, leaving ONLY the product with a 100% transparent background. Maintain exact product details, colors, and quality. Preserve all shadows attached to the product. Create crisp, clean edges with natural transparency. Perfect for professional product catalog integration.",
                n=1,
                size="1024x1024"
            )
            
            # Get result image URL
            image_url = response.data[0].url
            
            # Download and process the result
            response = requests.get(image_url)
            if response.status_code == 200:
                no_bg_img = Image.open(BytesIO(response.content)).convert("RGBA")
                
                # Validate the result
                quality = self._evaluate_transparency_quality(no_bg_img)
                if quality < 5.0:  # Below quality threshold
                    self.logger.warning(f"OpenAI result below quality threshold ({quality:.2f})")
                    raise Exception("Low quality result from OpenAI")
                    
                return no_bg_img
            else:
                raise Exception(f"Failed to download image: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"OpenAI background removal error: {str(e)}")
            raise
    
    def _evaluate_transparency_quality(self, image: Image.Image) -> float:
        """
        Evaluate the quality of transparency in an image.
        
        Args:
            image: PIL Image with transparency
            
        Returns:
            Quality score (higher is better)
        """
        if image.mode != 'RGBA':
            return 0.0
        
        # Get alpha channel
        _, _, _, alpha = image.split()
        alpha_array = np.array(alpha)
        
        # Calculate metrics for quality evaluation
        
        # 1. Histogram analysis - a good mask should have distinct foreground and background
        hist, _ = np.histogram(alpha_array, bins=256, range=(0, 256))
        hist_norm = hist / np.sum(hist)
        
        # Calculate entropy (higher means more information, better mask)
        from scipy import stats
        non_zero_hist = hist_norm[hist_norm > 0]
        if len(non_zero_hist) > 0:
            entropy = -np.sum(non_zero_hist * np.log2(non_zero_hist))
            entropy_score = min(10, max(0, entropy))
        else:
            entropy_score = 0
        
        # 2. Edge quality - sharp edges indicate good masking
        from scipy import ndimage
        edges = ndimage.sobel(alpha_array)
        edge_mean = np.mean(np.abs(edges))
        edge_score = min(10, edge_mean / 5)
        
        # 3. Foreground/background ratio - should be reasonable
        fg_ratio = np.sum(alpha_array > 127) / alpha_array.size
        if 0.05 <= fg_ratio <= 0.95:
            ratio_score = 10
        else:
            ratio_score = max(0, 10 - 20 * abs(fg_ratio - 0.5))
        
        # Combine scores with appropriate weighting
        quality_score = (
            entropy_score * 0.3 +
            edge_score * 0.5 +
            ratio_score * 0.2
        )
        
        return quality_score
    
    def _validate_transparency(self, image: Image.Image) -> bool:
        """
        Validate that an image has meaningful transparency.
        
        Args:
            image: PIL Image object with alpha channel
            
        Returns:
            True if image has meaningful transparency, False otherwise
        """
        if image.mode != 'RGBA':
            return False
        
        # Get alpha channel
        _, _, _, alpha = image.split()
        alpha_array = np.array(alpha)
        
        # Calculate transparent pixel percentage
        total_pixels = alpha_array.size
        transparent_pixels = np.sum(alpha_array < 128)
        transparent_percentage = transparent_pixels / total_pixels
        
        # Check if there's enough transparency (between 5% and 95%)
        # If too little or too much transparency, the removal probably failed
        return 0.05 <= transparent_percentage <= 0.95
    
    def _professional_product_enhancement(self, image: Image.Image, product_type: str) -> Image.Image:
        """
        Apply professional enhancements tailored to the product type.
        
        Args:
            image: PIL Image
            product_type: Type of product
            
        Returns:
            Enhanced image
        """
        # Make a copy to avoid modifying the original
        img = image.copy()
        
        # Apply basic enhancements
        # Sharpen for better details
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.3)
        
        # Slightly increase contrast for better definition
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)
        
        # Product-specific enhancements
        product_lower = product_type.lower()
        
        # Perfume, bottle, or glass products
        if any(term in product_lower for term in ["perfume", "bottle", "glass", "fragrance"]):
            self.logger.info("Applying specialized enhancements for glass/bottle product")
            
            # Enhance reflections and clarity
            img = self._enhance_glass_reflections(img)
            
            # Slightly brighten to enhance glass appearance
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.05)
            
            # Boost color vibrancy slightly for attractive appearance
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.1)
            
        # Electronic devices
        elif any(term in product_lower for term in ["electronics", "phone", "device", "computer", "laptop", "tech"]):
            self.logger.info("Applying specialized enhancements for electronic device")
            
            # Enhance screen and surface details
            img = self._enhance_device_screens(img)
            
            # Add subtle material enhancement for metals and plastics
            img = self._enhance_material_surfaces(img)
            
            # Increase definition for technical details
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.2)
            
        # Cosmetics and beauty products
        elif any(term in product_lower for term in ["cosmetic", "makeup", "beauty", "cream", "lotion"]):
            self.logger.info("Applying specialized enhancements for beauty product")
            
            # Soften slightly for beauty aesthetic
            img = img.filter(ImageFilter.SMOOTH_MORE)
            
            # Enhance colors for attractive appearance
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.1)
            
            # Brightness for clean look
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.05)
            
        # Clothing and apparel
        elif any(term in product_lower for term in ["clothing", "apparel", "fashion", "wear", "shoe"]):
            self.logger.info("Applying specialized enhancements for fashion product")
            
            # Enhance fabric textures
            img = self._enhance_fabric_textures(img)
            
            # Moderate color enhancement
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.08)
            
            # Subtle sharpening for fabric details
            img = img.filter(ImageFilter.SHARPEN)
            
        # Final pass for all products
        img = self._final_quality_enhancement(img)
        
        return img
    
    def _enhance_glass_reflections(self, image: Image.Image) -> Image.Image:
        """
        Enhance glass and reflective surface details.
        
        Args:
            image: PIL Image
            
        Returns:
            Enhanced image
        """
        # Split into RGBA channels
        r, g, b, a = image.split()
        
        # Create a brightness image
        brightness = Image.merge("RGB", (r, g, b)).convert("L")
        brightness_array = np.array(brightness)
        
        # Find bright areas (likely reflections)
        reflection_mask = brightness_array > 180
        
        # Dilate reflection areas slightly
        from scipy import ndimage
        reflection_mask = ndimage.binary_dilation(reflection_mask, structure=np.ones((3, 3)))
        
        # Create a reflection enhancement layer
        reflection_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
        
        # Get RGB arrays for processing
        r_array = np.array(r)
        g_array = np.array(g)
        b_array = np.array(b)
        
        # Enhance reflections by increasing brightness in reflection areas
        r_array = np.where(reflection_mask, np.minimum(r_array * 1.1, 255), r_array)
        g_array = np.where(reflection_mask, np.minimum(g_array * 1.1, 255), g_array)
        b_array = np.where(reflection_mask, np.minimum(b_array * 1.1, 255), b_array)
        
        # Create enhanced channels
        r_enhanced = Image.fromarray(r_array.astype(np.uint8))
        g_enhanced = Image.fromarray(g_array.astype(np.uint8))
        b_enhanced = Image.fromarray(b_array.astype(np.uint8))
        
        # Merge back into RGBA
        enhanced = Image.merge("RGBA", (r_enhanced, g_enhanced, b_enhanced, a))
        
        # Apply final glass effect with subtle blur for realistic glass look
        glass_effect = enhanced.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        
        return glass_effect
    
    def _enhance_device_screens(self, image: Image.Image) -> Image.Image:
        """
        Enhance electronic device screens.
        
        Args:
            image: PIL Image
            
        Returns:
            Enhanced image
        """
        # Split into RGBA channels
        r, g, b, a = image.split()
        rgb = Image.merge("RGB", (r, g, b))
        
        # Convert to LAB colorspace for better screen detection
        # (Since we can't use skimage directly, we'll simulate this with RGB channels)
        
        # Find potential screen areas using brightness and uniformity
        gray = rgb.convert("L")
        gray_array = np.array(gray)
        
        # Calculate local standard deviation (uniformity)
        from scipy import ndimage
        local_std = ndimage.generic_filter(gray_array, np.std, size=5)
        
        # Screen areas typically have low local standard deviation (uniform brightness)
        # and medium to high brightness
        screen_mask = (local_std < 15) & (gray_array > 40) & (gray_array < 220)
        
        # Clean up the mask with morphological operations
        screen_mask = ndimage.binary_opening(screen_mask, structure=np.ones((3, 3)))
        screen_mask = ndimage.binary_closing(screen_mask, structure=np.ones((5, 5)))
        
        # Create a screen enhancement layer
        screen_array = np.array(rgb)
        
        # Enhance contrast in screen areas
        for channel in range(3):
            channel_data = screen_array[:, :, channel]
            min_val = np.percentile(channel_data[screen_mask], 5)
            max_val = np.percentile(channel_data[screen_mask], 95)
            
            if max_val > min_val:
                # Normalize to 0-1
                normalized = (channel_data - min_val) / (max_val - min_val)
                
                # Apply contrast curve
                enhanced = 0.5 + (normalized - 0.5) * 1.2
                
                # Clip to 0-1 range
                enhanced = np.clip(enhanced, 0, 1)
                
                # Scale back to original range
                enhanced = enhanced * (max_val - min_val) + min_val
                
                # Apply only to screen areas
                channel_data = np.where(screen_mask, enhanced, channel_data)
                screen_array[:, :, channel] = np.clip(channel_data, 0, 255).astype(np.uint8)
        
        # Convert back to PIL Image
        enhanced_rgb = Image.fromarray(screen_array)
        
        # Merge back with alpha
        enhanced = Image.merge("RGBA", (
            enhanced_rgb.split()[0],
            enhanced_rgb.split()[1],
            enhanced_rgb.split()[2],
            a
        ))
        
        return enhanced
    
    def _enhance_material_surfaces(self, image: Image.Image) -> Image.Image:
        """
        Enhance material surfaces like metal, plastic, etc.
        
        Args:
            image: PIL Image
            
        Returns:
            Enhanced image
        """
        # Split into RGBA channels
        r, g, b, a = image.split()
        
        # Create brightness image
        brightness = ImageChops.add(ImageChops.add(r, g), b)
        
        # Identify potential material highlights
        bright_areas = brightness.point(lambda x: x > 200)
        
        # Create a highlight enhancement layer
        highlight_mask = np.array(bright_areas) > 128
        
        # Get RGB arrays for processing
        r_array = np.array(r)
        g_array = np.array(g)
        b_array = np.array(b)
        
        # Enhance highlights slightly
        r_array = np.where(highlight_mask, np.minimum(r_array * 1.1, 255), r_array)
        g_array = np.where(highlight_mask, np.minimum(g_array * 1.1, 255), g_array)
        b_array = np.where(highlight_mask, np.minimum(b_array * 1.1, 255), b_array)
        
        # Create enhanced channels
        r_enhanced = Image.fromarray(r_array.astype(np.uint8))
        g_enhanced = Image.fromarray(g_array.astype(np.uint8))
        b_enhanced = Image.fromarray(b_array.astype(np.uint8))
        
        # Merge back into RGBA
        enhanced = Image.merge("RGBA", (r_enhanced, g_enhanced, b_enhanced, a))
        
        # Apply subtle material-enhancing filter
        material_effect = enhanced.filter(ImageFilter.UnsharpMask(radius=1.5, percent=150, threshold=3))
        
        return material_effect
    
    def _enhance_fabric_textures(self, image: Image.Image) -> Image.Image:
        """
        Enhance fabric textures for clothing and textile products.
        
        Args:
            image: PIL Image
            
        Returns:
            Enhanced image
        """
        # Create a copy to avoid modifying the original
        img = image.copy()
        
        # Apply a texture-enhancing filter
        img = img.filter(ImageFilter.DETAIL)
        
        # Sharpen details slightly
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.15)
        
        # Increase contrast slightly for better texture definition
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.05)
        
        return img
    
    def _final_quality_enhancement(self, image: Image.Image) -> Image.Image:
        """
        Apply final quality enhancements for professional appearance.
        
        Args:
            image: PIL Image
            
        Returns:
            Enhanced image
        """
        # Apply subtle sharpening for final definition
        img = image.filter(ImageFilter.UnsharpMask(radius=1, percent=100, threshold=3))
        
        # Ensure image is in RGBA mode
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        return img
    
    def _analyze_product_image(self, image: Image.Image, product_type: str = None) -> Dict[str, Any]:
        """
        Advanced analysis of product image for optimal integration.
        
        Args:
            image: PIL Image
            product_type: Type of product
            
        Returns:
            Dictionary with analysis results
        """
        # Create analysis dictionary
        analysis = {}
        
        # Get basic dimensions
        width, height = image.size
        analysis["dimensions"] = (width, height)
        
        # Check if image has alpha channel
        has_alpha = image.mode == "RGBA"
        if has_alpha:
            # For transparent images, find the actual product bounds
            bbox = self._get_alpha_bounding_box(image)
        else:
            # For non-transparent images, use the full dimensions
            bbox = (0, 0, width, height)
        
        analysis["product_bbox"] = bbox
        
        # Calculate product dimensions and center
        product_width = bbox[2] - bbox[0]
        product_height = bbox[3] - bbox[1]
        product_center_x = (bbox[0] + bbox[2]) // 2
        product_center_y = (bbox[1] + bbox[3]) // 2
        
        analysis["product_dimensions"] = (product_width, product_height)
        analysis["product_center"] = (product_center_x, product_center_y)
        
        # Analyze orientation
        if product_width > product_height * 1.2:
            orientation = "landscape"
        elif product_height > product_width * 1.2:
            orientation = "portrait"
        else:
            orientation = "square"
        
        analysis["product_orientation"] = orientation
        
        # Extract dominant colors for better color matching
        analysis["dominant_colors"] = self._extract_dominant_colors(image)
        
        # Calculate aspect ratio
        aspect_ratio = product_width / product_height if product_height > 0 else 1.0
        analysis["aspect_ratio"] = aspect_ratio
        
        # Calculate visual weight distribution for balanced composition
        analysis["visual_weight"] = self._analyze_visual_weight(image)
        
        # Add product-specific analysis
        if product_type:
            analysis["product_specific"] = self._analyze_product_specific(image, product_type)
        
        return analysis
    
    def _extract_dominant_colors(self, image: Image.Image, num_colors: int = 5) -> List[Tuple[int, int, int]]:
        """
        Extract dominant colors from image using k-means clustering.
        
        Args:
            image: PIL Image
            num_colors: Number of colors to extract
            
        Returns:
            List of RGB color tuples
        """
        # Resize for faster processing
        img_small = image.copy().resize((100, 100), Image.LANCZOS)
        
        # If image has alpha, focus on non-transparent areas
        if img_small.mode == "RGBA":
            # Create a mask of non-transparent pixels
            r, g, b, a = img_small.split()
            mask = np.array(a) > 128
            
            # Extract colors only from non-transparent pixels
            img_array = np.array(img_small)
            valid_pixels = img_array[mask]
            
            if len(valid_pixels) == 0:
                # No valid pixels, return default colors
                return [(0, 0, 0), (128, 128, 128), (255, 255, 255)]
            
            # Extract RGB values
            rgb_pixels = valid_pixels[:, :3]
        else:
            # Convert to RGB and get all pixels
            img_small = img_small.convert("RGB")
            rgb_pixels = np.array(img_small).reshape(-1, 3)
        
        # Use k-means clustering to find dominant colors
        try:
            from sklearn.cluster import KMeans
            
            # Adjust number of clusters based on pixel count
            n_colors = min(num_colors, len(rgb_pixels))
            
            # Skip if not enough pixels
            if n_colors < 1:
                return [(0, 0, 0), (128, 128, 128), (255, 255, 255)]
            
            # Fit k-means
            kmeans = KMeans(n_clusters=n_colors, n_init=10, random_state=42)
            kmeans.fit(rgb_pixels)
            
            # Get the colors
            dominant_colors = [tuple(map(int, color)) for color in kmeans.cluster_centers_]
            
            # Sort by cluster size
            cluster_sizes = np.bincount(kmeans.labels_, minlength=n_colors)
            sorted_idx = np.argsort(cluster_sizes)[::-1]
            sorted_colors = [dominant_colors[i] for i in sorted_idx]
            
            return sorted_colors
            
        except Exception as e:
            # Fallback to simple method
            from collections import Counter
            
            # Convert pixels to tuples for counting
            rgb_tuples = [tuple(pixel) for pixel in rgb_pixels]
            
            # Count occurrences of each color
            color_counts = Counter(rgb_tuples).most_common(num_colors)
            
            # Extract just the colors, not the counts
            return [color for color, _ in color_counts]
    
    def _get_alpha_bounding_box(self, image: Image.Image) -> Tuple[int, int, int, int]:
        """
        Get precise bounding box of non-transparent pixels.
        
        Args:
            image: PIL Image with alpha channel
            
        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
        """
        # Make sure image has alpha channel
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        
        # Get alpha channel
        _, _, _, alpha = image.split()
        
        # Find non-transparent pixels (with threshold to avoid stray pixels)
        non_transparent = np.array(alpha) > 20
        
        # Find bounding box
        non_zero_indices = np.nonzero(non_transparent)
        if len(non_zero_indices[0]) > 0 and len(non_zero_indices[1]) > 0:
            min_y, max_y = np.min(non_zero_indices[0]), np.max(non_zero_indices[0])
            min_x, max_x = np.min(non_zero_indices[1]), np.max(non_zero_indices[1])
            return (min_x, min_y, max_x, max_y)
        else:
            # Return full image bounds if no non-transparent pixels found
            return (0, 0, image.width, image.height)
    
    def _analyze_visual_weight(self, image: Image.Image) -> Dict[str, float]:
        """
        Analyze the visual weight distribution in the image.
        
        Args:
            image: PIL Image
            
        Returns:
            Dictionary with visual weight analysis
        """
        # Convert to grayscale for analysis
        gray = image.convert("L")
        
        # Create numpy array for processing
        gray_array = np.array(gray)
        
        # If image has alpha, use it as a mask
        if image.mode == "RGBA":
            _, _, _, alpha = image.split()
            alpha_array = np.array(alpha) / 255.0
            
            # Apply alpha mask to grayscale
            masked_array = gray_array * alpha_array
        else:
            masked_array = gray_array
        
        # Calculate weight in different regions
        height, width = masked_array.shape
        
        # Calculate center of mass
        y_indices, x_indices = np.indices(masked_array.shape)
        total_mass = np.sum(masked_array)
        
        if total_mass > 0:
            center_x = np.sum(x_indices * masked_array) / total_mass
            center_y = np.sum(y_indices * masked_array) / total_mass
        else:
            center_x = width / 2
            center_y = height / 2
        
        # Normalize to 0-1 range
        center_x_norm = center_x / width
        center_y_norm = center_y / height
        
        # Calculate weight in each quadrant
        top_left = np.sum(masked_array[:height//2, :width//2])
        top_right = np.sum(masked_array[:height//2, width//2:])
        bottom_left = np.sum(masked_array[height//2:, :width//2])
        bottom_right = np.sum(masked_array[height//2:, width//2:])
        
        # Normalize quadrant weights
        total_weight = top_left + top_right + bottom_left + bottom_right
        if total_weight > 0:
            top_left_norm = top_left / total_weight
            top_right_norm = top_right / total_weight
            bottom_left_norm = bottom_left / total_weight
            bottom_right_norm = bottom_right / total_weight
        else:
            top_left_norm = top_right_norm = bottom_left_norm = bottom_right_norm = 0.25
        
        return {
            "center_of_mass": (center_x_norm, center_y_norm),
            "quadrant_weights": {
                "top_left": top_left_norm,
                "top_right": top_right_norm,
                "bottom_left": bottom_left_norm,
                "bottom_right": bottom_right_norm
            }
        }
    
    def _analyze_product_specific(self, image: Image.Image, product_type: str) -> Dict[str, Any]:
        """
        Perform product-specific analysis for better integration.
        
        Args:
            image: PIL Image
            product_type: Type of product
            
        Returns:
            Dictionary with product-specific analysis
        """
        product_lower = product_type.lower()
        
        # Default analysis dictionary
        analysis = {}
        
        # For bottles and perfumes
        if any(term in product_lower for term in ["bottle", "perfume", "container", "fragrance"]):
            analysis["product_category"] = "container"
            analysis["orientation"] = "vertical"
            
            # Detect bottle shape
            analysis["shape"] = self._detect_bottle_shape(image)
            
            # Detect reflective properties
            analysis["reflective"] = self._detect_reflective_properties(image)
            
        # For electronic devices
        elif any(term in product_lower for term in ["electronics", "phone", "device", "laptop", "tech"]):
            analysis["product_category"] = "electronics"
            
            # Detect screen area
            analysis["screen_areas"] = self._detect_screen_areas(image)
            
            # Detect edge characteristics
            analysis["edge_characteristics"] = self._detect_edge_characteristics(image)
            
        # For beauty and cosmetics
        elif any(term in product_lower for term in ["cosmetic", "makeup", "beauty", "cream", "lotion"]):
            analysis["product_category"] = "beauty"
            
            # Detect container type
            analysis["container_type"] = self._detect_container_type(image)
            
            # Detect color palette
            analysis["color_palette"] = self._detect_beauty_color_palette(image)
            
        # For clothing and apparel
        elif any(term in product_lower for term in ["clothing", "apparel", "fashion", "wear", "shoe"]):
            analysis["product_category"] = "fashion"
            
            # Detect fabric texture
            analysis["texture"] = self._detect_fabric_texture(image)
            
            # Detect color complexity
            analysis["color_complexity"] = self._detect_color_complexity(image)
            
        else:
            # General product analysis
            analysis["product_category"] = "general"
            analysis["symmetry"] = self._detect_symmetry(image)
            analysis["complexity"] = self._detect_visual_complexity(image)
        
        return analysis
    
    def _detect_bottle_shape(self, image: Image.Image) -> str:
        """
        Detect the general shape of a bottle.
        
        Args:
            image: PIL Image
            
        Returns:
            Shape description
        """
        # Get alpha channel for shape analysis
        if image.mode != "RGBA":
            return "unknown"
        
        _, _, _, alpha = image.split()
        alpha_array = np.array(alpha) > 128
        
        # Get bounding box
        bbox = self._get_alpha_bounding_box(image)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        
        # Calculate aspect ratio
        aspect_ratio = height / width if width > 0 else 1.0
        
        # Determine shape based on aspect ratio and width distribution
        if aspect_ratio > 3.5:
            return "tall_slender"
        elif aspect_ratio > 2.5:
            return "tall"
        elif aspect_ratio > 1.5:
            return "standard"
        else:
            return "wide"
    
    def _detect_reflective_properties(self, image: Image.Image) -> float:
        """
        Detect how reflective a product appears to be.
        
        Args:
            image: PIL Image
            
        Returns:
            Reflectivity score (0-1)
        """
        # Convert to RGB for analysis
        rgb = image.convert("RGB")
        
        # Calculate brightness
        gray = rgb.convert("L")
        gray_array = np.array(gray)
        
        # If image has alpha, use it as a mask
        if image.mode == "RGBA":
            _, _, _, alpha = image.split()
            alpha_array = np.array(alpha) / 255.0
            
            # Apply alpha mask
            masked_array = gray_array * alpha_array
        else:
            masked_array = gray_array
        
        # Find bright highlights (typical of reflective surfaces)
        highlights = masked_array > 220
        
        # Calculate highlight percentage
        valid_pixels = np.sum(masked_array > 0)
        if valid_pixels > 0:
            highlight_percentage = np.sum(highlights) / valid_pixels
        else:
            highlight_percentage = 0
        
        # Calculate local contrast (reflective surfaces often have high contrast)
        from scipy import ndimage
        local_std = ndimage.generic_filter(masked_array, np.std, size=5)
        
        # Calculate average contrast in non-zero areas
        non_zero = masked_array > 0
        if np.sum(non_zero) > 0:
            avg_contrast = np.mean(local_std[non_zero])
            # Normalize to 0-1 range
            avg_contrast_norm = min(1.0, avg_contrast / 30.0)
        else:
            avg_contrast_norm = 0
        
        # Combine metrics (higher values = more reflective)
        reflectivity = highlight_percentage * 0.6 + avg_contrast_norm * 0.4
        
        return reflectivity
    
    def _detect_screen_areas(self, image: Image.Image) -> Dict[str, Any]:
        """
        Detect potential screen areas in electronic devices.
        
        Args:
            image: PIL Image
            
        Returns:
            Dictionary with screen area info
        """
        # Convert to RGB for analysis
        rgb = image.convert("RGB")
        gray = rgb.convert("L")
        gray_array = np.array(gray)
        
        # If image has alpha, use it as a mask
        if image.mode == "RGBA":
            _, _, _, alpha = image.split()
            alpha_array = np.array(alpha) / 255.0
            
            # Apply alpha mask
            masked_array = gray_array * alpha_array
        else:
            masked_array = gray_array
        
        # Calculate local standard deviation (uniformity)
        from scipy import ndimage
        local_std = ndimage.generic_filter(masked_array, np.std, size=5)
        
        # Screen areas typically have low local standard deviation (uniform brightness)
        # and medium to high brightness
        potential_screens = (local_std < 15) & (masked_array > 40) & (masked_array < 220)
        
        # Clean up the mask with morphological operations
        screen_mask = ndimage.binary_opening(potential_screens, structure=np.ones((3, 3)))
        screen_mask = ndimage.binary_closing(screen_mask, structure=np.ones((5, 5)))
        
        # Find screen regions
        labeled, num_screens = ndimage.label(screen_mask)
        
        # Calculate screen area percentage
        non_zero_pixels = np.sum(masked_array > 0)
        if non_zero_pixels > 0:
            screen_percentage = np.sum(screen_mask) / non_zero_pixels
        else:
            screen_percentage = 0
        
        return {
            "screen_count": num_screens,
            "screen_percentage": screen_percentage,
            "has_significant_screen": screen_percentage > 0.15
        }
    
    def _detect_edge_characteristics(self, image: Image.Image) -> Dict[str, Any]:
        """
        Detect edge characteristics for better product integration.
        
        Args:
            image: PIL Image
            
        Returns:
            Dictionary with edge analysis
        """
        # Get alpha channel if available
        if image.mode == "RGBA":
            _, _, _, alpha = image.split()
            alpha_array = np.array(alpha)
            
            # Calculate edge gradient
            from scipy import ndimage
            grad_x = ndimage.sobel(alpha_array, axis=0)
            grad_y = ndimage.sobel(alpha_array, axis=1)
            gradient = np.sqrt(grad_x**2 + grad_y**2)
            
            # Normalize gradient
            gradient_norm = gradient / np.max(gradient) if np.max(gradient) > 0 else gradient
            
            # Calculate edge properties
            edge_complexity = np.mean(gradient_norm)
            edge_smoothness = 1.0 - edge_complexity
            
            return {
                "edge_complexity": edge_complexity,
                "edge_smoothness": edge_smoothness,
                "edge_character": "sharp" if edge_complexity > 0.4 else "smooth"
            }
        else:
            # Default values if no alpha channel
            return {
                "edge_complexity": 0.5,
                "edge_smoothness": 0.5,
                "edge_character": "medium"
            }
    
    def _detect_container_type(self, image: Image.Image) -> str:
        """
        Detect container type for beauty products.
        
        Args:
            image: PIL Image
            
        Returns:
            Container type description
        """
        # Get alpha channel for shape analysis
        if image.mode != "RGBA":
            return "standard"
        
        _, _, _, alpha = image.split()
        alpha_array = np.array(alpha) > 128
        
        # Get bounding box
        bbox = self._get_alpha_bounding_box(image)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        
        # Calculate aspect ratio
        aspect_ratio = height / width if width > 0 else 1.0
        
        # Determine container type based on aspect ratio and width distribution
        if aspect_ratio > 2.5:
            return "tall_bottle"
        elif aspect_ratio > 1.5:
            return "standard_bottle"
        elif aspect_ratio < 0.7:
            return "wide_jar"
        else:
            return "jar"
    
    def _detect_beauty_color_palette(self, image: Image.Image) -> str:
        """
        Detect color palette for beauty products.
        
        Args:
            image: PIL Image
            
        Returns:
            Color palette description
        """
        # Extract dominant colors
        dominant_colors = self._extract_dominant_colors(image, num_colors=3)
        
        # Calculate average HSV values
        import colorsys
        hsv_values = []
        
        for color in dominant_colors:
            r, g, b = [c/255.0 for c in color]
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            hsv_values.append((h, s, v))
        
        # Calculate average saturation and value
        avg_saturation = sum(s for _, s, _ in hsv_values) / len(hsv_values)
        avg_value = sum(v for _, _, v in hsv_values) / len(hsv_values)
        
        # Determine palette type
        if avg_saturation < 0.2:
            if avg_value > 0.8:
                return "minimalist_white"
            elif avg_value < 0.3:
                return "minimalist_black"
            else:
                return "minimalist_neutral"
        elif avg_saturation > 0.6:
            return "vibrant"
        else:
            return "elegant"
    
    def _detect_fabric_texture(self, image: Image.Image) -> str:
        """
        Detect fabric texture for fashion products.
        
        Args:
            image: PIL Image
            
        Returns:
            Texture description
        """
        # Convert to grayscale for texture analysis
        gray = image.convert("L")
        gray_array = np.array(gray)
        
        # If image has alpha, use it as a mask
        if image.mode == "RGBA":
            _, _, _, alpha = image.split()
            alpha_array = np.array(alpha) / 255.0
            
            # Apply alpha mask
            masked_array = gray_array * alpha_array
        else:
            masked_array = gray_array
        
        # Calculate local standard deviation as texture measure
        from scipy import ndimage
        local_std = ndimage.generic_filter(masked_array, np.std, size=5)
        
        # Calculate texture properties
        valid_pixels = masked_array > 0
        if np.sum(valid_pixels) > 0:
            texture_complexity = np.mean(local_std[valid_pixels])
            # Normalize to 0-1 range
            texture_complexity_norm = min(1.0, texture_complexity / 30.0)
        else:
            texture_complexity_norm = 0.5
        
        # Determine texture type
        if texture_complexity_norm < 0.3:
            return "smooth"
        elif texture_complexity_norm < 0.6:
            return "medium"
        else:
            return "textured"
    
    def _detect_color_complexity(self, image: Image.Image) -> str:
        """
        Detect color complexity for fashion products.
        
        Args:
            image: PIL Image
            
        Returns:
            Color complexity description
        """
        # Extract dominant colors
        dominant_colors = self._extract_dominant_colors(image, num_colors=10)
        
        # Calculate color diversity
        color_count = len(dominant_colors)
        
        # Calculate color distance between dominant colors
        total_distance = 0
        count = 0
        
        for i in range(len(dominant_colors)):
            for j in range(i+1, len(dominant_colors)):
                # Calculate Euclidean distance in RGB space
                color1 = np.array(dominant_colors[i])
                color2 = np.array(dominant_colors[j])
                distance = np.sqrt(np.sum((color1 - color2)**2))
                
                total_distance += distance
                count += 1
        
        # Calculate average distance
        avg_distance = total_distance / count if count > 0 else 0
        
        # Normalize to 0-1 range
        color_diversity = min(1.0, avg_distance / 300.0)
        
        # Determine color complexity
        if color_count <= 2 or color_diversity < 0.2:
            return "simple"
        elif color_count <= 4 or color_diversity < 0.5:
            return "moderate"
        else:
            return "complex"
    
    def _detect_symmetry(self, image: Image.Image) -> float:
        """
        Detect image symmetry for better placement.
        
        Args:
            image: PIL Image
            
        Returns:
            Symmetry score (0-1)
        """
        # Convert to grayscale for analysis
        gray = image.convert("L")
        gray_array = np.array(gray)
        
        # If image has alpha, use it as a mask
        if image.mode == "RGBA":
            _, _, _, alpha = image.split()
            alpha_array = np.array(alpha) / 255.0
            
            # Apply alpha mask
            masked_array = gray_array * alpha_array
        else:
            masked_array = gray_array
        
        # Calculate horizontal symmetry
        height, width = masked_array.shape
        left_half = masked_array[:, :width//2]
        right_half = masked_array[:, width//2:width]
        
        # Flip right half for comparison
        right_half_flipped = np.fliplr(right_half)
        
        # Resize to match if they don't
        if left_half.shape != right_half_flipped.shape:
            min_width = min(left_half.shape[1], right_half_flipped.shape[1])
            left_half = left_half[:, :min_width]
            right_half_flipped = right_half_flipped[:, :min_width]
        
        # Calculate symmetry score
        valid_pixels = np.logical_or(left_half > 0, right_half_flipped > 0)
        if np.sum(valid_pixels) > 0:
            diff = np.abs(left_half - right_half_flipped)
            symmetry_score = 1.0 - np.sum(diff[valid_pixels]) / (np.sum(valid_pixels) * 255)
        else:
            symmetry_score = 0.5
        
        return symmetry_score
    
    def _detect_visual_complexity(self, image: Image.Image) -> float:
        """
        Detect visual complexity of the product.
        
        Args:
            image: PIL Image
            
        Returns:
            Complexity score (0-1)
        """
        # Convert to grayscale for analysis
        gray = image.convert("L")
        gray_array = np.array(gray)
        
        # If image has alpha, use it as a mask
        if image.mode == "RGBA":
            _, _, _, alpha = image.split()
            alpha_array = np.array(alpha) / 255.0
            
            # Apply alpha mask
            masked_array = gray_array * alpha_array
        else:
            masked_array = gray_array
        
        # Calculate edge density
        from scipy import ndimage
        grad_x = ndimage.sobel(masked_array, axis=0)
        grad_y = ndimage.sobel(masked_array, axis=1)
        gradient = np.sqrt(grad_x**2 + grad_y**2)
        
        # Calculate complexity metrics
        valid_pixels = masked_array > 0
        if np.sum(valid_pixels) > 0:
            edge_density = np.sum(gradient[valid_pixels]) / np.sum(valid_pixels)
            
            # Normalize to 0-1 range
            complexity_score = min(1.0, edge_density / 50.0)
        else:
            complexity_score = 0.5
        
        return complexity_score
    
    def generate_context_aware_background(self, product_info: Dict[str, Any], 
                                      brand_analysis: Dict[str, Any],
                                      ad_copy: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate a professionally integrated background based on product analysis.
        
        Args:
            product_info: Product image analysis from process_product_image
            brand_analysis: Brand analysis information
            ad_copy: Ad copy information
            
        Returns:
            Dictionary with background image paths
        """
        try:
            self.logger.info("Generating context-aware background with enhanced algorithm")
            
            # Extract key information for background generation
            product_type = product_info["product_type"]
            industry = brand_analysis.get("industry", "General")
            brand_level = brand_analysis.get("brand_level", "Premium")
            product_orientation = product_info["analysis"]["product_orientation"]
            dominant_colors = product_info["analysis"]["dominant_colors"]
            image_description = ad_copy.get("image_description", "")
            
            # Check if we can use OpenAI for advanced background generation
            if self.has_openai and self.openai_client:
                try:
                    return self._generate_enhanced_background_with_ai(
                        product_info, brand_analysis, ad_copy,
                        product_type, industry, brand_level,
                        product_orientation, dominant_colors
                    )
                except Exception as e:
                    self.logger.warning(f"AI background generation failed: {str(e)}. Trying local method.")
            
            # Use local background generation as fallback
            return self._generate_enhanced_background_local(
                product_info, brand_analysis, ad_copy,
                product_type, industry, brand_level,
                product_orientation, dominant_colors
            )
        
        except Exception as e:
            self.logger.error(f"Error generating background: {str(e)}")
            self.logger.error(traceback.format_exc())
            
            # Return fallback background
            return self._generate_premium_fallback_background(product_info, brand_analysis)
    
    def _generate_enhanced_background_with_ai(self, product_info: Dict[str, Any], 
                                       brand_analysis: Dict[str, Any],
                                       ad_copy: Dict[str, Any],
                                       product_type: str, industry: str, brand_level: str,
                                       product_orientation: str, dominant_colors: List[Tuple[int, int, int]]) -> Dict[str, str]:
        """
        Generate background using OpenAI with enhanced prompting for better integration.
        
        Args:
            product_info: Product information dictionary
            brand_analysis: Brand analysis information
            ad_copy: Ad copy data
            product_type: Type of product
            industry: Industry category
            brand_level: Brand positioning level
            product_orientation: Product orientation (portrait/landscape/square)
            dominant_colors: List of dominant colors in product
            
        Returns:
            Dictionary with background image paths
        """
        # Extract key information for prompt crafting
        visual_weight = product_info["analysis"].get("visual_weight", {})
        product_specific = product_info["analysis"].get("product_specific", {})
        
        # Convert dominant colors to hex for easier reference
        color_hex = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in dominant_colors[:3]]
        
        # Get visual style from brand analysis
        visual_style = brand_analysis.get("visual_direction", "")
        
        # Create detailed, precise prompt for background generation
        bg_prompt = f"""Create a professional advertisement BACKGROUND ONLY for a {product_type} product.

VERY IMPORTANT INSTRUCTIONS:
- Create ONLY AN EMPTY BACKGROUND SCENE with NO products in it
- The background will have the product composited on top later
- Leave ample space for product placement in the {product_orientation} orientation
- Match the professional styling for {industry} industry at {brand_level} level
- Use colors that complement these product colors: {', '.join(color_hex)}
- Create a subtle, sophisticated background with appropriate depth and texture
- Include professional studio lighting effects and subtle shadows where the product will be placed

BRAND CONTEXT:
- Industry: {industry}
- Brand Level: {brand_level}
- Visual Style: {visual_style}

SPECIFIC DETAILS:
- Product Type: {product_type}
- Product Orientation: {product_orientation}
- Background should support a {product_specific.get('product_category', 'general')} product
- Create {product_specific.get('edge_character', 'balanced')} edge treatment
- Optimize for {ad_copy.get('image_description', 'professional product presentation')}

BACKGROUND STYLE:
- Create a {brand_level} quality background with professional studio lighting
- Use subtle gradients and textures appropriate for {industry}
- Include professional photographic elements like reflective surfaces or shadows
- Color palette should harmonize with: {', '.join(color_hex)}
- Create depth with subtle lighting effects and graduated backgrounds

DO NOT include any products, text, logos, or human elements. Create ONLY the empty background scene that will have the product composited onto it later.
"""

        # Generate background with DALL-E
        self.logger.info("Generating background with enhanced OpenAI prompt")
        response = self.openai_client.images.generate(
            model="dall-e-3",
            prompt=bg_prompt,
            size="1024x1024",
            quality="hd",
            n=1
        )
        
        image_url = response.data[0].url
        
        # Download image
        response = requests.get(image_url)
        response.raise_for_status()
        
        # Save the background image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bg_filepath = f"output/images/backgrounds/bg_{timestamp}.png"
        
        with open(bg_filepath, 'wb') as f:
            f.write(response.content)
        
        # Create a version optimized for composition
        bg_img = Image.open(BytesIO(response.content))
        
        # Apply professional enhancements for better integration
        enhanced_bg = self._enhance_background_for_product_integration(bg_img, product_info)
        
        # Save enhanced background
        enhanced_bg_path = f"output/images/backgrounds/bg_enhanced_{timestamp}.png"
        enhanced_bg.save(enhanced_bg_path)
        
        self.logger.info(f"AI-generated background saved to: {bg_filepath}")
        
        return {
            "background_path": bg_filepath,
            "enhanced_background_path": enhanced_bg_path,
            "generation_method": "dall-e"
        }
    
    def _generate_enhanced_background_local(self, product_info: Dict[str, Any], 
                                      brand_analysis: Dict[str, Any],
                                      ad_copy: Dict[str, Any],
                                      product_type: str, industry: str, brand_level: str,
                                      product_orientation: str, dominant_colors: List[Tuple[int, int, int]]) -> Dict[str, str]:
        """
        Generate high-quality background locally with enhanced algorithms.
        
        Args:
            product_info: Product information dictionary
            brand_analysis: Brand analysis information
            ad_copy: Ad copy data
            product_type: Type of product
            industry: Industry category
            brand_level: Brand positioning level
            product_orientation: Product orientation
            dominant_colors: List of dominant colors in product
            
        Returns:
            Dictionary with background image paths
        """
        # Determine optimal background style based on product and brand
        bg_style = self._determine_optimal_background_style(
            industry, brand_level, product_type, product_info
        )
        
        self.logger.info(f"Creating background with style: {bg_style}")
        
        # Generate background based on style
        width, height = 1024, 1024
        
        if bg_style == "luxury_gradient":
            bg_img = self._create_luxury_gradient_background(
                width, height, dominant_colors, product_orientation, brand_level
            )
        elif bg_style == "minimalist":
            bg_img = self._create_premium_minimalist_background(
                width, height, dominant_colors, product_orientation
            )
        elif bg_style == "studio":
            bg_img = self._create_professional_studio_background(
                width, height, dominant_colors, product_info, brand_level
            )
        elif bg_style == "technical":
            bg_img = self._create_technical_background(
                width, height, dominant_colors, product_orientation
            )
        elif bg_style == "lifestyle":
            bg_img = self._create_lifestyle_background(
                width, height, dominant_colors, industry
            )
        else:
            # Default to professional gradient
            bg_img = self._create_professional_gradient_background(
                width, height, dominant_colors, product_orientation, brand_level
            )
        
        # Save background image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bg_filepath = f"output/images/backgrounds/bg_{timestamp}.png"
        bg_img.save(bg_filepath)
        
        # Apply professional enhancements for better integration
        enhanced_bg = self._enhance_background_for_product_integration(bg_img, product_info)
        
        # Save enhanced background
        enhanced_bg_path = f"output/images/backgrounds/bg_enhanced_{timestamp}.png"
        enhanced_bg.save(enhanced_bg_path)
        
        self.logger.info(f"Locally generated background saved to: {bg_filepath}")
        
        return {
            "background_path": bg_filepath,
            "enhanced_background_path": enhanced_bg_path,
            "generation_method": "local",
            "style": bg_style
        }
    
    def _determine_optimal_background_style(self, industry: str, brand_level: str, 
                                     product_type: str, product_info: Dict[str, Any]) -> str:
        """
        Determine the optimal background style based on product and brand analysis.
        
        Args:
            industry: Industry category
            brand_level: Brand positioning level
            product_type: Type of product
            product_info: Full product information dictionary
            
        Returns:
            Background style name
        """
        industry_lower = industry.lower()
        brand_level_lower = brand_level.lower()
        product_lower = product_type.lower()
        
        # Extract additional insights from product analysis
        product_specific = product_info["analysis"].get("product_specific", {})
        reflective = product_specific.get("reflective", 0.5) if isinstance(product_specific.get("reflective"), float) else 0.5
        
        # Luxury products (premium perfumes, watches, high-end fashion)
        if "luxury" in brand_level_lower:
            if any(term in product_lower for term in ["perfume", "fragrance", "cologne"]):
                return "luxury_gradient"
            elif any(term in product_lower for term in ["watch", "jewelry", "accessory"]):
                return "luxury_gradient"
            elif any(term in industry_lower for term in ["fashion", "apparel", "clothing"]):
                return "minimalist"
            else:
                return "luxury_gradient"
        
        # Premium technical products (premium electronics, devices)
        elif "premium" in brand_level_lower and any(term in industry_lower for term in ["tech", "electronics", "device"]):
            return "technical"
        
        # Premium beauty and cosmetics
        elif "premium" in brand_level_lower and any(term in industry_lower for term in ["beauty", "cosmetic", "skincare"]):
            if reflective > 0.6:
                return "studio"
            else:
                return "minimalist"
        
        # Highly reflective products (bottles, glass products)
        elif reflective > 0.7:
            return "studio"
            
        # Fashion and lifestyle products
        elif any(term in industry_lower for term in ["fashion", "apparel", "clothing", "lifestyle"]):
            if "premium" in brand_level_lower:
                return "minimalist"
            else:
                return "lifestyle"
        
        # Technical products (devices, electronics)
        elif any(term in industry_lower for term in ["tech", "electronics", "digital"]):
            return "technical"
        
        # Default style based on brand level
        elif "premium" in brand_level_lower:
            return "studio"
        else:
            return "professional_gradient"
    
    def _create_professional_gradient_background(self, width: int, height: int, 
                                          dominant_colors: List[Tuple[int, int, int]],
                                          orientation: str, brand_level: str) -> Image.Image:
        """
        Create a professional gradient background optimized for product integration.
        
        Args:
            width: Background width
            height: Background height
            dominant_colors: Dominant colors from product
            orientation: Product orientation
            brand_level: Brand positioning level
            
        Returns:
            Background image
        """
        # Create new image
        bg = Image.new("RGB", (width, height), (240, 240, 240))
        draw = ImageDraw.Draw(bg)
        
        # Select optimal colors for gradient based on product colors
        if dominant_colors:
            # Extract main color
            main_color = dominant_colors[0]
            
            # Create a complementary color for gradient
            r, g, b = main_color
            
            # For premium brands, use more subtle gradients
            if "premium" in brand_level.lower() or "luxury" in brand_level.lower():
                # Create a more subtle, desaturated variant
                lightness = (r + g + b) / 3
                
                # Adjust saturation down and lightness up for elegant look
                factor = 0.7  # Reduced saturation
                
                # Move color towards a desaturated variant
                r2 = int(r * factor + lightness * (1 - factor))
                g2 = int(g * factor + lightness * (1 - factor))
                b2 = int(b * factor + lightness * (1 - factor))
                
                # Lighten for gradient end
                color1 = (
                    min(255, int(r2 * 0.7 + 75)),
                    min(255, int(g2 * 0.7 + 75)), 
                    min(255, int(b2 * 0.7 + 75))
                )
                
                # Darken for gradient start
                color2 = (
                    max(0, int(r2 * 0.8)),
                    max(0, int(g2 * 0.8)),
                    max(0, int(b2 * 0.8))
                )
            else:
                # For other brands, more standard gradients
                # Create complementary-ish colors for more dynamic gradient
                h_offset = 0.3  # Not fully complementary for a more harmonious look
                
                # Convert RGB to HSV
                import colorsys
                r_norm, g_norm, b_norm = r/255.0, g/255.0, b/255.0
                h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
                
                # Create complementary-ish hue
                h2 = (h + h_offset) % 1.0
                
                # Convert back to RGB
                r2_norm, g2_norm, b2_norm = colorsys.hsv_to_rgb(h2, s * 0.8, v)
                
                # Scale back to 0-255
                color1 = (int(r_norm * 255), int(g_norm * 255), int(b_norm * 255))
                color2 = (int(r2_norm * 255), int(g2_norm * 255), int(b2_norm * 255))
        else:
            # Default professional gradient
            if "luxury" in brand_level.lower():
                color1 = (240, 240, 245)  # Light silver
                color2 = (40, 40, 60)     # Dark blue-gray
            else:
                color1 = (230, 230, 240)  # Light blue-gray
                color2 = (60, 70, 100)    # Medium blue
        
        # Create gradient based on orientation for better product integration
        if orientation == "portrait":
            # For portrait products, use horizontal or diagonal gradient
            # to provide contrast and frame the product
            if "luxury" in brand_level.lower():
                # Radial gradient for luxury
                self._create_radial_gradient(draw, width, height, color1, color2)
            else:
                # Horizontal gradient
                for x in range(width):
                    # Calculate position in gradient (0 to 1)
                    t = x / width
                    
                    # Apply smooth easing function for more natural gradient
                    t = self._ease_function(t)
                    
                    # Calculate color at this position
                    r = int(color1[0] * (1 - t) + color2[0] * t)
                    g = int(color1[1] * (1 - t) + color2[1] * t)
                    b = int(color1[2] * (1 - t) + color2[2] * t)
                    
                    # Draw vertical line with this color
                    draw.line([(x, 0), (x, height)], fill=(r, g, b))
        else:
            # For landscape or square products, use vertical or diagonal gradient
            if "luxury" in brand_level.lower():
                # Radial gradient for luxury
                self._create_radial_gradient(draw, width, height, color1, color2)
            else:
                # Diagonal gradient
                for y in range(height):
                    for x in range(width):
                        # Calculate position in gradient (0 to 1)
                        t = (x + y) / (width + height)
                        
                        # Apply smooth easing function
                        t = self._ease_function(t)
                        
                        # Calculate color at this position
                        r = int(color1[0] * (1 - t) + color2[0] * t)
                        g = int(color1[1] * (1 - t) + color2[1] * t)
                        b = int(color1[2] * (1 - t) + color2[2] * t)
                        
                        # Set pixel color
                        draw.point((x, y), fill=(r, g, b))
        
        # Add subtle professional vignette
        bg = self._add_professional_vignette(bg, intensity=0.2)
        
        # Add subtle texture for depth
        bg = self._add_subtle_professional_texture(bg, intensity=0.05)
        
        return bg



    def _enhance_background_for_product_integration(self, background: Image.Image, product_info: Dict[str, Any]) -> Image.Image:
        """
        Enhance background specifically for optimal product integration.
    
        Args:
            background: Background image
            product_info: Product information dictionary
        
        Returns:
                Enhanced background image
     """
    # Make a copy to avoid modifying the original
        enhanced = background.copy()
    
    # Extract product specifics to guide enhancement
        product_orientation = product_info["analysis"]["product_orientation"]
        dominant_colors = product_info["analysis"]["dominant_colors"]
        product_specific = product_info["analysis"].get("product_specific", {})
        visual_weight = product_info["analysis"].get("visual_weight", {})
    
    # Create light gradient in center for product focus
        width, height = enhanced.size
        center_x, center_y = width // 2, height // 2
    
    # Create a radial gradient overlay for center emphasis
        gradient = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(gradient)
    
    # Adjust gradient radius based on product orientation
        if product_orientation == "portrait":
            radius = int(min(width, height) * 0.7)
        else:
            radius = int(min(width, height) * 0.65)
    
    # Draw gradient circles with decreasing opacity
        for i in range(radius, 0, -1):
            opacity = int(255 * (1 - (i / radius) ** 2))
            draw.ellipse(
            [center_x - i, center_y - i, center_x + i, center_y + i],
            fill=opacity
        )
    
    # Apply subtle blur to gradient
        gradient = gradient.filter(ImageFilter.GaussianBlur(radius=10))
    
    # Create light overlay using dominant color
        if dominant_colors:
            r, g, b = dominant_colors[0]
        # Create a very subtle color wash
            color_overlay = Image.new('RGB', (width, height), (r, g, b))
        # Blend with gradient
            gradient_rgb = Image.merge('RGB', (gradient, gradient, gradient))
            color_gradient = Image.blend(color_overlay, gradient_rgb, 0.85)
        
        # Apply to background with light screen blend
            enhanced = ImageChops.screen(enhanced, color_gradient)
    
    # Apply subtle vignette for depth
        enhanced = self._add_subtle_vignette(enhanced, 0.2)
    
    # Adjust contrast slightly for better product pop
        enhancer = ImageEnhance.Contrast(enhanced)
        enhanced = enhancer.enhance(0.95)  # Slightly reduce contrast
    
    # Add subtle studio lighting effect in center
        enhanced = self._add_subtle_studio_lighting(enhanced, product_orientation)
    
        return enhanced

    def _add_subtle_vignette(self, image: Image.Image, intensity: float = 0.3) -> Image.Image:
        """
    Add a subtle vignette effect to create depth and focus.
    
    Args:
        image: Source image
        intensity: Vignette intensity (0-1)
        
    Returns:
        Image with vignette applied
    """
    # Make a copy to avoid modifying the original
        img = image.copy()
        width, height = img.size
    
    # Create radial gradient mask
        mask = Image.new('L', (width, height), 255)
        draw = ImageDraw.Draw(mask)
    
    # Calculate gradient parameters
        max_radius = int(max(width, height) * 0.7)  # Extend to 70% of the image
    
    # Draw gradient circles with decreasing opacity
        for i in range(max_radius, 0, -1):
        # Non-linear gradient for more realistic look
            opacity = int(255 - (255 * intensity * (1 - (i / max_radius) ** 2)))
            draw.ellipse(
            [(width // 2) - i, (height // 2) - i, 
             (width // 2) + i, (height // 2) + i],
            fill=opacity
        )
    
    # Apply slight blur to the mask
        mask = mask.filter(ImageFilter.GaussianBlur(10))
    
    # Apply mask to image
        vignette = Image.new('RGB', (width, height), (0, 0, 0))
        return Image.composite(img, vignette, mask)

    def _add_subtle_studio_lighting(self, image: Image.Image, product_orientation: str) -> Image.Image:
        """
    Add subtle studio lighting effects to the background.
    
    Args:
        image: Background image
        product_orientation: Product orientation
        
    Returns:
        Image with studio lighting effects
    """
        width, height = image.size
    
    # Create lighting effect overlay
        lighting = Image.new('RGB', (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(lighting)
    
    # Position light source based on product orientation
        if product_orientation == "portrait":
        # For portrait products, light from above
            light_center_x = width // 2
            light_center_y = height // 4
            light_radius = int(min(width, height) * 0.6)
        elif product_orientation == "landscape":
        # For landscape products, light from upper left
            light_center_x = width // 3
            light_center_y = height // 3
            light_radius = int(min(width, height) * 0.7)
        else:  # square
        # For square products, light from upper center
            light_center_x = width // 2
            light_center_y = height // 3
            light_radius = int(min(width, height) * 0.65)
    
    # Draw radial gradient for light
        for i in range(light_radius, 0, -1):
        # Calculate falloff
            intensity = int(150 * (1 - (i / light_radius) ** 2))
            light_color = (intensity, intensity, intensity)
        
            draw.ellipse(
            [light_center_x - i, light_center_y - i, 
             light_center_x + i, light_center_y + i],
            fill=light_color
        )
    
    # Apply strong blur for soft light
        lighting = lighting.filter(ImageFilter.GaussianBlur(50))
    
    # Blend with original using screen mode
        result = ImageChops.screen(image, lighting)
    
        return result

    def _create_luxury_gradient_background(self, width: int, height: int, 
                                    dominant_colors: List[Tuple[int, int, int]],
                                    orientation: str, brand_level: str) -> Image.Image:
        """
    Create a luxury gradient background with premium aesthetic.
    
    Args:
        width: Background width
        height: Background height
        dominant_colors: Dominant colors from product
        orientation: Product orientation
        brand_level: Brand positioning level
        
    Returns:
        Luxury gradient background
    """
    # Choose appropriate colors based on dominant product colors
        if dominant_colors:
            main_color = dominant_colors[0]
            r, g, b = main_color
        
        # Create sophisticated color palette
        # Desaturate and adjust luminosity for elegant look
            avg_luminance = (r + g + b) / 3
        
        # Luxury products often use deep, rich colors with subtle gradient
            if "luxury" in brand_level.lower():
            # Rich, dark base
                color1 = (
                max(0, min(255, int(r * 0.4))), 
                max(0, min(255, int(g * 0.4))), 
                max(0, min(255, int(b * 0.4)))
            )
            
            # Slightly lighter for gradient
                color2 = (
                max(0, min(255, int(r * 0.6))),
                max(0, min(255, int(g * 0.6))),
                max(0, min(255, int(b * 0.6)))
            )
            else:
            # Less intense for premium (not luxury)
                color1 = (
                max(0, min(255, int(r * 0.5))),
                max(0, min(255, int(g * 0.5))),
                max(0, min(255, int(b * 0.5)))
            )
            
                color2 = (
                max(0, min(255, int(r * 0.7))),
                max(0, min(255, int(g * 0.7))),
                max(0, min(255, int(b * 0.7)))
            )
        else:
        # Default luxury colors
            color1 = (20, 20, 30)  # Deep, dark blue-black
            color2 = (60, 60, 80)  # Subtle dark blue
    
    # Create the base background
        bg = Image.new("RGB", (width, height), color1)
        draw = ImageDraw.Draw(bg)
    
    # Choose gradient type based on orientation
        if orientation == "portrait":
        # For portrait products, radial gradient looks elegant
            for i in range(max(width, height)):
                radius = i
            # Calculate color at this radius
                ratio = min(1.0, i / (max(width, height) * 0.8))
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            
            # Draw circle
                draw.ellipse(
                [(width // 2) - radius, (height // 2) - radius,
                 (width // 2) + radius, (height // 2) + radius],
                outline=(r, g, b)
            )
        else:
        # For landscape/square, diagonal gradient
            for y in range(height):
                for x in range(width):
                # Diagonal progress (0 to 1)
                    progress = (x + y) / (width + height)
                    r = int(color1[0] * (1 - progress) + color2[0] * progress)
                    g = int(color1[1] * (1 - progress) + color2[1] * progress)
                    b = int(color1[2] * (1 - progress) + color2[2] * progress)
                    draw.point((x, y), fill=(r, g, b))
    
    # Add subtle luxury texture overlay
        texture = self._create_luxury_texture_overlay(width, height)
        bg = Image.blend(bg, texture, 0.1)  # Very subtle blend
    
    # Add soft vignette for depth
        bg = self._add_subtle_vignette(bg, 0.4)
    
    # Add subtle lighting effects
        bg = self._add_luxury_lighting(bg, orientation)
    
        return bg

    def _create_luxury_texture_overlay(self, width: int, height: int) -> Image.Image:
        """
    Create a subtle luxury texture overlay.
    
    Args:
        width: Image width
        height: Image height
        
    Returns:
        Texture overlay image
    """
    # Create base image
        texture = Image.new("RGB", (width, height), (20, 20, 20))
        draw = ImageDraw.Draw(texture)
    
    # Add subtle pattern elements
    # 1. Fine grid pattern
        grid_spacing = 20
        grid_color = (30, 30, 40)
    
        for x in range(0, width, grid_spacing):
            for y in range(0, height, grid_spacing):
            # Vary color slightly for organic feel
                r, g, b = grid_color
                variation = random.randint(-5, 5)
                grid_color_var = (r + variation, g + variation, b + variation)
            
            # Draw subtle dots
                if random.random() < 0.3:
                    dot_size = random.randint(1, 2)
                    draw.rectangle(
                    [x - dot_size, y - dot_size, x + dot_size, y + dot_size],
                    fill=grid_color_var
                )
    
    # 2. Soft noise texture
        for _ in range(5000):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            size = random.randint(1, 3)
            intensity = random.randint(15, 35)
            color = (intensity, intensity, intensity)
        
            draw.point((x, y), fill=color)
    
    # Apply blur for soft texture
        texture = texture.filter(ImageFilter.GaussianBlur(1))
    
        return texture

    def _add_luxury_lighting(self, image: Image.Image, orientation: str) -> Image.Image:
        """
    Add premium lighting effects to luxury backgrounds.
    
    Args:
        image: Background image
        orientation: Product orientation
        
    Returns:
        Image with luxury lighting effects
    """
        width, height = image.size
    
    # Create lighting overlay
        lighting = Image.new('RGB', (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(lighting)
    
    # Add primary highlight
        if orientation == "portrait":
        # Upper center light for portrait
            center_x = width // 2
            center_y = height // 4
            radius = int(min(width, height) * 0.7)
        else:
        # Upper corner light for landscape
            center_x = width // 4
            center_y = height // 4
            radius = int(min(width, height) * 0.8)
    
    # Draw radial gradient for main light
        for i in range(radius, 0, -1):
            ratio = i / radius
            intensity = int(60 * (1 - ratio ** 2))
            draw.ellipse(
            [center_x - i, center_y - i, center_x + i, center_y + i],
            fill=(intensity, intensity, intensity)
        )
    
    # Add secondary, more subtle highlight
        sec_center_x = width - center_x
        sec_center_y = height - center_y
        sec_radius = int(radius * 0.7)
    
        for i in range(sec_radius, 0, -1):
            ratio = i / sec_radius
            intensity = int(30 * (1 - ratio ** 2))
            draw.ellipse(
            [sec_center_x - i, sec_center_y - i, sec_center_x + i, sec_center_y + i],
            fill=(intensity, intensity, intensity)
        )
    
    # Apply blur for soft lighting
        lighting = lighting.filter(ImageFilter.GaussianBlur(70))
    
    # Blend with original using screen mode
        result = ImageChops.screen(image, lighting)
    
        return result

    def _create_premium_minimalist_background(self, width: int, height: int, 
                                       dominant_colors: List[Tuple[int, int, int]],
                                       orientation: str) -> Image.Image:
        """
    Create a premium minimalist background with clean aesthetics.
    
    Args:
        width: Background width
        height: Background height
        dominant_colors: Dominant colors from product
        orientation: Product orientation
        
    Returns:
        Minimalist background image
    """
    # Choose appropriate base color from product or default
        if dominant_colors:
            main_color = dominant_colors[0]
            r, g, b = main_color
        
        # Calculate brightness
            brightness = (r * 0.299 + g * 0.587 + b * 0.114) / 255
        
        # For minimalist, we want either very light or very dark
            if brightness > 0.5:
            # Product is light, so go with dark background
                base_color = (20, 20, 20)  # Near black
            else:
            # Product is dark, so go with light background
                base_color = (240, 240, 240)  # Near white
        else:
        # Default to light background if no color info
            base_color = (240, 240, 240)
    
    # Create the base background
        bg = Image.new("RGB", (width, height), base_color)
    
    # Add subtle gradient
        gradient_overlay = Image.new("RGB", (width, height), base_color)
        draw = ImageDraw.Draw(gradient_overlay)
    
    # Determine if we're working with dark or light base
        is_dark = base_color[0] < 128
    
    # Set gradient parameters
        if is_dark:
        # For dark backgrounds
            start_color = (base_color[0] + 15, base_color[1] + 15, base_color[2] + 15)
            end_color = base_color
        else:
        # For light backgrounds
            start_color = base_color
            end_color = (base_color[0] - 15, base_color[1] - 15, base_color[2] - 15)
    
    # Create subtle gradient based on orientation
        if orientation == "portrait":
        # Horizontal gradient for portrait
            for x in range(width):
            # Calculate gradient color
                ratio = x / width
                r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
                g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
                b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            
                draw.line([(x, 0), (x, height)], fill=(r, g, b))
        else:
        # Radial gradient for landscape/square
            center_x, center_y = width // 2, height // 2
            max_radius = int(max(width, height) * 0.8)
        
            for i in range(max_radius, 0, -1):
                ratio = i / max_radius
                r = int(start_color[0] * ratio + end_color[0] * (1 - ratio))
                g = int(start_color[1] * ratio + end_color[1] * (1 - ratio))
                b = int(start_color[2] * ratio + end_color[2] * (1 - ratio))
            
                draw.ellipse(
                [center_x - i, center_y - i, center_x + i, center_y + i],
                outline=(r, g, b)
            )
    
    # Blend gradient with base
        bg = Image.blend(bg, gradient_overlay, 0.7)
    
    # Add minimal design elements if desired
        if random.random() < 0.5:  # 50% chance to have minimal elements
            bg = self._add_minimalist_elements(bg, is_dark, orientation)
    
    # Add very subtle texture
        bg = self._add_subtle_texture(bg, 0.03)
    
    # Add subtle vignette
        bg = self._add_subtle_vignette(bg, 0.15)
    
        return bg

    def _add_minimalist_elements(self, image: Image.Image, is_dark: bool, orientation: str) -> Image.Image:
        """
    Add subtle minimalist design elements to background.
    
    Args:
        image: Background image
        is_dark: Whether background is dark
        orientation: Product orientation
        
    Returns:
        Image with minimalist elements
    """
        width, height = image.size
        result = image.copy()
        draw = ImageDraw.Draw(result)
    
    # Choose element color based on background
        if is_dark:
            element_color = (55, 55, 55)  # Slightly lighter than dark background
        else:
            element_color = (220, 220, 220)  # Slightly darker than light background
    
    # Choose element type based on orientation
        if orientation == "portrait":
        # For portrait, add horizontal line elements
            line_y = height // 4
            line_length = width // 3
            line_start_x = (width - line_length) // 2
        
        # Draw subtle line
            draw.line(
            [(line_start_x, line_y), (line_start_x + line_length, line_y)],
            fill=element_color,
            width=1
        )
        
        # Add second line at bottom
            line_y = height * 3 // 4
            draw.line(
            [(line_start_x, line_y), (line_start_x + line_length, line_y)],
            fill=element_color,
            width=1
        )
        else:
        # For landscape/square, add corner elements
            corner_size = min(width, height) // 10
        
        # Top left corner element
            draw.line(
            [(corner_size, 0), (corner_size, corner_size)],
            fill=element_color,
            width=1
        )
            draw.line(
            [(0, corner_size), (corner_size, corner_size)],
            fill=element_color,
            width=1
        )
        
            # Bottom right corner element
            draw.line(
            [(width - corner_size, height), (width - corner_size, height - corner_size)],
            fill=element_color,
            width=1
        )
            draw.line(
            [(width, height - corner_size), (width - corner_size, height - corner_size)],
            fill=element_color,
            width=1
        )
    
        return result

    def _create_professional_studio_background(self, width: int, height: int, 
                                        dominant_colors: List[Tuple[int, int, int]],
                                        product_info: Dict[str, Any],
                                        brand_level: str) -> Image.Image:
        """
    Create a professional studio-style background with reflective surface.
    
    Args:
        width: Background width
        height: Background height
        dominant_colors: Dominant colors from product
        product_info: Product information dictionary
        brand_level: Brand positioning level
        
    Returns:
        Studio background image
    """
    # Analyze product for optimal studio setup
        product_orientation = product_info["analysis"]["product_orientation"]
        product_specific = product_info["analysis"].get("product_specific", {})
        reflective = product_specific.get("reflective", 0.5) if isinstance(product_specific.get("reflective"), float) else 0.5
    
    # Choose appropriate base color
        if "luxury" in brand_level.lower():
        # Luxury products often use dark backgrounds
            base_color = (15, 15, 20)  # Near black
            is_dark = True
        else:
        # Determine based on product colors
            if dominant_colors:
                main_color = dominant_colors[0]
                r, g, b = main_color
                brightness = (r * 0.299 + g * 0.587 + b * 0.114) / 255
            
                if brightness > 0.5:
                # Light product, use dark background
                    base_color = (30, 30, 35)
                    is_dark = True
                else:
                # Dark product, use light background
                    base_color = (230, 230, 235)
                    is_dark = False
            else:
            # Default to dark background for studio look
                base_color = (30, 30, 35)
                is_dark = True
    
    # Create the base background
        bg = Image.new("RGB", (width, height), base_color)
    
    # Add gradient for depth
        gradient = Image.new("RGB", (width, height), base_color)
        draw = ImageDraw.Draw(gradient)
    
    # Define gradient colors
        if is_dark:
            bottom_color = (max(0, base_color[0] - 10), 
                      max(0, base_color[1] - 10), 
                      max(0, base_color[2] - 10))
            top_color = (min(255, base_color[0] + 20), 
                    min(255, base_color[1] + 20), 
                    min(255, base_color[2] + 20))
        else:
            bottom_color = (max(0, base_color[0] - 20), 
                      max(0, base_color[1] - 20), 
                      max(0, base_color[2] - 20))
            top_color = (min(255, base_color[0] + 10), 
                    min(255, base_color[1] + 10), 
                    min(255, base_color[2] + 10))
    
    # Draw vertical gradient
        for y in range(height):
        # Calculate position-based color
            ratio = y / height
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Blend gradient with base
        bg = Image.blend(bg, gradient, 0.8)
    
    # Add realistic studio lighting
        bg = self._add_studio_lighting_effects(bg, is_dark)
    
    # Add reflective floor/surface for product
        bg = self._add_reflective_surface(bg, is_dark, dominant_colors, product_orientation)
    
    # Add subtle vignette
        bg = self._add_subtle_vignette(bg, 0.3)
    
        return bg

    def _add_studio_lighting_effects(self, image: Image.Image, is_dark: bool) -> Image.Image:
        """
    Add professional studio lighting effects to background.
    
    Args:
        image: Background image
        is_dark: Whether background is dark
        
    Returns:
        Image with studio lighting effects
    """
        width, height = image.size
    
    # Create lighting overlay
        lighting = Image.new('RGB', (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(lighting)
    
    # Set lighting intensity based on background
        if is_dark:
            main_intensity = 80
            secondary_intensity = 40
        else:
            main_intensity = 40
            secondary_intensity = 20
    
    # Main key light (upper left)
        key_x, key_y = width // 4, height // 4
        key_radius = int(min(width, height) * 0.7)
    
        for i in range(key_radius, 0, -1):
            ratio = i / key_radius
            intensity = int(main_intensity * (1 - ratio ** 2))
            draw.ellipse(
            [key_x - i, key_y - i, key_x + i, key_y + i],
            fill=(intensity, intensity, intensity)
        )
    
    # Fill light (upper right)
        fill_x, fill_y = width * 3 // 4, height // 3
        fill_radius = int(min(width, height) * 0.6)
    
        for i in range(fill_radius, 0, -1):
            ratio = i / fill_radius
            intensity = int(secondary_intensity * (1 - ratio ** 2))
            draw.ellipse(
            [fill_x - i, fill_y - i, fill_x + i, fill_y + i],
            fill=(intensity, intensity, intensity)
        )
    
    # Back light/rim light (upper center)
        rim_x, rim_y = width // 2, height // 6
        rim_radius = int(min(width, height) * 0.5)
    
        for i in range(rim_radius, 0, -1):
            ratio = i / rim_radius
            intensity = int(secondary_intensity * 1.5 * (1 - ratio ** 2))
            draw.ellipse(
            [rim_x - i, rim_y - i, rim_x + i, rim_y + i],
            fill=(intensity, intensity, intensity)
        )
    
    # Apply blur for soft lighting
        lighting = lighting.filter(ImageFilter.GaussianBlur(50))
    
    # Blend with original using screen mode
        result = ImageChops.screen(image, lighting)
    
        return result

    def _add_reflective_surface(self, image: Image.Image, is_dark: bool, 
                          dominant_colors: List[Tuple[int, int, int]],
                          orientation: str) -> Image.Image:
        """
    Add a professional reflective surface/floor to the background.
    
    Args:
        image: Background image
        is_dark: Whether background is dark
        dominant_colors: Dominant colors from product
        orientation: Product orientation
        
    Returns:
        Image with reflective surface
    """
        width, height = image.size
        result = image.copy()
    
    # Determine horizon line placement
        if orientation == "portrait":
            horizon_y = height * 3 // 5  # Lower for portrait products
        else:
            horizon_y = height * 2 // 3  # Higher for landscape products
    
    # Create mask for reflection area (below horizon)
        mask = Image.new('L', (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
    
    # Fill bottom area
        mask_draw.rectangle([0, horizon_y, width, height], fill=255)
    
    # Create gradient for fade effect
        gradient_height = height // 8
        for y in range(gradient_height):
            opacity = 255 - int(255 * (y / gradient_height))
            mask_draw.line([(0, horizon_y + y), (width, horizon_y + y)], fill=opacity)
    
    # Create reflection
    # Reflect the upper part of the image
        upper_part = image.crop((0, 0, width, horizon_y))
        reflection = upper_part.transpose(Image.FLIP_TOP_BOTTOM)
    
    # Create full reflection image
        reflection_full = Image.new('RGB', (width, height), (0, 0, 0))
        reflection_full.paste(reflection, (0, horizon_y))
    
    # Apply fading gradient to reflection
        for y in range(horizon_y, height):
            fade_factor = 0.7 * (1 - (y - horizon_y) / (height - horizon_y))
            for x in range(width):
                r, g, b = reflection_full.getpixel((x, y))
                reflection_full.putpixel((x, y), (
                int(r * fade_factor),
                int(g * fade_factor),
                int(b * fade_factor)
            ))
    
    # Blend reflection with original background
        result = Image.composite(reflection_full, result, mask)
    
    # Add highlight line at horizon
        draw = ImageDraw.Draw(result)
    
        if is_dark:
            highlight_color = (60, 60, 70)  # Light line for dark bg
        else:
            highlight_color = (200, 200, 210)  # Dark line for light bg
    
    # Draw subtle highlight line
        draw.line([(0, horizon_y), (width, horizon_y)], fill=highlight_color, width=1)
    
    # Add product-color-influenced reflection
        if dominant_colors:
            main_color = dominant_colors[0]
            r, g, b = main_color
        
        # Create a subtle color overlay
            color_intensity = 0.1  # Very subtle
            color_overlay = Image.new('RGB', (width, height - horizon_y), 
                                (int(r * color_intensity), 
                                 int(g * color_intensity), 
                                 int(b * color_intensity)))
        
        # Apply color overlay to reflection area
            result.paste(ImageChops.screen(
                result.crop((0, horizon_y, width, height)),
            color_overlay
        ), (0, horizon_y))
    
        return result

    def _generate_premium_fallback_background(self, product_info: Dict[str, Any], 
                                       brand_analysis: Dict[str, Any]) -> Dict[str, str]:
        """
    Generate a high-quality fallback background when other methods fail.
    
    Args:
        product_info: Product information dictionary
        brand_analysis: Brand analysis information
        
    Returns:
        Dictionary with background image paths
    """
    # Extract key information
        product_type = product_info.get("product_type", "generic")
        brand_level = brand_analysis.get("brand_level", "Premium")
    
        try:
            dominant_colors = product_info["analysis"]["dominant_colors"]
        except (KeyError, TypeError):
            dominant_colors = [(80, 80, 120), (30, 30, 60)]  # Default colors
    
        try:
            product_orientation = product_info["analysis"]["product_orientation"]
        except (KeyError, TypeError):
            product_orientation = "portrait"  # Default orientation
    
    # Create high-quality gradient background
        width, height = 1024, 1024
    
    # Create a sophisticated gradient
        bg = Image.new("RGB", (width, height), (240, 240, 240))
        draw = ImageDraw.Draw(bg)
    
    # Create color gradient from product colors
        color1 = dominant_colors[0]
        color2 = dominant_colors[1] if len(dominant_colors) > 1 else (
        255 - color1[0], 255 - color1[1], 255 - color1[2]
    )
    
        # Adjust colors for more professional look
        r1, g1, b1 = color1
        r2, g2, b2 = color2
    
    # For premium look, slightly desaturate
        avg1 = (r1 + g1 + b1) / 3
        avg2 = (r2 + g2 + b2) / 3
    
    # Adjust saturation
        factor = 0.8
        color1 = (
        int(r1 * factor + avg1 * (1 - factor)),
        int(g1 * factor + avg1 * (1 - factor)),
        int(b1 * factor + avg1 * (1 - factor))
    )
    
        color2 = (
        int(r2 * factor + avg2 * (1 - factor)),
        int(g2 * factor + avg2 * (1 - factor)),
        int(b2 * factor + avg2 * (1 - factor))
    )
    
    # Create diagonal gradient
        for y in range(height):
            for x in range(width):
            # Calculate position in gradient (0 to 1)
                pos = (x + y) / (width + height)
            
            # Calculate color at this position
                r = int(color1[0] * (1 - pos) + color2[0] * pos)
                g = int(color1[1] * (1 - pos) + color2[1] * pos)
                b = int(color1[2] * (1 - pos) + color2[2] * pos)
            
                draw.point((x, y), fill=(r, g, b))
    
    # Add subtle vignette
        bg = self._add_subtle_vignette(bg, 0.3)
    
    # Add subtle texture
        bg = self._add_subtle_texture(bg, 0.05)
    
    # Add light studio effect in center
        bg = self._add_subtle_studio_lighting(bg, product_orientation)
    
    # Save background
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bg_filepath = f"output/images/backgrounds/bg_fallback_{timestamp}.png"
        bg.save(bg_filepath)
    
    # Create enhanced version
        enhanced_bg = self._enhance_background_for_product_integration(bg, product_info)
        enhanced_bg_path = f"output/images/backgrounds/bg_enhanced_{timestamp}.png"
        enhanced_bg.save(enhanced_bg_path)
    
        self.logger.info(f"Premium fallback background saved to: {bg_filepath}")
    
        return {
        "background_path": bg_filepath,
        "enhanced_background_path": enhanced_bg_path,
        "generation_method": "fallback_premium"
    }

    def _add_subtle_texture(self, image: Image.Image, intensity: float = 0.1) -> Image.Image:
        """
    Add subtle texture to background for professional look.
    
    Args:
        image: Background image
        intensity: Texture intensity (0-1)
        
    Returns:
        Image with subtle texture
    """
        width, height = image.size
    
    # Create noise texture
        texture = Image.new('L', (width, height), 0)
    
    # Generate fine noise pattern
        for y in range(0, height, 1):
            for x in range(0, width, 1):
                noise_value = random.randint(0, 20)
                texture.putpixel((x, y), noise_value)
    
    # Apply blur to soften noise
        texture = texture.filter(ImageFilter.GaussianBlur(1))
    
    # Convert to RGB for blending
        texture_rgb = Image.merge('RGB', (texture, texture, texture))
    
    # Composite with original image using screen blend mode
        return Image.blend(image, texture_rgb, intensity)
    

    def _create_drop_shadow(self, image: Image.Image, intensity: float = 0.5, 
                     offset: Tuple[int, int] = (0, 0), 
                     blur_radius: int = 10) -> Image.Image:
        """
    Create a realistic drop shadow for any product type.
    
    Args:
        image: Product image
        intensity: Shadow intensity (0-1)
        offset: Shadow offset (x, y)
        blur_radius: Shadow blur radius
        
    Returns:
        Shadow image
    """
    # Create shadow mask from alpha channel
        if image.mode == 'RGBA':
            r, g, b, alpha = image.split()
            shadow_mask = alpha.copy()
        else:
        # If image doesn't have alpha, create a mask from non-black pixels
            image_gray = image.convert('L')
            shadow_mask = Image.new('L', image.size, 0)
            threshold = 20
            for y in range(image_gray.height):
                for x in range(image_gray.width):
                    pixel = image_gray.getpixel((x, y))
                    if pixel > threshold:
                        shadow_mask.putpixel((x, y), 255)
    
    # Apply blur to shadow
        shadow = Image.new('RGBA', image.size, (0, 0, 0, 0))
        shadow_intensity = int(255 * intensity)
        shadow_color = (0, 0, 0, shadow_intensity)
        shadow_solid = Image.new('RGBA', image.size, shadow_color)
    
    # Create shadow image
        shadow.paste(shadow_solid, (0, 0), shadow_mask)
    
    # Apply blur
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    # Apply offset if provided
        if offset != (0, 0):
            offset_shadow = Image.new('RGBA', image.size, (0, 0, 0, 0))
            offset_shadow.paste(shadow, offset)
            return offset_shadow
    
        return shadow
    
    def _add_adaptive_highlights(self, image: Image.Image, intensity: float = 0.2, 
                         orientation: str = 'unknown') -> Image.Image:
        """
    Add adaptive highlights that work for any product type.
    
    Args:
        image: Product image
        intensity: Highlight intensity (0-1)
        orientation: Product orientation
        
    Returns:
        Image with highlights
    """
    # Create a copy of the image
        result = image.copy()
        width, height = image.size
    
    # Create a highlight gradient
        highlight = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(highlight)
    
    # Determine highlight direction based on orientation
        if orientation == 'portrait':
        # For portrait objects, add highlight along top-right edge
            start_x, start_y = width * 0.6, 0
            end_x, end_y = width, height * 0.4
        elif orientation == 'landscape':
        # For landscape objects, add highlight along top edge
            start_x, start_y = width * 0.2, 0
            end_x, end_y = width * 0.8, height * 0.3
        else:
        # For square or unknown, add diagonal highlight
            start_x, start_y = width * 0.7, 0
            end_x, end_y = width, height * 0.3
    
    # Create gradient highlight
        for y in range(height):
            for x in range(width):
            # Calculate distance from highlight line
                dx = x - start_x
                dy = y - start_y
            
            # Calculate projection onto highlight direction
                direction_x = end_x - start_x
                direction_y = end_y - start_y
                direction_length = (direction_x**2 + direction_y**2)**0.5
            
                if direction_length > 0:
                    proj_x = (dx * direction_x + dy * direction_y) / direction_length
                    proj_y = (dx * direction_y - dy * direction_x) / direction_length
                
                # Distance from highlight line
                    distance = abs(proj_y)
                
                # Highlight intensity decreases with distance
                    alpha = max(0, int(255 * intensity * (1 - min(1, distance / (width * 0.15)))))
                
                # Only apply highlight within the projection range
                    if 0 <= proj_x <= direction_length and alpha > 0:
                        highlight.putpixel((x, y), (255, 255, 255, alpha))
    
    # Apply blur to make highlight soft
        highlight = highlight.filter(ImageFilter.GaussianBlur(radius=width // 30))
    
    # Blend with original using alpha composite
        result = Image.alpha_composite(result, highlight)
    
        return result

    def _add_professional_product_effects(self, product: Image.Image, 
                                   placement: Dict[str, int], 
                                   brand_level: str) -> Image.Image:
        """
    Add professional effects to product image with better background integration.
    """
        self.logger.info("Adding professional effects to product image")
    
    # Get placement details
        width = placement['width']
        height = placement['height']
        orientation = placement.get('orientation', 'portrait')  # Default to portrait for bottles
    
    # Resize product to target dimensions
        product_resized = product.resize((width, height), Image.LANCZOS)
    
    # Create a new image with alpha for effects
        result = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    # Create realistic drop shadow
        shadow_offset = (width // 25, height // 20)  # Subtle offset
        shadow_blur = max(10, min(30, width // 15))  # Appropriate blur radius
        shadow_intensity = 0.3  # More subtle shadow for luxury products
    
        shadow = self._create_drop_shadow(
        product_resized, 
        intensity=shadow_intensity, 
        offset=shadow_offset, 
        blur_radius=shadow_blur
    )
    
    # Add drop shadow
        result.paste(shadow, (0, 0), shadow)
    
    # Add the resized product
        result.paste(product_resized, (0, 0), product_resized)
    
    # Add subtle reflection on the product (for bottles/reflective products)
        if orientation == 'portrait':
            reflection_intensity = 0.15
            result = self._add_subtle_reflection(result, reflection_intensity)
    
        return result

    def _add_subtle_reflection(self, image: Image.Image, intensity: float = 0.15) -> Image.Image:
        """
    Add subtle reflection highlight to product for realistic appearance.
    """
    # Create a copy of the image
        result = image.copy()
        width, height = image.size
    
    # Create highlight gradient
        highlight = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(highlight)
    
    # Top-right highlight (most common for product photography)
        for y in range(height):
            for x in range(width):
            # Calculate distance from top-right
                dx = x - (width * 0.7)
                dy = y - (height * 0.3)
                distance = (dx**2 + dy**2)**0.5
            
            # Normalize distance
                norm_distance = 1.0 - min(1.0, distance / (width * 0.3))
            
            # Calculate alpha based on distance
                alpha = int(norm_distance * 40)  # Subtle highlight (max 40 alpha)
            
                if alpha > 0:
                    highlight.putpixel((x, y), (255, 255, 255, alpha))
    
    # Apply blur for soft highlight
        highlight = highlight.filter(ImageFilter.GaussianBlur(radius=width // 20))
    
    # Apply the highlight
        result = Image.alpha_composite(result, highlight)
    
        return result
    
    def _enhance_final_composite(self, composite: Image.Image, 
                         product_info: Dict[str, Any], 
                         brand_analysis: Dict[str, Any]) -> Image.Image:
        """
    Enhance the final composite with more conservative adjustments to preserve background.
    """
        self.logger.info("Enhancing final composite")
    
    # Create a copy of the composite
        enhanced = composite.copy()
    
    # Extract parameters
        brand_level = brand_analysis.get('brand_level', '').lower()
        industry = brand_analysis.get('industry', '').lower()
    
    # Much more conservative enhancements that preserve background details
        contrast = 1.02
        color_saturation = 1.03
        sharpness = 1.03
        vignette = 0.08
    
    # Apply enhancements
        enhancer = ImageEnhance.Contrast(enhanced)
        enhanced = enhancer.enhance(contrast)
    
        enhancer = ImageEnhance.Color(enhanced)
        enhanced = enhancer.enhance(color_saturation)
    
        enhancer = ImageEnhance.Sharpness(enhanced)
        enhanced = enhancer.enhance(sharpness)
    
    # Add very subtle vignette
        if vignette > 0:
            enhanced = self._add_subtle_vignette(enhanced, intensity=vignette)
    
        return enhanced
    
    def integrate_product_and_text(self, product_path: str, background_path: str, 
                             product_info: Dict[str, Any],
                             brand_analysis: Dict[str, Any],
                             ad_copy: Dict[str, Any]) -> Dict[str, str]:
        """
    Comprehensive integration of product image with background and text elements.
    
    Args:
        product_path: Path to enhanced product image
        background_path: Path to background image
        product_info: Product image analysis
        brand_analysis: Brand analysis information
        ad_copy: Ad copy with headline, subheadline, etc.
        
    Returns:
        Dictionary with final composite image paths
    """
    # Validate paths upfront
        if not product_path or not isinstance(product_path, str):
            self.logger.error(f"Invalid product path: {product_path}")
            raise ValueError(f"Invalid product path provided: {product_path}")
        
        if not background_path or not isinstance(background_path, str):
            self.logger.error(f"Invalid background path: {background_path}")
            raise ValueError(f"Invalid background path provided: {background_path}")
    
        if not os.path.exists(product_path):
            self.logger.error(f"Product image not found: {product_path}")
            raise FileNotFoundError(f"Product image not found: {product_path}")
        
        if not os.path.exists(background_path):
            self.logger.error(f"Background image not found: {background_path}")
            raise FileNotFoundError(f"Background image not found: {background_path}")
    
        self.logger.info("Integrating product with background and text elements")
    
    # Load images
        product = Image.open(product_path).convert("RGBA")
        background = Image.open(background_path).convert("RGBA")
    
    # Step 1: Calculate optimal product placement
        placement = self._calculate_optimal_placement(product, background, brand_analysis)
        self.logger.info(f"Calculated placement: {placement}")
    
    # Step 2: Add professional effects to product (shadows, reflections)
        product_with_effects = self._add_professional_product_effects(
        product, 
        placement, 
        brand_analysis.get("brand_level", "Premium")
    )
    
    # Step 3: Create the composite image with product
        composite = self._create_professional_composite(
        product_with_effects, 
        background, 
        placement
    )
    
    # Step 4: Enhance composition quality
        enhanced_composite = self._enhance_final_composite(
        composite, 
        product_info, 
        brand_analysis
    )
    
    # Step 5: Add typography if ad copy is provided
        if ad_copy and any(ad_copy.values()):
            typography_composite = self._add_professional_typography(
            enhanced_composite,
            ad_copy,
            brand_analysis,
            placement
        )
            final_image = typography_composite
        else:
            final_image = enhanced_composite
    
    # Save the composite images
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save intermediate composite
        composite_path = f"output/images/composites/composite_{timestamp}.png"
        enhanced_composite.save(composite_path)
    
    # Save final image with typography
        final_path = f"output/images/composites/final_{timestamp}.png"
        final_image.save(final_path)
    
        self.logger.info(f"Product integration complete: {final_path}")
    
        return {
        "composite_path": composite_path,
        "final_path": final_path,
        "image_path": final_path,  # Add this key for consistency
        "placement": placement
    }
    
    def _create_professional_composite(self, product_with_effects: Image.Image, 
                               background: Image.Image, 
                               placement: Dict[str, int]) -> Image.Image:
        """
    Create a professional composite with improved background preservation.
    """
        self.logger.info("Creating professional composite")
    
    # Make sure background is in RGBA mode
        if background.mode != 'RGBA':
            background = background.convert('RGBA')
    
    # Create a copy of the background
        composite = background.copy()
    
    # Get placement coordinates
        x, y = placement['x'], placement['y']
    
    # Create a mask for better blending
        if product_with_effects.mode == 'RGBA':
            r, g, b, a = product_with_effects.split()
            mask = a
        else:
            mask = None
    
    # Paste product onto background using alpha mask for proper compositing
        composite.paste(product_with_effects, (x, y), mask)
    
        return composite
    
    def _add_professional_typography(self, image: Image.Image, ad_copy: Dict[str, Any], 
                              brand_analysis: Dict[str, Any], 
                              placement: Dict[str, int]) -> Image.Image:
        """
    Add professional typography to the advertisement.
    
    Args:
        image: Composite image
        ad_copy: Ad copy dictionary with text elements
        brand_analysis: Brand analysis information
        placement: Product placement information
        
    Returns:
        Image with professional typography
    """
    # Make a copy of image to avoid modifying original
        composite = image.copy()
        width, height = composite.size
    
    # Extract text elements
        headline = ad_copy.get("headline", "")
        subheadline = ad_copy.get("subheadline", "")
        body_text = ad_copy.get("body_text", "")
        call_to_action = ad_copy.get("call_to_action", "")
    
    # Skip if no text is provided
        if not any([headline, subheadline, body_text, call_to_action]):
            return composite
    
    # Create text overlay
        text_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_overlay)
    
    # Determine brand style for typography
        brand_level = brand_analysis.get("brand_level", "Premium").lower()
        industry = brand_analysis.get("industry", "General").lower()
    
    # Determine text colors based on background
        bg_brightness = self._analyze_image_brightness(composite)
    
        if bg_brightness > 0.5:
        # Light background
            text_color = (20, 20, 20, 255)  # Near black
            secondary_color = (60, 60, 60, 255)  # Dark gray
        else:
        # Dark background
            text_color = (255, 255, 255, 255)  # White
            secondary_color = (220, 220, 220, 255)  # Light gray

    # Determine highlight color from brand analysis or product
        highlight_color = self._determine_highlight_color(brand_analysis, image)
    
    # Calculate safe text areas based on product placement
        safe_areas = self._calculate_text_safe_areas(placement, width, height)
    
    # Load appropriate fonts
        try:
            if "luxury" in brand_level:
            # Elegant serif fonts for luxury
                headline_font = ImageFont.truetype("arial.ttf", size=int(height * 0.06))
                subheadline_font = ImageFont.truetype("arial.ttf", size=int(height * 0.04))
                body_font = ImageFont.truetype("arial.ttf", size=int(height * 0.025))
                cta_font = ImageFont.truetype("arial.ttf", size=int(height * 0.035))
            elif "tech" in industry or "electronics" in industry:
            # Sans-serif fonts for tech
                headline_font = ImageFont.truetype("arial.ttf", size=int(height * 0.06))
                subheadline_font = ImageFont.truetype("arial.ttf", size=int(height * 0.04))
                body_font = ImageFont.truetype("arial.ttf", size=int(height * 0.025))
                cta_font = ImageFont.truetype("arial.ttf", size=int(height * 0.035))
            else:
            # Standard premium fonts
                headline_font = ImageFont.truetype("arial.ttf", size=int(height * 0.06))
                subheadline_font = ImageFont.truetype("arial.ttf", size=int(height * 0.04))
                body_font = ImageFont.truetype("arial.ttf", size=int(height * 0.025))
                cta_font = ImageFont.truetype("arial.ttf", size=int(height * 0.035))
        except:
        # Fallback to default font if custom fonts fail
            headline_font = None
            subheadline_font = None
            body_font = None
            cta_font = None
        
        # Adjust font sizes for default font
            headline_size = int(height * 0.06)
            subheadline_size = int(height * 0.04)
            body_size = int(height * 0.025)
            cta_size = int(height * 0.035)
    
    # Add headline text
        if headline:
        # Determine optimal headline position based on safe areas
            if safe_areas["top"]["available"]:
            # Place at top
                headline_x = width // 2
                headline_y = int(height * 0.1)
                alignment = "center"
            elif safe_areas["left"]["available"]:
            # Place on left
                headline_x = int(width * 0.1)
                headline_y = height // 2 - int(height * 0.2)
                alignment = "left"
            elif safe_areas["right"]["available"]:
            # Place on right
                headline_x = int(width * 0.9)
                headline_y = height // 2 - int(height * 0.2)
                alignment = "right"
            else:
            # Default to top
                headline_x = width // 2
                headline_y = int(height * 0.1)
                alignment = "center"
        
        # Draw headline with appropriate styling
            self._draw_styled_text(
            draw, 
            headline, 
            (headline_x, headline_y), 
            headline_font or headline_size,
            text_color,
            highlight_color,
            alignment,
            style="headline",
            brand_level=brand_level
        )
    
    # Add subheadline
        if subheadline:
        # Position subheadline relative to headline
            if headline:
                if alignment == "center":
                    subheadline_x = width // 2
                    subheadline_y = headline_y + int(height * 0.08)
                    sub_alignment = "center"
                elif alignment == "left":
                    subheadline_x = headline_x
                    subheadline_y = headline_y + int(height * 0.07)
                    sub_alignment = "left"
                else:  # right
                    subheadline_x = headline_x
                    subheadline_y = headline_y + int(height * 0.07)
                    sub_alignment = "right"
            else:
            # No headline, position subheadline independently
                if safe_areas["top"]["available"]:
                    subheadline_x = width // 2
                    subheadline_y = int(height * 0.15)
                    sub_alignment = "center"
                else:
                    subheadline_x = width // 2
                    subheadline_y = int(height * 0.1)
                    sub_alignment = "center"
        
        # Draw subheadline
            self._draw_styled_text(
            draw, 
            subheadline, 
            (subheadline_x, subheadline_y), 
            subheadline_font or subheadline_size,
            secondary_color,
            None,
            sub_alignment,
            style="subheadline",
            brand_level=brand_level
        )
    
    # Add body text if provided
        if body_text:
        # Position body text in available area
            if safe_areas["bottom"]["available"]:
                body_x = width // 2
                body_y = int(height * 0.7)
                body_alignment = "center"
                max_width = int(width * 0.8)
            elif safe_areas["left"]["available"]:
                body_x = int(width * 0.15)
                body_y = height // 2
                body_alignment = "left"
                max_width = int(width * 0.3)
            elif safe_areas["right"]["available"]:
                body_x = int(width * 0.85)
                body_y = height // 2
                body_alignment = "right"
                max_width = int(width * 0.3)
            else:
            # Default to bottom
                body_x = width // 2
                body_y = int(height * 0.75)
                body_alignment = "center"
                max_width = int(width * 0.7)
        
        # Format body text to fit available space
            formatted_body = self._format_text_to_fit(
            body_text,
            max_width,
            body_font or body_size
        )
        
        # Draw body text
            self._draw_styled_text(
            draw, 
            formatted_body, 
            (body_x, body_y), 
            body_font or body_size,
            secondary_color,
            None,
            body_alignment,
            style="body",
            brand_level=brand_level
        )
    
    # Add call to action
        if call_to_action:
        # Position CTA at bottom
            cta_x = width // 2
            cta_y = int(height * 0.9)
        
        # Draw CTA with special styling
            self._draw_styled_text(
            draw, 
            call_to_action, 
            (cta_x, cta_y), 
            cta_font or cta_size,
            highlight_color,
            None,
            "center",
            style="cta",
            brand_level=brand_level
        )
    
    # Composite text overlay with image
        result = Image.alpha_composite(composite.convert("RGBA"), text_overlay)
    
        return result

    def _analyze_image_brightness(self, image: Image.Image) -> float:
        """
    Analyze the overall brightness of an image.
    
    Args:
        image: PIL Image
        
    Returns:
        Brightness value (0-1)
    """
    # Convert to grayscale
        gray = image.convert("L")
        histogram = gray.histogram()
    
    # Calculate weighted brightness
        total_pixels = sum(histogram)
        if total_pixels == 0:
            return 0.5
    
        weighted_sum = sum(i * count for i, count in enumerate(histogram))
        average_brightness = weighted_sum / (total_pixels * 255)
    
        return average_brightness

    def _determine_highlight_color(self, brand_analysis: Dict[str, Any], image: Image.Image) -> Tuple[int, int, int, int]:
        """
    Determine an appropriate highlight color for typography.
    
    Args:
        brand_analysis: Brand analysis information
        image: Composite image
        
    Returns:
        RGBA color tuple
    """
    # Check for brand colors in analysis
        brand_colors = brand_analysis.get("brand_colors", [])
    
        if brand_colors and isinstance(brand_colors, list) and len(brand_colors) > 0:
        # Use first brand color
            color = brand_colors[0]
            if isinstance(color, tuple) and len(color) >= 3:
                r, g, b = color[:3]
                return (r, g, b, 255)
    
    # Extract vibrant color from image if no brand colors
        vibrant_color = self._extract_vibrant_color(image)
        if vibrant_color:
            r, g, b = vibrant_color
            return (r, g, b, 255)
    
    # Default highlight colors based on image brightness
        brightness = self._analyze_image_brightness(image)
    
        if brightness > 0.6:
        # Dark highlight for light images
            return (40, 90, 160, 255)  # Dark blue
        else:
        # Light highlight for dark images
            return (230, 180, 60, 255)  # Gold

    def _extract_vibrant_color(self, image: Image.Image) -> Optional[Tuple[int, int, int]]:
        """
    Extract a vibrant, saturated color from the image.
    
    Args:
        image: PIL Image
        
    Returns:
        RGB color tuple or None
    """
    # Resize for faster processing
        img_small = image.copy().resize((100, 100), Image.LANCZOS)
        img_small = img_small.convert("RGB")
    
    # Get pixel data
        pixels = list(img_small.getdata())
    
    # Calculate saturation and vibrance for each pixel
        import colorsys
        vibrant_pixels = []
    
        for r, g, b in pixels:
            r_norm, g_norm, b_norm = r/255.0, g/255.0, b/255.0
            h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
        
        # Only consider saturated, vibrant colors
            if s > 0.5 and v > 0.5:
                vibrance = s * v
                vibrant_pixels.append(((r, g, b), vibrance))
    
    # If no vibrant pixels found
        if not vibrant_pixels:
            return None
    
    # Sort by vibrance and get top results
        vibrant_pixels.sort(key=lambda x: x[1], reverse=True)
    
    # Return most vibrant color
        return vibrant_pixels[0][0]

    def _calculate_text_safe_areas(self, placement: Dict[str, int], width: int, height: int) -> Dict[str, Dict[str, Any]]:
        """
    Calculate safe areas for text placement based on product position.
    
    Args:
        placement: Product placement information
        width: Image width
        height: Image height
        
    Returns:
        Dictionary with safe area information
    """
    # Extract product bounds
        product_x = placement["x"]
        product_y = placement["y"]
        product_width = placement["width"]
        product_height = placement["height"]
    
    # Calculate product bounds
        product_left = product_x
        product_right = product_x + product_width
        product_top = product_y
        product_bottom = product_y + product_height
    
    # Define minimum space needed for text
        min_space_needed = height * 0.15
    
    # Calculate available space in each region
        top_space = product_top
        bottom_space = height - product_bottom
        left_space = product_left
        right_space = width - product_right
    
    # Determine which areas are available for text
        return {
        "top": {
            "available": top_space >= min_space_needed,
            "space": top_space,
            "bounds": (0, 0, width, product_top)
        },
        "bottom": {
            "available": bottom_space >= min_space_needed,
            "space": bottom_space,
            "bounds": (0, product_bottom, width, height)
        },
        "left": {
            "available": left_space >= min_space_needed,
            "space": left_space,
            "bounds": (0, 0, product_left, height)
        },
        "right": {
            "available": right_space >= min_space_needed,
            "space": right_space,
            "bounds": (product_right, 0, width, height)
        }
    }

    def _format_text_to_fit(self, text: str, max_width: int, font) -> str:
        """
    Format text to fit within a specified width.
    
    Args:
        text: Text to format
        max_width: Maximum width in pixels
        font: Font to use for measurement
        
    Returns:
        Formatted text with line breaks
    """
    # Split text into words
        words = text.split()
        if not words:
            return ""
    
    # Initialize variables
        lines = []
        current_line = words[0]
    
    # Process each word
        for word in words[1:]:
        # Try adding the word to the current line
            test_line = current_line + " " + word
        
        # Measure width
            try:
                if hasattr(font, "getbbox"):
                    text_width = font.getbbox(test_line)[2]
                else:
                # For older PIL versions or numeric font size
                    if isinstance(font, int):
                    # Approximate width calculation
                        text_width = len(test_line) * (font * 0.6)
                    else:
                        text_width = font.getsize(test_line)[0]
            except:
            # Fallback approximation
                text_width = len(test_line) * 10
        
        # Check if it fits
            if text_width <= max_width:
                current_line = test_line
            else:
            # Add current line and start a new one
                lines.append(current_line)
                current_line = word
    
    # Add the last line
        lines.append(current_line)
    
    # Join lines with newline characters
        return "\n".join(lines)

    def _draw_styled_text(self, draw, text: str, position: Tuple[int, int], 
                   font, color: Tuple[int, int, int, int], 
                   highlight_color: Optional[Tuple[int, int, int, int]],
                   alignment: str, style: str, brand_level: str) -> None:
        """
    Draw text with professional styling based on text type and brand level.
    
    Args:
        draw: ImageDraw object
        text: Text to draw
        position: Position (x, y)
        font: Font to use
        color: Text color
        highlight_color: Optional highlight color
        alignment: Text alignment (left, center, right)
        style: Text style (headline, subheadline, body, cta)
        brand_level: Brand positioning level
    """
        x, y = position
    
    # Handle multi-line text
        lines = text.split('\n')
    
    # Calculate text size
        try:
            if isinstance(font, int):
            # Approximate height for numeric font size
                line_height = int(font * 1.2)
                get_text_width = lambda line: len(line) * (font * 0.6)
            else:
            # Use font methods to get dimensions
                if hasattr(font, "getbbox"):
                    # For newer PIL versions
                    line_height = font.getbbox("Tg")[3] + font.getbbox("Tg")[1]
                    get_text_width = lambda line: font.getbbox(line)[2]
                else:
                # For older PIL versions
                    line_height = font.getsize("Tg")[1]
                    get_text_width = lambda line: font.getsize(line)[0]
        except:
        # Fallback approximation
            line_height = 30 if style == "headline" else 20
            get_text_width = lambda line: len(line) * 10
    
    # Apply special styling based on text type and brand level
        if style == "headline":
        # For luxury brands, add subtle text shadow or glow
            if "luxury" in brand_level:
            # Draw subtle shadow or glow
                shadow_color = (0, 0, 0, 100)  # Semi-transparent black
            
                for i, line in enumerate(lines):
                # Calculate position based on alignment
                    if alignment == "center":
                        text_width = get_text_width(line)
                        line_x = x - text_width // 2
                    elif alignment == "right":
                        text_width = get_text_width(line)
                        line_x = x - text_width
                    else:  # left
                        line_x = x

                    line_y = y + i * line_height
                
                # Draw shadow/glow
                    for offset in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                        draw.text((line_x + offset[0], line_y + offset[1]), line, font=font, fill=shadow_color)
        
        # For premium/standard, add underline or background highlight
            elif highlight_color:
                for i, line in enumerate(lines):
                # Calculate position based on alignment
                    if alignment == "center":
                        text_width = get_text_width(line)
                        line_x = x - text_width // 2
                    elif alignment == "right":
                        text_width = get_text_width(line)
                        line_x = x - text_width
                    else:  # left
                        line_x = x
                        text_width = get_text_width(line)
                
                    line_y = y + i * line_height
                
                # Add underline for premium brands
                    if "premium" in brand_level:
                        underline_y = line_y + line_height + 5
                        draw.line(
                        [(line_x, underline_y), (line_x + text_width, underline_y)],
                        fill=highlight_color,
                        width=2
                    )
    
        elif style == "cta":
        # For CTA, add button styling
            for i, line in enumerate(lines):
            # Calculate position based on alignment
                if alignment == "center":
                    text_width = get_text_width(line)
                    line_x = x - text_width // 2
                elif alignment == "right":
                    text_width = get_text_width(line)
                    line_x = x - text_width
                else:  # left
                    line_x = x
                    text_width = get_text_width(line)
            
                line_y = y + i * line_height
            
            # Add button background for CTA
                padding = 10
                button_bounds = [
                line_x - padding,
                line_y - padding // 2,
                line_x + text_width + padding,
                line_y + line_height + padding // 2
            ]
            
            # Draw button background
                if isinstance(color, tuple) and len(color) >= 3:
                    button_color = color[:3] + (180,)  # Semi-transparent
                    draw.rectangle(button_bounds, fill=button_color)
                
                # Use contrasting text color
                    r, g, b = color[:3]
                    brightness = (r * 0.299 + g * 0.587 + b * 0.114) / 255
                
                    if brightness > 0.5:
                        text_color = (0, 0, 0, 255)  # Black for light backgrounds
                    else:
                        text_color = (255, 255, 255, 255)  # White for dark backgrounds
                else:
                # Fallback
                    button_color = (40, 90, 160, 180)  # Semi-transparent blue
                    text_color = (255, 255, 255, 255)  # White
            
            # Override color for CTA text
                color = text_color
    
    # Draw the actual text
        for i, line in enumerate(lines):
        # Calculate position based on alignment
            if alignment == "center":
                text_width = get_text_width(line)
                line_x = x - text_width // 2
            elif alignment == "right":
                text_width = get_text_width(line)
                line_x = x - text_width
            else:  # left
                line_x = x
        
            line_y = y + i * line_height
        
        # Draw text
            draw.text((line_x, line_y), line, font=font, fill=color)