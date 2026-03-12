"""
Model Evaluator: Compares model performance with statistical rigor.

Runs the same set of product prompts through different models (or model versions)
and compares quality scores to measure improvement.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Evaluates and compares model performance on ad generation.

    Methodology:
    1. Define a fixed evaluation set of product prompts (diverse industries)
    2. Run each prompt through each model version
    3. Score each output with AdQualityScorer
    4. Compute per-metric and composite statistics
    5. Run statistical significance tests
    """

    # Fixed evaluation set — same products every time for fair comparison
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

    def __init__(self, generator, scorer):
        self.generator = generator
        self.scorer = scorer
        self.results_dir = "data/evaluations"
        os.makedirs(self.results_dir, exist_ok=True)

    def evaluate_current_model(self, model_label: str = None, num_products: int = None) -> Dict:
        """
        Run the current model through the evaluation set and score results.

        Args:
            model_label: Label for this evaluation run (e.g., "sft_v1", "sft_dpo_v1")
            num_products: Number of products to evaluate (None = all 10)

        Returns:
            Detailed evaluation report
        """
        if model_label is None:
            model_label = f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        products = self.EVAL_PRODUCTS[:num_products] if num_products else self.EVAL_PRODUCTS

        results = []
        for i, product_info in enumerate(products):
            prompt = product_info["prompt"]
            logger.info(f"Evaluating [{i+1}/{len(products)}]: {prompt}")

            try:
                ad_result = self.generator.create_ad(
                    prompt,
                    tone=product_info.get("tone", ""),
                    industry=product_info.get("industry", ""),
                )

                base_image = ad_result.get("_base_image")
                overlay_image = ad_result.get("_overlay_image")

                if base_image and overlay_image:
                    composite_score, quality_report = self.scorer.score_ad(
                        base_image, overlay_image, ad_result
                    )
                else:
                    composite_score = 0
                    quality_report = {"error": "Images not available for scoring"}

                results.append({
                    "product": prompt,
                    "industry": product_info.get("industry"),
                    "headline": ad_result.get("headline", ""),
                    "composite_score": composite_score,
                    "quality_report": quality_report,
                    "image_path": ad_result.get("final_path", ""),
                    "creative_brief_tone": ad_result.get("tone", ""),
                    "creative_brief_style": ad_result.get("visual_style", ""),
                })

            except Exception as e:
                logger.error(f"Failed to evaluate {prompt}: {e}")
                results.append({
                    "product": prompt,
                    "error": str(e),
                    "composite_score": 0,
                })

        scores = [r["composite_score"] for r in results if r.get("composite_score", 0) > 0]

        metric_scores = {}
        for metric in ["readability", "placement", "composition", "harmony", "copy"]:
            metric_vals = []
            for r in results:
                qr = r.get("quality_report", {})
                if isinstance(qr, dict) and "metrics" in qr:
                    val = qr["metrics"].get(metric, {})
                    if isinstance(val, dict):
                        metric_vals.append(val.get("score", 0))
            if metric_vals:
                metric_scores[metric] = {
                    "mean": round(float(np.mean(metric_vals)), 1),
                    "std": round(float(np.std(metric_vals)), 1),
                    "min": round(float(np.min(metric_vals)), 1),
                    "max": round(float(np.max(metric_vals)), 1),
                    "median": round(float(np.median(metric_vals)), 1),
                }

        report = {
            "model_label": model_label,
            "model_id": getattr(self.generator, "fine_tuned_model_id", "unknown"),
            "evaluated_at": datetime.now().isoformat(),
            "num_products": len(products),
            "num_successful": len(scores),
            "num_failed": len(products) - len(scores),
            "composite_stats": {
                "mean": round(float(np.mean(scores)), 1) if scores else 0,
                "std": round(float(np.std(scores)), 1) if scores else 0,
                "min": round(float(np.min(scores)), 1) if scores else 0,
                "max": round(float(np.max(scores)), 1) if scores else 0,
                "median": round(float(np.median(scores)), 1) if scores else 0,
            },
            "metric_stats": metric_scores,
            "grade_distribution": self._compute_grade_distribution(scores),
            "per_product_results": results,
        }

        report_path = os.path.join(self.results_dir, f"{model_label}.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(
            f"Evaluation complete: mean={report['composite_stats']['mean']}, saved to {report_path}"
        )

        return report

    def compare_models(self, report_a_path: str, report_b_path: str) -> Dict:
        """
        Compare two evaluation reports and compute improvement metrics.

        Uses Welch's t-test for statistical significance.

        Args:
            report_a_path: Path to baseline evaluation report (e.g., SFT model)
            report_b_path: Path to comparison evaluation report (e.g., SFT+DPO model)

        Returns:
            Comparison report with improvement percentages and significance
        """
        with open(report_a_path) as f:
            report_a = json.load(f)
        with open(report_b_path) as f:
            report_b = json.load(f)

        scores_a = [
            r["composite_score"]
            for r in report_a["per_product_results"]
            if r.get("composite_score", 0) > 0
        ]
        scores_b = [
            r["composite_score"]
            for r in report_b["per_product_results"]
            if r.get("composite_score", 0) > 0
        ]

        if not scores_a or not scores_b:
            return {"error": "Insufficient data for comparison"}

        mean_a = float(np.mean(scores_a))
        mean_b = float(np.mean(scores_b))
        improvement = mean_b - mean_a
        improvement_pct = (improvement / mean_a * 100) if mean_a > 0 else 0

        # Welch's t-test for statistical significance
        from scipy import stats
        t_stat, p_value = stats.ttest_ind(scores_b, scores_a, equal_var=False)

        # Per-metric comparison
        metric_comparison = {}
        for metric in ["readability", "placement", "composition", "harmony", "copy"]:
            a_stats = report_a.get("metric_stats", {}).get(metric, {})
            b_stats = report_b.get("metric_stats", {}).get(metric, {})
            if a_stats and b_stats:
                a_mean = a_stats.get("mean", 0)
                b_mean = b_stats.get("mean", 0)
                metric_comparison[metric] = {
                    "model_a_mean": a_mean,
                    "model_b_mean": b_mean,
                    "improvement": round(b_mean - a_mean, 1),
                    "improvement_pct": round((b_mean - a_mean) / max(a_mean, 1) * 100, 1),
                }

        comparison = {
            "model_a": {
                "label": report_a.get("model_label"),
                "model_id": report_a.get("model_id"),
                "mean_score": round(mean_a, 1),
                "std": round(float(np.std(scores_a)), 1),
            },
            "model_b": {
                "label": report_b.get("model_label"),
                "model_id": report_b.get("model_id"),
                "mean_score": round(mean_b, 1),
                "std": round(float(np.std(scores_b)), 1),
            },
            "improvement": {
                "absolute": round(improvement, 1),
                "percentage": round(improvement_pct, 1),
                "direction": "improvement" if improvement > 0 else "regression",
            },
            "statistical_significance": {
                "t_statistic": round(float(t_stat), 3),
                "p_value": round(float(p_value), 4),
                "is_significant": bool(p_value < 0.05),
                "confidence_level": "95%" if p_value < 0.05 else "not significant",
            },
            "metric_comparison": metric_comparison,
            "compared_at": datetime.now().isoformat(),
        }

        comp_path = os.path.join(
            self.results_dir,
            f"comparison_{report_a.get('model_label', 'a')}_vs_{report_b.get('model_label', 'b')}.json",
        )
        with open(comp_path, "w") as f:
            json.dump(comparison, f, indent=2)

        logger.info(
            f"Comparison complete: {comparison['model_a']['label']} ({mean_a:.1f}) vs "
            f"{comparison['model_b']['label']} ({mean_b:.1f}), "
            f"improvement={improvement:.1f} ({'significant' if p_value < 0.05 else 'not significant'})"
        )

        return comparison

    def _compute_grade_distribution(self, scores: List[float]) -> Dict:
        """Compute distribution of letter grades."""
        grades: Dict[str, int] = {
            "A+": 0, "A": 0, "A-": 0, "B+": 0, "B": 0, "B-": 0,
            "C+": 0, "C": 0, "C-": 0, "D": 0, "F": 0,
        }
        for s in scores:
            if s >= 90:   grades["A+"] += 1
            elif s >= 85: grades["A"] += 1
            elif s >= 80: grades["A-"] += 1
            elif s >= 75: grades["B+"] += 1
            elif s >= 70: grades["B"] += 1
            elif s >= 65: grades["B-"] += 1
            elif s >= 60: grades["C+"] += 1
            elif s >= 55: grades["C"] += 1
            elif s >= 50: grades["C-"] += 1
            elif s >= 40: grades["D"] += 1
            else:         grades["F"] += 1
        return {k: v for k, v in grades.items() if v > 0}
