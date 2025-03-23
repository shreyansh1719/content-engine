"""
Professional Typography System for Ad Generation
Orchestrates typography components to create studio-quality ad layouts
"""
import os
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont

from .brand_typography import BrandTypographyManager
from .typography_effects import TypographyEffectsEngine
from .layout_engine import TextLayoutEngine
from .font_pairing import FontPairingEngine
from .responsive_scaling import ResponsiveTextScaling

class TypographySystem:
    """
    Main orchestrator for the professional typography system.
    Coordinates all typography components to create cohesive, polished designs.
    """
    
    def __init__(self, fonts_directory: Optional[str] = None):
        """
        Initialize the typography system with all components.
        
        Args:
            fonts_directory: Optional custom fonts directory
        """
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize component engines
        self.brand_typography = BrandTypographyManager(fonts_directory)
        self.effects_engine = TypographyEffectsEngine()
        self.layout_engine = TextLayoutEngine()
        self.font_pairing = FontPairingEngine(fonts_directory)
        self.responsive_scaling = ResponsiveTextScaling()
        
        # Cache for generated typography styles
        self.style_cache = {}
        
    def create_typography(self, 
                         image: Image.Image,
                         text_elements: Dict[str, str],
                         brand_name: Optional[str] = None,
                         industry: Optional[str] = None,
                         brand_level: Optional[str] = None,
                         style_profile: Optional[Dict[str, Any]] = None) -> Image.Image:
        """
        Create professional typography for an advertisement image.
        
        Args:
            image: Base image for typography
            text_elements: Dictionary with text elements (headline, subheadline, body_text, cta)
            brand_name: Brand name for brand-specific typography
            industry: Industry category for industry-specific styling
            brand_level: Brand positioning (luxury, premium, mass-market, etc.)
            style_profile: Optional custom style profile overrides
            
        Returns:
            Image with professional typography applied
        """
        try:
            # Step 1: Analyze the image for optimal text placement
            image_analysis = self.layout_engine.analyze_image(image)
            
            # Step 2: Get typography style based on brand, industry and level
            typography_style = self.brand_typography.get_typography_style(
                brand_name=brand_name,
                industry=industry,
                brand_level=brand_level,
                style_overrides=style_profile
            )
            
            # Apply any style overrides
            if style_profile:
                typography_style.update(style_profile)
            
            # Step 3: Select font pairings based on typography style
            fonts = self.font_pairing.get_font_pairing(
                style=typography_style.get('style', 'modern'),
                brand_name=brand_name,
                text_elements=text_elements
            )
            
            # Step 4: Determine optimal text sizes based on image dimensions
            text_sizes = self.responsive_scaling.calculate_text_sizes(
                image_size=image.size,
                text_elements=text_elements,
                typography_style=typography_style
            )
            
            # Step 5: Calculate text positions based on layout strategy
            text_positions = self.layout_engine.calculate_text_positions(
                image=image,
                text_elements=text_elements,
                fonts=fonts,
                text_sizes=text_sizes,
                image_analysis=image_analysis,
                typography_style=typography_style
            )
            
            # Step 6: Create a new transparent overlay for text
            text_overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(text_overlay)
            
            # Step 7: Apply color scheme based on image analysis
            color_scheme = self.brand_typography.generate_color_scheme(
                image=image,
                typography_style=typography_style,
                brand_name=brand_name
            )
            
            # Step 8: Apply text elements with proper styling and effects
            self._apply_text_elements(
                draw=draw,
                text_elements=text_elements,
                fonts=fonts,
                text_sizes=text_sizes,
                text_positions=text_positions,
                color_scheme=color_scheme,
                typography_style=typography_style,
                image=image
            )
            
            # Step 9: Composite the text overlay with original image
            result_image = Image.alpha_composite(image.convert('RGBA'), text_overlay)
            
            return result_image
            
        except Exception as e:
            self.logger.error(f"Error creating typography: {str(e)}")
            # Return original image if typography creation fails
            return image
    
    def _apply_text_elements(self,
                            draw: ImageDraw.Draw,
                            text_elements: Dict[str, str],
                            fonts: Dict[str, ImageFont.FreeTypeFont],
                            text_sizes: Dict[str, int],
                            text_positions: Dict[str, Dict[str, Any]],
                            color_scheme: Dict[str, Any],
                            typography_style: Dict[str, Any],
                            image: Image.Image) -> None:
        """
        Apply all text elements with appropriate styling and effects.
        
        Args:
            draw: ImageDraw object
            text_elements: Dictionary with text elements
            fonts: Dictionary of fonts for each element
            text_sizes: Dictionary of text sizes for each element
            text_positions: Dictionary with positions and properties for each element
            color_scheme: Color scheme dictionary
            typography_style: Typography style dictionary
            image: Original image for reference
        """
        # Handle background panel if specified in style or positions
        if text_positions.get('background'):
            self._apply_background_panel(
                draw=draw,
                text_positions=text_positions,
                color_scheme=color_scheme,
                typography_style=typography_style,
                image_size=image.size
            )
        
        # Apply each text element
        text_elements_order = ['brand', 'headline', 'subheadline', 'body', 'cta']
        
        for element_name in text_elements_order:
            # Map element names from text_elements to position keys
            element_key = element_name
            if element_name == 'body':
                text_key = 'body_text'
            elif element_name == 'cta':
                text_key = 'call_to_action'
            else:
                text_key = element_name
            
            # Skip if element doesn't exist
            if text_key not in text_elements or not text_elements[text_key]:
                continue
                
            # Get text and position details
            text = text_elements[text_key]
            position_data = text_positions.get(element_key, {})
            
            if not position_data:
                continue
                
            position = position_data.get('position', (0, 0))
            alignment = position_data.get('alignment', 'center')
            
            # Get font and size
            font = fonts.get(element_key)
            if not font:
                continue
            
            # Get color
            text_color = color_scheme.get(f'{element_key}_color', color_scheme.get('text_color', (255, 255, 255, 255)))
            
            # Get effect treatment
            effect = typography_style.get('text_treatments', {}).get(element_key, 'simple')
            
            # Special case for CTA button
            if element_key == 'cta' and typography_style.get('cta_style') != 'text_only':
                button_style = typography_style.get('cta_style', 'rounded')
                button_color = color_scheme.get('button_color', color_scheme.get('accent_color', (41, 128, 185, 230)))
                
                self.effects_engine.create_button(
                    draw=draw,
                    text=text,
                    position=position,
                    font=font,
                    button_style=button_style,
                    text_color=text_color,
                    button_color=button_color,
                    typography_style=typography_style
                )
            else:
                # Apply regular text with effects
                self.effects_engine.apply_text_effect(
                    draw=draw,
                    text=text,
                    position=position,
                    font=font,
                    alignment=alignment,
                    effect=effect,
                    text_color=text_color,
                    accent_color=color_scheme.get('accent_color'),
                    typography_style=typography_style,
                    image=image
                )
    
    def _apply_background_panel(self,
                                draw: ImageDraw.Draw,
                                text_positions: Dict[str, Dict[str, Any]],
                                color_scheme: Dict[str, Any],
                                typography_style: Dict[str, Any],
                                image_size: Tuple[int, int]) -> None:
        """
        Apply a background panel for text if specified.
        
        Args:
            draw: ImageDraw object
            text_positions: Dictionary with text positions
            color_scheme: Color scheme dictionary
            typography_style: Typography style dictionary
            image_size: Size of the original image
        """
        background = text_positions.get('background', {})
        
        if not background.get('enabled', False):
            return
            
        # Get background parameters
        width, height = image_size
        bg_color = background.get('color', (0, 0, 0, 150))
        padding = background.get('padding', 0.1)
        y_start = int(background.get('y_start', 0.35) * height)
        y_end = int(background.get('y_end', 0.75) * height)
        
        # Apply background effect based on style
        bg_style = typography_style.get('background_style', 'simple')
        
        if bg_style == 'gradient':
            # Create gradient background
            for y in range(y_start, y_end):
                progress = (y - y_start) / (y_end - y_start)
                alpha = int(bg_color[3] * (1 - progress * 0.3))
                draw.line([(0, y), (width, y)], fill=(bg_color[0], bg_color[1], bg_color[2], alpha))
        
        elif bg_style == 'blur_panel':
            # This would normally use a blur effect, but simplified here
            # In a real implementation, this would involve creating a blurred copy of the image region
            draw.rectangle([0, y_start, width, y_end], fill=bg_color)
        
        elif bg_style == 'rounded_panel':
            # Draw a rounded rectangle panel
            radius = int(height * 0.02)  # 2% of height
            self.effects_engine.draw_rounded_rectangle(
                draw=draw,
                coords=[(int(width * 0.1), y_start), (int(width * 0.9), y_end)],
                color=bg_color,
                radius=radius
            )
        
        else:
            # Simple rectangle
            draw.rectangle([0, y_start, width, y_end], fill=bg_color)
    
    def get_available_styles(self) -> Dict[str, Dict[str, Any]]:
        """
        Get available typography style presets.
        
        Returns:
            Dictionary with available typography style presets
        """
        return self.brand_typography.get_available_styles()
    
    def get_style_preview(self, 
                         style_name: str, 
                         brand_name: Optional[str] = None,
                         industry: Optional[str] = None,
                         brand_level: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a preview of a typography style without applying it.
        
        Args:
            style_name: Name of the style preset
            brand_name: Optional brand name for brand-specific styling
            industry: Optional industry for industry-specific styling
            brand_level: Optional brand positioning
        
        Returns:
            Style preview dictionary with fonts, colors, and effects
        """
        return self.brand_typography.get_typography_style(
            style_name=style_name,
            brand_name=brand_name,
            industry=industry,
            brand_level=brand_level
        ) 
