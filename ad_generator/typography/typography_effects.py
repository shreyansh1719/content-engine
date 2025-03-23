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
                        image: Optional[Image.Image] = None) -> None:
        """
        Apply a text effect to the specified text.
        
        Args:
            draw: ImageDraw object to draw on
            text: Text string to render
            position: (x, y) position for text
            font: Font to use for text
            alignment: Text alignment (left, center, right)
            effect: Name of the effect to apply
            text_color: Text color (RGBA)
            accent_color: Accent color for effects (RGBA)
            typography_style: Optional typography style parameters
            image: Optional reference to original image for some effects
        """
        try:
            # Get effect parameters
            effect_params = self.effects_registry.get(effect, self.effects_registry["simple"]).get("params", {})
            
            # Override with typography style parameters if provided
            if typography_style and "effect_params" in typography_style:
                for key, value in typography_style["effect_params"].items():
                    effect_params[key] = value
            
            # Get text dimensions
            text_width, text_height = self._get_text_dimensions(text, font)
            
            # Apply text transformations if needed
            transform = effect_params.get("transform", None)
            if transform == "uppercase":
                text = text.upper()
            elif transform == "lowercase":
                text = text.lower()
            elif transform == "capitalize":
                text = text.title()
            
            # Apply letter spacing if needed
            letter_spacing = effect_params.get("letter_spacing", 0)
            if letter_spacing != 0:
                text = self._apply_letter_spacing(text, letter_spacing)
                # Recalculate dimensions with spacing
                text_width, text_height = self._get_text_dimensions(text, font)
            
            # Calculate position based on alignment
            x, y = position
            if alignment == "center":
                x = x - text_width // 2
            elif alignment == "right":
                x = x - text_width
            
            # For text background
            if effect_params.get("background_enabled", False):
                self._apply_text_background(
                    draw, 
                    text, 
                    (x, y), 
                    font, 
                    text_width, 
                    text_height, 
                    accent_color or (0, 0, 0, int(255 * effect_params.get("background_opacity", 0.7))),
                    effect_params
                )
            
            # For the glass effect
            if effect_params.get("glass_enabled", False) and image:
                self._apply_glass_effect(
                    draw, 
                    text, 
                    (x, y), 
                    font, 
                    text_color, 
                    image, 
                    effect_params
                )
                return  # Glass effect handles the text drawing
            
            # For metallic effect
            if effect_params.get("metallic_enabled", False):
                self._apply_metallic_effect(
                    draw, 
                    text, 
                    (x, y), 
                    font, 
                    text_color, 
                    accent_color, 
                    effect_params
                )
                return  # Metallic effect handles the text drawing
            
            # Create image for effects processing if needed
            effects_needed = (
                effect_params.get("shadow_enabled", False) or
                effect_params.get("glow_enabled", False) or
                effect_params.get("gradient_enabled", False) or
                effect_params.get("outline_enabled", False)
            )
            
            if effects_needed:
                # Create separate image for effects processing
                padding = 20  # Padding for effects that extend beyond text
                effects_img = Image.new(
                    'RGBA', 
                    (text_width + padding * 2, text_height + padding * 2), 
                    (0, 0, 0, 0)
                )
                effects_draw = ImageDraw.Draw(effects_img)
                
                # Apply shadow if enabled
                if effect_params.get("shadow_enabled", False):
                    self._apply_shadow(
                        effects_draw, 
                        text, 
                        (padding, padding), 
                        font, 
                        text_color, 
                        effect_params
                    )
                
                # Apply glow if enabled
                if effect_params.get("glow_enabled", False):
                    self._apply_glow(
                        effects_draw, 
                        text, 
                        (padding, padding), 
                        font, 
                        text_color, 
                        accent_color, 
                        effect_params
                    )
                
                # Apply outline if enabled
                if effect_params.get("outline_enabled", False):
                    self._apply_outline(
                        effects_draw, 
                        text, 
                        (padding, padding), 
                        font, 
                        text_color, 
                        accent_color or text_color, 
                        effect_params
                    )
                
                # Apply gradient if enabled
                if effect_params.get("gradient_enabled", False):
                    self._apply_gradient(
                        effects_draw, 
                        text, 
                        (padding, padding), 
                        font, 
                        text_color, 
                        accent_color, 
                        effect_params
                    )
                else:
                    # Draw regular text if no gradient
                    effects_draw.text((padding, padding), text, font=font, fill=text_color)
                
                # Paste effects image onto the main image
                # Calculate paste position
                paste_x = x - padding
                paste_y = y - padding
                draw._image.paste(effects_img, (paste_x, paste_y), effects_img)
            else:
                # Just draw the text directly if no effects needed
                draw.text((x, y), text, font=font, fill=text_color)
                
        except Exception as e:
            self.logger.error(f"Error applying text effect: {str(e)}")
            # Fallback to simple text rendering
            try:
                # Calculate position based on alignment
                x, y = position
                if alignment == "center":
                    x = x - text_width // 2
                elif alignment == "right":
                    x = x - text_width
                    
                draw.text((x, y), text, font=font, fill=text_color)
            except:
                pass
    
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
            if hasattr(draw, 'rounded_rectangle'):
                # Use native rounded rectangle if available (Pillow 8.0.0+)
                draw.rounded_rectangle([(x1, y1), (x2, y2)], radius, fill=None, outline=outline, width=width)
    
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
    
    def _apply_letter_spacing(self, text: str, spacing_factor: float) -> str:
        """
        Apply letter spacing to text.
        
        Args:
            text: Original text
            spacing_factor: Spacing factor relative to font size
            
        Returns:
            Text with spaces inserted between characters
        """
        if spacing_factor <= 0:
            return text
            
        # Add spaces between characters based on spacing factor
        spaced_text = ""
        space_width = int(abs(spacing_factor) * 10)
        
        for char in text:
            spaced_text += char
            if char != ' ':
                spaced_text += ' ' * space_width
                
        return spaced_text
    
    def _apply_shadow(self,
                     draw: ImageDraw.Draw,
                     text: str,
                     position: Tuple[int, int],
                     font: ImageFont.FreeTypeFont, 
                     text_color: Tuple[int, int, int, int],
                     params: Dict[str, Any]) -> None:
        """
        Apply shadow effect to text.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: (x, y) position
            font: Font to use
            text_color: Text color (RGBA)
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
    
    def _apply_glow(self,
                   draw: ImageDraw.Draw,
                   text: str,
                   position: Tuple[int, int],
                   font: ImageFont.FreeTypeFont,
                   text_color: Tuple[int, int, int, int],
                   accent_color: Optional[Tuple[int, int, int, int]],
                   params: Dict[str, Any]) -> None:
        """
        Apply glow effect to text.
        
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
        
        # Get glow parameters
        glow_radius = params.get("glow_radius", 5)
        glow_opacity = params.get("glow_opacity", 0.3)
        
        # Determine glow color
        if accent_color:
            glow_color = accent_color
        else:
            # Use a brighter version of the text color
            r, g, b, a = text_color
            glow_color = (
                min(r + 50, 255),
                min(g + 50, 255),
                min(b + 50, 255),
                int(a * glow_opacity)
            )
        
        # Create a separate image for the glow
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Add padding for glow
        padding = int(glow_radius * 3)
        glow_img = Image.new(
            'RGBA', 
            (text_width + padding * 2, text_height + padding * 2), 
            (0, 0, 0, 0)
        )
        glow_draw = ImageDraw.Draw(glow_img)
        
        # Extract glow color components
        gr, gg, gb, ga = glow_color
        
        # Draw progressively more transparent glows
        for i in range(3):
            alpha = int(ga / (i + 1))
            current_color = (gr, gg, gb, alpha)
            
            # Draw text multiple times with different offsets for omnidirectional glow
            for offset_x, offset_y in [(-i, -i), (-i, 0), (-i, i), (0, -i), (0, i), (i, -i), (i, 0), (i, i)]:
                glow_draw.text(
                    (padding + offset_x, padding + offset_y),
                    text, 
                    font=font, 
                    fill=current_color
                )
        
        # Apply Gaussian blur for smooth glow
        glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=glow_radius))
        
        # Paste glow layer
        paste_x = x - padding
        paste_y = y - padding
        draw._image.paste(glow_img, (paste_x, paste_y), glow_img)
        
        # Draw main text on top
        draw.text((x, y), text, font=font, fill=text_color)
    
    def _apply_outline(self,
                      draw: ImageDraw.Draw,
                      text: str,
                      position: Tuple[int, int],
                      font: ImageFont.FreeTypeFont,
                      text_color: Tuple[int, int, int, int],
                      outline_color: Tuple[int, int, int, int],
                      params: Dict[str, Any]) -> None:
        """
        Apply outline effect to text.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: (x, y) position
            font: Font to use
            text_color: Text color (RGBA)
            outline_color: Outline color (RGBA)
            params: Effect parameters
        """
        x, y = position
        
        # Get outline parameters
        thickness = params.get("outline_size", 1)
        opacity = params.get("outline_opacity", 1.0)
        
        # Adjust outline color opacity
        r, g, b, a = outline_color
        outline_color = (r, g, b, int(a * opacity))
        
        # Draw outline by drawing the text multiple times with offsets
        directions = [
            (-1, -1), (0, -1), (1, -1),
            (-1,  0),          (1,  0),
            (-1,  1), (0,  1), (1,  1)
        ]
        
        for _ in range(thickness):
            for dx, dy in directions:
                draw.text(
                    (x + dx, y + dy), 
                    text, 
                    font=font, 
                    fill=outline_color
                )
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)
    
    def _apply_gradient(self,
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
        layers = params.get("gradient_layers", 1)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Setup colors for gradient
        r1, g1, b1, a1 = text_color
        
        if accent_color:
            r2, g2, b2, a2 = accent_color
        else:
            # Calculate a darker variant for end color
            darkness = 0.7
            r2, g2, b2, a2 = (
                int(r1 * darkness),
                int(g1 * darkness),
                int(b1 * darkness),
                int(a1 * end_opacity)
            )
        
        # Create layered gradient effect
        for i in range(layers):
            # Calculate blend factor for this layer
            blend = i / layers if layers > 1 else 0
            
            # Interpolate colors
            r = int(r1 * (1 - blend) + r2 * blend)
            g = int(g1 * (1 - blend) + g2 * blend)
            b = int(b1 * (1 - blend) + b2 * blend)
            a = int(a1 * (1 - blend * (1 - end_opacity / start_opacity)))
            
            layer_color = (r, g, b, a)
            
            # Calculate offset based on direction
            if direction == "vertical":
                offset_y = int(text_height * blend * 0.1)
                offset_x = 0
            elif direction == "horizontal":
                offset_x = int(text_width * blend * 0.1)
                offset_y = 0
            elif direction == "diagonal":
                offset_x = int(text_width * blend * 0.05)
                offset_y = int(text_height * blend * 0.05)
            else:
                offset_x = 0
                offset_y = 0
                
            # Draw layer
            draw.text(
                (x + offset_x, y + offset_y), 
                text, 
                font=font, 
                fill=layer_color
            )
    
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
        metal_img = Image.new(
            'RGBA', 
            (text_width + padding * 2, text_height + padding * 2), 
            (0, 0, 0, 0)
        )
        metal_draw = ImageDraw.Draw(metal_img)
        
        # Draw shadow first if enabled
        if params.get("shadow_enabled", True):
            shadow_offset = params.get("shadow_offset", 3)
            shadow_opacity = params.get("shadow_opacity", 0.6)
            shadow_color = (0, 0, 0, int(255 * shadow_opacity))
            
            metal_draw.text(
                (padding + shadow_offset, padding + shadow_offset), 
                text, 
                font=font, 
                fill=shadow_color
            )
        
        # Determine base metal color
        if accent_color:
            base_color = accent_color
        else:
            base_color = text_color
        
        r, g, b, a = base_color
        
        # 1. Draw dark base
        dark_base = (
            int(r * shadows),
            int(g * shadows),
            int(b * shadows),
            a
        )
        metal_draw.text((padding, padding), text, font=font, fill=dark_base)
        
        # 2. Draw lighter shade for edge highlight
        edge_highlight = (
            min(int(r * 1.3), 255),
            min(int(g * 1.3), 255),
            min(int(b * 1.3), 255),
            a
        )
        metal_draw.text((padding - 1, padding - 1), text, font=font, fill=edge_highlight)
        
        # 3. Draw main text
        metal_draw.text((padding, padding), text, font=font, fill=base_color)
        
        # 4. Draw top edge highlight
        highlight_color = (
            min(int(r * 1.5), 255),
            min(int(g * 1.5), 255),
            min(int(b * 1.5), 255),
            int(a * 0.7)
        )
        metal_draw.text((padding - 1, padding - 2), text, font=font, fill=highlight_color)
        
        # Apply slight blur for smoother metallic look
        metal_img = metal_img.filter(ImageFilter.GaussianBlur(radius=0.3))
        
        # Paste the metallic image
        paste_x = x - padding
        paste_y = y - padding
        draw._image.paste(metal_img, (paste_x, paste_y), metal_img)
    
    def _apply_glass_effect(self,
                           draw: ImageDraw.Draw,
                           text: str,
                           position: Tuple[int, int],
                           font: ImageFont.FreeTypeFont,
                           text_color: Tuple[int, int, int, int],
                           image: Image.Image,
                           params: Dict[str, Any]) -> None:
        """
        Apply glass effect to text.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: (x, y) position
            font: Font to use
            text_color: Text color (RGBA)
            image: Original image for background
            params: Effect parameters
        """
        x, y = position
        
        # Get glass parameters
        blur_radius = params.get("glass_blur", 10)
        opacity = params.get("glass_opacity", 0.6)
        reflection_opacity = params.get("glass_reflection", 0.3)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Calculate the background area we need to blur
        padding = 10  # Extra space around text
        bg_left = max(0, x - padding)
        bg_top = max(0, y - padding)
        bg_right = min(image.width, x + text_width + padding)
        bg_bottom = min(image.height, y + text_height + padding)
        
        # Create a mask for the text area
        mask = Image.new('L', image.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.text((x, y), text, font=font, fill=255)
        
        # Blur the mask slightly for smoother edges
        mask = mask.filter(ImageFilter.GaussianBlur(radius=1))
        
        # Extract the region from the original image
        region = image.crop((bg_left, bg_top, bg_right, bg_bottom))
        
        # Apply blur to simulate glass effect
        blurred_region = region.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        # Create a new transparent overlay
        overlay = Image.new('RGBA', (bg_right - bg_left, bg_bottom - bg_top), (0, 0, 0, 0))
        
        # Paste the blurred region
        overlay.paste(blurred_region, (0, 0))
        
        # Apply semi-transparent white overlay for glass effect
        glass_overlay = Image.new('RGBA', overlay.size, (255, 255, 255, int(255 * opacity)))
        overlay = Image.alpha_composite(overlay, glass_overlay)
        
        # Add highlight gradient
        highlight = Image.new('RGBA', overlay.size, (0, 0, 0, 0))
        highlight_draw = ImageDraw.Draw(highlight)
        
        # Create top-to-bottom gradient for reflection
        for i in range(overlay.height // 3):
            alpha = int(255 * reflection_opacity * (1 - i / (overlay.height // 3)))
            highlight_draw.line(
                [(0, i), (overlay.width, i)],
                fill=(255, 255, 255, alpha)
            )
        
        # Add highlight to overlay
        overlay = Image.alpha_composite(overlay, highlight)
        
        # Paste back with mask
        draw._image.paste(overlay, (bg_left, bg_top), mask.crop((bg_left, bg_top, bg_right, bg_bottom)))
        
        # Draw text on top with semi-transparency
        r, g, b, a = text_color
        text_overlay_color = (r, g, b, int(a * 0.9))
        draw.text((x, y), text, font=font, fill=text_overlay_color)
    
    def _apply_text_background(self,
                              draw: ImageDraw.Draw,
                              text: str,
                              position: Tuple[int, int],
                              font: ImageFont.FreeTypeFont,
                              text_width: int,
                              text_height: int,
                              bg_color: Tuple[int, int, int, int],
                              params: Dict[str, Any]) -> None:
        """
        Apply background panel behind text.
        
        Args:
            draw: ImageDraw object
            text: Text to render
            position: (x, y) position
            font: Font to use
            text_width: Width of text
            text_height: Height of text
            bg_color: Background color (RGBA)
            params: Effect parameters
        """
        x, y = position
        
        # Get background parameters
        padding = params.get("background_padding", 15)
        radius = params.get("background_radius", 8)
        opacity = params.get("background_opacity", 0.7)
        
        # Calculate background rectangle area
        bg_left = x - padding
        bg_top = y - padding
        bg_right = x + text_width + padding
        bg_bottom = y + text_height + padding
        
        # Adjust color opacity
        r, g, b, a = bg_color
        bg_color_adjusted = (r, g, b, int(255 * opacity) if a > 200 else a)
        
        # Draw the background
        if radius > 0:
            self.draw_rounded_rectangle(
                draw,
                [(bg_left, bg_top), (bg_right, bg_bottom)],
                bg_color_adjusted,
                radius=radius
            )
        else:
            draw.rectangle(
                [(bg_left, bg_top), (bg_right, bg_bottom)],
                fill=bg_color_adjusted
            )
    
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
