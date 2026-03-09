"""
HTML/CSS Typography Renderer
Renders ad text overlays using Playwright headless Chromium for production-quality typography.
"""
import os
import logging
import tempfile
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


class HTMLTypographyRenderer:
    """Renders HTML/CSS typography overlays to transparent PNG images."""

    def __init__(self):
        """Initialize renderer. Raises if Playwright/Chromium not available."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                browser.close()
            logger.info("HTMLTypographyRenderer initialized — Playwright + Chromium ready")
        except Exception as e:
            raise RuntimeError(
                f"Playwright/Chromium not available: {e}. "
                f"Run: pip install playwright && playwright install chromium"
            ) from e

    def render_overlay(self, html_content: str, width: int = 1024, height: int = 1024) -> Image.Image:
        """
        Render an HTML document to a transparent PNG.

        Args:
            html_content: Complete HTML document (<!DOCTYPE html>...) with transparent background
            width: Output width in pixels
            height: Output height in pixels

        Returns:
            PIL Image in RGBA mode with transparent background where no content exists

        Raises:
            ValueError: If html_content is empty or not a valid HTML document
            RuntimeError: If rendering fails
        """
        if not html_content or (
            '<!DOCTYPE' not in html_content.upper() and '<html' not in html_content.lower()
        ):
            raise ValueError(
                f"Invalid HTML content: must be a complete HTML document. Got: {html_content[:100]}..."
            )

        tmp_dir = tempfile.mkdtemp(prefix="adcraft_")
        html_path = os.path.join(tmp_dir, "overlay.html")
        png_path = os.path.join(tmp_dir, "overlay.png")

        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    viewport={"width": width, "height": height},
                    device_scale_factor=1
                )

                # Use file:// URI with forward slashes
                page.goto(f"file:///{Path(html_path).as_posix()}")

                # Wait for Google Fonts
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(2000)

                page.screenshot(
                    path=png_path,
                    omit_background=True,
                    type="png"
                )

                browser.close()

            overlay = Image.open(png_path).convert("RGBA")

            if overlay.size != (width, height):
                logger.warning(
                    f"Rendered size {overlay.size} != expected ({width}, {height}), resizing"
                )
                overlay = overlay.resize((width, height), Image.LANCZOS)

            logger.info(f"HTML overlay rendered successfully: {overlay.size}")
            return overlay

        except Exception as e:
            logger.error(f"HTML rendering failed: {e}")
            raise RuntimeError(f"Failed to render HTML overlay: {e}") from e
        finally:
            for path in [html_path, png_path]:
                try:
                    os.unlink(path)
                except OSError:
                    pass
            try:
                os.rmdir(tmp_dir)
            except OSError:
                pass

    def composite_overlay(self, base_image: Image.Image, overlay: Image.Image) -> Image.Image:
        """
        Composite the transparent HTML overlay onto the DALL-E base image.

        Args:
            base_image: The DALL-E generated product image (RGB or RGBA)
            overlay: The rendered HTML typography overlay (RGBA with transparency)

        Returns:
            Composited image in RGB mode (ready for saving as PNG/JPEG)
        """
        if base_image.size != overlay.size:
            overlay = overlay.resize(base_image.size, Image.LANCZOS)

        if base_image.mode != 'RGBA':
            base_image = base_image.convert('RGBA')

        result = Image.alpha_composite(base_image, overlay)
        return result.convert('RGB')
