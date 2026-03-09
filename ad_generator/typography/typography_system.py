"""
Professional Typography System for Ad Generation
Orchestrates typography components to create studio-quality ad layouts
"""
import os
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont, ImageFilter
try:
    import numpy as np
    from collections import Counter as _Counter
    _NUMPY_OK = True
except ImportError:
    _NUMPY_OK = False

from .brand_typography import BrandTypographyManager
from .typography_effects import TypographyEffectsEngine
from .layout_engine import TextLayoutEngine
from .font_pairing import FontPairingEngine
from .responsive_scaling import ResponsiveTextScaling
import traceback

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
            self.logger.info(f"Creating typography for {brand_name} in {industry} industry")
        
        # Step 1: Analyze the image for optimal text placement
            self.logger.info("Analyzing image for optimal text placement")
            image_analysis = self.layout_engine.analyze_image(image)
        
        # Step 2: Get typography style based on brand, industry and level
            self.logger.info(f"Getting typography style for {brand_name}, {industry}, {brand_level}")
            typography_style = self.brand_typography.get_typography_style(
            brand_name=brand_name,
            industry=industry,
            brand_level=brand_level,
            style_overrides=style_profile
        )
        
        # Apply any style overrides
            if style_profile:
                typography_style.update(style_profile)
                self.logger.info(f"Applied style overrides: {style_profile}")
        
        # Step 3: Select font pairings based on typography style
            self.logger.info("Selecting font pairings")
            fonts = self.font_pairing.get_font_pairing(
            style=typography_style.get('style', 'modern'),
            brand_name=brand_name,
            text_elements=text_elements
        )
        
        # Log font selection results
            font_results = {k: (v is not None) for k, v in fonts.items()}
            self.logger.info(f"Font selection results: {font_results}")
        
        # Step 4: Determine optimal text sizes based on image dimensions
            self.logger.info("Calculating optimal text sizes")
            text_sizes = self.responsive_scaling.calculate_text_sizes(
            image_size=image.size,
            text_elements=text_elements,
            typography_style=typography_style
        )
        
        # Step 5: Calculate text positions based on layout strategy
            self.logger.info("Calculating text positions")
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
            self.logger.info("Generating color scheme")
            color_scheme = self.brand_typography.generate_color_scheme(
            image=image,
            typography_style=typography_style,
            brand_name=brand_name
        )
        
        # Step 8: Apply text elements with proper styling and effects
            self.logger.info("Applying text elements with effects")
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
            self.logger.info("Compositing text overlay with original image")
            result_image = Image.alpha_composite(image.convert('RGBA'), text_overlay)
        
            return result_image
        
        except Exception as e:
            self.logger.error(f"Error creating typography: {str(e)}")
            self.logger.error(traceback.format_exc())
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
    
    # ──────────────────────────────────────────────────────────────────────────
    # apply_typography — professional rendering pipeline
    # ──────────────────────────────────────────────────────────────────────────

    def apply_typography(self, image: Image.Image, ad_copy: Dict[str, str],
                         layout: Optional[Dict[str, Any]] = None) -> Image.Image:
        """
        Apply professional typography: image-aware colors, weight hierarchy,
        tracked headlines, zone-scrim overlays, and polished CTA buttons.
        """
        if not ad_copy:
            raise ValueError("ad_copy must be a non-empty dict")

        layout = layout or {}

        # ── Parse layout params ──────────────────────────────────────────────
        style         = layout.get('style',            'top_bottom')
        overlay_type  = layout.get('overlay_type',     'gradient_top_bottom')
        opacity       = float(layout.get('overlay_opacity', 0.7))
        headline_pos  = layout.get('headline_position','top_center')
        headline_size = layout.get('headline_size',    'large')
        cta_style     = layout.get('cta_style',        'pill_button')
        show_body_pref = layout.get('show_body_text',  True)
        mood          = layout.get('mood',             '')

        width, height = image.size

        # ── 1. Extract palette from the DALL-E image ─────────────────────────
        palette = self._extract_palette(image)

        # ── 2. Smart color selection (image-derived, not always white) ────────
        text_color   = self._choose_text_color(palette, layout)
        accent_color = self._choose_accent_color(palette, layout)
        is_dark      = palette['is_dark_image']

        # ── 3. Dramatic font-size hierarchy (≥2:1 headline:sub ratio) ─────────
        if headline_size == 'xlarge':
            h_px = max(64, width // 8)
            s_px = max(24, width // 28)
            b_px = max(18, width // 36)
            c_px = max(30, width // 24)
        elif headline_size == 'medium':
            h_px = max(38, width // 16)
            s_px = max(20, width // 30)
            b_px = max(16, width // 38)
            c_px = max(22, width // 26)
        else:  # large (default)
            h_px = max(52, width // 12)
            s_px = max(22, width // 26)
            b_px = max(18, width // 34)
            c_px = max(26, width // 22)

        # ── 4. Load fonts with weight contrast ────────────────────────────────
        fonts = self._load_weight_fonts(h_px, s_px, b_px, c_px)

        # ── 5. Calculate zones ───────────────────────────────────────────────
        zones, alignment, tx_start, tx_w = self._calculate_zones(
            style, headline_pos, width, height
        )

        # ── 6. Headline case transform ────────────────────────────────────────
        hl = ad_copy.get('headline', '').strip()
        playful_signals = ('playful', 'casual', 'fun', 'friendly', 'irreverent')
        is_playful = any(s in mood.lower() for s in playful_signals)
        if hl and not is_playful:
            hl = hl.upper()

        # ── 7. Scrim overlay (only behind text zones, not full image) ─────────
        active_zones = {k: v for k, v in zones.items() if v is not None}
        base = image.convert('RGBA')
        base = self._apply_scrim_to_zones(
            base, active_zones, opacity, overlay_type, accent_color,
            tx_start, tx_w
        )

        # ── 8. Render elements — each composites blurred shadow + text onto base ─
        pad         = max(int(width * 0.05), 24)
        hl_tracking = max(1, h_px // 24)

        if hl and zones.get('headline'):
            base = self._render_text_element(
                base, hl, fonts['headline'], zones['headline'],
                width, tx_w, tx_start, pad, text_color, alignment,
                tracking=hl_tracking, lh_mult=1.20,
                shadow_offset=(4, 4), shadow_blur=8, shadow_opacity=200,
                outline_width=2,
            )

        sh = ad_copy.get('subheadline', '').strip()
        if sh and zones.get('subheadline'):
            sub_c = (text_color[0], text_color[1], text_color[2], min(text_color[3], 220))
            base = self._render_text_element(
                base, sh, fonts['subheadline'], zones['subheadline'],
                width, tx_w, tx_start, pad, sub_c, alignment,
                tracking=0, lh_mult=1.40,
                shadow_offset=(2, 2), shadow_blur=5, shadow_opacity=160,
                outline_width=1,
            )

        if show_body_pref and zones.get('body'):
            body = ad_copy.get('body_text', '').strip()
            if body:
                z_top, z_bot = zones['body']
                if self._should_show_body_text(image, z_top, z_bot):
                    body_c = (text_color[0], text_color[1], text_color[2],
                              min(text_color[3], 200))
                    base = self._render_text_element(
                        base, body, fonts['body'], zones['body'],
                        width, tx_w, tx_start, pad, body_c, alignment,
                        tracking=0, lh_mult=1.45,
                        shadow_offset=(1, 1), shadow_blur=3, shadow_opacity=140,
                        outline_width=0,
                    )

        cta = ad_copy.get('call_to_action', '').strip()
        if cta and zones.get('cta'):
            base = self._render_cta(
                base, cta, fonts['cta'], zones['cta'],
                width, tx_start, tx_w,
                cta_style, text_color, accent_color, alignment,
                is_dark_image=is_dark,
            )

        return base.convert('RGB')

    # ── New image-based renderers (gaussian shadow + outline) ─────────────────

    def _wrap_text_with_font(self, text: str, font: ImageFont.FreeTypeFont,
                              max_width: int) -> List[str]:
        """Wrap text using font metrics — no ImageDraw required."""
        words = text.split()
        lines: List[str] = []
        current = ''
        for word in words:
            candidate = (current + ' ' + word).strip()
            try:
                w = font.getlength(candidate)
            except AttributeError:
                bb = font.getbbox(candidate)
                w  = bb[2] - bb[0]
            if w <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines or [text]

    def _should_show_body_text(self, img: Image.Image,
                                zone_y_start: int, zone_y_end: int) -> bool:
        """Return False if the body zone is too visually busy for small text."""
        if not _NUMPY_OK:
            return True
        try:
            region = img.crop((0, zone_y_start, img.width,
                               min(zone_y_end, img.height)))
            arr      = np.array(region.convert('L'))
            variance = float(np.var(arr))
            return variance < 2000
        except Exception:
            return True

    def _render_text_element(self, img: Image.Image, text: str,
                              font: ImageFont.FreeTypeFont,
                              zone: Optional[Tuple[int, int]],
                              total_w: int, area_w: int, area_left: int,
                              pad: int, color: Tuple, alignment: str,
                              tracking: int = 0, lh_mult: float = 1.35,
                              shadow_offset: Tuple = (3, 3), shadow_blur: int = 6,
                              shadow_opacity: int = 180,
                              outline_width: int = 0) -> Image.Image:
        """
        Render one text element onto img with:
          • Gaussian-blurred drop shadow
          • Optional outline (stroke) for legibility on busy backgrounds
          • Letter tracking on headlines
        Returns the updated RGBA image.
        """
        if zone is None:
            return img

        z_top, z_bot = zone
        z_h   = z_bot - z_top
        avail = (area_w if area_w > 0 else total_w) - 2 * pad

        # Auto-shrink font until text fits zone height
        font  = self._shrink_font_to_fit(font, text, avail, z_h, lh_mult)
        lines = self._wrap_text_with_font(text, font, avail)

        try:
            lh = font.getbbox('Ag')[3] - font.getbbox('Ag')[1]
        except Exception:
            lh = 14
        step    = int(lh * lh_mult)
        total_h = step * len(lines)
        start_y = z_top + max(0, (z_h - total_h) // 2)

        # Build per-line positions
        positions: List[Tuple[int, int, str]] = []
        for i, line in enumerate(lines):
            y = start_y + i * step
            if y + lh > z_bot:
                break
            lw = self._measure_tracked_text(line, font, tracking)
            if alignment == 'left':
                x = area_left + pad
            elif alignment == 'right':
                x = area_left + (area_w or total_w) - lw - pad
            else:
                aw = area_w if area_w < total_w else total_w
                x  = area_left + max(pad, (aw - lw) // 2)
            positions.append((x, y, line))

        if not positions:
            return img

        img = img.convert('RGBA')

        # ── Gaussian shadow ──────────────────────────────────────────────────
        if shadow_blur > 0 or shadow_offset != (0, 0):
            sh_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            sh_draw  = ImageDraw.Draw(sh_layer)
            ox, oy   = shadow_offset
            for x, y, line in positions:
                self._draw_tracked_text(sh_draw, x + ox, y + oy, line, font,
                                        (0, 0, 0, shadow_opacity), tracking)
            if shadow_blur > 0:
                sh_layer = sh_layer.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
            img = Image.alpha_composite(img, sh_layer)

        # ── Text layer (outline + fill) ───────────────────────────────────────
        tx_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        tx_draw  = ImageDraw.Draw(tx_layer)

        if outline_width > 0:
            oc = (0, 0, 0, 200)
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx == 0 and dy == 0:
                        continue
                    for x, y, line in positions:
                        # Use plain text for outline (±2px misalignment with tracking
                        # is imperceptible at this scale)
                        tx_draw.text((x + dx, y + dy), line, font=font, fill=oc)

        for x, y, line in positions:
            self._draw_tracked_text(tx_draw, x, y, line, font, color, tracking)

        return Image.alpha_composite(img, tx_layer)

    def _render_cta(self, img: Image.Image, text: str,
                    font: ImageFont.FreeTypeFont,
                    zone: Tuple[int, int],
                    total_w: int, area_left: int, area_w: int,
                    cta_style: str, text_color: Tuple,
                    accent_color: Tuple, alignment: str,
                    is_dark_image: bool = True) -> Image.Image:
        """Render CTA button with Gaussian-blurred drop shadow. Returns updated image."""
        z_top, z_bot = zone
        z_h   = z_bot - z_top
        text_up = text.upper()

        # Measure text with a throwaway draw
        _tmp_img  = Image.new('L', (2, 2))
        _tmp_draw = ImageDraw.Draw(_tmp_img)
        bbox      = _tmp_draw.textbbox((0, 0), text_up, font=font)
        tw, th    = bbox[2] - bbox[0], bbox[3] - bbox[1]

        # Resolve accent color — must contrast with background
        ar, ag, ab = accent_color[:3]
        acc_lum = 0.299*ar + 0.587*ag + 0.114*ab
        if is_dark_image and acc_lum < 55:
            ar, ag, ab = 230, 210, 170
        elif not is_dark_image and acc_lum > 210:
            ar, ag, ab = 30, 30, 70

        inner_lum = 0.299*ar + 0.587*ag + 0.114*ab
        inner_tc  = (10, 10, 10, 255) if inner_lum > 160 else (255, 255, 255, 255)

        if alignment == 'left':
            cx = area_left + min(int(total_w * 0.22), (area_w or total_w) // 2)
        else:
            cx = total_w // 2
        cy = z_top + z_h // 2

        img = img.convert('RGBA')

        if cta_style == 'text_underline':
            text_arrow = text_up + '  \u2192'
            layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw  = ImageDraw.Draw(layer)
            ab2   = draw.textbbox((0, 0), text_arrow, font=font)
            atw   = ab2[2] - ab2[0]
            x     = (area_left + int(total_w * 0.05) if alignment == 'left'
                     else max(int(total_w * 0.05), (total_w - atw) // 2))
            ty    = cy - th // 2
            tc    = (ar, ag, ab, 255)
            draw.text((x + 2, ty + 2), text_arrow, font=font, fill=(0, 0, 0, 120))
            draw.text((x, ty),          text_arrow, font=font, fill=tc)
            draw.line([(x, ty+th+5), (x+atw, ty+th+5)], fill=tc, width=3)
            draw.line([(x, ty+th+8), (x+atw, ty+th+8)], fill=(ar, ag, ab, 100), width=1)
            return Image.alpha_composite(img, layer)

        elif cta_style == 'square_button':
            layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw  = ImageDraw.Draw(layer)
            px = max(20, int(tw * 0.35)); py = max(10, int(th * 0.45))
            bw, bh = tw+2*px, th+2*py
            x0, y0 = cx-bw//2, cy-bh//2; x1, y1 = cx+bw//2, cy+bh//2
            draw.rectangle([x0, y0, x1, y1], fill=(ar, ag, ab, 40),
                           outline=(ar, ag, ab, 240), width=3)
            draw.text((x0+2, y0+2), text_up, font=font, fill=(0, 0, 0, 100))
            draw.text((cx-tw//2, cy-th//2), text_up, font=font, fill=(ar, ag, ab, 255))
            return Image.alpha_composite(img, layer)

        elif cta_style == 'block_inverted':
            layer  = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw   = ImageDraw.Draw(layer)
            margin = max(20, int(total_w * 0.15))
            bt = z_top + int(z_h * 0.10); bb = z_bot - int(z_h * 0.10)
            draw.rectangle([margin, bt, total_w-margin, bb], fill=(ar, ag, ab, 225))
            bh_block = bb - bt
            draw.text(((total_w-tw)//2, bt+(bh_block-th)//2),
                      text_up, font=font, fill=inner_tc)
            return Image.alpha_composite(img, layer)

        else:  # pill_button — true pill + Gaussian shadow
            tracking_cta = 2
            tw_t = self._measure_tracked_text(text_up, font, tracking_cta)
            px   = max(30, int(tw_t * 0.50)); py = max(14, int(th * 0.60))
            bw, bh_btn = tw_t + 2*px, th + 2*py
            x0, y0 = cx - bw//2, cy - bh_btn//2
            x1, y1 = cx + bw//2, cy + bh_btn//2
            r = bh_btn // 2

            # Gaussian shadow for button
            sh_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            sh_draw  = ImageDraw.Draw(sh_layer)
            try:
                sh_draw.rounded_rectangle([x0+3, y0+5, x1+3, y1+5],
                                          radius=r, fill=(0, 0, 0, 120))
            except (AttributeError, TypeError):
                sh_draw.rectangle([x0+3, y0+5, x1+3, y1+5], fill=(0, 0, 0, 120))
            sh_layer = sh_layer.filter(ImageFilter.GaussianBlur(radius=8))
            img = Image.alpha_composite(img, sh_layer)

            # Button fill
            layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw  = ImageDraw.Draw(layer)
            try:
                draw.rounded_rectangle([x0, y0, x1, y1], radius=r,
                                       fill=(ar, ag, ab, 240),
                                       outline=(255, 255, 255, 150), width=2)
            except (AttributeError, TypeError):
                draw.rectangle([x0, y0, x1, y1], fill=(ar, ag, ab, 240),
                               outline=(255, 255, 255, 150), width=2)

            tx_off = cx - tw_t // 2
            self._draw_tracked_text(draw, tx_off, cy - th//2,
                                    text_up, font, inner_tc, tracking_cta)
            return Image.alpha_composite(img, layer)

    # ── Color extraction & selection ──────────────────────────────────────────

    def _extract_palette(self, img: Image.Image) -> Dict[str, Any]:
        """Extract dominant colors and light/dark character from image."""
        try:
            if not _NUMPY_OK:
                raise ImportError("numpy unavailable")
            small  = img.resize((100, 100)).convert('RGB')
            pixels = np.array(small).reshape(-1, 3)
            quant  = (pixels // 32) * 32
            counts = _Counter(map(tuple, quant.tolist()))
            dominant = [c for c, _ in counts.most_common(8)]
            avg_brightness = float(np.mean(pixels))
        except Exception:
            dominant       = [(200, 200, 200)]
            avg_brightness = 80.0

        is_dark = avg_brightness < 128
        sorted_by_lum = sorted(dominant, key=lambda c: 0.299*c[0] + 0.587*c[1] + 0.114*c[2])
        return {
            'dominant':       dominant,
            'lightest':       sorted_by_lum[-1],
            'darkest':        sorted_by_lum[0],
            'is_dark_image':  is_dark,
            'avg_brightness': avg_brightness,
            'accent':         dominant[1] if len(dominant) > 1 else dominant[0],
        }

    def _choose_text_color(self, palette: Dict, layout: Dict) -> Tuple:
        """Return text color that contrasts with the image."""
        layout_hex = layout.get('text_color', '#FFFFFF')
        # Only trust GPT's suggestion when it chose something other than pure white
        if layout_hex and layout_hex.upper() not in ('#FFFFFF', '#FFF', ''):
            return self._parse_color(layout_hex)
        if palette['is_dark_image']:
            return (255, 255, 255, 255)
        # Light image → dark text
        d = palette['darkest']
        return (d[0], d[1], d[2], 255) if sum(d) < 300 else (15, 15, 15, 255)

    def _choose_accent_color(self, palette: Dict, layout: Dict) -> Tuple:
        """Return accent color from image palette for CTA/highlights."""
        layout_hex = layout.get('accent_color', '#FFFFFF')
        if layout_hex and layout_hex.upper() not in ('#FFFFFF', '#FFF', ''):
            return self._parse_color(layout_hex)
        accent = palette.get('accent', (200, 200, 200))
        brightness = (accent[0] + accent[1] + accent[2]) / 3
        if palette['is_dark_image'] and brightness < 60:
            return (230, 210, 170, 255)   # warm gold fallback
        if not palette['is_dark_image'] and brightness > 210:
            return (40, 40, 80, 255)      # dark navy fallback
        return (accent[0], accent[1], accent[2], 255)

    # ── Overlay / scrim ───────────────────────────────────────────────────────

    def _apply_scrim_to_zones(self, base: Image.Image, active_zones: Dict,
                               opacity: float, overlay_type: str,
                               accent_color: Tuple,
                               tx_start: int, tx_w: int) -> Image.Image:
        """
        Scrim overlay: darken only behind actual text zones, not the whole image.
        For frosted_strip / solid_bar / shadow_only: delegate to legacy overlay.
        For gradient_left: column-aware fade.
        For all others: feathered band behind each text cluster.
        """
        if overlay_type in ('frosted_strip', 'solid_bar', 'shadow_only'):
            return self._apply_overlay(base, overlay_type, opacity, accent_color)

        width, height = base.size
        ov    = Image.new('RGBA', base.size, (0, 0, 0, 0))
        d     = ImageDraw.Draw(ov)
        max_a = int(195 * max(0.2, min(1.0, opacity)))

        if overlay_type == 'gradient_left':
            fade = int(width * 0.50)
            for x in range(fade):
                p = x / fade
                d.line([(x, 0), (x, height - 1)],
                       fill=(0, 0, 0, int(max_a * (1 - p ** 0.7))))
            return Image.alpha_composite(base, ov)

        # --- Zone-scrim: group zones into clusters, feather at edges ---
        zone_list = sorted(active_zones.values())   # list of (top, bot)
        feather   = max(24, int(height * 0.04))

        # Merge overlapping / nearby zones
        merged: List[List[int]] = []
        for z_top, z_bot in zone_list:
            if merged and z_top <= merged[-1][1] + feather:
                merged[-1][1] = max(merged[-1][1], z_bot)
            else:
                merged.append([z_top, z_bot])

        # Horizontal bounds for the scrim (full-width vs column)
        if tx_w > 0 and tx_w < width:
            x0_scrim, x1_scrim = tx_start, tx_start + tx_w
        else:
            x0_scrim, x1_scrim = 0, width

        for z_top, z_bot in merged:
            pad_top = max(0, z_top - feather)
            pad_bot = min(height, z_bot + feather)
            for y in range(pad_top, pad_bot):
                if y < z_top:
                    alpha = int(max_a * (1 - (z_top - y) / feather))
                elif y > z_bot:
                    alpha = int(max_a * (1 - (y - z_bot) / feather))
                else:
                    alpha = max_a
                alpha = max(0, min(255, alpha))
                d.line([(x0_scrim, y), (x1_scrim - 1, y)], fill=(0, 0, 0, alpha))

        # Blur scrim edges for natural blending
        ov = ov.filter(ImageFilter.GaussianBlur(radius=12))
        return Image.alpha_composite(base, ov)

    def _apply_overlay(self, base: Image.Image, overlay_type: str,
                       opacity: float, accent_color: Tuple) -> Image.Image:
        """Legacy full-image overlay (kept for frosted_strip / solid_bar / shadow_only)."""
        width, height = base.size
        ov  = Image.new('RGBA', base.size, (0, 0, 0, 0))
        d   = ImageDraw.Draw(ov)
        max_a = int(220 * max(0.2, min(1.0, opacity)))

        if overlay_type == 'frosted_strip':
            alpha = int(max_a * 0.88)
            d.rectangle([0, int(height*0.60), width, height],
                        fill=(15, 15, 25, alpha))
            d.rectangle([0, 0, width, int(height*0.38)],
                        fill=(15, 15, 25, int(alpha * 0.90)))
        elif overlay_type == 'shadow_only':
            d.rectangle([0, 0, width, height], fill=(0, 0, 0, 28))
        elif overlay_type == 'solid_bar':
            r, g, b = accent_color[:3]
            bar_a   = min(255, int(max_a * 1.1))
            d.rectangle([0, 0, width, int(height*0.22)],         fill=(r, g, b, bar_a))
            d.rectangle([0, int(height*0.70), width, height],    fill=(r, g, b, bar_a))
        else:  # gradient_top_bottom fallback
            depth = int(height * 0.32)
            for y in range(depth):
                p = y / depth
                d.line([(0, y),           (width-1, y)],
                       fill=(0, 0, 0, int(max_a * (1 - p))))
                d.line([(0, height-1-y),  (width-1, height-1-y)],
                       fill=(0, 0, 0, int(min(255, max_a * (1 - p) * 1.1))))

        return Image.alpha_composite(base, ov)

    # ── Font loading ──────────────────────────────────────────────────────────

    def _load_weight_fonts(self, headline_px: int, sub_px: int,
                            body_px: int, cta_px: int
                            ) -> Dict[str, ImageFont.FreeTypeFont]:
        """
        Load fonts with strong weight contrast:
          headline    → ExtraBold / Bold   (maximum impact)
          subheadline → Light              (elegance through contrast)
          body        → Light              (reads small)
          cta         → Bold               (readable at medium size)
        """
        module_dir   = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(module_dir))
        fr           = os.path.join(project_root, 'fonts')

        candidates: Dict[str, List[str]] = {
            'headline': [
                os.path.join(fr, 'display', 'Montserrat-ExtraBold.ttf'),
                os.path.join(fr, 'display', 'Montserrat-Bold.ttf'),
                os.path.join(fr, 'display', 'Oswald-Bold.ttf'),
                'C:/Windows/Fonts/arialbd.ttf',
            ],
            'subheadline': [
                os.path.join(fr, 'display', 'Montserrat-Light.ttf'),
                os.path.join(fr, 'display', 'Montserrat-Regular.ttf'),
                os.path.join(fr, 'sans',    'OpenSans-Light.ttf'),
                os.path.join(fr, 'sans',    'OpenSans-Regular.ttf'),
                'C:/Windows/Fonts/arial.ttf',
            ],
            'body': [
                os.path.join(fr, 'sans', 'OpenSans-Light.ttf'),
                os.path.join(fr, 'sans', 'Roboto-Light.ttf'),
                os.path.join(fr, 'sans', 'OpenSans-Regular.ttf'),
                os.path.join(fr, 'sans', 'Roboto-Regular.ttf'),
                'C:/Windows/Fonts/arial.ttf',
            ],
            'cta': [
                os.path.join(fr, 'display', 'Montserrat-Bold.ttf'),
                os.path.join(fr, 'display', 'Montserrat-SemiBold.ttf'),
                os.path.join(fr, 'display', 'Oswald-Bold.ttf'),
                'C:/Windows/Fonts/arialbd.ttf',
            ],
        }
        sizes = {
            'headline': headline_px, 'subheadline': sub_px,
            'body': body_px, 'cta': cta_px,
        }

        loaded: Dict[str, ImageFont.FreeTypeFont] = {}
        for key, paths in candidates.items():
            font = None
            for path in paths:
                try:
                    font = ImageFont.truetype(path, sizes[key])
                    break
                except (IOError, OSError):
                    pass
            if font is None:
                self.logger.error("All font candidates failed for '%s', using default", key)
                font = ImageFont.load_default()
            loaded[key] = font
        return loaded

    # ── Text drawing ──────────────────────────────────────────────────────────

    def _measure_tracked_text(self, text: str, font: ImageFont.FreeTypeFont,
                               tracking: int) -> int:
        """Return pixel width of text with tracking applied."""
        total = 0
        for i, char in enumerate(text):
            try:
                w = font.getbbox(char)[2] - font.getbbox(char)[0]
            except Exception:
                w = 10
            total += w + (tracking if i < len(text) - 1 else 0)
        return total

    def _draw_tracked_text(self, draw: ImageDraw.Draw, x: int, y: int,
                            text: str, font: ImageFont.FreeTypeFont,
                            fill: Tuple, tracking: int = 0) -> int:
        """Draw text character-by-character with letter spacing. Returns width."""
        cur_x = x
        for char in text:
            draw.text((cur_x, y), char, font=font, fill=fill)
            try:
                w = font.getbbox(char)[2] - font.getbbox(char)[0]
            except Exception:
                w = draw.textbbox((0, 0), char, font=font)[2]
            cur_x += w + tracking
        return cur_x - x

    def _shrink_font_to_fit(self, font: ImageFont.FreeTypeFont,
                             text: str, avail_w: int, zone_h: int,
                             lh_mult: float, min_size: int = 14
                             ) -> ImageFont.FreeTypeFont:
        """Reduce font size until wrapped text fits inside zone_h."""
        try:
            path = font.path
            size = int(font.size)
        except AttributeError:
            return font  # bitmap / default font — cannot resize

        while size >= min_size:
            try:
                f = ImageFont.truetype(path, size)
            except (IOError, OSError):
                break
            lines  = self._wrap_text_with_font(text, f, avail_w)
            try:
                lh = f.getbbox('Ag')[3] - f.getbbox('Ag')[1]
            except Exception:
                lh = size
            needed = len(lines) * int(lh * lh_mult)
            if needed <= zone_h:
                return f
            size -= 3
        return font

    def _draw_element_in_zone(self, draw: ImageDraw.Draw, text: str,
                               font: ImageFont.FreeTypeFont,
                               zone: Optional[Tuple[int, int]],
                               total_w: int, area_w: int, area_left: int,
                               pad: int, color: Tuple, alignment: str,
                               tracking: int = 0,
                               line_height_mult: float = 1.35,
                               is_headline: bool = False) -> None:
        """Draw text in zone with tracking, auto-shrink, proper vertical rhythm."""
        if zone is None:
            return
        z_top, z_bot = zone
        z_h   = z_bot - z_top
        avail = (area_w if area_w > 0 else total_w) - 2 * pad

        # Auto-shrink font if text won't fit at current size
        font  = self._shrink_font_to_fit(font, text, avail, z_h, line_height_mult)
        lines = self._wrap_text(draw, text, font, avail)

        bbox  = draw.textbbox((0, 0), 'Ag', font=font)
        lh    = bbox[3] - bbox[1]
        step  = int(lh * line_height_mult)
        total_h = step * len(lines)
        start_y = z_top + max(0, (z_h - total_h) // 2)

        shadow_off = max(2, lh // 18) if is_headline else max(1, lh // 22)
        shadow_a   = 190 if is_headline else 150

        for i, line in enumerate(lines):
            y = start_y + i * step
            if y + lh > z_bot:
                break   # never overflow zone

            lw = self._measure_tracked_text(line, font, tracking)

            if alignment == 'left':
                x = area_left + pad
            elif alignment == 'right':
                x = area_left + (area_w if area_w else total_w) - lw - pad
            else:  # center
                avail_w = area_w if area_w < total_w else total_w
                x = area_left + max(pad, (avail_w - lw) // 2)

            # Shadow pass
            self._draw_tracked_text(draw, x + shadow_off, y + shadow_off,
                                    line, font, (0, 0, 0, shadow_a), tracking)
            # Main pass
            self._draw_tracked_text(draw, x, y, line, font, color, tracking)

    def _draw_cta_v2(self, draw: ImageDraw.Draw, text: str,
                      font: ImageFont.FreeTypeFont,
                      zone: Tuple[int, int],
                      total_w: int, area_left: int, area_w: int,
                      cta_style: str, text_color: Tuple,
                      accent_color: Tuple, alignment: str,
                      is_dark_image: bool = True) -> None:
        """Render CTA with polished visual quality: shadows, accent colors, arrow."""
        z_top, z_bot = zone
        z_h   = z_bot - z_top
        text_up = text.upper()

        bbox    = draw.textbbox((0, 0), text_up, font=font)
        tw, th  = bbox[2] - bbox[0], bbox[3] - bbox[1]

        # Resolve accent RGB — must contrast against expected background
        ar, ag, ab = accent_color[:3]
        acc_lum = 0.299*ar + 0.587*ag + 0.114*ab
        if is_dark_image and acc_lum < 55:
            ar, ag, ab = 230, 210, 170   # warm gold on dark
        elif not is_dark_image and acc_lum > 210:
            ar, ag, ab = 30, 30, 70      # dark navy on light

        # Inner text color: contrast against button fill
        inner_lum = 0.299*ar + 0.587*ag + 0.114*ab
        inner_tc  = (10, 10, 10, 255) if inner_lum > 160 else (255, 255, 255, 255)

        if alignment == 'left':
            cx = area_left + min(int(total_w * 0.22), (area_w or total_w) // 2)
        else:
            cx = total_w // 2
        cy = z_top + z_h // 2

        if cta_style == 'text_underline':
            text_arrow = text_up + "  →"
            ab2  = draw.textbbox((0, 0), text_arrow, font=font)
            atw  = ab2[2] - ab2[0]
            x    = (area_left + int(total_w*0.05)
                    if alignment == 'left'
                    else max(int(total_w*0.05), (total_w - atw) // 2))
            ty   = cy - th // 2
            tc   = (ar, ag, ab, 255)
            draw.text((x+2, ty+2), text_arrow, font=font, fill=(0, 0, 0, 120))
            draw.text((x,   ty),   text_arrow, font=font, fill=tc)
            draw.line([(x, ty+th+5), (x+atw, ty+th+5)], fill=tc, width=3)
            draw.line([(x, ty+th+8), (x+atw, ty+th+8)], fill=(ar, ag, ab, 100), width=1)

        elif cta_style == 'square_button':
            px = max(20, int(tw * 0.35));  py = max(10, int(th * 0.45))
            bw, bh = tw + 2*px, th + 2*py
            x0, y0 = cx - bw//2, cy - bh//2
            x1, y1 = cx + bw//2, cy + bh//2
            draw.rectangle([x0, y0, x1, y1],
                           fill=(ar, ag, ab, 40), outline=(ar, ag, ab, 240), width=3)
            draw.text((cx-tw//2+2, cy-th//2+2), text_up, font=font, fill=(0, 0, 0, 120))
            draw.text((cx-tw//2,   cy-th//2),   text_up, font=font, fill=(ar, ag, ab, 255))

        elif cta_style == 'block_inverted':
            margin = max(20, int(total_w * 0.15))
            bt = z_top + int(z_h * 0.10)
            bb = z_bot - int(z_h * 0.10)
            draw.rectangle([margin, bt, total_w - margin, bb], fill=(ar, ag, ab, 225))
            bh_block = bb - bt
            draw.text(((total_w - tw) // 2, bt + (bh_block - th) // 2),
                      text_up, font=font, fill=inner_tc)

        else:  # pill_button (default) — true pill + multi-layer shadow
            tracking_cta = 2
            tw_t = self._measure_tracked_text(text_up, font, tracking_cta)
            px   = max(30, int(tw_t * 0.50));  py = max(14, int(th * 0.60))
            bw, bh = tw_t + 2*px, th + 2*py
            x0, y0 = cx - bw//2, cy - bh//2
            x1, y1 = cx + bw//2, cy + bh//2
            r = bh // 2   # true pill shape

            # Soft shadow layers
            for off in range(5, 0, -1):
                sh_a = int(55 * (6 - off) / 5)
                try:
                    draw.rounded_rectangle(
                        [x0+off, y0+off+2, x1+off, y1+off+2],
                        radius=r, fill=(0, 0, 0, sh_a)
                    )
                except (AttributeError, TypeError):
                    pass

            # Button fill
            try:
                draw.rounded_rectangle([x0, y0, x1, y1], radius=r,
                                       fill=(ar, ag, ab, 235),
                                       outline=(255, 255, 255, 160), width=2)
            except (AttributeError, TypeError):
                draw.rectangle([x0, y0, x1, y1], fill=(ar, ag, ab, 235),
                                outline=(255, 255, 255, 160), width=2)

            tx_off = cx - tw_t // 2
            self._draw_tracked_text(draw, tx_off, cy - th//2,
                                    text_up, font, inner_tc, tracking_cta)

    def _parse_color(self, hex_color: Any, alpha: int = 255) -> Tuple[int, int, int, int]:
        """Parse a hex color string to an RGBA tuple."""
        try:
            h = str(hex_color).lstrip('#')
            if len(h) == 6:
                return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)
        except (ValueError, AttributeError):
            pass
        return (255, 255, 255, alpha)

    def _calculate_zones(self, style: str, headline_pos: str,
                          width: int, height: int) -> Tuple[Dict, str, int, int]:
        """
        Return (zones_dict, alignment, text_x_start, text_area_width).
        zones_dict values are (top_y, bot_y) or None (skip that element).
        """
        def pct(f): return int(height * f)

        if style == 'left_column':
            return ({
                'headline':    (pct(0.08), pct(0.26)),
                'subheadline': (pct(0.28), pct(0.42)),
                'body':        (pct(0.44), pct(0.65)),
                'cta':         (pct(0.70), pct(0.82)),
            }, 'left', int(width*0.04), int(width*0.42))

        if style == 'bottom_banner':
            return ({
                'headline':    (pct(0.62), pct(0.74)),
                'subheadline': (pct(0.75), pct(0.84)),
                'body':        None,
                'cta':         (pct(0.86), pct(0.95)),
            }, 'center', 0, width)

        if style == 'bold_statement':
            return ({
                'headline':    (pct(0.28), pct(0.58)),
                'subheadline': (pct(0.60), pct(0.72)),
                'body':        None,
                'cta':         (pct(0.76), pct(0.90)),
            }, 'center', 0, width)

        if style in ('centered', 'floating_cards'):
            return ({
                'headline':    (pct(0.32), pct(0.50)),
                'subheadline': (pct(0.52), pct(0.62)),
                'body':        None,                        # no body in product zone (35-70%)
                'cta':         (pct(0.76), pct(0.87)),
            }, 'center', 0, width)

        if style == 'split_horizontal':
            return ({
                'headline':    (pct(0.12), pct(0.30)),
                'subheadline': (pct(0.32), pct(0.46)),
                'body':        (pct(0.48), pct(0.64)),
                'cta':         (pct(0.68), pct(0.80)),
            }, 'left', int(width*0.52), int(width*0.44))

        if style == 'diagonal':
            return ({
                'headline':    (pct(0.08), pct(0.26)),
                'subheadline': (pct(0.28), pct(0.40)),
                'body':        (pct(0.70), pct(0.82)),
                'cta':         (pct(0.84), pct(0.94)),
            }, 'center', 0, width)

        # --- top_bottom (default) — headline_position adjusts behaviour ---
        if headline_pos == 'top_left':
            return ({
                'headline':    (pct(0.05), pct(0.22)),
                'subheadline': (pct(0.23), pct(0.35)),
                'body':        (pct(0.70), pct(0.82)),
                'cta':         (pct(0.84), pct(0.94)),
            }, 'left', 0, width)

        if headline_pos == 'center':
            return ({
                'headline':    (pct(0.35), pct(0.52)),
                'subheadline': (pct(0.54), pct(0.64)),
                'body':        (pct(0.70), pct(0.80)),     # enforced ≥70% (product zone ends at 70%)
                'cta':         (pct(0.82), pct(0.93)),
            }, 'center', 0, width)

        if headline_pos == 'bottom_left':
            return ({
                'headline':    (pct(0.63), pct(0.75)),
                'subheadline': (pct(0.76), pct(0.85)),
                'body':        None,
                'cta':         (pct(0.87), pct(0.96)),
            }, 'left', 0, width)

        # top_center (default)
        return ({
            'headline':    (pct(0.05), pct(0.22)),
            'subheadline': (pct(0.23), pct(0.35)),
            'body':        (pct(0.70), pct(0.82)),
            'cta':         (pct(0.84), pct(0.94)),
        }, 'center', 0, width)

    def _draw_zoned_text(self, draw: ImageDraw.Draw, text: str,
                          font: ImageFont.FreeTypeFont,
                          zone: Tuple[int, int],
                          total_w: int, area_w: int, area_left: int,
                          pad: int, color: Tuple, alignment: str) -> None:
        """Wrap and draw text inside zone with correct alignment."""
        if zone is None:
            return
        avail = (area_w if area_w > 0 else total_w) - 2 * pad
        lines = self._wrap_text(draw, text, font, avail)

        z_top, z_bot = zone
        z_h = z_bot - z_top
        bbox  = draw.textbbox((0, 0), 'Ag', font=font)
        lh    = bbox[3] - bbox[1]
        step  = int(lh * 1.25)
        total_h = step * len(lines)
        start_y = z_top + max(0, (z_h - total_h) // 2)

        for i, line in enumerate(lines):
            y = start_y + i * step
            if y + lh <= z_top or y >= z_bot:
                continue
            lb = draw.textbbox((0, 0), line, font=font)
            lw = lb[2] - lb[0]

            if alignment == 'left':
                x = area_left + pad
            elif alignment == 'right':
                x = area_left + (area_w if area_w else total_w) - lw - pad
            else:  # center
                if area_w < total_w:
                    x = area_left + max(pad, (area_w - lw) // 2)
                else:
                    x = max(pad, (total_w - lw) // 2)

            shadow = max(1, lh // 22)
            draw.text((x+shadow, y+shadow), line, font=font, fill=(0, 0, 0, 160))
            draw.text((x, y),               line, font=font, fill=color)

    def _draw_cta_styled(self, draw: ImageDraw.Draw, text: str,
                          font: ImageFont.FreeTypeFont,
                          zone: Tuple[int, int],
                          total_w: int, area_left: int, area_w: int,
                          cta_style: str, cta_color: Tuple,
                          accent_color: Tuple, alignment: str) -> None:
        """Render CTA in the chosen style."""
        z_top, z_bot = zone
        z_h   = z_bot - z_top
        text_up = text.upper()
        bbox  = draw.textbbox((0, 0), text_up, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        fill  = (cta_color[0], cta_color[1], cta_color[2], 235)
        dark  = (20, 20, 20, 255)

        # Horizontal centre of the CTA element
        if alignment == 'left':
            cx = area_left + min(int(total_w * 0.22), (area_w or total_w) // 2)
        else:
            cx = total_w // 2
        cy = z_top + z_h // 2

        if cta_style == 'square_button':
            px = max(20, int(tw * 0.35)); py = max(10, int(th * 0.45))
            bw, bh = tw+2*px, th+2*py
            x0,y0 = cx-bw//2, cy-bh//2; x1,y1 = cx+bw//2, cy+bh//2
            draw.rectangle([x0,y0,x1,y1], fill=fill, outline=(255,255,255,200), width=2)
            draw.text((cx-tw//2, cy-th//2), text_up, font=font, fill=dark)

        elif cta_style == 'text_underline':
            x = area_left + int(total_w*0.05) if alignment == 'left' else max(int(total_w*0.05),(total_w-tw)//2)
            ty = cy - th//2
            tc = (cta_color[0], cta_color[1], cta_color[2], 255)
            draw.text((x, ty), text_up, font=font, fill=tc)
            draw.line([(x, ty+th+4), (x+tw, ty+th+4)], fill=tc, width=2)

        elif cta_style == 'block_inverted':
            bt = z_top + int(z_h*0.08); bb = z_bot - int(z_h*0.08)
            draw.rectangle([0, bt, total_w, bb], fill=(cta_color[0],cta_color[1],cta_color[2],230))
            draw.text(((total_w-tw)//2, (bt+bb)//2-th//2), text_up, font=font, fill=dark)

        else:  # pill_button (default)
            px = max(24, int(tw*0.45)); py = max(12, int(th*0.55))
            bw, bh = tw+2*px, th+2*py
            x0,y0 = cx-bw//2, cy-bh//2; x1,y1 = cx+bw//2, cy+bh//2
            r = bh // 3
            try:
                draw.rounded_rectangle([x0,y0,x1,y1], radius=r, fill=fill,
                                        outline=(255,255,255,255), width=2)
            except (AttributeError, TypeError):
                draw.rectangle([x0,y0,x1,y1], fill=fill, outline=(255,255,255,255), width=2)
            draw.text((cx-tw//2, cy-th//2), text_up, font=font, fill=dark)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _load_sized_fonts(
            self,
            headline_px: int,
            sub_px: int,
            body_px: int,
            cta_px: int,
    ) -> Dict[str, ImageFont.FreeTypeFont]:
        """
        Load four fonts (headline, subheadline, body, cta) at the given sizes.
        Tries known bundled paths; logs an ERROR (not silent) and falls back to
        PIL default if every candidate fails.
        """
        module_dir   = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(module_dir))
        fr           = os.path.join(project_root, 'fonts')   # fonts root

        candidates: Dict[str, List[str]] = {
            'headline': [
                os.path.join(fr, 'display', 'Montserrat-Bold.ttf'),
                os.path.join(fr, 'display', 'Oswald-Bold.ttf'),
            ],
            'subheadline': [
                os.path.join(fr, 'display', 'Montserrat-SemiBold.ttf'),
                os.path.join(fr, 'display', 'Montserrat-Regular.ttf'),
            ],
            'body': [
                os.path.join(fr, 'sans', 'OpenSans-Regular.ttf'),
                os.path.join(fr, 'sans', 'Roboto-Regular.ttf'),
            ],
            'cta': [
                os.path.join(fr, 'display', 'Montserrat-Bold.ttf'),
                os.path.join(fr, 'display', 'Oswald-Bold.ttf'),
            ],
        }
        sizes = {
            'headline':    headline_px,
            'subheadline': sub_px,
            'body':        body_px,
            'cta':         cta_px,
        }

        loaded: Dict[str, ImageFont.FreeTypeFont] = {}
        for key, paths in candidates.items():
            font = None
            for path in paths:
                try:
                    font = ImageFont.truetype(path, sizes[key])
                    self.logger.debug("Loaded %s font: %s @ %dpx", key, os.path.basename(path), sizes[key])
                    break
                except (IOError, OSError) as exc:
                    self.logger.warning("Font not found: %s — %s", path, exc)
            if font is None:
                self.logger.error(
                    "All font candidates failed for '%s' (fonts root: %r). "
                    "Falling back to PIL default — output quality will be degraded.",
                    key, fr
                )
                font = ImageFont.load_default()
            loaded[key] = font

        return loaded

    def _wrap_text(
            self,
            draw: ImageDraw.Draw,
            text: str,
            font: ImageFont.FreeTypeFont,
            max_width: int,
    ) -> List[str]:
        """Word-wrap *text* so every line fits within *max_width* pixels (textbbox-based)."""
        words = text.split()
        lines: List[str] = []
        current = ''

        for word in words:
            candidate = (current + ' ' + word).strip()
            bbox = draw.textbbox((0, 0), candidate, font=font)
            if bbox[2] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines or [text]

    def _draw_text_in_zone(
            self,
            draw: ImageDraw.Draw,
            text: str,
            font: ImageFont.FreeTypeFont,
            zone: Tuple[int, int],
            width: int,
            padding_x: int,
            color: Tuple[int, int, int, int],
    ) -> None:
        """
        Wrap and draw *text* centered vertically inside *zone* (zone_top, zone_bottom).

        Bug 2 fix: uses textbbox() for exact pixel widths; clamps x to ≥ padding_x.
        Bug 3 fix: only paints within the supplied zone; skips lines that fall outside.
        """
        max_w = width - 2 * padding_x
        lines = self._wrap_text(draw, text, font, max_w)

        zone_top, zone_bottom = zone
        zone_h = zone_bottom - zone_top

        sample_bbox = draw.textbbox((0, 0), 'Ag', font=font)
        line_h      = sample_bbox[3] - sample_bbox[1]
        line_step   = int(line_h * 1.25)

        total_h = line_step * len(lines)
        start_y = zone_top + max(0, (zone_h - total_h) // 2)

        for i, line in enumerate(lines):
            y = start_y + i * line_step

            # Skip lines that fall completely outside the zone
            if y + line_h <= zone_top or y >= zone_bottom:
                self.logger.warning("Line '%s...' skipped — outside zone %s", line[:25], zone)
                continue

            line_bbox  = draw.textbbox((0, 0), line, font=font)
            line_w     = line_bbox[2] - line_bbox[0]

            # Centre-align, clamped to padding
            x = max(padding_x, (width - line_w) // 2)
            x = min(x, width - line_w - padding_x)

            # Subtle shadow for depth
            shadow = max(1, line_h // 22)
            draw.text((x + shadow, y + shadow), line, font=font, fill=(0, 0, 0, 130))
            draw.text((x, y), line, font=font, fill=color)

    def _draw_cta_button(
            self,
            draw: ImageDraw.Draw,
            text: str,
            font: ImageFont.FreeTypeFont,
            zone: Tuple[int, int],
            width: int,
    ) -> None:
        """
        Draw a CTA button centred in *zone*.

        Bug 4 fix: fill opacity ≥ 220, rounded rect, white border, generous padding,
                   dark legible text.
        Bug 3 fix: positioned inside the CTA zone (84-94 % of height).
        """
        zone_top, zone_bottom = zone
        zone_h = zone_bottom - zone_top

        cta_text = text.upper()
        bbox      = draw.textbbox((0, 0), cta_text, font=font)
        text_w    = bbox[2] - bbox[0]
        text_h    = bbox[3] - bbox[1]

        pad_x = max(24, int(text_w * 0.45))
        pad_y = max(12, int(text_h * 0.55))

        btn_w = text_w + 2 * pad_x
        btn_h = text_h + 2 * pad_y

        cx = width // 2
        cy = zone_top + zone_h // 2

        x0 = cx - btn_w // 2
        y0 = cy - btn_h // 2
        x1 = cx + btn_w // 2
        y1 = cy + btn_h // 2

        radius      = btn_h // 3
        fill_color  = (230, 230, 230, 235)   # light silver, opacity = 235 ≥ 220
        border_color = (255, 255, 255, 255)  # white border

        try:
            draw.rounded_rectangle(
                [x0, y0, x1, y1],
                radius=radius,
                fill=fill_color,
                outline=border_color,
                width=2,
            )
        except (AttributeError, TypeError):
            # Pillow < 8.2 fallback
            draw.rectangle([x0, y0, x1, y1], fill=fill_color, outline=border_color, width=2)

        text_x = cx - text_w // 2
        text_y = cy - text_h // 2
        draw.text((text_x, text_y), cta_text, font=font, fill=(20, 20, 20, 255))

    # ──────────────────────────────────────────────────────────────────────────

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
