"""test_imports.py — Verify all core modules import without errors."""
import pytest


def test_ad_generator():
    from ad_generator.generator import AdGenerator
    assert AdGenerator is not None


def test_image_maker():
    from ad_generator.image_maker import ModernStudioImageGenerator
    assert ModernStudioImageGenerator is not None


def test_product_integration():
    from ad_generator.product_integration import EnhancedProductIntegrator
    assert EnhancedProductIntegrator is not None


def test_analytics():
    from ad_generator.analytics import AdMetricsAnalyzer
    assert AdMetricsAnalyzer is not None


def test_typography():
    from ad_generator.typography import TypographySystem
    assert TypographySystem is not None


def test_social_media():
    from ad_generator.social_media import search_social_media_ads
    assert callable(search_social_media_ads)


def test_improved_ad_generator():
    from improved_ad_generator import ImprovedAdGenerator
    assert ImprovedAdGenerator is not None
