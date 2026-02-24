# Typography Integration Module
"""
Typography Integration Module

This module bridges your existing typography system with the video ad generator.
It leverages the typography system's capabilities for text styling in videos.
"""

import logging
import os
from typing import Dict, Any, List, Tuple, Optional

from .utils import setup_logger

# Setup logger
logger = setup_logger('typography_integration')

def initialize_typography_system() -> Tuple[bool, Dict[str, Any]]:
    """
    Initialize the typography system components if available.
    
    Returns:
        Tuple of (success, system_components)
    """
    try:
        # Try to import typography system components
        from typography_system import TypographySystem
        from brand_typography import BrandTypographyManager
        from typography_effects import TypographyEffectsEngine
        from layout_engine import TextLayoutEngine
        from font_pairing import FontPairingEngine
        from responsive_scaling import ResponsiveTextScaling
        
        # Initialize components
        typography_system = TypographySystem()
        brand_typography = BrandTypographyManager()
        effects_engine = TypographyEffectsEngine()
        layout_engine = TextLayoutEngine()
        font_pairing = FontPairingEngine()
        responsive_scaling = ResponsiveTextScaling()
        
        # Return components
        components = {
            'typography_system': typography_system,
            'brand_typography': brand_typography,
            'effects_engine': effects_engine,
            'layout_engine': layout_engine,
            'font_pairing': font_pairing,
            'responsive_scaling': responsive_scaling
        }
        
        logger.info("Typography system components initialized successfully")
        return True, components
        
    except ImportError as e:
        logger.warning(f"Typography system not found: {e}")
        return False, {}
    except Exception as e:
        logger.error(f"Error initializing typography system: {e}")
        return False, {}

def get_brand_typography_config(
    brand_name: str,
    industry: Optional[str] = None,
    brand_level: Optional[str] = None,
    components: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Get typography configuration for a specific brand.
    
    Args:
        brand_name: Name of the brand
        industry: Industry category (optional)
        brand_level: Brand positioning level (optional)
        components: Typography system components
        
    Returns:
        Typography configuration for the brand
    """
    if not components:
        # Try to initialize components
        success, components = initialize_typography_system()
        if not success:
            # Return default configuration
            return _get_default_typography_config(brand_name)
    
    try:
        # Get typography style from brand typography manager
        typography_system = components.get('typography_system')
        brand_typography = components.get('brand_typography')
        
        if typography_system:
            # Use typography system to get full style
            style = typography_system.get_style_preview(
                brand_name=brand_name,
                industry=industry,
                brand_level=brand_level
            )
            
            # Extract relevant configuration for video text
            config = _extract_video_text_config(style)
            return config
            
        elif brand_typography:
            # Use brand typography manager directly
            style = brand_typography.get_typography_style(
                brand_name=brand_name,
                industry=industry,
                brand_level=brand_level
            )
            
            # Extract relevant configuration for video text
            config = _extract_video_text_config(style)
            return config
            
        else:
            # Return default configuration
            return _get_default_typography_config(brand_name)
            
    except Exception as e:
        logger.error(f"Error getting brand typography: {e}")
        return _get_default_typography_config(brand_name)

def apply_typography_to_text_overlay(
    text: str,
    element_type: str,
    brand_config: Dict[str, Any],
    image_size: Tuple[int, int],
    components: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Apply typography styling to text for video overlay.
    
    Args:
        text: Text content
        element_type: Type of text element (headline, subheadline, etc.)
        brand_config: Brand configuration
        image_size: Image size (width, height)
        components: Typography system components
        
    Returns:
        Text styling configuration for video overlay
    """
    if not components:
        # Try to initialize components
        success, components = initialize_typography_system()
        if not success:
            # Return default styling
            return _get_default_text_styling(text, element_type, brand_config)
    
    try:
        # Get components
        typography_system = components.get('typography_system')
        effects_engine = components.get('effects_engine')
        layout_engine = components.get('layout_engine')
        responsive_scaling = components.get('responsive_scaling')
        
        # Calculate text size based on responsive scaling
        if responsive_scaling:
            text_sizes = responsive_scaling.calculate_text_sizes(
                image_size=image_size,
                text_elements={element_type: text},
                typography_style=brand_config
            )
            size = text_sizes.get(element_type, 60 if element_type == 'headline' else 40)
        else:
            # Default sizes
            size = 60 if element_type == 'headline' else 40
        
        # Determine text effect based on brand config
        effect = brand_config.get('text_treatments', {}).get(element_type, 'simple')
        
        # Determine text position based on layout engine
        position = (0.5, 0.5)  # Default to center
        if layout_engine:
            # Create a mock image for analysis
            from PIL import Image
            mock_image = Image.new('RGB', image_size, (0, 0, 0))
            
            # Analyze image for optimal text placement
            analysis = layout_engine.analyze_image(mock_image)
            
            # Get text positions
            composition_template = {'text_zones': {
                element_type: {'y_range': [0.3, 0.7], 'preferred_alignment': 'center'}
            }}
            
            positions = layout_engine.calculate_text_positions(
                mock_image,
                {element_type: text},
                {},  # No fonts available
                {element_type: size},
                analysis,
                brand_config
            )
            
            if element_type in positions:
                position = positions[element_type].get('position', (0.5, 0.5))
                position = (position[0] / image_size[0], position[1] / image_size[1])
        
        # Compile styling configuration
        styling = {
            'text': text,
            'size': size,
            'effect': effect,
            'position': position,
            'color': brand_config.get('color_scheme', {}).get(f'{element_type}_color', (255, 255, 255))
        }
        
        return styling
        
    except Exception as e:
        logger.error(f"Error applying typography to text: {e}")
        return _get_default_text_styling(text, element_type, brand_config)

def _extract_video_text_config(style: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant configuration for video text from typography style.
    
    Args:
        style: Typography style dictionary
        
    Returns:
        Video text configuration
    """
    # Default text effect mappings
    effect_mappings = {
        'clean_gradient': 'gradient',
        'elegant_serif': 'minimal_elegant',
        'dynamic_bold': 'dynamic',
        'premium_gradient': 'gradient',
        'luxury_metallic': 'elegant',
        'subtle_glow': 'subtle_glow',
        'minimal_elegant': 'minimal_elegant',
        'simple': 'simple'
    }
    
    # Extract text treatments
    text_treatments = {}
    for element, treatment in style.get('text_treatments', {}).items():
        text_treatments[element] = effect_mappings.get(treatment, 'simple')
    
    # Extract color scheme
    colors = style.get('color_scheme', {})
    
    # Extract text placement
    text_placement = style.get('text_placement', 'centered')
    
    return {
        'font': style.get('font', 'Arial-Bold'),
        'font_fallback': 'Arial',
        'colors': {
            'primary': colors.get('primary', '#000000'),
            'secondary': colors.get('secondary', '#FFFFFF'),
            'accent': colors.get('accent', '#0066CC')
        },
        'text_styles': {
            'headline': {'fontsize': int(style.get('headline_size_factor', 0.08) * 1000)},
            'subheadline': {'fontsize': int(style.get('subheadline_size_factor', 0.04) * 1000)},
            'body': {'fontsize': int(style.get('body_size_factor', 0.032) * 1000)},
            'cta': {'fontsize': int(style.get('cta_size_factor', 0.038) * 1000)},
            'brand': {'fontsize': int(style.get('brand_size_factor', 0.05) * 1000)}
        },
        'text_treatments': text_treatments,
        'text_placement': text_placement,
        'animation': 'standard'
    }

def _get_default_typography_config(brand_name: str) -> Dict[str, Any]:
    """
    Get default typography configuration for a brand.
    
    Args:
        brand_name: Name of the brand
        
    Returns:
        Default typography configuration
    """
    return {
        'font': 'Arial-Bold',
        'font_fallback': 'Arial',
        'colors': {
            'primary': '#0066CC',
            'secondary': '#FFFFFF',
            'accent': '#FFD700'
        },
        'text_styles': {
            'headline': {'fontsize': 70, 'color': 'white', 'font': 'Arial-Bold'},
            'subheadline': {'fontsize': 40, 'color': 'white', 'font': 'Arial'},
            'body': {'fontsize': 30, 'color': 'white', 'font': 'Arial'},
            'cta': {'fontsize': 50, 'color': 'white', 'font': 'Arial-Bold', 'bg_color': '#0066CC'},
            'brand': {'fontsize': 45, 'color': 'white', 'font': 'Arial-Bold'}
        },
        'text_treatments': {
            'headline': 'simple',
            'subheadline': 'simple',
            'body': 'simple',
            'cta': 'simple',
            'brand': 'simple'
        },
        'text_placement': 'centered',
        'animation': 'standard'
    }

def _get_default_text_styling(text: str, element_type: str, brand_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get default text styling for video overlay.
    
    Args:
        text: Text content
        element_type: Type of text element
        brand_config: Brand configuration
        
    Returns:
        Default text styling
    """
    # Default sizes
    sizes = {
        'headline': 70,
        'subheadline': 40,
        'body': 30,
        'cta': 50,
        'brand': 45
    }
    
    # Default positions (normalized 0-1)
    positions = {
        'headline': (0.5, 0.3),
        'subheadline': (0.5, 0.4),
        'body': (0.5, 0.5),
        'cta': (0.5, 0.7),
        'brand': (0.5, 0.8)
    }
    
    # Get effect from brand config if available
    effect = brand_config.get('text_treatments', {}).get(element_type, 'simple')
    
    return {
        'text': text,
        'size': sizes.get(element_type, 40),
        'effect': effect,
        'position': positions.get(element_type, (0.5, 0.5)),
        'color': brand_config.get('text_styles', {}).get(element_type, {}).get('color', 'white')
    }

if __name__ == "__main__":
    # Test the typography integration
    logger.info("Testing typography integration")
    
    # Initialize typography system
    success, components = initialize_typography_system()
    logger.info(f"Typography system initialization: {'Success' if success else 'Failed'}")
    
    if success:
        # Test brand typography configuration
        config = get_brand_typography_config("Sample Brand", "technology", "premium", components)
        logger.info(f"Brand typography config: {config.get('font', 'unknown font')}")
        
        # Test text styling
        styling = apply_typography_to_text_overlay(
            "Sample Headline",
            "headline",
            config,
            (1920, 1080),
            components
        )
        logger.info(f"Text styling: {styling.get('size')}px, effect: {styling.get('effect')}")
    
    logger.info("Typography integration tests completed")