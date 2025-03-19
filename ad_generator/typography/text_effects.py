"""
Text Effects Engine for ad generation system.
Provides professional text treatments and visual effects.
"""
import logging
import math
from typing import Dict, Tuple, Any, Optional, List, Union
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance, ImageChops, ImageColor
import numpy as np

class TextEffectsEngine:
    """Handles sophisticated text effects and treatments for professional typography."""
    
    def __init__(self):
        """Initialize the text effects engine."""
        self.logger = logging.getLogger(__name__)
        
        # Default effects parameters that define how various effects look
        self.default_effects_params = {
            'shadow': {
                'offset': 2,            # Offset distance in pixels
                'blur_radius': 3,       # Gaussian blur radius for shadow
                'color': (0, 0, 0, 150) # Shadow color with alpha
            },
            'glow': {
                'radius': 5,            # Glow radius
                'intensity': 0.7,       # Glow intensity (0-1)
                'color': (255, 255, 255, 100) # Glow color with alpha
            },
            'gradient': {
                'direction': 'vertical', # vertical, horizontal, diagonal
                'start_opacity': 1.0,    # Start opacity
                'end_opacity': 0.7       # End opacity
            },
            'outline': {
                'thickness': 1,          # Outline thickness in pixels
                'color': (255, 255, 255, 180) # Outline color with alpha
            },
            'background': {
                'padding': 15,           # Padding around text in pixels
                'radius': 8,             # Corner radius for rounded rectangles
                'opacity': 0.7,          # Background opacity
                'blur': 0                # Blur for background edges
            }
        }
    
    def apply_text_effect(self, draw: ImageDraw, text: str, position: Tuple[int, int], 
                         font: ImageFont.FreeTypeFont, treatment: str, 
                         text_color: Tuple[int, int, int, int], 
                         brightness_map: Optional[Dict[str, float]] = None, 
                         accent_color: Optional[Tuple[int, int, int, int]] = None,
                         image: Optional[Image.Image] = None,
                         treatment_params: Optional[Dict] = None) -> ImageDraw:
        """
        Apply professional text treatment with advanced effects.
        
        Args:
            draw: ImageDraw object
            text: Text to draw
            position: Text position (x, y)
            font: Font to use
            treatment: Text treatment style 
            text_color: Text color (RGBA tuple)
            brightness_map: Image brightness map (optional)
            accent_color: Accent color for certain effects (optional)
            image: Reference to original image for advanced effects (optional)
            treatment_params: Additional parameters for treatments (optional)
            
        Returns:
            Modified draw object
        """
        x, y = position
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Center text horizontally (unless positioning logic changes)
        x = x - text_width // 2
        
        # Parse custom params if provided
        params = treatment_params or {}
        
        # Apply treatment based on specified style
        if treatment == "premium_gradient":
            self._apply_premium_gradient_effect(draw, text, (x, y), font, text_color, params)
            
        elif treatment == "luxury_metallic":
            # Create a metallic effect for luxury brands
            self._apply_luxury_metallic_effect(draw, text, (x, y), font, text_color, accent_color, params)
        
        elif treatment == "elegant_shadow":
            # Subtle sophisticated shadow for elegant typography
            self._apply_elegant_shadow_effect(draw, text, (x, y), font, text_color, params)
            
        elif treatment == "subtle_glow":
            # Subtle glow effect for key elements
            self._apply_subtle_glow_effect(draw, text, (x, y), font, text_color, accent_color or text_color, params)
            
        elif treatment == "layered_gradient":
            # Complex gradient with layers for depth
            self._apply_layered_gradient_effect(draw, text, (x, y), font, text_color, 
                                               accent_color or text_color, params)
            
        elif treatment == "premium_outline":
            # Premium outline effect with subtle inner glow
            self._apply_premium_outline_effect(draw, text, (x, y), font, text_color, 
                                             accent_color or (255, 255, 255, 200), params)
            
        elif treatment == "glass_effect":
            # Modern glass-like effect with transparency and blur
            if image:
                self._apply_glass_effect(draw, text, (x, y), font, text_color, image, params)
            else:
                # Fallback if original image not provided
                self._apply_subtle_background(draw, text, (x, y), font, text_color, 
                                            text_width, text_height, brightness_map, params)
            
        elif treatment == "subtle_bg":
            # Enhanced subtle background with better aesthetics
            self._apply_subtle_background(draw, text, (x, y), font, text_color, 
                                        text_width, text_height, brightness_map, params)
            
        elif treatment == "minimal_elegant":
            # Minimal treatment with perfect letter spacing and subtle shadow
            self._apply_minimal_elegant(draw, text, (x, y), font, text_color, params)
            
        elif treatment == "vibrant_overlay":
            # Vibrant semi-transparent overlay with text
            self._apply_vibrant_overlay(draw, text, (x, y), font, text_color, 
                                       accent_color or text_color, params)
            
        elif treatment == "gradient":
            # Improved gradient text effect with better control
            self._apply_gradient_effect(draw, text, (x, y), font, text_color, params)
            
        elif treatment == "outline":
            # Enhanced outline with better quality
            self._apply_outline_effect(draw, text, (x, y), font, text_color, 
                                     accent_color or (0, 0, 0, 200), params)
            
        elif treatment == "glow":
            # Enhanced glow effect with better quality
            self._apply_glow_effect(draw, text, (x, y), font, text_color, 
                                  accent_color or (255, 255, 255, 100), params)
            
        elif treatment == "shadow":
            # Enhanced shadow effect with better quality
            self._apply_shadow_effect(draw, text, (x, y), font, text_color, params)
            
        elif treatment == "simple":
            # Just draw the text with no effects
            draw.text((x, y), text, font=font, fill=text_color)
            
        else:
            # Default - improved subtle shadow for contrast
            self._apply_shadow_effect(draw, text, (x, y), font, text_color, params)
        
        return draw
    
    def create_button(self, draw: ImageDraw, text: str, position: Tuple[int, int], 
                     font: ImageFont.FreeTypeFont, button_style: str, 
                     text_color: Tuple[int, int, int, int], 
                     button_color: Tuple[int, int, int, int],
                     button_params: Optional[Dict] = None) -> Tuple[Any, Tuple[int, int, int, int]]:
        """
        Create a professional button for CTA.
        
        Args:
            draw: ImageDraw object
            text: Button text
            position: Button position (center x, center y)
            font: Font to use
            button_style: Button style name
            text_color: Text color
            button_color: Button color
            button_params: Additional button parameters
            
        Returns:
            Tuple of (modified draw object, button bounds)
        """
        x, y = position
        params = button_params or {}
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Calculate button size with padding
        padding_x = params.get('padding_x', 20)
        padding_y = params.get('padding_y', 12)
        button_width = text_width + (padding_x * 2)
        button_height = text_height + (padding_y * 2)
        
        # Center the button
        button_left = x - button_width // 2
        button_top = y - button_height // 2
        
        # Define button coordinates
        button_bounds = [
            button_left, 
            button_top, 
            button_left + button_width, 
            button_top + button_height
        ]
        
        # Apply button style
        if button_style == "rounded":
            # Premium rounded button
            self._draw_rounded_button(
                draw, 
                button_bounds, 
                text, 
                font, 
                text_color, 
                button_color, 
                params
            )
        
        elif button_style == "minimal_line":
            # Minimal button with just borders
            self._draw_minimal_line_button(
                draw, 
                button_bounds, 
                text, 
                font, 
                text_color, 
                button_color, 
                params
            )
            
        elif button_style == "glass":
            # Glass effect button
            self._draw_glass_button(
                draw, 
                button_bounds, 
                text, 
                font, 
                text_color, 
                button_color, 
                params
            )
            
        elif button_style == "gradient":
            # Gradient button
            self._draw_gradient_button(
                draw, 
                button_bounds, 
                text, 
                font, 
                text_color, 
                button_color, 
                params
            )
            
        elif button_style == "pill":
            # Pill-shaped button (fully rounded)
            self._draw_pill_button(
                draw, 
                button_bounds, 
                text, 
                font, 
                text_color, 
                button_color, 
                params
            )
            
        else:
            # Default flat button
            self._draw_flat_button(
                draw, 
                button_bounds, 
                text, 
                font, 
                text_color, 
                button_color, 
                params
            )
            
        # Return the draw object and button bounds
        return draw, tuple(button_bounds)
    
    def _get_text_dimensions(self, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
        """Get dimensions of text with given font."""
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
    
    def _apply_premium_gradient_effect(self, draw, text, position, font, text_color, params=None):
        """
        Apply premium gradient text effect with enhanced quality.
        
        This effect creates a sophisticated gradient text treatment by rendering multiple
        copies of the text with varying opacity, creating a smooth professional gradient.
        """
        x, y = position
        params = params or {}
        
        # Determine gradient direction
        direction = params.get('direction', 'vertical')
        start_opacity = params.get('start_opacity', 1.0)
        end_opacity = params.get('end_opacity', 0.7)
        shadow_opacity = params.get('shadow_opacity', 0.5)
        shadow_offset = params.get('shadow_offset', 2)
        gradient_steps = params.get('steps', 10)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate transparent image for gradient effect
        gradient_img = Image.new('RGBA', (text_width * 3, text_height * 3), (0, 0, 0, 0))
        gradient_draw = ImageDraw.Draw(gradient_img)
        
        # Calculate center position
        center_x = text_width * 3 // 2
        center_y = text_height * 3 // 2
        
        # Draw subtle shadow for depth
        shadow_color = (0, 0, 0, int(255 * shadow_opacity))
        gradient_draw.text((center_x + shadow_offset, center_y + shadow_offset), text, font=font, fill=shadow_color)
        
        # Get base text color components
        r, g, b, a = text_color
        
        # Draw text in multiple steps with decreasing opacity for gradient effect
        for i in range(gradient_steps):
            step_ratio = i / (gradient_steps - 1)
            opacity = start_opacity - (start_opacity - end_opacity) * step_ratio
            alpha = int(a * opacity)
            
            if direction == 'vertical':
                # Vertical gradient (top to bottom)
                offset_y = int(text_height * step_ratio * 0.2)
                gradient_draw.text((center_x, center_y + offset_y), text, font=font, fill=(r, g, b, alpha))
            
            elif direction == 'horizontal':
                # Horizontal gradient (left to right)
                offset_x = int(text_width * step_ratio * 0.2)
                gradient_draw.text((center_x + offset_x, center_y), text, font=font, fill=(r, g, b, alpha))
            
            elif direction == 'diagonal':
                # Diagonal gradient
                offset_x = int(text_width * step_ratio * 0.15)
                offset_y = int(text_height * step_ratio * 0.15)
                gradient_draw.text((center_x + offset_x, center_y + offset_y), text, font=font, fill=(r, g, b, alpha))
            
            else:
                # Radial gradient (center to edge)
                gradient_draw.text((center_x, center_y), text, font=font, fill=(r, g, b, alpha))
        
        # Draw the main text on top
        gradient_draw.text((center_x, center_y), text, font=font, fill=text_color)
        
        # Apply subtle blur for smoother effect
        gradient_img = gradient_img.filter(ImageFilter.GaussianBlur(0.5))
        
        # Calculate the position to paste the gradient image onto the original
        paste_x = x - center_x + text_width
        paste_y = y - center_y + text_height
        
        # Draw the gradient image onto the original
        draw._image.paste(gradient_img, (paste_x, paste_y), gradient_img)
    
    def _apply_luxury_metallic_effect(self, draw, text, position, font, text_color, accent_color=None, params=None):
        """
        Apply a luxury metallic effect ideal for premium brands.
        
        This creates a sophisticated metallic appearance with highlights, shadows, and
        subtle reflections that mimic the look of metal lettering.
        """
        x, y = position
        params = params or {}
        
        accent_color = accent_color or (255, 215, 0, 200)  # Default gold accent if none provided
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate image for metallic effect
        metal_img = Image.new('RGBA', (text_width * 3, text_height * 3), (0, 0, 0, 0))
        metal_draw = ImageDraw.Draw(metal_img)
        
        # Calculate center position
        center_x = text_width * 3 // 2
        center_y = text_height * 3 // 2
        
        # Draw shadow for depth
        shadow_color = (0, 0, 0, 150)
        shadow_offset = params.get('shadow_offset', 3)
        metal_draw.text((center_x + shadow_offset, center_y + shadow_offset), text, font=font, fill=shadow_color)
        
        # Base metal color (often silver or gold)
        r, g, b, a = text_color
        
        # Draw multiple layers for metallic effect
        # 1. Draw dark base
        base_color = (r//2, g//2, b//2, a)
        metal_draw.text((center_x, center_y), text, font=font, fill=base_color)
        
        # 2. Draw lighter shade slightly offset for edge highlight
        highlight_color = (min(r + 40, 255), min(g + 40, 255), min(b + 40, 255), a)
        metal_draw.text((center_x - 1, center_y - 1), text, font=font, fill=highlight_color)
        
        # 3. Draw accent color as sheen in middle
        ar, ag, ab, aa = accent_color
        sheen_color = (ar, ag, ab, aa // 2)
        metal_draw.text((center_x, center_y), text, font=font, fill=sheen_color)
        
        # 4. Draw main text on top
        metal_draw.text((center_x, center_y), text, font=font, fill=text_color)
        
        # 5. Add top edge highlight
        edge_highlight = (min(r + 80, 255), min(g + 80, 255), min(b + 80, 255), a // 2)
        metal_draw.text((center_x, center_y - 2), text, font=font, fill=edge_highlight)
        
        # Apply very subtle blur for a smoother finish
        metal_img = metal_img.filter(ImageFilter.GaussianBlur(0.3))
        
        # Calculate the position to paste the metallic image
        paste_x = x - center_x + text_width
        paste_y = y - center_y + text_height
        
        # Draw the metallic image onto the original
        draw._image.paste(metal_img, (paste_x, paste_y), metal_img)
    
    def _apply_elegant_shadow_effect(self, draw, text, position, font, text_color, params=None):
        """
        Apply elegant shadow effect with perfect balance and subtle depth.
        
        Creates a sophisticated shadow that gives depth without overwhelming the text.
        """
        x, y = position
        params = params or {}
        
        # Set shadow parameters
        shadow_offset = params.get('shadow_offset', 2)
        shadow_alpha = params.get('shadow_alpha', 120)
        shadow_blur = params.get('shadow_blur', 2)
        
        # Create a separate image for the shadow
        # Make it larger to accommodate the blur
        padding = max(30, shadow_offset + shadow_blur * 3)
        text_width, text_height = self._get_text_dimensions(text, font)
        
        shadow_img = Image.new('RGBA', (
            text_width + padding * 2, 
            text_height + padding * 2
        ), (0, 0, 0, 0))
        
        shadow_draw = ImageDraw.Draw(shadow_img)
        
        # Draw shadow
        shadow_color = (0, 0, 0, shadow_alpha)
        shadow_draw.text((padding, padding), text, font=font, fill=shadow_color)
        
        # Apply Gaussian blur to shadow
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(shadow_blur))
        
        # Calculate the position to paste the shadow
        paste_x = x - padding + shadow_offset
        paste_y = y - padding + shadow_offset
        
        # Paste shadow
        draw._image.paste(shadow_img, (paste_x, paste_y), shadow_img)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)
    
    def _apply_subtle_glow_effect(self, draw, text, position, font, text_color, glow_color=None, params=None):
        """
        Apply a subtle professional glow effect.
        
        Creates a refined halo around text that adds emphasis without looking overdone.
        """
        x, y = position
        params = params or {}
        
        # Set glow parameters
        glow_color = glow_color or (255, 255, 255, 100)
        glow_radius = params.get('glow_radius', 5)
        glow_iterations = params.get('iterations', 3)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate image for the glow effect
        # Make it larger to accommodate the glow
        padding = glow_radius * 3
        glow_img = Image.new('RGBA', (
            text_width + padding * 2, 
            text_height + padding * 2
        ), (0, 0, 0, 0))
        
        glow_draw = ImageDraw.Draw(glow_img)
        
        # Extract glow color components
        gr, gg, gb, ga = glow_color
        
        # Draw progressively lighter glows with decreasing opacity
        for i in range(glow_iterations, 0, -1):
            alpha = int(ga * (i / glow_iterations))
            current_color = (gr, gg, gb, alpha)
            
            # Draw text multiple times with different offsets for omnidirectional glow
            for offset_x in range(-1, 2):
                for offset_y in range(-1, 2):
                    if offset_x == 0 and offset_y == 0:
                        continue
                    
                    glow_draw.text(
                        (padding + offset_x * i, padding + offset_y * i),
                        text, 
                        font=font, 
                        fill=current_color
                    )
        
        # Apply Gaussian blur for smooth glow
        glow_img = glow_img.filter(ImageFilter.GaussianBlur(glow_radius / 2))
        
        # Calculate the position to paste the glow
        paste_x = x - padding
        paste_y = y - padding
        
        # Paste glow layer
        draw._image.paste(glow_img, (paste_x, paste_y), glow_img)
        
        # Draw main text on top
        draw.text((x, y), text, font=font, fill=text_color)
    
    def _apply_layered_gradient_effect(self, draw, text, position, font, text_color, accent_color=None, params=None):
        """
        Apply a sophisticated layered gradient effect.
        
        Creates a complex gradient with multiple layers for enhanced depth and visual interest.
        """
        x, y = position
        params = params or {}
        
        # Set gradient parameters
        accent_color = accent_color or text_color
        direction = params.get('direction', 'vertical')
        layers = params.get('layers', 3)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate image for the gradient effect
        padding = 20
        gradient_img = Image.new('RGBA', (
            text_width + padding * 2, 
            text_height + padding * 2
        ), (0, 0, 0, 0))
        
        gradient_draw = ImageDraw.Draw(gradient_img)
        
        # Extract color components
        r1, g1, b1, a1 = text_color
        r2, g2, b2, a2 = accent_color
        
        # Add shadow for depth
        shadow_color = (0, 0, 0, 100)
        gradient_draw.text((padding + 2, padding + 2), text, font=font, fill=shadow_color)
        
        # Create gradient layers
        for i in range(layers):
            # Calculate blend factor for this layer
            blend = i / (layers - 1) if layers > 1 else 0
            
            # Interpolate colors
            r = int(r1 * (1 - blend) + r2 * blend)
            g = int(g1 * (1 - blend) + r2 * blend)
            b = int(b1 * (1 - blend) + r2 * blend)
            a = int(a1 * (1 - blend) + r2 * blend)
            
            layer_color = (r, g, b, a)
            
            # Calculate offset based on direction
            if direction == 'vertical':
                offset_y = int(text_height * blend * 0.2)
                offset_x = 0
            elif direction == 'horizontal':
                offset_x = int(text_width * blend * 0.2)
                offset_y = 0
            elif direction == 'diagonal':
                offset_x = int(text_width * blend * 0.1)
                offset_y = int(text_height * blend * 0.1)
            else:
                offset_x = 0
                offset_y = 0
                
            # Draw layer
            gradient_draw.text(
                (padding + offset_x, padding + offset_y), 
                text, 
                font=font, 
                fill=layer_color
            )
        
        # Apply subtle blur for smoother effect
        gradient_img = gradient_img.filter(ImageFilter.GaussianBlur(0.5))
        
        # Calculate the position to paste the gradient
        paste_x = x - padding
        paste_y = y - padding
        
        # Paste gradient
        draw._image.paste(gradient_img, (paste_x, paste_y), gradient_img)
        
        # Draw final text on top for sharpness
        draw.text((x, y), text, font=font, fill=text_color)
    
    def _apply_premium_outline_effect(self, draw, text, position, font, text_color, outline_color=None, params=None):
        """
        Apply premium outline effect with subtle inner glow.
        
        Creates a sophisticated outline with perfect balance and inner lighting.
        """
        x, y = position
        params = params or {}
        
        # Set outline parameters
        outline_color = outline_color or (255, 255, 255, 200)
        thickness = params.get('thickness', 1)
        glow_intensity = params.get('glow_intensity', 0.5)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate image for the outline effect
        padding = max(20, thickness * 4)
        outline_img = Image.new('RGBA', (
            text_width + padding * 2, 
            text_height + padding * 2
        ), (0, 0, 0, 0))
        
        outline_draw = ImageDraw.Draw(outline_img)
        
        # Extract outline color components
        or_, og, ob, oa = outline_color
        
        # Draw outline by drawing the text multiple times with offsets
        directions = [
            (-1, -1), (0, -1), (1, -1),
            (-1,  0),          (1,  0),
            (-1,  1), (0,  1), (1,  1)
        ]
        
        for _ in range(thickness):
            for dx, dy in directions:
                outline_draw.text(
                    (padding + dx, padding + dy), 
                    text, 
                    font=font, 
                    fill=outline_color
                )
        
        # Create inner glow by drawing slightly brighter text underneath
        inner_glow_color = (
            min(255, int(or_ * 1.2)), 
            min(255, int(og * 1.2)), 
            min(255, int(ob * 1.2)), 
            int(oa * glow_intensity)
        )
        
        outline_draw.text(
            (padding, padding), 
            text, 
            font=font, 
            fill=inner_glow_color
        )
        
        # Draw main text
        outline_draw.text(
            (padding, padding), 
            text, 
            font=font, 
            fill=text_color
        )
        
        # Calculate the position to paste the outline
        paste_x = x - padding
        paste_y = y - padding
        
        # Paste outline
        draw._image.paste(outline_img, (paste_x, paste_y), outline_img)
    
    def _apply_glass_effect(self, draw, text, position, font, text_color, image, params=None):
        """
        Apply a modern glass effect with reflection and translucency.
        
        Creates a sophisticated glass-like appearance for text with background blur
        and subtle reflections.
        """
        x, y = position
        params = params or {}
        
        # Set glass effect parameters
        blur_radius = params.get('blur_radius', 10)
        opacity = params.get('opacity', 0.8)
        reflection_opacity = params.get('reflection_opacity', 0.3)
        padding = params.get('padding', 15)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Calculate the background rectangle area
        bg_left = x - padding
        bg_top = y - padding
        bg_right = x + text_width + padding
        bg_bottom = y + text_height + padding
        
        # Create a mask for the glass area
        mask = Image.new('L', image.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(
            [bg_left, bg_top, bg_right, bg_bottom],
            radius=10,
            fill=255
        )
        
        # Create a copy of the portion of the background image
        bg_crop = image.crop((bg_left, bg_top, bg_right, bg_bottom))
        
        # Apply blur to simulate glass effect
        blurred_bg = bg_crop.filter(ImageFilter.GaussianBlur(blur_radius))
        
        # Create a new image for the glass effect
        glass = Image.new('RGBA', (bg_right - bg_left, bg_bottom - bg_top), (255, 255, 255, 0))
        
        # Add the blurred background to the glass image
        glass.paste(blurred_bg, (0, 0))
        
        # Adjust opacity to create translucency
        glass_overlay = Image.new('RGBA', glass.size, (255, 255, 255, int(255 * opacity)))
        glass = Image.alpha_composite(glass, glass_overlay)
        
        # Add subtle highlight gradient for reflection
        highlight = Image.new('RGBA', glass.size, (0, 0, 0, 0))
        highlight_draw = ImageDraw.Draw(highlight)
        
        # Create gradient for reflection
        for i in range(glass.height // 3):
            alpha = int(255 * reflection_opacity * (1 - i / (glass.height // 3)))
            highlight_draw.line(
                [(0, i), (glass.width, i)],
                fill=(255, 255, 255, alpha)
            )
        
        # Add highlight to glass
        glass = Image.alpha_composite(glass, highlight)
        
        # Paste the glass effect into the main image
        draw._image.paste(glass, (bg_left, bg_top), mask.crop((bg_left, bg_top, bg_right, bg_bottom)))
        
        # Draw text on top
        draw.text((x, y), text, font=font, fill=text_color)
    
    def _apply_subtle_background(self, draw, text, position, font, text_color, text_width, text_height, brightness_map=None, params=None):
        """
        Apply enhanced subtle background with refined aesthetics.
        
        Creates a sophisticated background for text with optimal opacity and blur.
        """
        x, y = position
        params = params or {}
        
        # Set background parameters
        bg_padding = params.get('padding', 15)
        corner_radius = params.get('radius', 8)
        
        # Determine background color based on brightness and params
        bg_color = params.get('bg_color', None)
        bg_opacity = params.get('opacity', 0.7)
        
        if not bg_color:
            if brightness_map and brightness_map.get('overall', 0.5) > 0.5:
                # For bright images, use dark background
                bg_color = (0, 0, 0, int(255 * bg_opacity))
            else:
                # For dark images, use light background
                bg_color = (255, 255, 255, int(255 * bg_opacity))
        elif len(bg_color) == 3:
            # If RGB provided without alpha, add alpha
            bg_color = (*bg_color, int(255 * bg_opacity))
        
        # Create a separate image for the background with rounded corners
        bg_img = Image.new('RGBA', (
            text_width + bg_padding * 2,
            text_height + bg_padding * 2
        ), (0, 0, 0, 0))
        
        bg_draw = ImageDraw.Draw(bg_img)
        
        # Draw rounded rectangle background
        bg_draw.rounded_rectangle(
            [(0, 0), (bg_img.width, bg_img.height)],
            radius=corner_radius,
            fill=bg_color
        )
        
        # Apply blur to edges if specified
        if params.get('blur', 0) > 0:
            bg_img = bg_img.filter(ImageFilter.GaussianBlur(params.get('blur')))
        
        # Add subtle gradient overlay for depth if specified
        if params.get('gradient', False):
            gradient = Image.new('RGBA', bg_img.size, (0, 0, 0, 0))
            gradient_draw = ImageDraw.Draw(gradient)
            
            direction = params.get('gradient_direction', 'vertical')
            start_opacity = params.get('gradient_start_opacity', 0.05)
            end_opacity = params.get('gradient_end_opacity', 0.2)
            
            if direction == 'vertical':
                for i in range(bg_img.height):
                    alpha = int(255 * (start_opacity + (end_opacity - start_opacity) * i / bg_img.height))
                    gradient_draw.line([(0, i), (bg_img.width, i)], fill=(0, 0, 0, alpha))
            else:
                for i in range(bg_img.width):
                    alpha = int(255 * (start_opacity + (end_opacity - start_opacity) * i / bg_img.width))
                    gradient_draw.line([(i, 0), (i, bg_img.height)], fill=(0, 0, 0, alpha))
            
            bg_img = Image.alpha_composite(bg_img, gradient)
        
        # Calculate the position to paste the background
        paste_x = x - bg_padding
        paste_y = y - bg_padding
        
        # Paste background
        draw._image.paste(bg_img, (paste_x, paste_y), bg_img)
        
        # Draw text
        draw.text((x, y), text, font=font, fill=text_color)
    
    def _apply_minimal_elegant(self, draw, text, position, font, text_color, params=None):
        """
        Apply minimal elegant text treatment with perfect spacing and subtle effects.
        
        Creates a refined, understated text style with perfect readability.
        """
        x, y = position
        params = params or {}
        
        # Set letter spacing parameters
        letter_spacing = params.get('letter_spacing', 0.05)
        shadow_enabled = params.get('shadow_enabled', True)
        
        # Apply minimal letter spacing if needed
        if letter_spacing > 0:
            spaced_text = self._apply_letter_spacing(text, letter_spacing)
            
            # Apply subtle shadow if enabled
            if shadow_enabled:
                shadow_color = (0, 0, 0, 60)
                shadow_offset = 1
                draw.text((x + shadow_offset, y + shadow_offset), spaced_text, font=font, fill=shadow_color)
            
            # Draw main text
            draw.text((x, y), spaced_text, font=font, fill=text_color)
        else:
            # Apply subtle shadow if enabled
            if shadow_enabled:
                shadow_color = (0, 0, 0, 60)
                shadow_offset = 1
                draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
            
            # Draw main text
            draw.text((x, y), text, font=font, fill=text_color)
    
    def _apply_vibrant_overlay(self, draw, text, position, font, text_color, accent_color=None, params=None):
        """
        Apply vibrant semi-transparent overlay with text.
        
        Creates a colorful backdrop for text with modern, vibrant appearance.
        """
        x, y = position
        params = params or {}
        
        # Set overlay parameters
        accent_color = accent_color or (41, 128, 185, 200)  # Default blue accent
        padding = params.get('padding', 15)
        opacity = params.get('opacity', 0.8)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Calculate overlay bounds
        overlay_left = x - padding
        overlay_top = y - padding
        overlay_right = x + text_width + padding
        overlay_bottom = y + text_height + padding
        
        # Extract accent color components and apply opacity
        ar, ag, ab, aa = accent_color
        overlay_color = (ar, ag, ab, int(aa * opacity))
        
        # Draw accent rectangle with rounded corners
        draw.rounded_rectangle(
            [(overlay_left, overlay_top), (overlay_right, overlay_bottom)],
            radius=10,
            fill=overlay_color
        )
        
        # Draw text
        draw.text((x, y), text, font=font, fill=text_color)
    
    def _apply_gradient_effect(self, draw, text, position, font, text_color, params=None):
        """
        Apply improved gradient text effect with better control.
        
        Creates a professional gradient effect for text with customizable parameters.
        """
        x, y = position
        params = params or {}
        
        # Get shadow parameters
        shadow_offset = params.get('shadow_offset', 2)
        shadow_color = params.get('shadow_color', (0, 0, 0, 100))
        
        # Create shadow layer
        for offset in range(1, shadow_offset + 1):
            draw.text(
                (x + offset, y + offset), 
                text, 
                font=font, 
                fill=shadow_color
            )
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)
    
    def _apply_outline_effect(self, draw, text, position, font, text_color, outline_color=None, params=None):
        """
        Apply enhanced outline effect with better quality.
        
        Creates a clean outline around text with configurable thickness.
        """
        x, y = position
        params = params or {}
        
        # Set outline parameters
        outline_color = outline_color or (0, 0, 0, 200)
        thickness = params.get('thickness', 1)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate image for the outline
        outline_img = Image.new('RGBA', (
            text_width + thickness * 8,
            text_height + thickness * 8
        ), (0, 0, 0, 0))
        
        outline_draw = ImageDraw.Draw(outline_img)
        
        # Calculate center position
        center_x = outline_img.width // 2
        center_y = outline_img.height // 2
        
        # Draw outline by offsetting text in all directions
        for offset_x in range(-thickness, thickness + 1):
            for offset_y in range(-thickness, thickness + 1):
                # Skip the center position (this will be the actual text)
                if offset_x == 0 and offset_y == 0:
                    continue
                
                outline_draw.text(
                    (center_x + offset_x, center_y + offset_y),
                    text,
                    font=font,
                    fill=outline_color
                )
        
        # Draw the main text in the center
        outline_draw.text(
            (center_x, center_y),
            text,
            font=font,
            fill=text_color
        )
        
        # Calculate paste position
        paste_x = x - center_x + text_width // 2
        paste_y = y - center_y + text_height // 2
        
        # Paste outline image
        draw._image.paste(outline_img, (paste_x, paste_y), outline_img)
    
    def _apply_glow_effect(self, draw, text, position, font, text_color, glow_color=None, params=None):
        """
        Apply enhanced glow effect with better quality.
        
        Creates a subtle glow around text for emphasis and improved readability.
        """
        x, y = position
        params = params or {}
        
        # Set glow parameters
        glow_color = glow_color or (255, 255, 255, 100)
        glow_radius = params.get('radius', 5)
        intensity = params.get('intensity', 0.7)
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate image for glow effect
        glow_img = Image.new('RGBA', (
            text_width + glow_radius * 4,
            text_height + glow_radius * 4
        ), (0, 0, 0, 0))
        
        glow_draw = ImageDraw.Draw(glow_img)
        
        # Calculate center position
        center_x = glow_img.width // 2
        center_y = glow_img.height // 2
        
        # Extract glow color and adjust intensity
        gr, gg, gb, ga = glow_color
        glow_color_adjusted = (gr, gg, gb, int(ga * intensity))
        
        # Draw text with glow color
        glow_draw.text(
            (center_x, center_y),
            text,
            font=font,
            fill=glow_color_adjusted
        )
        
        # Apply blur for glow effect
        glow_img = glow_img.filter(ImageFilter.GaussianBlur(glow_radius))
        
        # Calculate paste position
        paste_x = x - center_x + text_width // 2
        paste_y = y - center_y + text_height // 2
        
        # Paste glow image
        draw._image.paste(glow_img, (paste_x, paste_y), glow_img)
        
        # Draw main text on top for sharpness
        draw.text((x, y), text, font=font, fill=text_color)
    
    def _apply_shadow_effect(self, draw, text, position, font, text_color, params=None):
        """
        Apply enhanced shadow effect with better quality.
        
        Creates a realistic shadow under text with configurable parameters.
        """
        x, y = position
        params = params or {}
        
        # Get shadow parameters from default effects if not specified
        shadow_params = self.default_effects_params['shadow']
        
        # Update with custom params if provided
        if params:
            shadow_params.update({k: v for k, v in params.items() if k in shadow_params})
        
        # Extract parameters
        offset = shadow_params['offset']
        blur_radius = shadow_params['blur_radius']
        shadow_color = shadow_params['color']
        
        # Get text dimensions
        text_width, text_height = self._get_text_dimensions(text, font)
        
        # Create a separate image for shadow
        # Make it larger to accommodate blur
        padding = max(20, offset + blur_radius * 3)
        shadow_img = Image.new('RGBA', (
            text_width + padding * 2,
            text_height + padding * 2
        ), (0, 0, 0, 0))
        
        shadow_draw = ImageDraw.Draw(shadow_img)
        
        # Draw shadow text
        shadow_draw.text(
            (padding, padding),
            text,
            font=font,
            fill=shadow_color
        )
        
        # Apply blur
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(blur_radius))
        
        # Calculate paste position for shadow
        paste_x = x - padding + offset
        paste_y = y - padding + offset
        
        # Paste shadow
        draw._image.paste(shadow_img, (paste_x, paste_y), shadow_img)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)
    
    def _draw_rounded_button(self, draw, bounds, text, font, text_color, button_color, params=None):
        """Draw a premium rounded button with sophisticated lighting effects."""
        params = params or {}
        
        # Unpack bounds
        left, top, right, bottom = bounds
        
        # Get parameters
        radius = params.get('radius', min(15, (bottom - top) // 3))
        highlight_opacity = params.get('highlight_opacity', 0.3)
        shadow_opacity = params.get('shadow_opacity', 0.4)
        
        # Extract button color components
        br, bg, bb, ba = button_color
        
        # Draw outer shadow for depth
        shadow_color = (0, 0, 0, int(100 * shadow_opacity))
        draw.rounded_rectangle(
            [left + 2, top + 2, right + 2, bottom + 2],
            radius=radius,
            fill=shadow_color
        )
        
        # Draw main button
        draw.rounded_rectangle(
            [left, top, right, bottom],
            radius=radius,
            fill=button_color
        )
        
        # Draw highlight at top for 3D effect
        highlight_height = int((bottom - top) * 0.4)
        highlight_color = (255, 255, 255, int(255 * highlight_opacity))
        
        # Use polygon for highlight to create a subtle gradient effect
        draw.rounded_rectangle(
            [left + 1, top + 1, right - 1, top + highlight_height],
            radius=radius - 1,
            fill=highlight_color
        )
        
        # Calculate text position for centering
        text_width, text_height = self._get_text_dimensions(text, font)
        text_x = left + (right - left - text_width) // 2
        text_y = top + (bottom - top - text_height) // 2
        
        # Draw text shadow
        draw.text((text_x + 1, text_y + 1), text, font=font, fill=(0, 0, 0, 100))
        
        # Draw text
        draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    def _draw_minimal_line_button(self, draw, bounds, text, font, text_color, button_color, params=None):
        """Draw a minimal button with just borders."""
        params = params or {}
        
        # Unpack bounds
        left, top, right, bottom = bounds
        
        # Get parameters
        border_width = params.get('border_width', 1)
        radius = params.get('radius', min(8, (bottom - top) // 4))
        
        # Draw border
        draw.rounded_rectangle(
            [left, top, right, bottom],
            radius=radius,
            outline=button_color,
            width=border_width
        )
        
        # Calculate text position for centering
        text_width, text_height = self._get_text_dimensions(text, font)
        text_x = left + (right - left - text_width) // 2
        text_y = top + (bottom - top - text_height) // 2
        
        # Draw text
        draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    def _draw_glass_button(self, draw, bounds, text, font, text_color, button_color, params=None):
        """Draw a glass effect button with translucency and reflections."""
        params = params or {}
        
        # Unpack bounds
        left, top, right, bottom = bounds
        width = right - left
        height = bottom - top
        
        # Get parameters
        radius = params.get('radius', min(10, height // 3))
        opacity = params.get('opacity', 0.6)
        
        # Create a separate image for the glass button
        button_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        button_draw = ImageDraw.Draw(button_img)
        
        # Extract button color
        br, bg, bb, ba = button_color
        
        # Draw the base color with adjusted opacity
        base_color = (br, bg, bb, int(ba * opacity))
        button_draw.rounded_rectangle(
            [(0, 0), (width, height)],
            radius=radius,
            fill=base_color
        )
        
        # Add top highlight (glass reflection)
        highlight_height = height // 3
        
        # Create gradient for reflection
        for i in range(highlight_height):
            alpha = int(100 * (1 - i / highlight_height))
            highlight_color = (255, 255, 255, alpha)
            button_draw.rounded_rectangle(
                [(1, 1), (width - 1, 1 + i)],
                radius=radius - 1,
                fill=highlight_color
            )
        
        # Add bottom shadow for depth
        shadow_height = height // 4
        shadow_top = height - shadow_height
        
        # Create gradient for shadow
        for i in range(shadow_height):
            alpha = int(50 * i / shadow_height)
            shadow_color = (0, 0, 0, alpha)
            button_draw.rounded_rectangle(
                [(1, shadow_top + i), (width - 1, shadow_top + i + 1)],
                radius=radius - 1,
                fill=shadow_color
            )
        
        # Paste button into main image
        draw._image.paste(button_img, (left, top), button_img)
        
        # Calculate text position for centering
        text_width, text_height = self._get_text_dimensions(text, font)
        text_x = left + (width - text_width) // 2
        text_y = top + (height - text_height) // 2
        
        # Draw text with subtle shadow
        draw.text((text_x + 1, text_y + 1), text, font=font, fill=(0, 0, 0, 70))
        draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    def _draw_gradient_button(self, draw, bounds, text, font, text_color, button_color, params=None):
        """Draw a button with gradient fill."""
        params = params or {}
        
        # Unpack bounds
        left, top, right, bottom = bounds
        width = right - left
        height = bottom - top
        
        # Get parameters
        radius = params.get('radius', min(10, height // 3))
        direction = params.get('direction', 'vertical')
        
        # Create separate image for gradient button
        button_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        button_draw = ImageDraw.Draw(button_img)
        
        # Extract button color
        br, bg, bb, ba = button_color
        
        # Calculate gradient colors
        start_color = button_color
        if params.get('end_color'):
            end_color = params.get('end_color')
        else:
            # Create darker variant of button color for end
            darkness_factor = 0.7
            end_color = (
                int(br * darkness_factor),
                int(bg * darkness_factor),
                int(bb * darkness_factor),
                ba
            )
        
        # Draw gradient
        if direction == 'vertical':
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
        
        # Add subtle highlight for 3D effect
        highlight_height = height // 4
        highlight = Image.new('RGBA', (width, highlight_height), (0, 0, 0, 0))
        highlight_draw = ImageDraw.Draw(highlight)
        
        for y in range(highlight_height):
            alpha = int(50 * (1 - y / highlight_height))
            highlight_draw.line([(0, y), (width, y)], fill=(255, 255, 255, alpha))
        
        # Create mask for highlight rounded corners
        highlight_mask = Image.new('L', (width, highlight_height), 0)
        highlight_mask_draw = ImageDraw.Draw(highlight_mask)
        highlight_mask_draw.rounded_rectangle(
            [(0, 0), (width, highlight_height * 2)],
            radius=radius,
            fill=255
        )
        
        # Apply mask to highlight
        highlight.putalpha(highlight_mask)
        
        # Composite highlight onto button
        button_img = Image.alpha_composite(button_img, highlight)
        
        # Paste button into main image
        draw._image.paste(button_img, (left, top), button_img)
        
        # Calculate text position for centering
        text_width, text_height = self._get_text_dimensions(text, font)
        text_x = left + (width - text_width) // 2
        text_y = top + (height - text_height) // 2
        
        # Draw text with subtle shadow
        draw.text((text_x + 1, text_y + 1), text, font=font, fill=(0, 0, 0, 70))
        draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    def _draw_pill_button(self, draw, bounds, text, font, text_color, button_color, params=None):
        """Draw a pill-shaped button (fully rounded ends)."""
        params = params or {}
        
        # Unpack bounds
        left, top, right, bottom = bounds
        width = right - left
        height = bottom - top
        
        # Pill buttons have fully rounded ends (radius = height/2)
        radius = height // 2
        
        # Draw button with shadow
        shadow_color = (0, 0, 0, 80)
        draw.rounded_rectangle(
            [left + 1, top + 1, right + 1, bottom + 1],
            radius=radius,
            fill=shadow_color
        )
        
        # Draw main button
        draw.rounded_rectangle(
            [left, top, right, bottom],
            radius=radius,
            fill=button_color
        )
        
        # Add highlight for 3D effect
        highlight_height = height // 2
        highlight_color = (255, 255, 255, 60)
        draw.rounded_rectangle(
            [left + 1, top + 1, right - 1, top + highlight_height],
            radius=radius - 1,
            fill=highlight_color
        )
        
        # Calculate text position for centering
        text_width, text_height = self._get_text_dimensions(text, font)
        text_x = left + (width - text_width) // 2
        text_y = top + (height - text_height) // 2
        
        # Draw text with subtle shadow
        draw.text((text_x + 1, text_y + 1), text, font=font, fill=(0, 0, 0, 70))
        draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    def _draw_flat_button(self, draw, bounds, text, font, text_color, button_color, params=None):
        """Draw a flat button with no 3D effects."""
        params = params or {}
        
        # Unpack bounds
        left, top, right, bottom = bounds
        width = right - left
        height = bottom - top
        
        # Get parameters
        radius = params.get('radius', min(5, height // 6))
        
        # Draw button
        draw.rounded_rectangle(
            [left, top, right, bottom],
            radius=radius,
            fill=button_color
        )
        
        # Calculate text position for centering
        text_width, text_height = self._get_text_dimensions(text, font)
        text_x = left + (width - text_width) // 2
        text_y = top + (height - text_height) // 2
        
        # Draw text
        draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    def _apply_letter_spacing(self, text, spacing_factor):
        """Apply letter spacing to text."""
        if spacing_factor <= 0:
            return text
            
        # Add spaces between characters based on spacing factor
        spaced_text = ""
        space_width = int(spacing_factor * 10)
        
        for char in text:
            spaced_text += char
            if char != ' ':
                spaced_text += ' ' * space_width
                
        return spaced_text