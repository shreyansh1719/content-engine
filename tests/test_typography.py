"""test_typography.py — Verify typography rendering works end-to-end."""
import os
import pytest
from PIL import Image


@pytest.fixture(scope="module")
def typography_system():
    from ad_generator.typography.typography_system import TypographySystem
    return TypographySystem()


def test_typography_creates_image(typography_system, tmp_path):
    img = Image.new("RGB", (1200, 628), color=(30, 30, 30))
    ad_copy = {
        "headline": "DISCOVER EXCELLENCE",
        "subheadline": "Premium Quality You Can Trust",
        "call_to_action": "SHOP NOW",
    }
    result = typography_system.create_typography(img, ad_copy, brand_name="TestBrand", industry="technology")
    assert result is not None
    assert result.size == (1200, 628)

    out = tmp_path / "test_typography.png"
    result.save(str(out))
    assert out.exists()


def test_typography_returns_image_on_bad_input(typography_system):
    """Should return the original image rather than crashing on empty copy."""
    img = Image.new("RGB", (800, 400), color=(0, 0, 0))
    result = typography_system.create_typography(img, {}, brand_name=None, industry=None)
    assert result is not None
