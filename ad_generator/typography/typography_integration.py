"""
Integration module to connect EnhancedTypographySystem with StudioImageGenerator
"""
import logging
import os
import datetime
from typing import Dict, List, Tuple, Any, Optional, Union
from PIL import Image

def integrate_enhanced_typography(image_maker_instance):
    """
    Integrate the enhanced typography system with an existing StudioImageGenerator.
    
    Args:
        image_maker_instance: The StudioImageGenerator instance to enhance
        
    Returns:
        Enhanced StudioImageGenerator instance
    """
    # Import new system
    logger = logging.getLogger(__name__)
    logger.info("Integrating enhanced typography system")
    
    try:
        # Import OpenCV if available
        import cv2
        logger.info("OpenCV is available for advanced image analysis")
    except ImportError:
        logger.warning("OpenCV not found. Installing opencv-python is recommended for best results")
    
    # Create instance of enhanced typography system
    from ad_generator.typography.enhanced_typography import EnhancedTypographySystem
    enhanced_typography = EnhancedTypographySystem(
        font_manager=image_maker_instance.font_manager if hasattr(image_maker_instance, 'font_manager') else None,
        text_effects=image_maker_instance.text_effects if hasattr(image_maker_instance, 'text_effects') else None,
        brand_typography=image_maker_instance.brand_typography if hasattr(image_maker_instance, 'brand_typography') else None
    )
    
    # Store reference to the enhanced system
    image_maker_instance.enhanced_typography = enhanced_typography
    
    # Define the enhanced method
    def enhanced_apply_integrated_typography(self, image_path, headline, subheadline=None,
                                        call_to_action=None, brand_name=None,
                                        industry=None, brand_level="premium",
                                        text_placement="dynamic", color_scheme=None):
        """
        Apply professional typography with enhanced integration and perfect text placement.
        
        Args:
            image_path: Path to the image
            headline: Main headline text
            subheadline: Subheadline text (optional)
            call_to_action: Call to action text (optional)
            brand_name: Brand name (optional)
            industry: Industry category (optional)
            brand_level: Brand positioning level (optional)
            text_placement: Text placement style (optional)
            color_scheme: Color scheme specification (optional)
            
        Returns:
            Path to the final image with text
        """
        # Validate image path thoroughly
        if not image_path or not isinstance(image_path, str):
            self.logger.error(f"Invalid image path for typography: {image_path}")
            raise ValueError(f"Invalid image path provided: {image_path}")
        
        if not os.path.exists(image_path):
            self.logger.error(f"Image not found for typography: {image_path}")
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        self.logger.info(f"Applying enhanced typography to {image_path}")
        
        # Open original image
        original_image = Image.open(image_path).convert('RGBA')
        
        # Get text elements
        text_elements = {
            'headline': headline,
            'subheadline': subheadline,
            'body': '',
            'call_to_action': call_to_action,
            'brand_name': brand_name
        }
        
        # Generate optimized colors based on image analysis
        if hasattr(self, 'color_optimizer') and self.color_optimizer:
            optimized_colors = self.color_optimizer.optimize_colors(
                image=original_image,
                brand_name=brand_name,
                industry=industry,
                brand_level=brand_level
            )
            self.logger.info(f"Applied smart color optimization for {brand_name} in {industry}")
        else:
            # Create basic color scheme if optimizer not available
            optimized_colors = {
                "headline_color": (255, 255, 255, 255),
                "subheadline_color": (220, 220, 220, 255),
                "body_color": (200, 200, 200, 255),
                "cta_text_color": (255, 255, 255, 255),
                "cta_button_color": (41, 128, 185, 230),
                "brand_color": (255, 255, 255, 255),
                "accent_color": (41, 128, 185, 255)
            }
        
        # Create style profile with optimized colors
        style_profile = {
            "style": self._select_best_ad_style(industry, brand_level, "perfume" if "perfume" in image_path.lower() else "generic"),
            "text_placement": text_placement,
            "color_overrides": {
                "headline_color": optimized_colors["headline_color"],
                "subheadline_color": optimized_colors["subheadline_color"],
                "body_color": optimized_colors["body_color"],
                "cta_text_color": optimized_colors["cta_text_color"],
                "cta_button_color": optimized_colors["cta_button_color"],
                "brand_color": optimized_colors["brand_color"],
                "accent_color": optimized_colors["accent_color"]
            }
        }
        
        # Add color scheme if provided
        if color_scheme:
            style_profile["color_scheme"] = color_scheme
        
        # Use the enhanced typography system
        result_image = self.enhanced_typography.create_typography(
            image=original_image,
            text_elements=text_elements,
            brand_name=brand_name,
            industry=industry,
            brand_level=brand_level,
            style_profile=style_profile
        )
        
        # Save and return
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_path = f"output/images/final_ad_{timestamp}.png"
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        result_image.convert('RGB').save(final_path, 'PNG', quality=100)
        self.logger.info(f"Final image with enhanced typography saved: {final_path}")
        
        return final_path
    
    # Replace the apply_integrated_typography method with the enhanced version
    image_maker_instance.apply_integrated_typography = enhanced_apply_integrated_typography.__get__(image_maker_instance)
    
    return image_maker_instance