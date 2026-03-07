"""test_product_integration.py — Verify compositing pipeline works."""
import os
import pytest
from PIL import Image, ImageDraw


@pytest.fixture(scope="module")
def integrator():
    from ad_generator.product_integration import EnhancedProductIntegrator
    return EnhancedProductIntegrator()


@pytest.fixture()
def test_product_image(tmp_path):
    """Create a simple red-square-on-white test image."""
    img = Image.new("RGB", (400, 400), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 300, 300], fill="red")
    path = str(tmp_path / "test_product.png")
    img.save(path)
    return path


def test_process_product_image(integrator, test_product_image):
    result = integrator.process_product_image(test_product_image, product_type="general")
    assert result is not None
    assert isinstance(result, dict)
    assert "background_removed_path" in result or "enhanced_path" in result


def test_process_returns_existing_file(integrator, test_product_image):
    result = integrator.process_product_image(test_product_image, product_type="general")
    out_key = "enhanced_path" if "enhanced_path" in result else "background_removed_path"
    assert os.path.exists(result[out_key])
