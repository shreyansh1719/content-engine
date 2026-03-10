"""
HTML/CSS Typography Renderer
Renders ad text overlays using Playwright headless Chromium for production-quality typography.

Playwright is invoked via a subprocess to avoid conflicts with asyncio event loops
(e.g. when called from FastAPI/uvicorn context).
"""
import json
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)

# Path to the standalone renderer script (same directory as this file)
_RENDER_SCRIPT = Path(__file__).parent / "render_subprocess.py"


class HTMLTypographyRenderer:
    """Renders HTML/CSS typography overlays to transparent PNG images."""

    def __init__(self):
        """Initialize renderer. Raises if Playwright/Chromium not available."""
        try:
            result = subprocess.run(
                [sys.executable, "-c",
                 "from playwright.sync_api import sync_playwright; "
                 "p = sync_playwright().start(); b = p.chromium.launch(headless=True); "
                 "b.close(); p.stop(); print('ok')"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0 or "ok" not in result.stdout:
                raise RuntimeError(result.stderr or result.stdout)
            logger.info("HTMLTypographyRenderer initialized — Playwright + Chromium ready")
        except Exception as e:
            raise RuntimeError(
                f"Playwright/Chromium not available: {e}. "
                f"Run: pip install playwright && playwright install chromium"
            ) from e

    def render_overlay(self, html_content: str, width: int = 1024, height: int = 1024) -> Image.Image:
        """
        Render an HTML document to a transparent PNG via a subprocess.

        Using a subprocess guarantees no asyncio event loop conflicts when called
        from FastAPI/uvicorn (e.g. in multipart-upload endpoints).

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
            "<!DOCTYPE" not in html_content.upper() and "<html" not in html_content.lower()
        ):
            raise ValueError(
                f"Invalid HTML content: must be a complete HTML document. Got: {html_content[:100]}..."
            )

        # Create a temp PNG output path
        tmp_fd, png_path = tempfile.mkstemp(prefix="adcraft_overlay_", suffix=".png")
        os.close(tmp_fd)

        try:
            payload = json.dumps({
                "html":   html_content,
                "width":  width,
                "height": height,
                "output": png_path,
            })

            result = subprocess.run(
                [sys.executable, str(_RENDER_SCRIPT)],
                input=payload,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"Render subprocess exited {result.returncode}: {result.stderr or result.stdout}"
                )

            try:
                output = json.loads(result.stdout.strip())
            except json.JSONDecodeError:
                raise RuntimeError(f"Unexpected subprocess output: {result.stdout[:200]}")

            if not output.get("success"):
                raise RuntimeError(f"Playwright render failed: {output.get('error', 'unknown')}")

            overlay = Image.open(png_path).convert("RGBA")

            if overlay.size != (width, height):
                logger.warning(
                    f"Rendered size {overlay.size} != expected ({width}, {height}), resizing"
                )
                overlay = overlay.resize((width, height), Image.LANCZOS)

            logger.info(f"HTML overlay rendered successfully: {overlay.size}")
            return overlay

        except subprocess.TimeoutExpired:
            raise RuntimeError("Playwright rendering timed out after 120 s")
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to render HTML overlay: {e}") from e
        finally:
            try:
                os.unlink(png_path)
            except OSError:
                pass

    def composite_overlay(self, base_image: Image.Image, overlay: Image.Image) -> Image.Image:
        """
        Composite the transparent HTML overlay onto the product base image.

        Args:
            base_image: The gpt-image-1 generated product image (RGB or RGBA)
            overlay: The rendered HTML typography overlay (RGBA with transparency)

        Returns:
            Composited image in RGB mode (ready for saving as PNG/JPEG)
        """
        if base_image.size != overlay.size:
            overlay = overlay.resize(base_image.size, Image.LANCZOS)

        if base_image.mode != "RGBA":
            base_image = base_image.convert("RGBA")

        result = Image.alpha_composite(base_image, overlay)
        return result.convert("RGB")
