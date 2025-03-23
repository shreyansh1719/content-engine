"""
Advanced Image Processing Module for Marketplace Scraper
"""

import os
import logging
import random
import time
import traceback
from typing import Dict, List, Any, Optional
from datetime import datetime

import requests
import numpy as np
from PIL import Image
from io import BytesIO

class ImageProcessor:
    def __init__(self, output_dir: str):
        """
        Initialize image processing capabilities
        
        Args:
            output_dir: Directory to save processed images
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def process_image(self, image_url: str) -> Dict[str, Any]:
        """
        Process image from URL and extract features
        
        Args:
            image_url: URL of the image to process
            
        Returns:
            Dictionary of extracted image features
        """
        try:
            # Download the image
            image_array = self.download_image(image_url)
            
            if image_array is None:
                return {"error": "Failed to download image"}
            
            # Save a copy of the image
            image_path = self.save_image(image_array)
            
            # Extract features
            color_features = self.extract_color_features(image_array)
            quality_metrics = self.calculate_image_quality_metrics(image_array)
            composition_analysis = self.analyze_composition(image_array)
            
            # Combine all features
            features = {
                "source_url": image_url,
                "saved_path": image_path,
                "dimensions": {
                    "width": image_array.shape[1],
                    "height": image_array.shape[0]
                },
                "aspect_ratio": image_array.shape[1] / image_array.shape[0] if image_array.shape[0] > 0 else 0,
                "color_features": color_features,
                "quality_metrics": quality_metrics,
                "composition": composition_analysis,
                "processing_time": datetime.now().isoformat()
            }
            
            self.logger.info(f"Successfully processed image: {image_url}")
            return features
            
        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def download_image(self, image_url: str) -> Optional[np.ndarray]:
        """
        Download image from URL
        
        Args:
            image_url: URL of the image to download
        
        Returns:
            Numpy array of the downloaded image or None if failed
        """
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Convert to PIL Image
            image = Image.open(BytesIO(response.content))
            
            # Convert to RGB if not already
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array
            image_array = np.array(image)
            
            return image_array
            
        except Exception as e:
            self.logger.warning(f"Image download error: {e}")
            return None
    
    def save_image(self, image: np.ndarray) -> str:
        """
        Save image to file
        
        Args:
            image: Numpy array of the image
        
        Returns:
            Path to saved image
        """
        try:
            # Generate unique filename
            filename = f"img_{random.randint(1000, 9999)}_{int(time.time())}.jpg"
            filepath = os.path.join(self.output_dir, filename)
            
            # Convert back to PIL Image for saving
            pil_image = Image.fromarray(image)
            pil_image.save(filepath, 'JPEG', quality=95)
            
            return filepath
            
        except Exception as e:
            self.logger.warning(f"Image save error: {e}")
            return ""
    
    def extract_color_features(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extract color features from image
        
        Args:
            image: Numpy array of the image
        
        Returns:
            Dictionary of color features
        """
        try:
            # Calculate average RGB values
            avg_color = np.mean(image, axis=(0, 1))
            
            # Find dominant colors by clustering
            # For simplicity, we'll use a histogram approach here
            # In a production system, you might use K-means clustering
            pixels = image.reshape(-1, 3)
            
            # Create color bins (simplified approach)
            bins = 5
            hist, _ = np.histogramdd(pixels, bins=bins, range=[(0, 256), (0, 256), (0, 256)])
            
            # Find most frequent bins
            idx = np.unravel_index(np.argsort(hist.ravel())[-5:], hist.shape)
            
            # Convert bin indices to RGB values
            bin_width = 256 / bins
            dominant_colors = []
            
            for i in range(len(idx[0])):
                r = int((idx[0][i] + 0.5) * bin_width)
                g = int((idx[1][i] + 0.5) * bin_width)
                b = int((idx[2][i] + 0.5) * bin_width)
                frequency = hist[idx[0][i], idx[1][i], idx[2][i]]
                
                # Convert to hex value
                hex_value = f"#{r:02x}{g:02x}{b:02x}"
                
                dominant_colors.append({
                    "rgb": [r, g, b],
                    "hex": hex_value,
                    "frequency": float(frequency) / pixels.shape[0]  # Normalized frequency
                })
            
            # Calculate color statistics
            color_std = np.std(pixels, axis=0)
            color_variance = np.var(pixels, axis=0)
            
            # Calculate brightness
            brightness = np.mean(pixels, axis=0).sum() / 3 / 255
            
            # Calculate saturation (simplified)
            rgb_mean = np.mean(pixels, axis=1)
            max_rgb = np.max(pixels, axis=1)
            min_rgb = np.min(pixels, axis=1)
            saturation = np.mean((max_rgb - min_rgb) / (max_rgb + 1e-8))
            
            return {
                "avg_color": {
                    "rgb": avg_color.tolist(),
                    "hex": f"#{int(avg_color[0]):02x}{int(avg_color[1]):02x}{int(avg_color[2]):02x}"
                },
                "dominant_colors": dominant_colors,
                "brightness": brightness,
                "saturation": saturation,
                "color_variance": color_variance.tolist(),
                "color_std": color_std.tolist()
            }
            
        except Exception as e:
            self.logger.warning(f"Color feature extraction error: {e}")
            return {}
    
    def calculate_image_quality_metrics(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Calculate image quality metrics
        
        Args:
            image: Numpy array of the image
        
        Returns:
            Dictionary of quality metrics
        """
        try:
            # Convert to grayscale for some calculations
            if image.ndim == 3:
                gray = np.dot(image[..., :3], [0.299, 0.587, 0.114])
            else:
                gray = image
            
            # Calculate contrast
            contrast = np.std(gray)
            
            # Calculate blur estimation (Laplacian variance)
            # Higher values = less blurry
            from scipy import ndimage
            laplacian = np.abs(ndimage.laplace(gray))
            blur_score = np.var(laplacian)
            
            # Noise estimation (simplified)
            # We're using the standard deviation of high frequency components
            from scipy.ndimage import gaussian_filter
            smoothed = gaussian_filter(gray, sigma=2)
            noise = gray - smoothed
            noise_level = np.std(noise)
            
            # Colorfulness metric (simplified)
            if image.ndim == 3:
                r, g, b = image[..., 0], image[..., 1], image[..., 2]
                rg = r - g
                yb = 0.5 * (r + g) - b
                colorfulness = np.sqrt(np.var(rg) + np.var(yb)) + 0.3 * np.sqrt(np.mean(rg)**2 + np.mean(yb)**2)
            else:
                colorfulness = 0
            
            return {
                "contrast": float(contrast),
                "blur_score": float(blur_score),  # Higher = less blurry
                "noise_level": float(noise_level),
                "colorfulness": float(colorfulness),
                "quality_assessment": self._assess_quality(contrast, blur_score, noise_level)
            }
            
        except Exception as e:
            self.logger.warning(f"Quality metrics calculation error: {e}")
            return {}
    
    def _assess_quality(self, contrast: float, blur_score: float, noise_level: float) -> str:
        """
        Provide a qualitative assessment of image quality
        
        Args:
            contrast: Contrast measure
            blur_score: Blur score (higher = less blurry)
            noise_level: Noise level
            
        Returns:
            Quality assessment string
        """
        # These thresholds should be calibrated based on your specific dataset
        if blur_score < 100:
            blur_quality = "blurry"
        elif blur_score < 500:
            blur_quality = "acceptable"
        else:
            blur_quality = "sharp"
        
        if contrast < 20:
            contrast_quality = "low contrast"
        elif contrast < 50:
            contrast_quality = "medium contrast"
        else:
            contrast_quality = "high contrast"
        
        if noise_level > 15:
            noise_quality = "noisy"
        elif noise_level > 5:
            noise_quality = "slightly noisy"
        else:
            noise_quality = "clean"
        
        # Overall quality assessment
        if blur_quality == "sharp" and contrast_quality == "high contrast" and noise_quality == "clean":
            return "excellent"
        elif blur_quality == "blurry" or contrast_quality == "low contrast":
            return "poor"
        else:
            return "average"
    
    def analyze_composition(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze image composition
        
        Args:
            image: Numpy array of the image
            
        Returns:
            Dictionary with composition analysis
        """
        try:
            height, width = image.shape[:2]
            
            # Calculate rule of thirds points
            third_h, third_w = height // 3, width // 3
            roi_points = [
                (third_w, third_h),
                (third_w * 2, third_h),
                (third_w, third_h * 2),
                (third_w * 2, third_h * 2)
            ]
            
            # Simplified subject detection
            # In a production system, you would use more sophisticated subject detection
            # But here we'll use a simple approach based on contrast
            if image.ndim == 3:
                gray = np.dot(image[..., :3], [0.299, 0.587, 0.114])
            else:
                gray = image
                
            # Apply Gaussian blur to reduce noise
            from scipy.ndimage import gaussian_filter
            blurred = gaussian_filter(gray, sigma=5)
            
            # Calculate gradient magnitude
            from scipy import ndimage
            gx = ndimage.sobel(blurred, axis=0)
            gy = ndimage.sobel(blurred, axis=1)
            gradient_magnitude = np.sqrt(gx**2 + gy**2)
            
            # Threshold to find edges
            threshold = np.percentile(gradient_magnitude, 90)
            edges = gradient_magnitude > threshold
            
            # Find potential subject location
            # Using center of mass of edges
            if np.any(edges):
                y_indices, x_indices = np.where(edges)
                subject_y = int(np.mean(y_indices))
                subject_x = int(np.mean(x_indices))
            else:
                # Default to center if no clear subject
                subject_y, subject_x = height // 2, width // 2
            
            # Check if subject is near rule of thirds points
            follows_rule_of_thirds = False
            for point_x, point_y in roi_points:
                if (abs(subject_x - point_x) < width * 0.1 and 
                    abs(subject_y - point_y) < height * 0.1):
                    follows_rule_of_thirds = True
                    break
            
            # Assess symmetry
            # Simplified approach - compare left/right halves
            left_half = gray[:, :width//2]
            right_half = gray[:, width//2:]
            right_half_flipped = np.fliplr(right_half)
            
            # Calculate symmetry score (lower = more symmetric)
            if left_half.shape == right_half_flipped.shape:
                symmetry_score = np.mean(np.abs(left_half - right_half_flipped))
                is_symmetric = symmetry_score < 20  # Threshold can be adjusted
            else:
                symmetry_score = 100
                is_symmetric = False
            
            # Check for presence of horizon line (simplified)
            # Looking for horizontal edges in middle third of image
            middle_third = gradient_magnitude[third_h:third_h*2, :]
            horizontal_edges = ndimage.sobel(middle_third, axis=0)
            has_horizon = np.percentile(horizontal_edges, 95) > threshold
            
            return {
                "follows_rule_of_thirds": follows_rule_of_thirds,
                "subject_position": {
                    "x": subject_x / width,  # Normalized
                    "y": subject_y / height
                },
                "symmetry": {
                    "score": float(symmetry_score),
                    "is_symmetric": is_symmetric
                },
                "has_horizon": has_horizon,
                "composition_type": self._determine_composition_type(
                    follows_rule_of_thirds, subject_x, subject_y, width, height, is_symmetric
                )
            }
            
        except Exception as e:
            self.logger.warning(f"Composition analysis error: {e}")
            return {}
    
    def _determine_composition_type(
        self, follows_rule_of_thirds: bool, subject_x: int, subject_y: int, 
        width: int, height: int, is_symmetric: bool
    ) -> str:
        """
        Determine the composition type based on analysis
        
        Args:
            follows_rule_of_thirds: Whether image follows rule of thirds
            subject_x: Subject x position
            subject_y: Subject y position
            width: Image width
            height: Image height
            is_symmetric: Whether image is symmetric
            
        Returns:
            Composition type
        """
        # Central composition
        if abs(subject_x - width/2) < width * 0.1 and abs(subject_y - height/2) < height * 0.1:
            return "central" if is_symmetric else "near_central"
        
        # Rule of thirds
        if follows_rule_of_thirds:
            return "rule_of_thirds"
        
        # Diagonal composition
        diagonal_distance = min(
            abs(subject_y/height - subject_x/width),  # Top-left to bottom-right
            abs(subject_y/height - (1 - subject_x/width))  # Top-right to bottom-left
        )
        
        if diagonal_distance < 0.15:
            return "diagonal"
        
        # Golden ratio (simplified check)
        golden_ratio = 1.618
        golden_x = width / golden_ratio
        golden_y = height / golden_ratio
        
        if (abs(subject_x - golden_x) < width * 0.1 and 
            abs(subject_y - golden_y) < height * 0.1):
            return "golden_ratio"
        
        # Default
        return "other"