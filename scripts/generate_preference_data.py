"""
Step 2: Generate preference pairs via batch A/B testing.

Runs 10 products × 3 variants each through the full pipeline and collects
preference pairs via FeedbackLoop.

Usage:
    python scripts/generate_preference_data.py --dry-run   # 2 products, 2 variants
    python scripts/generate_preference_data.py             # full batch, 10 products
"""
import argparse
import json
import logging
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Retry decorator
# ---------------------------------------------------------------------------

def _retry(fn, retries=3, initial_delay=2.0):
    """Exponential-backoff retry wrapper (works without tenacity)."""
    try:
        import tenacity
        from tenacity import retry, stop_after_attempt, wait_exponential
        decorated = retry(
            stop=stop_after_attempt(retries),
            wait=wait_exponential(multiplier=1, min=initial_delay, max=30),
            reraise=True,
        )(fn)
        return decorated
    except ImportError:
        pass

    def wrapper(*args, **kwargs):
        delay = initial_delay
        last_exc = None
        for attempt in range(retries):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                last_exc = exc
                if attempt < retries - 1:
                    logging.getLogger("retry").warning(
                        f"Attempt {attempt + 1}/{retries} failed ({exc}); retrying in {delay:.1f}s"
                    )
                    time.sleep(delay)
                    delay *= 2
        raise last_exc

    return wrapper


# ---------------------------------------------------------------------------
# Product set
# ---------------------------------------------------------------------------

PRODUCTS = [
    {"prompt": "Rolex Submariner luxury dive watch", "brand": "Rolex", "industry": "luxury"},
    {"prompt": "Nike Air Jordan 1 streetwear sneakers", "brand": "Nike", "industry": "sportswear"},
    {"prompt": "Apple AirPods Pro 3 wireless earbuds", "brand": "Apple", "industry": "technology"},
    {"prompt": "Oatly oat milk dairy alternative", "brand": "Oatly", "industry": "food_beverage"},
    {"prompt": "Tesla Model S Plaid electric sedan", "brand": "Tesla", "industry": "automotive"},
    {"prompt": "Chanel No. 5 eau de parfum", "brand": "Chanel", "industry": "fragrance"},
    {"prompt": "Sony PlayStation 5 Pro console", "brand": "Sony", "industry": "gaming"},
    {"prompt": "Dyson Airwrap multi-styler", "brand": "Dyson", "industry": "beauty_tech"},
    {"prompt": "Levi's 501 original fit jeans", "brand": "Levi's", "industry": "fashion"},
    {"prompt": "Nespresso Vertuo Pop coffee machine", "brand": "Nespresso", "industry": "appliances"},
]


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("generate_preference_data")


def setup_pipeline():
    """Instantiate generator, scorer, ab engine, and feedback loop."""
    from ad_generator.generator import AdGenerator
    from ad_generator.quality_scorer import AdQualityScorer
    from ad_generator.ab_testing import ABTestEngine
    from ad_generator.feedback_loop import FeedbackLoop

    api_key = os.getenv("OPENAI_API_KEY", "").strip() or None
    generator = AdGenerator(openai_api_key=api_key)
    scorer = AdQualityScorer(client=generator.openai_client)
    ab_engine = ABTestEngine(generator=generator, scorer=scorer)
    feedback_loop = FeedbackLoop()
    ab_engine.feedback_loop = feedback_loop

    return ab_engine, feedback_loop


def run_single_product(ab_engine, product_info: dict, num_variants: int) -> dict:
    """
    Run one A/B test for a single product.
    Returns summary dict with scores, gaps, and pair count.
    """
    prompt = product_info["prompt"]
    logger.info(f"Running A/B test: {prompt} ({num_variants} variants)")

    result = ab_engine.run_test(prompt, num_variants=num_variants)

    variants = result.get("variants", [])
    scores = [v.get("composite_score", 0) for v in variants]
    winner = result.get("winner", {})

    # Compute gaps between all pairs
    gaps = []
    for i in range(len(variants)):
        for j in range(i + 1, len(variants)):
            gap = abs(variants[i]["composite_score"] - variants[j]["composite_score"])
            if gap >= 5.0:  # Only meaningful pairs
                gaps.append(gap)

    summary = {
        "product": prompt,
        "brand": product_info.get("brand", ""),
        "industry": product_info.get("industry", ""),
        "num_variants": len(variants),
        "scores": scores,
        "winner_score": winner.get("score", 0),
        "winner_headline": winner.get("headline", ""),
        "avg_score": round(sum(scores) / max(len(scores), 1), 1),
        "pairs_collected": len(gaps),
        "gaps": gaps,
    }
    logger.info(
        f"  scores={scores}, winner={winner.get('score', 0):.1f}, "
        f"pairs_with_gap>5={len(gaps)}"
    )
    return summary


def main():
    parser = argparse.ArgumentParser(description="Batch A/B testing for preference pair generation")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run 2 products with 2 variants to verify pipeline (no full budget spend)",
    )
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        logger.error("OPENAI_API_KEY not set")
        sys.exit(1)

    if args.dry_run:
        products = PRODUCTS[:2]
        num_variants = 2
        logger.info("DRY RUN mode: 2 products × 2 variants")
    else:
        products = PRODUCTS
        num_variants = 3
        logger.info(f"FULL RUN: {len(products)} products × {num_variants} variants")

    logger.info("Initializing pipeline ...")
    ab_engine, feedback_loop = setup_pipeline()

    summaries = []
    failures = []

    for i, product_info in enumerate(products):
        logger.info(f"\n[{i + 1}/{len(products)}] {product_info['prompt']}")
        try:
            summary = run_single_product(ab_engine, product_info, num_variants)
            summaries.append(summary)
        except Exception as exc:
            logger.error(f"  FAILED: {exc}")
            logger.error(traceback.format_exc())
            failures.append({
                "product": product_info["prompt"],
                "error": str(exc),
                "traceback": traceback.format_exc(),
            })
            time.sleep(10)
            continue

    # ── End-of-run summary ──
    total = len(products)
    succeeded = len(summaries)
    failed = len(failures)
    total_pairs = feedback_loop.get_stats().get("total_preference_pairs", 0)

    all_gaps = [g for s in summaries for g in s.get("gaps", [])]
    avg_gap = round(sum(all_gaps) / max(len(all_gaps), 1), 1)
    widest = max(summaries, key=lambda s: max(s["gaps"]) if s["gaps"] else 0, default=None)
    narrowest = min(
        [s for s in summaries if s["gaps"]],
        key=lambda s: min(s["gaps"]),
        default=None,
    )

    print("\n" + "=" * 60)
    print("BATCH A/B TESTING COMPLETE")
    print("=" * 60)
    print(f"  Products tested  : {total}")
    print(f"  Succeeded        : {succeeded}")
    print(f"  Failed           : {failed}")
    print(f"  Preference pairs : {total_pairs}")
    print(f"  Avg score gap    : {avg_gap}")
    if widest and widest["gaps"]:
        print(f"  Widest gap       : {max(widest['gaps']):.1f} ({widest['product']})")
    if narrowest and narrowest["gaps"]:
        print(f"  Narrowest gap    : {min(narrowest['gaps']):.1f} ({narrowest['product']})")

    if failures:
        print(f"\n  Failures:")
        for f in failures:
            print(f"    - {f['product']}: {f['error']}")
    print("=" * 60)

    # ── Save batch report ──
    Path("data/feedback_loop").mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"data/feedback_loop/batch_run_{ts}.json"
    report = {
        "run_at": datetime.now().isoformat(),
        "dry_run": args.dry_run,
        "total_products": total,
        "succeeded": succeeded,
        "failed": failed,
        "total_pairs_collected": total_pairs,
        "avg_score_gap": avg_gap,
        "summaries": summaries,
        "failures": failures,
    }
    with open(report_path, "w") as fp:
        json.dump(report, fp, indent=2, default=str)
    logger.info(f"Batch report saved: {report_path}")

    # ── Dry-run verification ──
    if args.dry_run:
        print("\n[dry-run verification]")
        pairs_dir = Path("data/feedback_loop/preference_pairs")
        pair_files = list(pairs_dir.glob("*.json")) if pairs_dir.exists() else []
        print(f"  Pair files on disk: {len(pair_files)}")
        if total_pairs == 0:
            print("  WARN: 0 preference pairs collected — check score gaps and pipeline")
        else:
            print(f"  {total_pairs} pairs collected ✓")
            print(f"  Dry run PASSED — safe to run full batch")

    logger.info("Done.")


if __name__ == "__main__":
    main()
