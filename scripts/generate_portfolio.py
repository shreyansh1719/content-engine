"""
Step 5: Generate final portfolio using the winning model.

Generates 10 ads through the full pipeline, scores each, ranks by composite
score, and copies the top 6 to docs/samples/ with product-based filenames.

Usage:
    python scripts/generate_portfolio.py
"""
import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Ensure project root is on sys.path when running as script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("generate_portfolio")

PORTFOLIO_PRODUCTS = [
    {"prompt": "Rolex Submariner luxury dive watch", "slug": "rolex"},
    {"prompt": "Nike Air Jordan 1 streetwear sneakers", "slug": "nike"},
    {"prompt": "Apple AirPods Pro 3 wireless earbuds", "slug": "apple"},
    {"prompt": "Chanel No. 5 eau de parfum", "slug": "chanel"},
    {"prompt": "Tesla Model S Plaid electric sedan", "slug": "tesla"},
    {"prompt": "Sony PlayStation 5 Pro console", "slug": "sony"},
    {"prompt": "Dyson Airwrap multi-styler", "slug": "dyson"},
    {"prompt": "Oatly oat milk dairy alternative", "slug": "oatly"},
    {"prompt": "Levi's 501 original fit jeans", "slug": "levis"},
    {"prompt": "Nespresso Vertuo Pop coffee machine", "slug": "nespresso"},
]


def main():
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        logger.error("OPENAI_API_KEY not set")
        sys.exit(1)

    model_id = os.getenv("FINE_TUNED_MODEL_ID", "").strip()
    if not model_id:
        logger.error("FINE_TUNED_MODEL_ID not set")
        sys.exit(1)

    logger.info(f"Using model: {model_id}")

    from ad_generator.generator import AdGenerator
    from ad_generator.quality_scorer import AdQualityScorer

    generator = AdGenerator(openai_api_key=api_key)
    generator.fine_tuned_model_id = model_id
    scorer = AdQualityScorer(client=generator.openai_client)

    ads = []
    for i, product_info in enumerate(PORTFOLIO_PRODUCTS):
        prompt = product_info["prompt"]
        slug = product_info["slug"]
        logger.info(f"[{i+1}/{len(PORTFOLIO_PRODUCTS)}] {prompt}")

        try:
            result = generator.create_ad(prompt)

            base_image = result.get("_base_image")
            overlay_image = result.get("_overlay_image")

            if base_image and overlay_image:
                composite_score, quality_report = scorer.score_ad(base_image, overlay_image, result)
            else:
                composite_score = 0.0
                quality_report = {"error": "Images not returned"}

            ads.append({
                "slug": slug,
                "prompt": prompt,
                "headline": result.get("headline", ""),
                "subheadline": result.get("subheadline", ""),
                "call_to_action": result.get("call_to_action", ""),
                "tone": result.get("tone", ""),
                "visual_style": result.get("visual_style", ""),
                "composite_score": composite_score,
                "grade": quality_report.get("grade", "N/A"),
                "quality_report": quality_report,
                "image_path": result.get("final_path", ""),
                "creative_brief": {
                    k: result.get(k, "")
                    for k in ["headline", "caption", "tone", "visual_style",
                              "conceptual_technique", "call_to_action", "emotion"]
                },
            })
            logger.info(f"  score={composite_score:.1f}  grade={quality_report.get('grade', '?')}")

        except Exception as exc:
            logger.error(f"  FAILED: {exc}")
            ads.append({
                "slug": slug,
                "prompt": prompt,
                "composite_score": 0.0,
                "error": str(exc),
            })

    # Sort by score descending
    ads.sort(key=lambda a: a.get("composite_score", 0), reverse=True)

    # Copy top 6 to docs/samples/
    samples_dir = Path("docs/samples")
    samples_dir.mkdir(parents=True, exist_ok=True)

    top6 = [a for a in ads if a.get("image_path") and not a.get("error")][:6]
    for ad in top6:
        src = ad["image_path"]
        dst = samples_dir / f"{ad['slug']}.png"
        if src and Path(src).exists():
            shutil.copy(src, dst)
            ad["sample_path"] = str(dst)
            logger.info(f"  Copied {src} -> {dst}  (score={ad['composite_score']:.1f})")
        else:
            logger.warning(f"  Image not found for {ad['slug']}: {src}")

    # Save metadata
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "model_id": model_id,
        "total_generated": len(ads),
        "top_6": top6,
        "all_ads_ranked": ads,
    }
    metadata_path = samples_dir / "portfolio_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    # Print summary
    print("\n" + "=" * 60)
    print("PORTFOLIO GENERATION COMPLETE")
    print("=" * 60)
    print(f"  Generated   : {len(ads)} ads")
    print(f"  Top 6 in    : {samples_dir}/")
    print()
    for i, ad in enumerate(ads[:6], 1):
        print(f"  {i}. {ad['slug']:10s}  score={ad.get('composite_score', 0):.1f}  grade={ad.get('grade', '?')}  headline=\"{ad.get('headline', '')[:50]}\"")
    print("=" * 60)

    logger.info(f"Portfolio metadata: {metadata_path}")
    logger.info("Done. Next step: update README.md with real metrics.")


if __name__ == "__main__":
    main()
