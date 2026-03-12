"""
Step 4: Three-way model evaluation with statistical significance testing.

Evaluates three models on the same 10-product set:
  - Baseline: raw gpt-4.1-mini-2025-04-14 (no fine-tuning)
  - SFT: ft model from SFT_MODEL_ID
  - SFT+DPO: ft model from FINE_TUNED_MODEL_ID

Produces two output files:
  data/evaluations/three_way_comparison_{timestamp}.json
  data/evaluations/three_way_comparison_{timestamp}.md

Usage:
    python scripts/run_evaluation.py
"""
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import numpy as np
    from scipy import stats as scipy_stats
except ImportError:
    print("ERROR: numpy/scipy not installed")
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("run_evaluation")

EVAL_PRODUCTS = [
    {"prompt": "Rolex Submariner luxury dive watch", "industry": "Luxury", "tone": "Premium"},
    {"prompt": "Nike Air Jordan 1 streetwear sneakers", "industry": "Fashion", "tone": "Bold"},
    {"prompt": "Apple AirPods Pro wireless earbuds", "industry": "Technology", "tone": "Minimalist"},
    {"prompt": "Chanel No. 5 perfume fragrance", "industry": "Luxury", "tone": "Emotional"},
    {"prompt": "Oatly oat milk dairy alternative", "industry": "Food & Beverage", "tone": "Playful"},
    {"prompt": "Tesla Model S electric sedan", "industry": "Automotive", "tone": "Premium"},
    {"prompt": "Sony PlayStation 5 Pro gaming console", "industry": "Gaming", "tone": "Bold"},
    {"prompt": "Dyson Airwrap hair styling tool", "industry": "Beauty", "tone": "Premium"},
    {"prompt": "Levi's 501 Original jeans", "industry": "Fashion", "tone": "Raw"},
    {"prompt": "Nespresso Vertuo coffee machine", "industry": "Food & Beverage", "tone": "Premium"},
]

METRICS = ["readability", "placement", "composition", "harmony", "copy"]


def evaluate_model(generator, scorer, model_label: str, model_id: str) -> dict:
    """
    Run all eval products through a generator and score each result.
    Handles baseline failures gracefully.
    """
    logger.info(f"\n{'='*50}")
    logger.info(f"Evaluating: {model_label} ({model_id})")
    logger.info(f"{'='*50}")

    results = []
    for i, product_info in enumerate(EVAL_PRODUCTS):
        prompt = product_info["prompt"]
        logger.info(f"  [{i+1}/{len(EVAL_PRODUCTS)}] {prompt}")

        try:
            ad_result = generator.create_ad(
                prompt,
                tone=product_info.get("tone", ""),
            )

            base_image = ad_result.get("_base_image")
            overlay_image = ad_result.get("_overlay_image")

            if base_image and overlay_image:
                composite_score, quality_report = scorer.score_ad(
                    base_image, overlay_image, ad_result
                )
            else:
                composite_score = 0
                quality_report = {"error": "Images not returned by generator — scoring skipped"}

            results.append({
                "product": prompt,
                "industry": product_info.get("industry"),
                "headline": ad_result.get("headline", ""),
                "composite_score": composite_score,
                "quality_report": quality_report,
                "image_path": ad_result.get("final_path", ""),
                "tone": ad_result.get("tone", ""),
                "visual_style": ad_result.get("visual_style", ""),
                "baseline_failed_structured": False,
            })
            logger.info(f"    score={composite_score:.1f}")

        except json.JSONDecodeError as parse_exc:
            # Baseline frequently fails structured output parsing
            logger.warning(f"    baseline failed structured output for {prompt}: {parse_exc}")
            results.append({
                "product": prompt,
                "composite_score": 0,
                "quality_report": {"copy": {"score": 0}, "metrics": {}},
                "error": f"structured_parse_failure: {parse_exc}",
                "baseline_failed_structured": True,
            })

        except Exception as exc:
            logger.error(f"    FAILED: {exc}")
            results.append({
                "product": prompt,
                "composite_score": 0,
                "quality_report": {},
                "error": str(exc),
                "baseline_failed_structured": False,
            })

    scores = [r["composite_score"] for r in results if r.get("composite_score", 0) > 0]

    metric_stats = {}
    for metric in METRICS:
        vals = []
        for r in results:
            qr = r.get("quality_report", {})
            if isinstance(qr, dict) and "metrics" in qr:
                mv = qr["metrics"].get(metric, {})
                if isinstance(mv, dict) and "score" in mv:
                    vals.append(mv["score"])
        if vals:
            metric_stats[metric] = {
                "mean": round(float(np.mean(vals)), 1),
                "std": round(float(np.std(vals)), 1),
                "values": vals,
            }

    report = {
        "model_label": model_label,
        "model_id": model_id,
        "evaluated_at": datetime.now().isoformat(),
        "num_products": len(EVAL_PRODUCTS),
        "num_successful": len(scores),
        "num_failed": len(EVAL_PRODUCTS) - len(scores),
        "composite_stats": {
            "mean": round(float(np.mean(scores)), 1) if scores else 0.0,
            "std": round(float(np.std(scores)), 1) if scores else 0.0,
            "min": round(float(np.min(scores)), 1) if scores else 0.0,
            "max": round(float(np.max(scores)), 1) if scores else 0.0,
        },
        "metric_stats": metric_stats,
        "per_product_results": results,
    }
    return report


def welch_t_test(scores_a: list, scores_b: list) -> dict:
    if len(scores_a) < 2 or len(scores_b) < 2:
        return {"t_statistic": 0.0, "p_value": 1.0, "significant": False}
    t_stat, p_val = scipy_stats.ttest_ind(scores_b, scores_a, equal_var=False)
    return {
        "t_statistic": round(float(t_stat), 3),
        "p_value": round(float(p_val), 4),
        "significant": bool(p_val < 0.05),
    }


def sig_stars(p: float) -> str:
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "n.s."


def write_markdown_report(comparison: dict, out_path: str):
    baseline = comparison["baseline"]
    sft = comparison["sft"]
    dpo = comparison["sft_dpo"]
    pairs = comparison["pairwise"]

    lines = [
        "# Three-Way Model Evaluation Report",
        "",
        f"Generated: {comparison['evaluated_at']}",
        "",
        "## Composite Score Summary",
        "",
        "| Model | Mean ± Std | Min | Max | Successful |",
        "|-------|-----------|-----|-----|-----------|",
    ]

    for label, rep in [("Baseline (gpt-4.1-mini)", baseline), ("SFT", sft), ("SFT+DPO", dpo)]:
        cs = rep["composite_stats"]
        lines.append(
            f"| {label} | {cs['mean']} ± {cs['std']} | {cs['min']} | {cs['max']} | {rep['num_successful']}/{rep['num_products']} |"
        )

    lines += [
        "",
        "## Per-Metric Breakdown",
        "",
        "| Metric | Baseline | SFT | SFT+DPO |",
        "|--------|---------|-----|---------|",
    ]
    for metric in METRICS:
        b_mean = baseline.get("metric_stats", {}).get(metric, {}).get("mean", "N/A")
        s_mean = sft.get("metric_stats", {}).get(metric, {}).get("mean", "N/A")
        d_mean = dpo.get("metric_stats", {}).get(metric, {}).get("mean", "N/A")
        lines.append(f"| {metric.capitalize()} | {b_mean} | {s_mean} | {d_mean} |")

    lines += [
        "",
        "## Pairwise Statistical Significance (Welch's t-test)",
        "",
        "| Comparison | Δ Score | p-value | Significant |",
        "|-----------|---------|---------|-------------|",
    ]

    for key, (label_a, rep_a, label_b, rep_b) in [
        ("baseline_vs_sft", ("Baseline", baseline, "SFT", sft)),
        ("sft_vs_dpo", ("SFT", sft, "SFT+DPO", dpo)),
        ("baseline_vs_dpo", ("Baseline", baseline, "SFT+DPO", dpo)),
    ]:
        p = pairs[key]
        mean_a = rep_a["composite_stats"]["mean"]
        mean_b = rep_b["composite_stats"]["mean"]
        delta = round(mean_b - mean_a, 1)
        direction = "+" if delta >= 0 else ""
        stars = sig_stars(p["p_value"])
        lines.append(
            f"| {label_a} vs {label_b} | {direction}{delta} | {p['p_value']} | {stars} |"
        )

    lines += [
        "",
        "\\* p<0.05, \\** p<0.01, n.s. = not significant",
        "",
        "## Winner",
        "",
    ]

    models = [
        ("Baseline (gpt-4.1-mini)", baseline),
        ("SFT", sft),
        ("SFT+DPO", dpo),
    ]
    winner_label, winner_rep = max(models, key=lambda x: x[1]["composite_stats"]["mean"])
    lines.append(f"**{winner_label}** with mean composite score {winner_rep['composite_stats']['mean']}/100")
    lines.append("")

    lines += [
        "## Model Migration Note",
        "",
        "Migrated from deprecated `ft:gpt-4o-mini-2024-07-18` to `gpt-4.1-mini-2025-04-14`.",
        "gpt-4.1-mini supports DPO fine-tuning (gpt-4o-mini does not).",
        "",
        f"- SFT model: `{sft['model_id']}`",
        f"- SFT+DPO model: `{dpo['model_id']}`",
    ]

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Markdown report: {out_path}")


def main():
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        logger.error("OPENAI_API_KEY not set")
        sys.exit(1)

    sft_model_id = os.getenv("SFT_MODEL_ID", os.getenv("FINE_TUNED_MODEL_ID", "")).strip()
    dpo_model_id = os.getenv("FINE_TUNED_MODEL_ID", "").strip()
    baseline_model_id = "gpt-4.1-mini-2025-04-14"

    if not sft_model_id:
        logger.error("SFT_MODEL_ID not set. Run retrain_sft_model.py first.")
        sys.exit(1)

    if not dpo_model_id:
        logger.error("FINE_TUNED_MODEL_ID not set. Run run_dpo_training.py first.")
        sys.exit(1)

    logger.info(f"Baseline : {baseline_model_id}")
    logger.info(f"SFT      : {sft_model_id}")
    logger.info(f"SFT+DPO  : {dpo_model_id}")

    from ad_generator.generator import AdGenerator
    from ad_generator.quality_scorer import AdQualityScorer

    # --- Evaluate baseline ---
    baseline_gen = AdGenerator(openai_api_key=api_key)
    # Override fine_tuned_model_id to use raw base model (no fine-tuning)
    baseline_gen.fine_tuned_model_id = baseline_model_id
    scorer = AdQualityScorer(client=baseline_gen.openai_client)
    baseline_report = evaluate_model(baseline_gen, scorer, "baseline", baseline_model_id)

    # --- Evaluate SFT ---
    sft_gen = AdGenerator(openai_api_key=api_key)
    sft_gen.fine_tuned_model_id = sft_model_id
    sft_report = evaluate_model(sft_gen, scorer, "sft", sft_model_id)

    # --- Evaluate SFT+DPO ---
    dpo_gen = AdGenerator(openai_api_key=api_key)
    dpo_gen.fine_tuned_model_id = dpo_model_id
    dpo_report = evaluate_model(dpo_gen, scorer, "sft_dpo", dpo_model_id)

    # --- Pairwise t-tests ---
    def extract_scores(report):
        return [r["composite_score"] for r in report["per_product_results"] if r.get("composite_score", 0) > 0]

    b_scores = extract_scores(baseline_report)
    s_scores = extract_scores(sft_report)
    d_scores = extract_scores(dpo_report)

    pairwise = {
        "baseline_vs_sft": welch_t_test(b_scores, s_scores),
        "sft_vs_dpo": welch_t_test(s_scores, d_scores),
        "baseline_vs_dpo": welch_t_test(b_scores, d_scores),
    }

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    comparison = {
        "evaluated_at": datetime.now().isoformat(),
        "baseline": baseline_report,
        "sft": sft_report,
        "sft_dpo": dpo_report,
        "pairwise": pairwise,
    }

    out_dir = Path("data/evaluations")
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / f"three_way_comparison_{ts}.json"
    with open(json_path, "w") as f:
        json.dump(comparison, f, indent=2, default=str)
    logger.info(f"JSON report: {json_path}")

    md_path = str(out_dir / f"three_way_comparison_{ts}.md")
    write_markdown_report(comparison, md_path)

    # --- Print summary ---
    print("\n" + "=" * 60)
    print("THREE-WAY EVALUATION SUMMARY")
    print("=" * 60)
    for label, rep in [("Baseline", baseline_report), ("SFT", sft_report), ("SFT+DPO", dpo_report)]:
        cs = rep["composite_stats"]
        print(f"  {label:12s}: {cs['mean']} ± {cs['std']}  ({rep['num_successful']}/{rep['num_products']} succeeded)")

    print("\n  Pairwise significance:")
    for key, result in pairwise.items():
        stars = sig_stars(result["p_value"])
        print(f"    {key}: p={result['p_value']}  {stars}")

    print(f"\n  Reports saved to {out_dir}/")
    print("=" * 60)
    print(f"\n[done] Evaluation complete. Next step: run scripts/generate_portfolio.py")


if __name__ == "__main__":
    main()
