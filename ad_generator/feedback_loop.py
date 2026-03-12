"""
Feedback Loop: Collects preference pairs from ad generation for model improvement.

Sources of preference signal:
1. Automated quality scores (WCAG contrast, placement, composition, copy quality)
2. User ratings (1-5 stars from frontend feedback)
3. A/B test results (winner vs loser variants)

Output: Preference pairs in a format ready for DPO dataset building.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class FeedbackLoop:
    """
    Collects and manages preference data for model improvement.

    The feedback loop works in three stages:
    1. COLLECT: Gather quality scores and user feedback from generated ads
    2. PAIR: Create preference pairs (preferred vs non-preferred outputs for the same input)
    3. EXPORT: Format pairs for DPO training
    """

    def __init__(self, data_dir: str = "data/feedback_loop"):
        self.data_dir = data_dir
        self.pairs_dir = os.path.join(data_dir, "preference_pairs")
        self.raw_dir = os.path.join(data_dir, "raw_feedback")
        self.exports_dir = os.path.join(data_dir, "exports")

        for d in [self.data_dir, self.pairs_dir, self.raw_dir, self.exports_dir]:
            os.makedirs(d, exist_ok=True)

        self.preference_pairs = self._load_existing_pairs()
        logger.info(f"FeedbackLoop initialized with {len(self.preference_pairs)} existing preference pairs")

    def _load_existing_pairs(self) -> List[Dict]:
        """Load all previously saved preference pairs."""
        pairs = []
        for f in Path(self.pairs_dir).glob("*.json"):
            try:
                with open(f) as fh:
                    pairs.append(json.load(fh))
            except Exception as e:
                logger.warning(f"Failed to load {f}: {e}")
        return pairs

    def collect_from_ab_test(self, ab_test_result: Dict) -> List[Dict]:
        """
        Extract preference pairs from an A/B test result.

        An A/B test with N variants produces N*(N-1)/2 preference pairs.
        For 3 variants, that's 3 pairs:
        - variant1 vs variant2
        - variant1 vs variant3
        - variant2 vs variant3

        The variant with the higher composite quality score is "preferred."

        We only create pairs where the score difference is meaningful (>5 points).
        Pairs with very close scores are ambiguous and would add noise to training.

        Args:
            ab_test_result: Output from ABTestEngine.run_test()

        Returns:
            List of preference pair dicts
        """
        variants = ab_test_result.get("variants", [])
        product = ab_test_result.get("product", "")
        test_id = ab_test_result.get("test_id", "")

        if len(variants) < 2:
            logger.warning(f"Need at least 2 variants for preference pairs, got {len(variants)}")
            return []

        new_pairs = []
        min_score_difference = 5.0  # Minimum score gap to consider a meaningful preference

        for i in range(len(variants)):
            for j in range(i + 1, len(variants)):
                v_a = variants[i]
                v_b = variants[j]

                score_a = v_a.get("composite_score", 0)
                score_b = v_b.get("composite_score", 0)

                score_diff = abs(score_a - score_b)

                if score_diff < min_score_difference:
                    logger.debug(
                        f"Skipping pair — score difference {score_diff:.1f} < {min_score_difference} threshold"
                    )
                    continue

                # Determine preferred and non-preferred
                if score_a > score_b:
                    preferred = v_a
                    non_preferred = v_b
                else:
                    preferred = v_b
                    non_preferred = v_a

                pair = {
                    "pair_id": f"pair_{test_id}_{i}_{j}",
                    "source": "ab_test_quality_score",
                    "product_prompt": product,
                    "score_difference": round(score_diff, 1),
                    "preferred": {
                        "variant_id": preferred.get("variant_id"),
                        "composite_score": preferred.get("composite_score"),
                        "grade": preferred.get("grade"),
                        "creative_brief": self._extract_creative_brief(preferred.get("ad_data", {})),
                        "quality_breakdown": {
                            metric: preferred.get("quality_report", {}).get("metrics", {}).get(metric, {}).get("score", 0)
                            for metric in ["readability", "placement", "composition", "harmony", "copy"]
                        },
                    },
                    "non_preferred": {
                        "variant_id": non_preferred.get("variant_id"),
                        "composite_score": non_preferred.get("composite_score"),
                        "grade": non_preferred.get("grade"),
                        "creative_brief": self._extract_creative_brief(non_preferred.get("ad_data", {})),
                        "quality_breakdown": {
                            metric: non_preferred.get("quality_report", {}).get("metrics", {}).get(metric, {}).get("score", 0)
                            for metric in ["readability", "placement", "composition", "harmony", "copy"]
                        },
                    },
                    "created_at": datetime.now().isoformat(),
                    "metadata": {
                        "test_id": test_id,
                        "num_variants": len(variants),
                        "scoring_weights": (
                            ab_test_result.get("variants", [{}])[0]
                            .get("quality_report", {})
                            .get("weights", {})
                        ),
                    },
                }

                pair_path = os.path.join(self.pairs_dir, f"{pair['pair_id']}.json")
                with open(pair_path, "w") as f:
                    json.dump(pair, f, indent=2, default=str)

                self.preference_pairs.append(pair)
                new_pairs.append(pair)

                logger.info(
                    f"Created preference pair: "
                    f"preferred={preferred.get('composite_score', 0):.1f} "
                    f"vs non_preferred={non_preferred.get('composite_score', 0):.1f} "
                    f"(diff={score_diff:.1f})"
                )

        return new_pairs

    def collect_from_user_feedback(self, ad_data: Dict, rating: int, feedback_text: str = ""):
        """
        Record user feedback for a generated ad.

        Ratings 4-5 are considered positive signal.
        Ratings 1-2 are considered negative signal.
        Rating 3 is neutral and ignored for preference pairing.

        User feedback is paired with other ads for the same product category
        that have opposite ratings.

        Args:
            ad_data: The full ad result dict
            rating: 1-5 star rating
            feedback_text: Optional text feedback
        """
        feedback_entry = {
            "feedback_id": f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            "rating": rating,
            "feedback_text": feedback_text,
            "is_positive": rating >= 4,
            "is_negative": rating <= 2,
            "creative_brief": self._extract_creative_brief(ad_data),
            "product": ad_data.get("product", ""),
            "brand": ad_data.get("brand_name", ""),
            "industry": ad_data.get("industry", ""),
            "quality_score": ad_data.get("quality_report", {}).get("composite_score", 0)
            if isinstance(ad_data.get("quality_report"), dict)
            else 0,
            "created_at": datetime.now().isoformat(),
        }

        fb_path = os.path.join(self.raw_dir, f"{feedback_entry['feedback_id']}.json")
        with open(fb_path, "w") as f:
            json.dump(feedback_entry, f, indent=2, default=str)

        logger.info(f"Recorded user feedback: rating={rating}, product={ad_data.get('product', '')}")

        self._try_pair_user_feedback(feedback_entry)

    def _try_pair_user_feedback(self, new_feedback: Dict):
        """
        Try to create preference pairs by matching positive and negative feedback
        for similar products/industries.
        """
        all_feedback = []
        for f in Path(self.raw_dir).glob("*.json"):
            try:
                with open(f) as fh:
                    all_feedback.append(json.load(fh))
            except Exception:
                continue

        if new_feedback["is_positive"]:
            matches = [
                fb
                for fb in all_feedback
                if fb["is_negative"]
                and fb.get("industry") == new_feedback.get("industry")
                and fb["feedback_id"] != new_feedback["feedback_id"]
            ]

            for match in matches:
                pair_id = f"pair_userfb_{new_feedback['feedback_id']}_{match['feedback_id']}"
                # Avoid duplicate pairs
                if any(p.get("pair_id") == pair_id for p in self.preference_pairs):
                    continue

                pair = {
                    "pair_id": pair_id,
                    "source": "user_feedback",
                    "product_prompt": new_feedback.get("product", ""),
                    "score_difference": abs(new_feedback["rating"] - match["rating"]),
                    "preferred": {
                        "creative_brief": new_feedback["creative_brief"],
                        "user_rating": new_feedback["rating"],
                        "composite_score": new_feedback.get("quality_score", 0),
                    },
                    "non_preferred": {
                        "creative_brief": match["creative_brief"],
                        "user_rating": match["rating"],
                        "composite_score": match.get("quality_score", 0),
                    },
                    "created_at": datetime.now().isoformat(),
                }

                pair_path = os.path.join(self.pairs_dir, f"{pair['pair_id']}.json")
                with open(pair_path, "w") as f:
                    json.dump(pair, f, indent=2, default=str)

                self.preference_pairs.append(pair)
                logger.info(
                    f"Created user feedback preference pair: "
                    f"rating {new_feedback['rating']} vs {match['rating']}"
                )

    def _extract_creative_brief(self, ad_data: Dict) -> Dict:
        """Extract the creative brief fields that the fine-tuned model outputs."""
        brief_fields = [
            "tone", "visual_style", "conceptual_technique", "emotion",
            "typography_style", "color_scheme", "visual_direction",
            "headline", "caption", "call_to_action", "ad_style",
            "target_market", "key_benefits", "product_highlight",
            "core_principles", "platform_context",
        ]
        return {k: ad_data.get(k, "") for k in brief_fields if ad_data.get(k)}

    def get_stats(self) -> Dict:
        """Return statistics about collected feedback data."""
        ab_pairs = [p for p in self.preference_pairs if p.get("source") == "ab_test_quality_score"]
        user_pairs = [p for p in self.preference_pairs if p.get("source") == "user_feedback"]

        raw_count = len(list(Path(self.raw_dir).glob("*.json")))

        score_diffs = [p.get("score_difference", 0) for p in self.preference_pairs]

        return {
            "total_preference_pairs": len(self.preference_pairs),
            "ab_test_pairs": len(ab_pairs),
            "user_feedback_pairs": len(user_pairs),
            "raw_feedback_entries": raw_count,
            "avg_score_difference": round(sum(score_diffs) / max(len(score_diffs), 1), 1),
            "max_score_difference": round(max(score_diffs) if score_diffs else 0, 1),
            "min_score_difference": round(min(score_diffs) if score_diffs else 0, 1),
            "ready_for_dpo": len(self.preference_pairs) >= 20,
            "recommended_min_pairs": 50,
            "data_dir": self.data_dir,
        }
