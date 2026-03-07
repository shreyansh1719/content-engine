"""test_mock_generation.py — Full pipeline test in dev/mock mode."""
import os
import pytest


def test_dev_mode_flag():
    """DEV_MODE should be True when OPENAI_API_KEY is absent."""
    import os as _os
    orig = _os.environ.pop("OPENAI_API_KEY", None)
    try:
        import importlib, ad_generator.generator as gen_mod
        importlib.reload(gen_mod)
        assert gen_mod.DEV_MODE is True
    finally:
        if orig is not None:
            _os.environ["OPENAI_API_KEY"] = orig
        import importlib, ad_generator.generator as gen_mod2
        importlib.reload(gen_mod2)


def test_mock_ad_creates_image(tmp_path, monkeypatch):
    """AdGenerator.create_ad in mock mode must return a valid image path."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    # Reload with patched env
    import importlib
    import ad_generator.generator as gen_mod
    importlib.reload(gen_mod)

    gen = gen_mod.AdGenerator()
    result = gen.create_ad("Apple iPhone 15 Pro premium smartphone")

    assert result is not None
    assert result.get("headline")
    assert result.get("final_path") or result.get("image_path")
    path = result.get("final_path") or result.get("image_path")
    assert os.path.exists(path), f"Mock image not found at {path}"
    assert result.get("dev_mode") is True


def test_mock_ad_contains_required_fields(monkeypatch):
    """Mock ad must contain all fields expected by the API."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    import importlib
    import ad_generator.generator as gen_mod
    importlib.reload(gen_mod)

    gen = gen_mod.AdGenerator()
    result = gen.create_ad("Levi's 501 jeans classic denim")

    required = ["headline", "subheadline", "body_text", "call_to_action", "generation_time"]
    for field in required:
        assert field in result, f"Missing field: {field}"
        assert result[field], f"Empty field: {field}"
