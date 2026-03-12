"""
AdCraft Pro — Automated A/B Testing Engine

Generates multiple ad variants, scores each one with AdQualityScorer,
ranks them by composite score, and explains why the winner won.

Usage:
    from ad_generator.generator import AdGenerator
    from ad_generator.quality_scorer import AdQualityScorer
    from ad_generator.ab_testing import ABTestEngine

    g = AdGenerator()
    scorer = AdQualityScorer(client=g.openai_client)
    ab = ABTestEngine(generator=g, scorer=scorer)
    result = ab.run_test("Nike Air Jordan 1 streetwear sneakers", num_variants=3)
"""
import logging
import time
import uuid
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger("ABTestEngine")


class ABTestEngine:
    """
    Generates N ad variants, scores each with AdQualityScorer, and selects a winner.

    Each variant goes through the full pipeline independently:
    fine-tuned model → gpt-image-1 → image analysis → GPT-4o copy+HTML →
    Playwright render → Pillow composite → quality scoring.

    The generator's _used_styles list naturally discourages layout repetition
    between variants within the same session.
    """

    def __init__(self, generator, scorer):
        """
        Args:
            generator : AdGenerator instance (handles ad creation)
            scorer    : AdQualityScorer instance (handles scoring)
        """
        self.generator = generator
        self.scorer = scorer
        self.feedback_loop = None  # Set externally to enable preference pair collection

    def run_test(
        self,
        prompt: str,
        num_variants: int = 3,
        product_image_path: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate and evaluate multiple ad variants.

        Args:
            prompt             : Product/brand description string
            num_variants       : How many variants to generate (clamped 2-4)
            product_image_path : Optional path to a product photo
            **kwargs           : Forwarded to generator.create_ad (tone, visual_style, …)

        Returns:
            {
                "test_id"     : str,
                "product"     : str,
                "num_variants": int,
                "variants"    : [
                    {
                        "variant_id"     : str,
                        "ad_data"        : dict,   # copy fields, tone, style, …
                        "quality_report" : dict,   # full scoring breakdown
                        "composite_score": float,  # 0-100
                        "grade"          : str,    # A+ … F
                        "image_path"     : str,    # local filesystem path
                    },
                    …
                ],
                "winner"     : {
                    "variant_id": str,
                    "score"     : float,
                    "grade"     : str,
                    "margin"    : float,  # score gap above 2nd place
                    "headline"  : str,
                },
                "comparison" : {
                    "score_range"      : [min, max],
                    "avg_score"        : float,
                    "std_score"        : float,
                    "metric_comparison": {metric: [score_per_variant]},
                },
            }
        """
        num_variants = max(2, min(int(num_variants), 4))
        test_id = f"abtest_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        variants: List[Dict[str, Any]] = []

        for i in range(num_variants):
            variant_id = f"v{i + 1}_{uuid.uuid4().hex[:4]}"
            logger.info(
                "A/B test %s — generating variant %d/%d (%s)",
                test_id, i + 1, num_variants, variant_id,
            )

            try:
                result = self.generator.create_ad(
                    prompt,
                    product_image_path=product_image_path,
                    **kwargs,
                )

                base_image = result.get("_base_image")
                overlay_image = result.get("_overlay_image")
                final_path = result.get("final_path", "")

                if base_image is not None and overlay_image is not None:
                    composite_score, quality_report = self.scorer.score_ad(
                        base_image, overlay_image, result
                    )
                else:
                    logger.warning(
                        "Variant %s: PIL images missing from generator result; "
                        "scoring unavailable.",
                        variant_id,
                    )
                    composite_score = 0.0
                    quality_report = {
                        "composite_score": 0.0,
                        "grade": "N/A",
                        "metrics": {},
                        "strengths": [],
                        "weaknesses": [],
                        "recommendations": [],
                        "note": "PIL images not returned by generator — scoring skipped",
                    }

                # Strip private (_-prefixed) and non-serialisable fields
                ad_data = {
                    k: v
                    for k, v in result.items()
                    if not k.startswith("_") and k != "image"
                }

                variants.append(
                    {
                        "variant_id": variant_id,
                        "ad_data": ad_data,
                        "quality_report": quality_report,
                        "composite_score": composite_score,
                        "grade": quality_report.get("grade", "N/A"),
                        "image_path": final_path,
                    }
                )
                logger.info(
                    "Variant %s scored %.1f (%s)",
                    variant_id, composite_score, quality_report.get("grade", "?"),
                )

            except Exception as exc:
                logger.error("Variant %s failed: %s", variant_id, exc, exc_info=True)
                variants.append(
                    {
                        "variant_id": variant_id,
                        "ad_data": {"error": str(exc)},
                        "quality_report": {
                            "composite_score": 0.0,
                            "grade": "F",
                            "metrics": {},
                            "strengths": [],
                            "weaknesses": [],
                            "recommendations": [],
                            "error": str(exc),
                        },
                        "composite_score": 0.0,
                        "grade": "F",
                        "image_path": "",
                    }
                )

        # Rank best → worst
        variants.sort(key=lambda v: v["composite_score"], reverse=True)

        winner = variants[0]
        runner_up = variants[1] if len(variants) > 1 else None
        margin = winner["composite_score"] - (runner_up["composite_score"] if runner_up else 0.0)

        # Per-metric comparison table
        metric_names = ["readability", "placement", "composition", "harmony", "copy"]
        metric_comparison: Dict[str, List[float]] = {}
        for metric in metric_names:
            metric_comparison[metric] = [
                v.get("quality_report", {}).get("metrics", {}).get(metric, {}).get("score", 0.0)
                for v in variants
            ]

        all_scores = [v["composite_score"] for v in variants]

        logger.info(
            "A/B test %s complete — winner: %s (%.1f, %s), margin: %.1f",
            test_id,
            winner["variant_id"],
            winner["composite_score"],
            winner["grade"],
            margin,
        )

        result = {
            "test_id": test_id,
            "product": prompt,
            "num_variants": len(variants),
            "variants": variants,
            "winner": {
                "variant_id": winner["variant_id"],
                "score": winner["composite_score"],
                "grade": winner["grade"],
                "margin": round(margin, 1),
                "headline": winner["ad_data"].get("headline", ""),
            },
            "comparison": {
                "score_range": [round(min(all_scores), 1), round(max(all_scores), 1)],
                "avg_score": round(float(np.mean(all_scores)), 1),
                "std_score": round(float(np.std(all_scores)), 1),
                "metric_comparison": metric_comparison,
            },
        }

        # Feed preference pairs into feedback loop if wired in
        if self.feedback_loop is not None:
            try:
                new_pairs = self.feedback_loop.collect_from_ab_test(result)
                logger.info(f"Collected {len(new_pairs)} preference pairs from A/B test {test_id}")
            except Exception as _fe:
                logger.warning(f"Feedback loop collection failed: {_fe}")

        return result
