"""
Typography Effects Engine for Professional Ad Generation
Provides sophisticated text effects and treatments for advertising typography
"""
import math
import logging
from typing import Dict, List, Tuple, Any, Optional, Union
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops

class TypographyEffectsEngine:
    """
    Engine for applying professional typography effects.
    Provides studio-quality text treatments commonly used in high-end advertising.
    """
    
    def __init__(self):
        """Initialize the typography effects engine."""
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize effects registry
        self.effects_registry = self._initialize_effects_registry()
        
        # Initialize button style registry
        self.button_registry = self._initialize_button_registry()
    
    def _initialize_effects_registry(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize the registry of available text effects.
        
        Returns:
            Dictionary mapping effect names to their parameters
        """
        return {
            "simple": {
                "description": "Clean, simple text with no effects",
                "params": {
                    "shadow_enabled": False,
                    "glow_enabled": False,
                    "gradient_enabled": False,
                    "outline_enabled": False
                }
            },
            
            "clean_gradient": {
                "description": "Text with subtle vertical gradient",
                "params": {
                    "shadow_enabled": True,
                    "shadow_offset": 1,
                    "shadow_opacity": 0.4,
                    "gradient_enabled": True,
                    "gradient_direction": "vertical",
                    "gradient_start_opacity": 1.0,
                    "gradient_end_opacity": 0.7,
                    "glow_enabled": False,
                    "outline_enabled": False
                }
            },
            
            "elegant_serif": {
                "description": "Elegant serif typography with subtle shadow",
                "params": {
                    "shadow_enabled": True,
                    "shadow_offset": 1,
                    "shadow_opacity": 0.3,
                    "shadow_blur": 1.0,
                    "glow_enabled": False,
                    "gradient_enabled": False,
                    "outline_enabled": True,
                    "outline_size": 1,
                    "outline_opacity": 0.2,
                    "letter_spacing": 0.05
                }
            },
            
            "dynamic_bold": {
                "description": "Bold text with dramatic shadow and gradient",
                "params": {
                    "shadow_enabled": True,
                    "shadow_offset": 3,
                    "shadow_opacity": 0.6,
                    "shadow_blur": 2.0,
                    "gradient_enabled": True,
                    "gradient_direction": "diagonal",
                    "gradient_start_opacity": 1.0,
                    "gradient_end_opacity": 0.8,
                    "outline_enabled": False
                }
            },
            
            "premium_gradient": {
                "description": "Premium look with smooth gradient and subtle glow",
                "params": {
                    "shadow_enabled": True,
                    "shadow_offset": 2,
                    "shadow_opacity": 0.5,
                    "gradient_enabled": True,
                    "gradient_direction": "vertical",
                    "gradient_start_opacity": 1.0,
                    "gradient_end_opacity": 0.8,
                    "gradient_steps": 10,
                    "glow_enabled": True,
                    "glow_opacity": 0.15,
                    "glow_radius": 3,
                    "outline_enabled": False
                }
            },
            
            "luxury_metallic": {
                "description": "Luxury metallic effect for premium brands",
                "params": {
                    "shadow_enabled": True,
                    "shadow_offset": 3,
                    "shadow_opacity": 0.6,
                    "gradient_enabled": True,
                    "gradient_direction": "vertical",
                    "gradient_start_opacity": 1.0,
                    "gradient_end_opacity": 0.8,
                    "metallic_enabled": True,
                    "metallic_highlight": 0.7,
                    "metallic_shadows": 0.3,
                    "outline_enabled": True,
                    "outline_size": 1,
                    "outline_opacity": 0.5
                }
            },
            
            "subtle_glow": {
                "description": "Text with subtle glowing effect",
                "params": {
                    "shadow_enabled": False,
                    "glow_enabled": True,
                    "glow_radius": 5,
                    "glow_opacity": 0.3,
                    "glow_color_factor": 0.8,
                    "gradient_enabled": False,
                    "outline_enabled": False
                }
            },
            
            "layered_gradient": {
                "description": "Complex layered gradient for depth",
                "params": {
                    "shadow_enabled": True,
                    "shadow_offset": 2,
                    "shadow_opacity": 0.5,
                    "gradient_enabled": True,
                    "gradient_direction": "vertical",
                    "gradient_layers": 3,
                    "glow_enabled": False,
                    "outline_enabled": False
                }
            },
            
            "minimal_elegant": {
                "description": "Minimal, elegant typography with perfect spacing",
                "params": {
                    "shadow_enabled": False,
                    "gradient_enabled": False,
                    "glow_enabled": False,
                    "outline_enabled": False,
                    "letter_spacing": 0.05,
                    "lightweight": True
                }
            },
            
            "vibrant_overlay": {
                "description": "Vibrant text with colorful background panel",
                "params": {
                    "shadow_enabled": False,
                    "gradient_enabled": False,
                    "glow_enabled": False,
                    "outline_enabled": False,
                    "background_enabled": True,
                    "background_opacity": 0.8,
                    "background_padding": 15,
                    "background_radius": 10
                }
            },
            
            "glass_effect": {
                "description": "Modern glass-like effect with transparency",
                "params": {
                    "shadow_enabled": False,
                    "gradient_enabled": False,
                    "glow_enabled": False,
                    "outline_enabled": False,
                    "glass_enabled": True,
                    "glass_opacity": 0.6,
                    "glass_blur": 10,
                    "glass_reflection": 0.3
                }
            },
            
            "nike_bold": {
                "description": "Nike-style bold condensed typography",
                "params": {
                    "shadow_enabled": False,
                    "gradient_enabled": False,
                    "glow_enabled": False,
                    "outline_enabled": True,
                    "outline_size": 1,
                    "outline_opacity": 0.8,
                    "condensed": True,
                    "letter_spacing": -0.05,
                    "transform": "uppercase"
                }
            },
            
            "subtle_bg": {
                "description": "Text with subtle background for better legibility",
                "params": {
                    "shadow_enabled": False,
                    "gradient_enabled": False,
                    "glow_enabled": False,
                    "outline_enabled": False,
                    "background_enabled": True,
                    "background_opacity": 0.7,
                    "background_padding": 15,
                    "background_radius": 8,
                    "background_blur": 0
                }
            },
            
            "shadow": {
                "description": "Simple shadow effect for text",
                "params": {
                    "shadow_enabled": True,
                    "shadow_offset": 2,
                    "shadow_opacity": 0.5,
                    "shadow_blur": 1,
                    "gradient_enabled": False,
                    "glow_enabled": False,
                    "outline_enabled": False
                }
            }
        }
    
    def _initialize_button_registry(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize the registry of button styles.
        
        Returns:
            Dictionary mapping button style names to their parameters
        """
        return {
            "rounded": {
                "description": "Rounded button with subtle 3D effect",
                "params": {
                    "radius": 10,
                    "padding_x": 20,
                    "padding_y": 12,
                    "highlight_opacity": 0.3,
                    "shadow_opacity": 0.4
                }
            },
            
            "minimal_line": {
                "description": "Minimal button with just a border",
                "params": {
                    "radius": 8,
                    "padding_x": 20,
                    "padding_y": 10,
                    "border_width": 1
                }
            },
            
            "pill": {
                "description": "Pill-shaped button with rounded ends",
                "params": {
                    "padding_x": 25,
                    "padding_y": 12,
                    "highlight_opacity": 0.3,
                    "shadow_opacity": 0.4
                }
            },
            
            "gradient": {
                "description": "Button with gradient fill",
                "params": {
                    "radius": 10,
                    "padding_x": 20,
                    "padding_y": 12,
                    "direction": "vertical",
                    "darkness_factor": 0.7
                }
            },
            
            "glass": {
                "description": "Modern glass-like button",
                "params": {
                    "radius": 10,
                    "padding_x": 20,
                    "padding_y": 12,
                    "opacity": 0.6,
                    "reflection_opacity": 0.3
                }
            },
            
            "flat": {
                "description": "Simple flat button with no effects",
                "params": {
                    "radius": 5,
                    "padding_x": 20,
                    "padding_y": 10
                }
            }
        }
    
    def apply_text_effect(self,
                         draw: ImageDraw.Draw,
                         text: str,
                         position: Tuple[int, int],
                         font: ImageFont.FreeTypeFont,
                         alignment: str = "center",
                         effect: str = "simple",
                         text_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
                         accent_color: Optional[Tuple[int, int, int, int]] = None,
                         typography_style: Optional[Dict[str, Any]] = None,
                         image: Optional[Image.Image] = None) -> bool:
        """
        Apply text effect with detailed error tracking.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: Position (x, y) for the text
            font: Font to use
            alignment: Text alignment ("left", "center", "right")
            effect: Name of the effect to apply
            text_color: Text color (RGBA)
            accent_color: Accent color for effects (RGBA)
            typography_style: Typography style dictionary
            image: Original image for reference
            
        Returns:
            True if effect was applied successfully, False otherwise
        """
        try:
            # Check if font is valid
            if font is None:
                self.logger.error("Font is None, cannot apply text effect")
                # Use emergency fallback
                try:
                    font = ImageFont.load_default()
                    self.logger.info("Using PIL default font as emergency fallback")
                except Exception as e:
                    self.logger.error(f"Failed to load default font: {str(e)}")
                    return False
            
            # Force full opacity for text color
            r, g, b, a = text_color
            if a < 200:  # If alpha is less than 200 (out of 255)
                text_color = (r, g, b, 255)  # Force full opacity
                self.logger.info(f"Forcing full opacity for text color: {text_color}")
            
            # Get effect parameters
            effect_params = self.effects_registry.get(effect, self.effects_registry["simple"]).get("params", {})
            
            # Override with typography style parameters if provided
            if typography_style and "effect_params" in typography_style:
                for key, value in typography_style["effect_params"].items():
                    effect_params[key] = value
            
            # Get text dimensions
            text_width, text_height = self._get_text_dimensions(text, font)
            
            # Calculate position based on alignment
            x, y = position
            if alignment == "center":
                x = x - text_width // 2
            elif alignment == "right":
                x = x - text_width
            
            # Apply appropriate effect based on effect name
            self.logger.info(f"Applying effect '{effect}' to text: {text[:20]}{'...' if len(text) > 20 else ''}")
            
            # Map effect names to their implementation methods
            effect_methods = {
                "clean_gradient": self._apply_clean_gradient_effect,
                "elegant_serif": self._apply_elegant_serif_effect,
                "subtle_shadow": self._apply_shadow,
                "shadow": self._apply_shadow,
                "subtle_glow": self._apply_subtle_glow_effect,
                "dynamic_bold": self._apply_shadow,  # Using shadow with specific params
                "minimal_elegant": self._apply_minimal_elegant_effect,
                "luxury_metallic": self._apply_metallic_effect,
                "vibrant_overlay": self._apply_vibrant_overlay_effect,
                "gradient": self._apply_gradient_effect,
                "premium_gradient": self._apply_premium_gradient,
                "layered_gradient": self._apply_layered_gradient,
                "glass_effect": self._apply_glass_effect_text,
                "nike_bold": self._apply_nike_bold_effect,
                "subtle_bg": self._apply_subtle_bg_effect
            }
            
            # Apply the effect if it has a specific implementation
            if effect in effect_methods:
                effect_methods[effect](draw, text, (x, y), font, text_color, accent_color, effect_params)
            else:
                # Default to simple rendering
                draw.text((x, y), text, font=font, fill=text_color)
            
            self.logger.info(f"Successfully applied effect '{effect}'")
            return True  # Return success
        
        except Exception as e:
            self.logger.error(f"Error applying text effect '{effect}': {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())  # Log detailed stack trace
            
            # Emergency rendering - make sure text appears even if effect fails
            try:
                x, y = position
                if alignment == "center":
                    try:
                        text_width, text_height = self._get_text_dimensions(text, font)
                        x = x - text_width // 2
                    except:
                        pass  # Keep original x if getting dimensions fails
                elif alignment == "right":
                    try:
                        text_width, text_height = self._get_text_dimensions(text, font)
                        x = x - text_width
                    except:
                        pass  # Keep original x if getting dimensions fails
                
                # Use high contrast fallback colors for visibility
                fallback_color = (255, 255, 255, 255)  # Bright white with full opacity
                
                # Draw text with basic settings
                draw.text((x, y), text, font=font, fill=fallback_color)
                self.logger.info(f"Used fallback text rendering at position {(x, y)}")
                return False  # Effect failed but we showed the text
            except Exception as e2:
                self.logger.error(f"Emergency text rendering also failed: {str(e2)}")
                return False
    
    def create_button(self,
                     draw: ImageDraw.Draw,
                     text: str,
                     position: Tuple[int, int],
                     font: ImageFont.FreeTypeFont,
                     button_style: str = "rounded",
                     text_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
                     button_color: Tuple[int, int, int, int] = (41, 128, 185, 230),
                     typography_style: Optional[Dict[str, Any]] = None) -> None:
        """
        Create a button with the specified style.
        
        Args:
            draw: ImageDraw object to draw on
            text: Button text
            position: (x, y) center position of the button
            font: Font to use for text
            button_style: Name of the button style
            text_color: Text color (RGBA)
            button_color: Button color (RGBA)
            typography_style: Optional typography style parameters
        """
        try:
            # Get button style parameters
            style_params = self.button_registry.get(button_style, self.button_registry["rounded"]).get("params", {})
            
            # Override with typography style parameters if provided
            if typography_style and "button_params" in typography_style:
                for key, value in typography_style["button_params"].items():
                    style_params[key] = value
            
            # Apply text transformations if needed
            if typography_style and "text_transform" in typography_style and "cta" in typography_style["text_transform"]:
                transform = typography_style["text_transform"]["cta"]
                if transform == "uppercase":
                    text = text.upper()
                elif transform == "lowercase":
                    text = text.lower()
                elif transform == "capitalize":
                    text = text.title()
            
            # Get text dimensions
            text_width, text_height = self._get_text_dimensions(text, font)
            
            # Calculate button dimensions
            padding_x = style_params.get("padding_x", 20)
            padding_y = style_params.get("padding_y", 12)
            button_width = text_width + (padding_x * 2)
            button_height = text_height + (padding_y * 2)
            
            # Calculate button position (centered on the provided position)
            x, y = position
            button_left = x - button_width // 2
            button_top = y - button_height // 2
            button_right = button_left + button_width
            button_bottom = button_top + button_height
            
            # Apply the appropriate button style
            if button_style == "rounded":
                self._draw_rounded_button(
                    draw,
                    (button_left, button_top, button_right, button_bottom),
                    text,
                    font,
                    text_color,
                    button_color,
                    style_params
                )
            elif button_style == "minimal_line":
                self._draw_minimal_line_button(
                    draw,
                    (button_left, button_top, button_right, button_bottom),
                    text,
                    font,
                    text_color,
                    button_color,
                    style_params
                )
            elif button_style == "pill":
                self._draw_pill_button(
                    draw,
                    (button_left, button_top, button_right, button_bottom),
                    text,
                    font,
                    text_color,
                    button_color,
                    style_params
                )
            elif button_style == "gradient":
                self._draw_gradient_button(
                    draw,
                    (button_left, button_top, button_right, button_bottom),
                    text,
                    font,
                    text_color,
                    button_color,
                    style_params
                )
            elif button_style == "glass":
                self._draw_glass_button(
                    draw,
                    (button_left, button_top, button_right, button_bottom),
                    text,
                    font,
                    text_color,
                    button_color,
                    style_params
                )
            else:  # Default to flat
                self._draw_flat_button(
                    draw,
                    (button_left, button_top, button_right, button_bottom),
                    text,
                    font,
                    text_color,
                    button_color,
                    style_params
                )
                
        except Exception as e:
            self.logger.error(f"Error creating button: {str(e)}")
            # Fallback to simple text rendering
            try:
                x, y = position
                text_width, text_height = self._get_text_dimensions(text, font)
                draw.text((x - text_width // 2, y - text_height // 2), text, font=font, fill=text_color)
            except:
                pass
    
    def draw_rounded_rectangle(self,
                              draw: ImageDraw.Draw,
                              coords: List[Tuple[int, int]],
                              color: Tuple[int, int, int, int],
                              radius: int = 10,
                              outline: Optional[Tuple[int, int, int, int]] = None,
                              width: int = 1) -> None:
        """
        Draw a rounded rectangle on the image.
        
        Args:
            draw: ImageDraw object
            coords: [(x1, y1), (x2, y2)] rectangle coordinates
            color: Fill color (RGBA)
            radius: Corner radius
            outline: Optional outline color
            width: Outline width if outline specified
        """
        # Check if the native rounded_rectangle method is available (Pillow >= 8.0.0)
        if hasattr(draw, 'rounded_rectangle'):
            try:
                # Use the built-in method if available
                draw.rounded_rectangle(
                    [(coords[0][0], coords[0][1]), (coords[1][0], coords[1][1])],
                    radius=radius,
                    fill=color,
                    outline=outline,
                    width=width
                )
                return
            except Exception as e:
                self.logger.warning(f"Native rounded_rectangle failed: {str(e)}, falling back to manual implementation")
        
        # Fall back to manual implementation
        x1, y1 = coords[0]
        x2, y2 = coords[1]
        
        # Draw rectangle
        draw.rectangle([(x1 + radius, y1), (x2 - radius, y2)], fill=color, outline=outline)
        draw.rectangle([(x1, y1 + radius), (x2, y2 - radius)], fill=color, outline=outline)
        
        # Draw corners
        draw.pieslice([(x1, y1), (x1 + radius * 2, y1 + radius * 2)], 180, 270, fill=color, outline=outline)
        draw.pieslice([(x2 - radius * 2, y1), (x2, y1 + radius * 2)], 270, 0, fill=color, outline=outline)
        draw.pieslice([(x1, y2 - radius * 2), (x1 + radius * 2, y2)], 90, 180, fill=color, outline=outline)
        draw.pieslice([(x2 - radius * 2, y2 - radius * 2), (x2, y2)], 0, 90, fill=color, outline=outline)
        
        # Draw outline separately if specified
        if outline:
            # This is a simplified outline approach - a full implementation would handle the corners better
            try:
                # Top line
                draw.line([(x1 + radius, y1), (x2 - radius, y1)], fill=outline, width=width)
                # Right line
                draw.line([(x2, y1 + radius), (x2, y2 - radius)], fill=outline, width=width)
                # Bottom line
                draw.line([(x1 + radius, y2), (x2 - radius, y2)], fill=outline, width=width)
                # Left line
                draw.line([(x1, y1 + radius), (x1, y2 - radius)], fill=outline, width=width)
            except Exception as e:
                self.logger.warning(f"Drawing outline failed: {str(e)}")
    
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
    
    def _apply_shadow(self,
                     draw: ImageDraw.Draw,
                     text: str,
                     position: Tuple[int, int],
                     font: ImageFont.FreeTypeFont, 
                     text_color: Tuple[int, int, int, int],
                     accent_color: Optional[Tuple[int, int, int, int]],
                     params: Dict[str, Any]) -> None:
        """
        Apply shadow effect to text.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: (x, y) position
            font: Font to use
            text_color: Text color (RGBA)
            accent_color: Optional accent color (RGBA)
            params: Effect parameters
        """
        x, y = position
        
        # Get shadow parameters
        shadow_offset = params.get("shadow_offset", 2)
        shadow_opacity = params.get("shadow_opacity", 0.5)
        shadow_blur = params.get("shadow_blur", 0)
        
        # Calculate shadow color based on text color
        shadow_color = (0, 0, 0, int(255 * shadow_opacity))
        
        if shadow_blur > 0:
            # For blurred shadow, create a separate image
            text_width, text_height = self._get_text_dimensions(text, font)
            
            # Create larger image to accommodate blur
            blur_padding = int(shadow_blur * 3)
            shadow_img = Image.new(
                'RGBA', 
                (text_width + blur_padding * 2, text_height + blur_padding * 2), 
                (0, 0, 0, 0)
            )
            shadow_draw = ImageDraw.Draw(shadow_img)
            
            # Draw shadow text
            shadow_draw.text(
                (blur_padding, blur_padding), 
                text, 
                font=font, 
                fill=shadow_color
            )
            
            # Apply blur
            shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
            
            # Composite shadow onto the main image
            # Offset position for shadow
            offset_x = x + shadow_offset - blur_padding
            offset_y = y + shadow_offset - blur_padding
            
            draw._image.paste(shadow_img, (offset_x, offset_y), shadow_img)
        else:
            # Simple shadow without blur
            draw.text(
                (x + shadow_offset, y + shadow_offset), 
                text, 
                font=font, 
                fill=shadow_color
            )
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)

    def _apply_elegant_serif_effect(self,
                                   draw: ImageDraw.Draw,
                                   text: str,
                                   position: Tuple[int, int],
                                   font: ImageFont.FreeTypeFont,
                                   text_color: Tuple[int, int, int, int],
                                   accent_color: Optional[Tuple[int, int, int, int]],
                                   params: Dict[str, Any]) -> None:
        """
        Apply elegant serif effect to text.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: (x, y) position
            font: Font to use
            text_color: Text color (RGBA)
            accent_color: Accent color (RGBA)
            params: Effect parameters
        """
        x, y = position
        
        # Get effect parameters
        shadow_enabled = params.get("shadow_enabled", True)
        shadow_offset = params.get("shadow_offset", 1)
        shadow_opacity = params.get("shadow_opacity", 0.3)
        shadow_blur = params.get("shadow_blur", 1.0)
        outline_enabled = params.get("outline_enabled", True)
        outline_size = params.get("outline_size", 1)
        outline_opacity = params.get("outline_opacity", 0.2)
        letter_spacing = params.get("letter_spacing", 0.05)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate layer for the text effect
        padding = 20
        text_layer = Image.new('RGBA', (text_width + padding * 2, text_height + padding * 2), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        
        # Apply shadow if enabled
        if shadow_enabled:
            shadow_color = (0, 0, 0, int(255 * shadow_opacity))
            
            # Draw shadow
            text_draw.text(
                (padding + shadow_offset, padding + shadow_offset), 
                text, 
                font=font, 
                fill=shadow_color
            )
            
            # Apply blur to shadow
            if shadow_blur > 0:
                text_layer = text_layer.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
        
        # Determine outline color
        outline_color = accent_color if accent_color else (0, 0, 0, int(255 * outline_opacity))
        
        # Apply outline if enabled
        if outline_enabled:
            for dx, dy in [(-outline_size, 0), (outline_size, 0), (0, -outline_size), (0, outline_size)]:
                text_draw.text(
                    (padding + dx, padding + dy), 
                    text, 
                    font=font, 
                    fill=outline_color
                )
        
        # Draw main text
        text_draw.text((padding, padding), text, font=font, fill=text_color)
        
        # Apply subtle enhancements for serif elegance
        enhanced_layer = text_layer.copy()
        enhanced_layer = enhanced_layer.filter(ImageFilter.SMOOTH_MORE)
        
        # Paste the result
        draw._image.paste(text_layer, (x - padding, y - padding), text_layer)

    def _apply_gradient_effect(self,
                              draw: ImageDraw.Draw,
                              text: str,
                              position: Tuple[int, int],
                              font: ImageFont.FreeTypeFont,
                              text_color: Tuple[int, int, int, int],
                              accent_color: Optional[Tuple[int, int, int, int]],
                              params: Dict[str, Any]) -> None:
        """
        Apply gradient effect to text.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: (x, y) position
            font: Font to use
            text_color: Text color (RGBA)
            accent_color: Accent color (RGBA)
            params: Effect parameters
        """
        x, y = position
        
        # Get gradient parameters
        direction = params.get("gradient_direction", "vertical")
        start_opacity = params.get("gradient_start_opacity", 1.0)
        end_opacity = params.get("gradient_end_opacity", 0.7)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate image for gradient text
        gradient_img = Image.new('RGBA', (text_width + 20, text_height + 20), (0, 0, 0, 0))
        gradient_draw = ImageDraw.Draw(gradient_img)
        
        # Extract color components
        r1, g1, b1, a1 = text_color
        
        if accent_color:
            r2, g2, b2, a2 = accent_color
        else:
            # Calculate a darker variant for gradient
            r2, g2, b2 = int(r1 * 0.7), int(g1 * 0.7), int(b1 * 0.7)
            a2 = int(a1 * end_opacity)
        
        # Apply gradient based on direction
        if direction == "vertical":
            # Create vertical gradient
            for i in range(text_height):
                # Calculate color for this position in the gradient
                ratio = i / text_height
                r = int(r1 * (1 - ratio) + r2 * ratio)
                g = int(g1 * (1 - ratio) + g2 * ratio)
                b = int(b1 * (1 - ratio) + b2 * ratio)
                a = int(a1 * (1 - ratio * (1 - end_opacity/start_opacity)))
                
                # Draw text line by line with current color
                line_color = (r, g, b, a)
                gradient_draw.text((10, 10 + i), text, font=font, fill=line_color)
        
        elif direction == "horizontal":
            # For horizontal gradient, we need to approach differently
            # Draw text in multiple layers
            steps = 10  # Number of gradient steps
            for i in range(steps):
                # Calculate color for this step
                ratio = i / (steps - 1)
                r = int(r1 * (1 - ratio) + r2 * ratio)
                g = int(g1 * (1 - ratio) + g2 * ratio)
                b = int(b1 * (1 - ratio) + b2 * ratio)
                a = int(a1 * (1 - ratio * (1 - end_opacity/start_opacity)))
                
                # Calculate horizontal slice
                slice_width = text_width // steps
                clip_left = i * slice_width
                clip_right = (i + 1) * slice_width
                
                # Draw this slice with current color
                mask = Image.new('L', (text_width + 20, text_height + 20), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.rectangle([(clip_left + 10, 0), (clip_right + 10, text_height + 20)], fill=255)
                
                # Draw text with current color through mask
                temp_img = Image.new('RGBA', (text_width + 20, text_height + 20), (0, 0, 0, 0))
                temp_draw = ImageDraw.Draw(temp_img)
                temp_draw.text((10, 10), text, font=font, fill=(r, g, b, a))
                
                # Composite with mask
                gradient_img.paste(temp_img, (0, 0), mask)
        
        else:  # diagonal or any other type, default behavior
            # Draw text with single color
            gradient_draw.text((10, 10), text, font=font, fill=text_color)
        
        # Apply shadow if enabled
        if params.get("shadow_enabled", True):
            shadow_offset = params.get("shadow_offset", 2)
            shadow_opacity = params.get("shadow_opacity", 0.5)
            shadow_color = (0, 0, 0, int(255 * shadow_opacity))
            
            shadow_img = Image.new('RGBA', (text_width + 20, text_height + 20), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_img)
            shadow_draw.text((10 + shadow_offset, 10 + shadow_offset), text, font=font, fill=shadow_color)
            
            if params.get("shadow_blur", 0) > 0:
                shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=params.get("shadow_blur", 0)))
            
            # Composite shadow and gradient
            composite = Image.alpha_composite(shadow_img, gradient_img)
        else:
            composite = gradient_img
        
        # Paste the final composite
        draw._image.paste(composite, (x - 10, y - 10), composite)

    def _apply_metallic_effect(self,
                              draw: ImageDraw.Draw,
                              text: str,
                              position: Tuple[int, int],
                              font: ImageFont.FreeTypeFont,
                              text_color: Tuple[int, int, int, int],
                              accent_color: Optional[Tuple[int, int, int, int]],
                              params: Dict[str, Any]) -> None:
        """
        Apply metallic effect to text.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: (x, y) position
            font: Font to use
            text_color: Text color (RGBA)
            accent_color: Accent color (RGBA)
            params: Effect parameters
        """
        x, y = position
        
        # Get metallic parameters
        highlight = params.get("metallic_highlight", 0.7)
        shadows = params.get("metallic_shadows", 0.3)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate image for metallic effect
        padding = 20
        metal_img = Image.new('RGBA', (text_width + padding * 2, text_height + padding * 2), (0, 0, 0, 0))
        metal_draw = ImageDraw.Draw(metal_img)
        
        # Determine base metallic color (gold or silver by default)
        if accent_color:
            base_color = accent_color
        else:
            # Default to gold
            base_color = (212, 175, 55, 255)  # Gold color
        
        r, g, b, a = base_color
        
        # Draw shadow first
        if params.get("shadow_enabled", True):
            shadow_offset = params.get("shadow_offset", 3)
            shadow_opacity = params.get("shadow_opacity", 0.6)
            shadow_color = (0, 0, 0, int(255 * shadow_opacity))
            
            metal_draw.text((padding + shadow_offset, padding + shadow_offset), 
                           text, font=font, fill=shadow_color)
        
        # 1. Draw darker base for depth
        dark_base = (int(r * shadows), int(g * shadows), int(b * shadows), a)
        metal_draw.text((padding, padding), text, font=font, fill=dark_base)
        
        # 2. Draw multiple layers for metallic effect
        # Bottom highlight
        bottom_highlight = (min(int(r * 1.2), 255), min(int(g * 1.2), 255), min(int(b * 1.2), 255), int(a * 0.9))
        metal_draw.text((padding, padding + 1), text, font=font, fill=bottom_highlight)
        
        # Main color
        metal_draw.text((padding, padding), text, font=font, fill=base_color)
        
        # Top highlight for metallic shine
        top_highlight = (min(int(r * highlight), 255), min(int(g * highlight), 255), min(int(b * highlight), 255), int(a * 0.8))
        metal_draw.text((padding, padding - 1), text, font=font, fill=top_highlight)
        
        # Extreme highlight for sparkle effect
        sparkle = (min(int(r * 1.5), 255), min(int(g * 1.5), 255), min(int(b * 1.5), 255), int(a * 0.6))
        metal_draw.text((padding - 1, padding - 1), text, font=font, fill=sparkle)
        
        # Apply outline if specified
        if params.get("outline_enabled", True):
            outline_size = params.get("outline_size", 1)
            outline_opacity = params.get("outline_opacity", 0.5)
            outline_color = (0, 0, 0, int(255 * outline_opacity))
            
            for dx, dy in [(outline_size, 0), (-outline_size, 0), (0, outline_size), (0, -outline_size)]:
                if dx != 0 or dy != 0:  # Skip center position
                    metal_draw.text((padding + dx, padding + dy), text, font=font, fill=outline_color)
        
        # Apply slight blur for smoother metallic look
        metal_img = metal_img.filter(ImageFilter.GaussianBlur(radius=0.3))
        
        # Paste the metallic image
        draw._image.paste(metal_img, (x - padding, y - padding), metal_img)
    
    def _apply_clean_gradient_effect(self, 
                                    draw: ImageDraw.Draw,
                                    text: str,
                                    position: Tuple[int, int],
                                    font: ImageFont.FreeTypeFont,
                                    text_color: Tuple[int, int, int, int],
                                    accent_color: Optional[Tuple[int, int, int, int]],
                                    params: Dict[str, Any]) -> None:
        """
        Apply clean gradient effect with modern typography.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: (x, y) position
            font: Font to use
            text_color: Text color (RGBA)
            accent_color: Optional accent color for gradient
            params: Effect parameters
        """
        x, y = position
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate layer for the text effect
        text_layer = Image.new('RGBA', (text_width + 40, text_height + 40), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        
        # Extract color components
        r, g, b, a = text_color
        
        # Determine gradient end color
        if accent_color:
            end_color = accent_color
        else:
            # Create a slightly different color for gradient end
            lightness_factor = 1.3
            end_color = (
                min(int(r * lightness_factor), 255),
                min(int(g * lightness_factor), 255),
                min(int(b * lightness_factor), 255),
                a
            )
        
        # Draw gradient text
        steps = text_height
        for i in range(steps):
            # Calculate color for this position
            ratio = i / steps
            current_r = int(r * (1 - ratio) + end_color[0] * ratio)
            current_g = int(g * (1 - ratio) + end_color[1] * ratio)
            current_b = int(b * (1 - ratio) + end_color[2] * ratio)
            current_a = int(a * (1 - ratio * 0.2))  # Slight fade
            
            line_color = (current_r, current_g, current_b, current_a)
            text_draw.text((20, 20 + i), text, font=font, fill=line_color)
        
        # Add subtle shadow
        shadow_color = (0, 0, 0, 80)
        shadow_layer = Image.new('RGBA', (text_width + 40, text_height + 40), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_layer)
        shadow_draw.text((21, 21), text, font=font, fill=shadow_color)
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(1))
        
        # Combine shadow and text
        result = Image.alpha_composite(shadow_layer, text_layer)
        
        # Paste the result
        draw._image.paste(result, (x - 20, y - 20), result)
    
    def _apply_subtle_glow_effect(self,
                                 draw: ImageDraw.Draw,
                                 text: str,
                                 position: Tuple[int, int],
                                 font: ImageFont.FreeTypeFont,
                                 text_color: Tuple[int, int, int, int],
                                 accent_color: Optional[Tuple[int, int, int, int]],
                                 params: Dict[str, Any]) -> None:
        """
        Apply subtle glow effect to text.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: (x, y) position
            font: Font to use
            text_color: Text color (RGBA)
            accent_color: Accent color (RGBA)
            params: Effect parameters
        """
        x, y = position
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Add padding for glow
        padding = 20
        glow_img = Image.new('RGBA', (text_width + padding * 2, text_height + padding * 2), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)
        
        # Get glow parameters
        glow_radius = params.get("glow_radius", 5)
        glow_opacity = params.get("glow_opacity", 0.3)
        
        # Determine glow color
        if accent_color:
            r, g, b, a = accent_color
            glow_color = (r, g, b, int(255 * glow_opacity))
        else:
            # Use a brighter version of text color
            r, g, b, a = text_color
            glow_color = (
                min(r + 50, 255),
                min(g + 50, 255),
                min(b + 50, 255),
                int(255 * glow_opacity)
            )
        
        # Draw glow
        glow_draw.text((padding, padding), text, font=font, fill=glow_color)
        
        # Apply blur to glow
        glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=glow_radius))
        
        # Draw main text on separate layer
        text_layer = Image.new('RGBA', (text_width + padding * 2, text_height + padding * 2), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        text_draw.text((padding, padding), text, font=font, fill=text_color)
        
        # Composite glow and text
        result = Image.alpha_composite(glow_img, text_layer)
        
        # Paste the result
        draw._image.paste(result, (x - padding, y - padding), result)
    
    def _apply_minimal_elegant_effect(self,
                                     draw: ImageDraw.Draw,
                                     text: str,
                                     position: Tuple[int, int],
                                     font: ImageFont.FreeTypeFont,
                                     text_color: Tuple[int, int, int, int],
                                     accent_color: Optional[Tuple[int, int, int, int]],
                                     params: Dict[str, Any]) -> None:
        """
        Apply minimal elegant effect.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: (x, y) position
            font: Font to use
            text_color: Text color (RGBA)
            accent_color: Accent color (RGBA)
            params: Effect parameters
        """
        x, y = position
        
        # Get letter spacing parameter
        letter_spacing = params.get("letter_spacing", 0.05)
        lightweight = params.get("lightweight", True)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate layer
        text_layer = Image.new('RGBA', (text_width + 40, text_height + 40), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        
        # Apply letter spacing if specified
        if letter_spacing > 0:
            # Draw each character with spacing
            spaced_width = 0
            for char in text:
                char_width, _ = self._get_text_dimensions(char, font)
                text_draw.text((20 + spaced_width, 20), char, font=font, fill=text_color)
                spaced_width += char_width + int(text_height * letter_spacing)
        else:
            # Draw text normally
            text_draw.text((20, 20), text, font=font, fill=text_color)
        
        # Apply very subtle shadow if not lightweight
        if not lightweight:
            shadow_color = (0, 0, 0, 40)
            shadow_offset = 1
            shadow_layer = Image.new('RGBA', (text_width + 40, text_height + 40), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_layer)
            
            if letter_spacing > 0:
                # Draw shadow for each character with spacing
                spaced_width = 0
                for char in text:
                    char_width, _ = self._get_text_dimensions(char, font)
                    shadow_draw.text((20 + spaced_width + shadow_offset, 20 + shadow_offset), 
                                  char, font=font, fill=shadow_color)
                    spaced_width += char_width + int(text_height * letter_spacing)
            else:
                # Draw shadow normally
                shadow_draw.text((20 + shadow_offset, 20 + shadow_offset), 
                              text, font=font, fill=shadow_color)
            
            # Composite shadow and text
            result = Image.alpha_composite(shadow_layer, text_layer)
        else:
            result = text_layer
        
        # Paste the result
        draw._image.paste(result, (x - 20, y - 20), result)
    
    def _apply_vibrant_overlay_effect(self,
                                     draw: ImageDraw.Draw,
                                     text: str,
                                     position: Tuple[int, int],
                                     font: ImageFont.FreeTypeFont,
                                     text_color: Tuple[int, int, int, int],
                                     accent_color: Optional[Tuple[int, int, int, int]],
                                     params: Dict[str, Any]) -> None:
        """
        Apply vibrant text with colorful background panel.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: (x, y) position
            font: Font to use
            text_color: Text color (RGBA)
            accent_color: Accent color (RGBA)
            params: Effect parameters
        """
        x, y = position
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Get background parameters
        bg_opacity = params.get("background_opacity", 0.8)
        padding = params.get("background_padding", 15)
        radius = params.get("background_radius", 10)
        
        # Determine background color
        if accent_color:
            r, g, b, _ = accent_color
            bg_color = (r, g, b, int(255 * bg_opacity))
        else:
            # Use a complementary color to text
            r, g, b, _ = text_color
            bg_color = (255 - r, 255 - g, 255 - b, int(255 * bg_opacity))
        
        # Create background layer
        bg_width = text_width + (padding * 2)
        bg_height = text_height + (padding * 2)
        
        bg_layer = Image.new('RGBA', (bg_width + 20, bg_height + 20), (0, 0, 0, 0))
        bg_draw = ImageDraw.Draw(bg_layer)
        
        # Draw rounded rectangle background
        self.draw_rounded_rectangle(
            bg_draw,
            [(10, 10), (10 + bg_width, 10 + bg_height)],
            bg_color,
            radius=radius
        )
        
        # Create text layer
        text_layer = Image.new('RGBA', (bg_width + 20, bg_height + 20), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        
        # Draw text centered on the background
        text_x = 10 + padding + (text_width // 2)
        text_y = 10 + padding
        
        # Draw text with subtle shadow for depth
        text_draw.text((text_x + 1, text_y + 1), text, font=font, fill=(0, 0, 0, 80), anchor="mt")
        text_draw.text((text_x, text_y), text, font=font, fill=text_color, anchor="mt")
        
        # Composite background and text
        result = Image.alpha_composite(bg_layer, text_layer)
        
        # Position the composite
        result_x = x - (bg_width // 2) - 10
        result_y = y - 10
        
        # Paste the result
        draw._image.paste(result, (result_x, result_y), result)
    
    def _apply_premium_gradient(self,
                               draw: ImageDraw.Draw,
                               text: str,
                               position: Tuple[int, int],
                               font: ImageFont.FreeTypeFont,
                               text_color: Tuple[int, int, int, int],
                               accent_color: Optional[Tuple[int, int, int, int]],
                               params: Dict[str, Any]) -> None:
        """
        Apply premium gradient effect with subtle glow.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: (x, y) position
            font: Font to use
            text_color: Text color (RGBA)
            accent_color: Accent color (RGBA)
            params: Effect parameters
        """
        x, y = position
        
        # Get parameters
        shadow_enabled = params.get("shadow_enabled", True)
        shadow_offset = params.get("shadow_offset", 2)
        shadow_opacity = params.get("shadow_opacity", 0.5)
        gradient_steps = params.get("gradient_steps", 10)
        glow_enabled = params.get("glow_enabled", True)
        glow_opacity = params.get("glow_opacity", 0.15)
        glow_radius = params.get("glow_radius", 3)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate layer for the text effect
        padding = 30  # Extra space for effects
        text_layer = Image.new('RGBA', (text_width + padding * 2, text_height + padding * 2), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        
        # Apply shadow if enabled
        if shadow_enabled:
            shadow_color = (0, 0, 0, int(255 * shadow_opacity))
            text_draw.text(
                (padding + shadow_offset, padding + shadow_offset),
                text,
                font=font,
                fill=shadow_color
            )
        
        # Apply glow if enabled
        if glow_enabled:
            # Determine glow color
            if accent_color:
                r, g, b, a = accent_color
                glow_color = (r, g, b, int(255 * glow_opacity))
            else:
                # Use a brighter version of text color
                r, g, b, a = text_color
                glow_color = (
                    min(r + 50, 255),
                    min(g + 50, 255),
                    min(b + 50, 255),
                    int(255 * glow_opacity)
                )
            
            # Create glow layer
            glow_layer = Image.new('RGBA', text_layer.size, (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_layer)
            glow_draw.text((padding, padding), text, font=font, fill=glow_color)
            
            # Apply blur for glow effect
            glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=glow_radius))
            
            # Composite with text layer
            text_layer = Image.alpha_composite(glow_layer, text_layer)
        
        # Apply gradient effect
        r1, g1, b1, a1 = text_color
        
        if accent_color:
            r2, g2, b2, a2 = accent_color
        else:
            # Create complementary color
            r2 = min(r1 + 70, 255)
            g2 = min(g1 + 70, 255)
            b2 = min(b1 + 70, 255)
            a2 = a1
        
        # Create gradient layer
        gradient_layer = Image.new('RGBA', text_layer.size, (0, 0, 0, 0))
        gradient_draw = ImageDraw.Draw(gradient_layer)
        
        # Draw gradient text
        for i in range(text_height):
            # Calculate position in gradient (0 to 1)
            pos = i / text_height
            
            # Calculate color for this position
            r = int(r1 * (1 - pos) + r2 * pos)
            g = int(g1 * (1 - pos) + g2 * pos)
            b = int(b1 * (1 - pos) + b2 * pos)
            a = int(a1 * (1 - pos * 0.1))  # Slight fade
            
            current_color = (r, g, b, a)
            
            # Draw text at this position
            gradient_draw.text((padding, padding + i), text, font=font, fill=current_color)
        
        # Composite with result
        text_layer = Image.alpha_composite(text_layer, gradient_layer)
        
        # Paste the result
        draw._image.paste(text_layer, (x - padding, y - padding), text_layer)

    def _apply_layered_gradient(self,
                               draw: ImageDraw.Draw,
                               text: str,
                               position: Tuple[int, int],
                               font: ImageFont.FreeTypeFont,
                               text_color: Tuple[int, int, int, int],
                               accent_color: Optional[Tuple[int, int, int, int]],
                               params: Dict[str, Any]) -> None:
        """
        Apply complex layered gradient for depth.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: (x, y) position
            font: Font to use
            text_color: Text color (RGBA)
            accent_color: Accent color (RGBA)
            params: Effect parameters
        """
        x, y = position
        
        # Get parameters
        shadow_enabled = params.get("shadow_enabled", True)
        shadow_offset = params.get("shadow_offset", 2)
        shadow_opacity = params.get("shadow_opacity", 0.5)
        gradient_direction = params.get("gradient_direction", "vertical")
        gradient_layers = params.get("gradient_layers", 3)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate layer for the text effect
        padding = 30  # Extra space for effects
        text_layer = Image.new('RGBA', (text_width + padding * 2, text_height + padding * 2), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        
        # Apply shadow if enabled
        if shadow_enabled:
            shadow_color = (0, 0, 0, int(255 * shadow_opacity))
            text_draw.text(
                (padding + shadow_offset, padding + shadow_offset),
                text,
                font=font,
                fill=shadow_color
            )
        
        # Extract color components
        r1, g1, b1, a1 = text_color
        
        if accent_color:
            r2, g2, b2, a2 = accent_color
        else:
            # Create gradient end color
            r2 = int(r1 * 0.7)
            g2 = int(g1 * 0.7)
            b2 = int(b1 * 0.7)
            a2 = a1
        
        # Create multiple gradient layers
        for layer in range(gradient_layers):
            # Calculate offset for this layer
            if gradient_direction == "vertical":
                offset_x = 0
                offset_y = layer * 2  # Offset each layer by 2 pixels
            else:  # horizontal
                offset_x = layer * 2
                offset_y = 0
            
            # Calculate blend factor for colors
            blend = layer / (gradient_layers - 1) if gradient_layers > 1 else 0
            
            # Calculate color for this layer
            r = int(r1 * (1 - blend) + r2 * blend)
            g = int(g1 * (1 - blend) + g2 * blend)
            b = int(b1 * (1 - blend) + b2 * blend)
            a = int(a1 * (1 - blend * 0.2))  # Slight fade
            
            layer_color = (r, g, b, a)
            
            # Create layer
            layer_img = Image.new('RGBA', text_layer.size, (0, 0, 0, 0))
            layer_draw = ImageDraw.Draw(layer_img)
            
            # Draw text on this layer
            layer_draw.text(
                (padding + offset_x, padding + offset_y),
                text,
                font=font,
                fill=layer_color
            )
            
            # Composite with text layer
            text_layer = Image.alpha_composite(text_layer, layer_img)
        
        # Paste the result
        draw._image.paste(text_layer, (x - padding, y - padding), text_layer)

    def _apply_glass_effect_text(self,
                               draw: ImageDraw.Draw,
                               text: str,
                               position: Tuple[int, int],
                               font: ImageFont.FreeTypeFont,
                               text_color: Tuple[int, int, int, int],
                               accent_color: Optional[Tuple[int, int, int, int]],
                               params: Dict[str, Any]) -> None:
        """
        Apply modern glass-like effect with transparency.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: (x, y) position
            font: Font to use
            text_color: Text color (RGBA)
            accent_color: Accent color (RGBA)
            params: Effect parameters
        """
        x, y = position
        
        # Get parameters
        glass_opacity = params.get("glass_opacity", 0.6)
        glass_blur = params.get("glass_blur", 10)
        glass_reflection = params.get("glass_reflection", 0.3)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate layer for the text effect
        padding = 30  # Extra space for effects
        text_layer = Image.new('RGBA', (text_width + padding * 2, text_height + padding * 2), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        
        # Extract color components
        r, g, b, a = text_color
        
        # Create glass background
        bg_color = (255, 255, 255, int(255 * glass_opacity * 0.6))
        
        # Draw text background with rounded corners
        self.draw_rounded_rectangle(
            text_draw,
            [(padding - 10, padding - 10), (padding + text_width + 10, padding + text_height + 10)],
            bg_color,
            radius=10
        )
        
        # Add reflection gradient at top
        highlight_height = int(text_height * 0.4)
        for i in range(highlight_height):
            alpha = int(255 * glass_reflection * (1 - i / highlight_height))
            highlight_color = (255, 255, 255, alpha)
            
            text_draw.line(
                [(padding - 10, padding - 10 + i), (padding + text_width + 10, padding - 10 + i)],
                fill=highlight_color
            )
        
        # Draw text
        text_draw.text((padding, padding), text, font=font, fill=text_color)
        
        # Apply blur to create glass effect
        text_layer = text_layer.filter(ImageFilter.GaussianBlur(radius=1))
        
        # Draw text again on top for sharpness
        text_draw = ImageDraw.Draw(text_layer)
        text_draw.text((padding, padding), text, font=font, fill=text_color)
        
        # Paste the result
        draw._image.paste(text_layer, (x - padding, y - padding), text_layer)

    def _apply_nike_bold_effect(self,
                               draw: ImageDraw.Draw,
                               text: str,
                               position: Tuple[int, int],
                               font: ImageFont.FreeTypeFont,
                               text_color: Tuple[int, int, int, int],
                               accent_color: Optional[Tuple[int, int, int, int]],
                               params: Dict[str, Any]) -> None:
        """
        Apply Nike-style bold condensed typography.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: (x, y) position
            font: Font to use
            text_color: Text color (RGBA)
            accent_color: Accent color (RGBA)
            params: Effect parameters
        """
        x, y = position
        
        # Get parameters
        outline_enabled = params.get("outline_enabled", True)
        outline_size = params.get("outline_size", 1)
        outline_opacity = params.get("outline_opacity", 0.8)
        condensed = params.get("condensed", True)
        letter_spacing = params.get("letter_spacing", -0.05)
        transform = params.get("transform", "uppercase")
        
        # Transform text if needed
        if transform == "uppercase":
            text = text.upper()
        elif transform == "lowercase":
            text = text.lower()
        elif transform == "capitalize":
            text = text.title()
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate layer for the text effect
        padding = 30  # Extra space for effects
        text_layer = Image.new('RGBA', (text_width + padding * 2, text_height + padding * 2), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        
        # Handle condensed text with custom letter spacing
        if condensed and letter_spacing != 0:
            # Calculate letter spacing in pixels
            spacing_px = int(text_height * letter_spacing)
            
            # Draw each character with spacing
            pos_x = padding
            for char in text:
                char_width, _ = self._get_text_dimensions(char, font)
                
                # Apply outline if enabled
                if outline_enabled:
                    outline_color = (0, 0, 0, int(255 * outline_opacity))
                    for dx, dy in [(outline_size, 0), (-outline_size, 0), (0, outline_size), (0, -outline_size)]:
                        text_draw.text(
                            (pos_x + dx, padding + dy),
                            char,
                            font=font,
                            fill=outline_color
                        )
                
                # Draw character
                text_draw.text((pos_x, padding), char, font=font, fill=text_color)
                
                # Move to next position with spacing
                pos_x += char_width + spacing_px
        else:
            # Apply outline if enabled
            if outline_enabled:
                outline_color = (0, 0, 0, int(255 * outline_opacity))
                for dx, dy in [(outline_size, 0), (-outline_size, 0), (0, outline_size), (0, -outline_size)]:
                    text_draw.text(
                        (padding + dx, padding + dy),
                        text,
                        font=font,
                        fill=outline_color
                    )
            
            # Draw text normally
            text_draw.text((padding, padding), text, font=font, fill=text_color)
        
        # Paste the result
        draw._image.paste(text_layer, (x - padding, y - padding), text_layer)

    def _apply_subtle_bg_effect(self,
                               draw: ImageDraw.Draw,
                               text: str,
                               position: Tuple[int, int],
                               font: ImageFont.FreeTypeFont,
                               text_color: Tuple[int, int, int, int],
                               accent_color: Optional[Tuple[int, int, int, int]],
                               params: Dict[str, Any]) -> None:
        """
        Apply text with subtle background for better legibility.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: (x, y) position
            font: Font to use
            text_color: Text color (RGBA)
            accent_color: Accent color (RGBA)
            params: Effect parameters
        """
        x, y = position
        
        # Get parameters
        background_enabled = params.get("background_enabled", True)
        background_opacity = params.get("background_opacity", 0.7)
        background_padding = params.get("background_padding", 15)
        background_radius = params.get("background_radius", 8)
        background_blur = params.get("background_blur", 0)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate layer for the text effect
        padding = max(30, background_padding + 10)  # Extra space for effects
        text_layer = Image.new('RGBA', (text_width + padding * 2, text_height + padding * 2), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        
        # Create background if enabled
        if background_enabled:
            # Determine background color
            if accent_color:
                r, g, b, a = accent_color
            else:
                # Use dark gray for light text, light gray for dark text
                r, g, b, a = text_color
                brightness = (r * 299 + g * 587 + b * 114) / 1000
                if brightness > 128:
                    r, g, b = 0, 0, 0  # Dark background for light text
                else:
                    r, g, b = 255, 255, 255  # Light background for dark text
            
            bg_color = (r, g, b, int(255 * background_opacity))
            
            # Draw background with rounded corners
            self.draw_rounded_rectangle(
                text_draw,
                [
                    (padding - background_padding, padding - background_padding),
                    (padding + text_width + background_padding, padding + text_height + background_padding)
                ],
                bg_color,
                radius=background_radius
            )
            
            # Apply blur if specified
            if background_blur > 0:
                text_layer = text_layer.filter(ImageFilter.GaussianBlur(radius=background_blur))
                
                # Redraw background after blur
                text_draw = ImageDraw.Draw(text_layer)
                self.draw_rounded_rectangle(
                    text_draw,
                    [
                        (padding - background_padding, padding - background_padding),
                        (padding + text_width + background_padding, padding + text_height + background_padding)
                    ],
                    bg_color,
                    radius=background_radius
                )
        
        # Draw text
        text_draw.text((padding, padding), text, font=font, fill=text_color)

    # Paste the result
        draw._image.paste(text_layer, (x - padding, y - padding), text_layer)
    
    def _draw_rounded_button(self,
                            draw: ImageDraw.Draw,
                            bounds: Tuple[int, int, int, int],
                            text: str,
                            font: ImageFont.FreeTypeFont,
                            text_color: Tuple[int, int, int, int],
                            button_color: Tuple[int, int, int, int],
                            params: Dict[str, Any]) -> None:
        """
        Draw a rounded button.
        
        Args:
            draw: ImageDraw object
            bounds: (left, top, right, bottom) bounds
            text: Button text
            font: Font to use
            text_color: Text color (RGBA)
            button_color: Button color (RGBA)
            params: Button parameters
        """
        left, top, right, bottom = bounds
        button_width = right - left
        button_height = bottom - top
        
        # Get parameters
        radius = params.get("radius", min(15, button_height // 3))
        highlight_opacity = params.get("highlight_opacity", 0.3)
        shadow_opacity = params.get("shadow_opacity", 0.4)
        
        # Draw outer shadow for depth
        shadow_color = (0, 0, 0, int(100 * shadow_opacity))
        self.draw_rounded_rectangle(
            draw,
            [(left + 2, top + 2), (right + 2, bottom + 2)],
            shadow_color,
            radius=radius
        )
        
        # Draw main button
        self.draw_rounded_rectangle(
            draw,
            [(left, top), (right, bottom)],
            button_color,
            radius=radius
        )
        
        # Draw highlight at top for 3D effect
        highlight_height = int(button_height * 0.4)
        highlight_color = (255, 255, 255, int(255 * highlight_opacity))
        
        self.draw_rounded_rectangle(
            draw,
            [(left + 1, top + 1), (right - 1, top + highlight_height)],
            highlight_color,
            radius=radius - 1
        )
        
        # Calculate text position
        text_width, text_height = self._get_text_dimensions(text, font)
        text_x = left + (button_width - text_width) // 2
        text_y = top + (button_height - text_height) // 2
        
        # Draw text with slight shadow
        draw.text((text_x + 1, text_y + 1), text, font=font, fill=(0, 0, 0, 100))
        draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    def _draw_minimal_line_button(self,
                                 draw: ImageDraw.Draw,
                                 bounds: Tuple[int, int, int, int],
                                 text: str,
                                 font: ImageFont.FreeTypeFont,
                                 text_color: Tuple[int, int, int, int],
                                 button_color: Tuple[int, int, int, int],
                                 params: Dict[str, Any]) -> None:
        """
        Draw a minimal button with just borders.
        
        Args:
            draw: ImageDraw object
            bounds: (left, top, right, bottom) bounds
            text: Button text
            font: Font to use
            text_color: Text color (RGBA)
            button_color: Button color (RGBA)
            params: Button parameters
        """
        left, top, right, bottom = bounds
        button_width = right - left
        button_height = bottom - top
        
        # Get parameters
        border_width = params.get("border_width", 1)
        radius = params.get("radius", min(8, button_height // 4))
        
        # Draw border
        if hasattr(draw, 'rounded_rectangle'):
            # Use native rounded rectangle if available (Pillow 8.0.0+)
            draw.rounded_rectangle(
                [(left, top), (right, bottom)],
                radius=radius,
                outline=button_color,
                width=border_width
            )
        else:
            # Fallback for older Pillow versions
            self.draw_rounded_rectangle(
                draw,
                [(left, top), (right, bottom)],
                (0, 0, 0, 0),  # Transparent fill
                radius=radius,
                outline=button_color
            )
        
        # Calculate text position
        text_width, text_height = self._get_text_dimensions(text, font)
        text_x = left + (button_width - text_width) // 2
        text_y = top + (button_height - text_height) // 2
        
        # Draw text
        draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    def _draw_pill_button(self,
                         draw: ImageDraw.Draw,
                         bounds: Tuple[int, int, int, int],
                         text: str,
                         font: ImageFont.FreeTypeFont,
                         text_color: Tuple[int, int, int, int],
                         button_color: Tuple[int, int, int, int],
                         params: Dict[str, Any]) -> None:
        """
        Draw a pill-shaped button (fully rounded ends).
        
        Args:
            draw: ImageDraw object
            bounds: (left, top, right, bottom) bounds
            text: Button text
            font: Font to use
            text_color: Text color (RGBA)
            button_color: Button color (RGBA)
            params: Button parameters
        """
        left, top, right, bottom = bounds
        button_width = right - left
        button_height = bottom - top
        
        # Pill buttons have fully rounded ends (radius = height/2)
        radius = button_height // 2
        
        # Get parameters
        highlight_opacity = params.get("highlight_opacity", 0.3)
        shadow_opacity = params.get("shadow_opacity", 0.4)
        
        # Draw button with shadow
        shadow_color = (0, 0, 0, int(100 * shadow_opacity))
        self.draw_rounded_rectangle(
            draw,
            [(left + 1, top + 1), (right + 1, bottom + 1)],
            shadow_color,
            radius=radius
        )
        
        # Draw main button
        self.draw_rounded_rectangle(
            draw,
            [(left, top), (right, bottom)],
            button_color,
            radius=radius
        )
        
        # Add highlight for 3D effect
        highlight_height = button_height // 2
        highlight_color = (255, 255, 255, int(255 * highlight_opacity))
        self.draw_rounded_rectangle(
            draw,
            [(left + 1, top + 1), (right - 1, top + highlight_height)],
            highlight_color,
            radius=radius - 1
        )
        
        # Calculate text position
        text_width, text_height = self._get_text_dimensions(text, font)
        text_x = left + (button_width - text_width) // 2
        text_y = top + (button_height - text_height) // 2
        
        # Draw text with subtle shadow
        draw.text((text_x + 1, text_y + 1), text, font=font, fill=(0, 0, 0, 80))
        draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    def _draw_gradient_button(self,
                             draw: ImageDraw.Draw,
                             bounds: Tuple[int, int, int, int],
                             text: str,
                             font: ImageFont.FreeTypeFont,
                             text_color: Tuple[int, int, int, int],
                             button_color: Tuple[int, int, int, int],
                             params: Dict[str, Any]) -> None:
        """
        Draw a button with gradient fill.
        
        Args:
            draw: ImageDraw object
            bounds: (left, top, right, bottom) bounds
            text: Button text
            font: Font to use
            text_color: Text color (RGBA)
            button_color: Button color (RGBA)
            params: Button parameters
        """
        left, top, right, bottom = bounds
        width = right - left
        height = bottom - top
        
        # Get parameters
        radius = params.get("radius", min(10, height // 3))
        direction = params.get("direction", "vertical")
        darkness_factor = params.get("darkness_factor", 0.7)
        
        # Create separate image for gradient button
        button_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        button_draw = ImageDraw.Draw(button_img)
        
        # Calculate gradient colors
        r, g, b, a = button_color
        
        start_color = button_color
        end_color = (
            int(r * darkness_factor),
            int(g * darkness_factor),
            int(b * darkness_factor),
            a
        )
        
        # Draw gradient
        if direction == "vertical":
            # Vertical gradient (top to bottom)
            for y in range(height):
                # Calculate color for this line
                ratio = y / height
                r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
                g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
                b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
                a = int(start_color[3] * (1 - ratio) + end_color[3] * ratio)
                
                line_color = (r, g, b, a)
                button_draw.line([(0, y), (width, y)], fill=line_color)
        else:
            # Horizontal gradient (left to right)
            for x in range(width):
                # Calculate color for this line
                ratio = x / width
                r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
                g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
                b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
                a = int(start_color[3] * (1 - ratio) + end_color[3] * ratio)
                
                line_color = (r, g, b, a)
                button_draw.line([(x, 0), (x, height)], fill=line_color)
        
        # Create mask for rounded corners
        mask = Image.new('L', (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), (width, height)], radius=radius, fill=255)
        
        # Apply mask for rounded corners
        button_img.putalpha(mask)
        
        # Add subtle shadow
        shadow_img = Image.new('RGBA', (width + 4, height + 4), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        shadow_draw.rounded_rectangle([(2, 2), (width + 2, height + 2)], radius=radius, fill=(0, 0, 0, 80))
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=1))
        
        # Paste shadow
        draw._image.paste(shadow_img, (left - 2, top - 2), shadow_img)
        
        # Paste button
        draw._image.paste(button_img, (left, top), button_img)
        
        # Calculate text position
        text_width, text_height = self._get_text_dimensions(text, font)
        text_x = left + (width - text_width) // 2
        text_y = top + (height - text_height) // 2
        
        # Draw text with subtle shadow
        draw.text((text_x + 1, text_y + 1), text, font=font, fill=(0, 0, 0, 80))
        draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    def _draw_glass_button(self,
                          draw: ImageDraw.Draw,
                          bounds: Tuple[int, int, int, int],
                          text: str,
                          font: ImageFont.FreeTypeFont,
                          text_color: Tuple[int, int, int, int],
                          button_color: Tuple[int, int, int, int],
                          params: Dict[str, Any]) -> None:
        """
        Draw a glass-effect button.
        
        Args:
            draw: ImageDraw object
            bounds: (left, top, right, bottom) bounds
            text: Button text
            font: Font to use
            text_color: Text color (RGBA)
            button_color: Button color (RGBA)
            params: Button parameters
        """
        left, top, right, bottom = bounds
        width = right - left
        height = bottom - top
        
        # Get parameters
        radius = params.get("radius", 10)
        opacity = params.get("opacity", 0.6)
        reflection_opacity = params.get("reflection_opacity", 0.3)
        
        # Create a separate image for the glass button
        button_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        button_draw = ImageDraw.Draw(button_img)
        
        # Extract color components
        r, g, b, a = button_color
        
        # Draw base with adjusted opacity
        base_color = (r, g, b, int(a * opacity))
        button_draw.rounded_rectangle(
            [(0, 0), (width, height)],
            radius=radius,
            fill=base_color
        )
        
        # Add top highlight (glass reflection)
        highlight_height = height // 3
        
        # Create gradient for highlight
        for i in range(highlight_height):
            alpha = int(255 * reflection_opacity * (1 - i / highlight_height))
            highlight_color = (255, 255, 255, alpha)
            button_draw.line(
                [(0, i), (width, i)],
                fill=highlight_color
            )
        
        # Add bottom shadow for depth
        shadow_height = height // 4
        shadow_top = height - shadow_height
        
        # Create gradient for shadow
        for i in range(shadow_height):
            alpha = int(80 * i / shadow_height)
            shadow_color = (0, 0, 0, alpha)
            button_draw.line(
                [(0, shadow_top + i), (width, shadow_top + i)],
                fill=shadow_color
            )
        
        # Add subtle outer glow
        glow_img = Image.new('RGBA', (width + 10, height + 10), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)
        glow_draw.rounded_rectangle(
            [(5, 5), (width + 5, height + 5)],
            radius=radius + 2,
            fill=(r, g, b, 50)
        )
        glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=3))
        
        # Paste glow
        draw._image.paste(glow_img, (left - 5, top - 5), glow_img)
        
        # Paste button
        draw._image.paste(button_img, (left, top), button_img)
        
        # Calculate text position
        text_width, text_height = self._get_text_dimensions(text, font)
        text_x = left + (width - text_width) // 2
        text_y = top + (height - text_height) // 2
        
        # Draw text with subtle shadow
        draw.text((text_x + 1, text_y + 1), text, font=font, fill=(0, 0, 0, 80))
        draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    def _draw_flat_button(self,
                         draw: ImageDraw.Draw,
                         bounds: Tuple[int, int, int, int],
                         text: str,
                         font: ImageFont.FreeTypeFont,
                         text_color: Tuple[int, int, int, int],
                         button_color: Tuple[int, int, int, int],
                         params: Dict[str, Any]) -> None:
        """
        Draw a flat button with no 3D effects.
        
        Args:
            draw: ImageDraw object
            bounds: (left, top, right, bottom) bounds
            text: Button text
            font: Font to use
            text_color: Text color (RGBA)
            button_color: Button color (RGBA)
            params: Button parameters
        """
        left, top, right, bottom = bounds
        width = right - left
        height = bottom - top
        
        # Get parameters
        radius = params.get("radius", min(5, height // 6))
        
        # Draw button
        self.draw_rounded_rectangle(
            draw,
            [(left, top), (right, bottom)],
            button_color,
            radius=radius
        )
        
        # Calculate text position
        text_width, text_height = self._get_text_dimensions(text, font)
        text_x = left + (width - text_width) // 2
        text_y = top + (height - text_height) // 2
        
        # Draw text 
        draw.text((text_x, text_y), text, font=font, fill=text_color)