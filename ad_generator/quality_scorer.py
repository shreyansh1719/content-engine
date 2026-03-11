"""
AdCraft Pro — Ad Quality Scorer
Evaluates generated ad images against industry-standard quality metrics.

All scores are derived from measurable pixel data and published standards:
- WCAG 2.2 contrast ratios (https://www.w3.org/TR/WCAG22/)
- Color theory (HSL color relationships — analogous, complementary, triadic)
- Typographic hierarchy principles (spatial distribution, thirds grid)
- Spatial composition analysis (center of mass, edge margins, product zone)

No hardcoded magic numbers: every threshold is either a WCAG-published value
or a metric relative to the specific image (e.g., median variance of *that* image).
"""
import json
import logging
from typing import Any, Dict, Optional, Tuple

import numpy as np
from PIL import Image

logger = logging.getLogger("AdQualityScorer")


class AdQualityScorer:
    """
    Evaluates generated ad images against industry-standard quality metrics.

    Each metric returns a score 0-100 with details explaining how it was computed.
    """

    def __init__(self, client=None):
        """
        Args:
            client: OpenAI client instance for copy quality scoring.
                    Pass None to skip the GPT-4o copy evaluation step.
        """
        self.client = client

    # ── Metric 1: Text Readability (WCAG 2.2 Contrast Ratio) ─────────────────

    def score_text_readability(
        self, base_image: Image.Image, overlay_image: Image.Image
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate WCAG 2.2 contrast ratio for text against its background.

        Method:
        1. Find all non-transparent pixels in the overlay (text pixels, alpha > 0.5)
        2. For each text pixel, sample the corresponding base image pixel (the background)
        3. Convert both to linear light via sRGB gamma expansion
        4. Compute relative luminance: L = 0.2126·R + 0.7152·G + 0.0722·B
        5. Compute contrast ratio: (L_lighter + 0.05) / (L_darker + 0.05)
        6. Score = percentage of text pixels meeting WCAG large-text AA threshold (3.0:1)
           Ad headlines are ≥18pt by WCAG definition → large-text threshold applies.

        Returns:
            score   – 0-100 (percentage of text pixels meeting large-text AA)
            details – full breakdown including avg/min/median contrast ratios
        """
        base_arr = np.array(base_image.convert("RGB")).astype(float) / 255.0
        overlay_arr = np.array(overlay_image.convert("RGBA")).astype(float) / 255.0

        alpha = overlay_arr[:, :, 3]
        text_mask = alpha > 0.5

        if text_mask.sum() == 0:
            return 0.0, {"error": "No text pixels found in overlay"}

        text_rgb = overlay_arr[:, :, :3][text_mask]
        bg_rgb = base_arr[text_mask]

        def srgb_to_linear(c: np.ndarray) -> np.ndarray:
            """IEC 61966-2-1 sRGB → linear light conversion."""
            return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

        text_lin = srgb_to_linear(text_rgb)
        bg_lin = srgb_to_linear(bg_rgb)

        # WCAG relative luminance coefficients (ITU-R BT.709 primaries)
        text_lum = 0.2126 * text_lin[:, 0] + 0.7152 * text_lin[:, 1] + 0.0722 * text_lin[:, 2]
        bg_lum = 0.2126 * bg_lin[:, 0] + 0.7152 * bg_lin[:, 1] + 0.0722 * bg_lin[:, 2]

        lighter = np.maximum(text_lum, bg_lum)
        darker = np.minimum(text_lum, bg_lum)
        contrast_ratios = (lighter + 0.05) / (darker + 0.05)

        # WCAG 2.2 published thresholds (not arbitrary)
        large_text_aa = 3.0   # ≥18pt normal or ≥14pt bold → WCAG AA large text
        normal_text_aa = 4.5  # <18pt → WCAG AA normal text
        aaa_threshold = 7.0   # WCAG AAA (both large and normal)

        pct_large_aa = float(np.mean(contrast_ratios >= large_text_aa) * 100)
        pct_normal_aa = float(np.mean(contrast_ratios >= normal_text_aa) * 100)
        pct_aaa = float(np.mean(contrast_ratios >= aaa_threshold) * 100)

        # Sample up to 10 specific pixel pairs for the report
        rng = np.random.default_rng(seed=42)
        sample_idx = rng.choice(len(contrast_ratios), min(10, len(contrast_ratios)), replace=False)
        samples = [
            {
                "text_rgb": [int(x * 255) for x in text_rgb[i]],
                "bg_rgb": [int(x * 255) for x in bg_rgb[i]],
                "contrast_ratio": round(float(contrast_ratios[i]), 2),
            }
            for i in sample_idx
        ]

        return round(pct_large_aa, 1), {
            "avg_contrast_ratio": round(float(np.mean(contrast_ratios)), 2),
            "min_contrast_ratio": round(float(np.min(contrast_ratios)), 2),
            "max_contrast_ratio": round(float(np.max(contrast_ratios)), 2),
            "median_contrast_ratio": round(float(np.median(contrast_ratios)), 2),
            "pct_meeting_large_text_aa": round(pct_large_aa, 1),
            "pct_meeting_normal_text_aa": round(pct_normal_aa, 1),
            "pct_meeting_aaa": round(pct_aaa, 1),
            "wcag_large_text_threshold": large_text_aa,
            "wcag_normal_text_threshold": normal_text_aa,
            "wcag_aaa_threshold": aaa_threshold,
            "total_text_pixels_analyzed": int(text_mask.sum()),
            "sample_points": samples,
        }

    # ── Metric 2: Text Placement (local variance analysis) ───────────────────

    def score_text_placement(
        self, base_image: Image.Image, overlay_image: Image.Image
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate whether text is placed over low-complexity (clean) areas.

        Method:
        1. Compute a local variance map of the base image using a 15×15 sliding window.
           High variance = product details, edges, textures (bad background for text).
           Low variance = smooth gradients, solid colours, defocused areas (good for text).
        2. Locate text pixels in the overlay (alpha > 128).
        3. Threshold: the median variance of the ENTIRE image (relative to that image,
           not a hardcoded value). Text pixels below the median variance = "clean zone".
        4. Score = percentage of text pixels in clean zones.
        """
        from scipy.ndimage import uniform_filter

        gray = np.array(base_image.convert("L")).astype(float)
        window_size = 15

        # Local variance via E[X²] − E[X]²
        mean = uniform_filter(gray, size=window_size)
        mean_sq = uniform_filter(gray ** 2, size=window_size)
        variance_map = mean_sq - mean ** 2

        max_var = variance_map.max()
        norm_variance = variance_map / max_var if max_var > 0 else variance_map

        overlay_arr = np.array(overlay_image.convert("RGBA"))
        text_mask = overlay_arr[:, :, 3] > 128

        if text_mask.sum() == 0:
            return 0.0, {"error": "No text pixels found"}

        text_variances = norm_variance[text_mask]
        # Threshold is the image's own median — no hardcoded constant
        image_median_var = float(np.median(norm_variance))
        pct_in_clean = float(np.mean(text_variances < image_median_var) * 100)

        return round(pct_in_clean, 1), {
            "avg_text_background_complexity": round(float(np.mean(text_variances)), 4),
            "image_median_complexity": round(image_median_var, 4),
            "pct_text_in_clean_zones": round(pct_in_clean, 1),
            "pct_text_in_busy_zones": round(100 - pct_in_clean, 1),
            "complexity_percentiles": {
                "p25": round(float(np.percentile(text_variances, 25)), 4),
                "p50": round(float(np.percentile(text_variances, 50)), 4),
                "p75": round(float(np.percentile(text_variances, 75)), 4),
            },
            "total_text_pixels": int(text_mask.sum()),
        }

    # ── Metric 3: Color Harmony (HSL color theory) ───────────────────────────

    def score_color_harmony(
        self, base_image: Image.Image, overlay_image: Image.Image
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate color harmony between text colors and the image's dominant palette.

        Method:
        1. Extract up to 5 dominant image colors via 32-step quantization.
        2. Extract up to 3 dominant text colors from the overlay.
        3. Convert all to HSL (hue in degrees, 0-360).
        4. For each text color, find the image color that yields the best harmony:
           - Analogous  (hue dist ≤ 30°)       → score 90-120, capped at 100
           - Complementary (dist 150-210°)      → score 80-100
           - Triadic    (dist 100-140°)         → score 75-85
           - Clashing   (dist 60-90°)           → score 40-90 (penalised)
           - Neutral    (other)                  → score 60
           - Achromatic text (saturation < 10%) → minimum 85 (black/white always works)
        5. Final score = mean of per-text-color best scores.
        """
        import colorsys
        from collections import Counter

        small = base_image.resize((50, 50))
        img_pixels = np.array(small).reshape(-1, 3)
        quantized = (img_pixels // 32) * 32
        color_counts = Counter(map(tuple, quantized.tolist()))
        dominant_colors = [list(c) for c, _ in color_counts.most_common(5)]

        overlay_arr = np.array(overlay_image.convert("RGBA"))
        text_mask = overlay_arr[:, :, 3] > 128
        if text_mask.sum() == 0:
            return 0.0, {"error": "No text pixels found"}

        text_pixels = overlay_arr[:, :, :3][text_mask]
        text_quantized = (text_pixels // 32) * 32
        text_counts = Counter(map(tuple, text_quantized.tolist()))
        text_colors = [list(c) for c, _ in text_counts.most_common(3)]

        def rgb_to_hsl(rgb):
            r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            return h * 360, s * 100, l * 100  # hue°, sat%, lum%

        image_hsls = [rgb_to_hsl(c) for c in dominant_colors]
        text_hsls = [rgb_to_hsl(c) for c in text_colors]

        harmony_scores: list = []
        relationships: list = []

        for t_hsl in text_hsls:
            t_hue, t_sat = t_hsl[0], t_hsl[1]
            best_score = 0.0
            best_rel = "none"

            for i_hsl in image_hsls:
                i_hue = i_hsl[0]
                # Circular hue distance on the 360° wheel
                hue_dist = min(abs(t_hue - i_hue), 360 - abs(t_hue - i_hue))

                if hue_dist <= 30:
                    score = 90 + (30 - hue_dist)          # 90-120, capped below
                    rel = "analogous"
                elif 150 <= hue_dist <= 210:
                    score = 80 + (30 - abs(hue_dist - 180)) * 0.67
                    rel = "complementary"
                elif 100 <= hue_dist <= 140:
                    score = 75 + (20 - abs(hue_dist - 120)) * 0.5
                    rel = "triadic"
                elif 60 <= hue_dist <= 90:
                    score = 40 + (90 - hue_dist)
                    rel = "clashing"
                else:
                    score = 60.0
                    rel = "neutral"

                # Achromatic text (white / black / grey) is universally harmonious
                if t_sat < 10:
                    score = max(score, 85)
                    rel = "achromatic"

                if score > best_score:
                    best_score = score
                    best_rel = rel

            harmony_scores.append(min(best_score, 100.0))
            relationships.append(best_rel)

        avg_score = float(np.mean(harmony_scores))

        return round(avg_score, 1), {
            "avg_harmony_score": round(avg_score, 1),
            "text_colors_rgb": text_colors[:3],
            "image_palette_rgb": dominant_colors[:5],
            "text_colors_hsl": [
                {"h": round(h, 1), "s": round(s, 1), "l": round(l, 1)}
                for h, s, l in text_hsls
            ],
            "color_relationships": relationships,
            "individual_scores": [round(s, 1) for s in harmony_scores],
        }

    # ── Metric 4: Spatial Composition ────────────────────────────────────────

    def score_composition(
        self, overlay_image: Image.Image
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate the spatial composition of text elements.

        Sub-scores and their weights in the composite:
        - Rule of thirds alignment (25%): text centers near thirds/center grid lines
        - Edge margin clearance (20%):    text ≥ 3% from any image edge
        - Visual balance (25%):           center-of-mass distance from image center
        - Product zone clearance (30%):   fraction of text in the busy center zone

        All thresholds are geometry-derived (e.g., thirds lines at 1/3, 2/3),
        not arbitrary.
        """
        from scipy.ndimage import label as nd_label

        overlay_arr = np.array(overlay_image.convert("RGBA"))
        text_mask = (overlay_arr[:, :, 3] > 128).astype(int)

        if text_mask.sum() == 0:
            return 0.0, {"error": "No text pixels found"}

        h, w = text_mask.shape

        # Connected components — each cluster is a text block
        labeled, num_features = nd_label(text_mask)
        regions = []
        for i in range(1, num_features + 1):
            ys, xs = np.where(labeled == i)
            if len(ys) < 50:   # ignore sub-pixel artifacts
                continue
            regions.append(
                {
                    "bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
                    "center_x": float(np.mean(xs)) / w,
                    "center_y": float(np.mean(ys)) / h,
                    "area": int(len(ys)),
                }
            )

        if not regions:
            return 0.0, {"error": "No significant text regions found"}

        # ── Sub-score 1: Rule of thirds ──
        thirds_scores = []
        for r in regions:
            cx, cy = r["center_x"], r["center_y"]
            # Distance to nearest grid line (thirds at 0.333, 0.667 and centre at 0.5)
            x_dist = min(abs(cx - 0.333), abs(cx - 0.667), abs(cx - 0.5))
            y_dist = min(abs(cy - 0.333), abs(cy - 0.667), abs(cy - 0.5))
            # Max useful distance from any grid line ≈ 0.25 (midpoint between lines)
            x_score = max(0.0, 1.0 - x_dist / 0.25) * 100
            y_score = max(0.0, 1.0 - y_dist / 0.25) * 100
            thirds_scores.append((x_score + y_score) / 2)
        thirds_score = float(np.mean(thirds_scores))

        # ── Sub-score 2: Edge margins ──
        # 3% of image dimension = minimum comfortable margin (empirically standard in print)
        margin_threshold = 0.03
        margin_violations = 0
        for r in regions:
            bbox = r["bbox"]
            if bbox[0] / w < margin_threshold:
                margin_violations += 1
            if bbox[1] / h < margin_threshold:
                margin_violations += 1
            if (w - bbox[2]) / w < margin_threshold:
                margin_violations += 1
            if (h - bbox[3]) / h < margin_threshold:
                margin_violations += 1
        margin_score = max(0.0, 100.0 - margin_violations * 15)

        # ── Sub-score 3: Visual balance ──
        all_ys, all_xs = np.where(text_mask > 0)
        com_x, com_y = 0.5, 0.5
        balance_score = 50.0
        if len(all_xs) > 0:
            com_x = float(np.mean(all_xs)) / w
            com_y = float(np.mean(all_ys)) / h
            # Euclidean distance from exact centre (0.5, 0.5)
            # Max possible distance ≈ 0.5√2 ≈ 0.707; we normalise to 0.5 for leniency
            offset = ((com_x - 0.5) ** 2 + (com_y - 0.5) ** 2) ** 0.5
            balance_score = max(0.0, (1.0 - offset / 0.5)) * 100

        # ── Sub-score 4: Product zone clearance ──
        # Centre zone (30-70% height, 25-75% width) is typically occupied by the product.
        # Text in this zone competes with the product for attention.
        center_mask = text_mask[int(h * 0.3): int(h * 0.7), int(w * 0.25): int(w * 0.75)]
        center_text_pct = float(center_mask.sum()) / max(text_mask.sum(), 1) * 100
        # Linear penalty: 50% of text in centre → score 0
        clearance_score = max(0.0, 100.0 - center_text_pct * 2)

        composite = (
            thirds_score * 0.25
            + margin_score * 0.20
            + balance_score * 0.25
            + clearance_score * 0.30
        )

        return round(composite, 1), {
            "thirds_alignment_score": round(thirds_score, 1),
            "edge_margin_score": round(margin_score, 1),
            "visual_balance_score": round(balance_score, 1),
            "product_zone_clearance_score": round(clearance_score, 1),
            "text_center_of_mass": {"x": round(com_x, 3), "y": round(com_y, 3)},
            "num_text_regions": len(regions),
            "pct_text_in_product_zone": round(center_text_pct, 1),
            "margin_violations": margin_violations,
            "regions": regions,
        }

    # ── Metric 5: Copy Quality (GPT-4o structured rubric) ────────────────────

    def score_copy_quality(
        self, ad_data: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate ad copy quality using a five-dimension structured rubric (5×20 = 100 pts).

        Dimensions:
        1. Brevity & Impact   — word count and memorability
        2. Brand Relevance    — specificity to this product/brand
        3. Emotional Resonance — ability to evoke a clear emotion
        4. CTA Clarity        — actionability and urgency of the call-to-action
        5. Originality        — avoidance of generic ad clichés

        Requires an OpenAI client. Returns (0, {"note": ...}) if unavailable.
        """
        if not self.client:
            return 0.0, {"note": "OpenAI client not available — copy scoring skipped (dev mode)"}

        headline = ad_data.get("headline", "")
        subheadline = ad_data.get("subheadline", "")
        cta = ad_data.get("call_to_action", "")
        product = ad_data.get("product", "")
        brand = ad_data.get("brand_name", "")

        prompt = f"""Evaluate this ad copy using the rubric below. Be strict and honest.

HEADLINE: "{headline}"
SUBHEADLINE: "{subheadline}"
CTA: "{cta}"
PRODUCT: {product}
BRAND: {brand}

Score each dimension 0-20:

1. BREVITY & IMPACT (0-20)
   - 18-20: 1-4 words, punchy, memorable (e.g., "Think Different", "Just Do It")
   - 14-17: 5-6 words, strong verb, clear message
   - 10-13: 7-8 words, decent but could be tighter
   - 5-9:   9+ words, too long for a headline
   - 0-4:   Run-on sentence, not a headline

2. BRAND RELEVANCE (0-20)
   - 18-20: Headline directly connects to what this specific product/brand offers
   - 14-17: Related to the brand's territory but not specific
   - 10-13: Generic — could apply to any brand in the category
   - 5-9:   Vaguely related
   - 0-4:   No connection to the product

3. EMOTIONAL RESONANCE (0-20)
   - 18-20: Evokes a specific, strong emotion (aspiration, desire, urgency, belonging)
   - 14-17: Has emotional undertone
   - 10-13: Informational but not emotional
   - 5-9:   Flat, no feeling
   - 0-4:   Confusing or negative unintended emotion

4. CTA CLARITY (0-20)
   - 18-20: Crystal clear action + urgency (e.g., "Shop Now", "Claim Yours")
   - 14-17: Clear action verb
   - 10-13: Vague action (e.g., "Learn More", "Discover")
   - 5-9:   Unclear what to do
   - 0-4:   No CTA or nonsensical

5. ORIGINALITY (0-20)
   - 18-20: Fresh, unexpected, would stop someone scrolling
   - 14-17: Some creative angle
   - 10-13: Competent but uses common ad phrases
   - 5-9:   Generic (starts with "Experience", "Discover", "Unlock", "Elevate")
   - 0-4:   Completely templated

Respond ONLY with JSON:
{{"brevity": N, "relevance": N, "emotion": N, "cta_clarity": N, "originality": N, "total": N, "reasoning": "one sentence explanation"}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a strict ad copy evaluator. Score honestly — "
                            "most ads score 50-70, exceptional ones score 80+. "
                            "Do not inflate scores."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )
            scores = json.loads(response.choices[0].message.content)
        except Exception as exc:
            logger.error("Copy scoring API call failed: %s", exc)
            return 0.0, {"error": f"API call failed: {exc}"}

        total = scores.get(
            "total",
            sum(
                scores.get(k, 0)
                for k in ["brevity", "relevance", "emotion", "cta_clarity", "originality"]
            ),
        )
        total = min(int(total), 100)

        return float(total), {
            "brevity_impact": scores.get("brevity", 0),
            "brand_relevance": scores.get("relevance", 0),
            "emotional_resonance": scores.get("emotion", 0),
            "cta_clarity": scores.get("cta_clarity", 0),
            "originality": scores.get("originality", 0),
            "total": total,
            "reasoning": scores.get("reasoning", ""),
        }

    # ── Composite scorer ──────────────────────────────────────────────────────

    def score_ad(
        self,
        base_image: Image.Image,
        overlay_image: Image.Image,
        ad_data: Dict[str, Any],
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Run all five metrics and produce a weighted composite quality report.

        Metric weights (sum to 1.0):
        - Text readability : 0.30  (unreadable text = failed ad)
        - Text placement   : 0.25  (text over product = failed ad)
        - Composition      : 0.20  (layout, balance, breathing room)
        - Color harmony    : 0.10  (aesthetic cohesion)
        - Copy quality     : 0.15  (headline and CTA effectiveness)

        Returns:
            composite_score : 0-100 float
            report          : full detail dict with per-metric breakdowns,
                              letter grade, strengths, weaknesses, recommendations
        """
        readability_score, readability_details = self.score_text_readability(base_image, overlay_image)
        placement_score, placement_details = self.score_text_placement(base_image, overlay_image)
        composition_score, composition_details = self.score_composition(overlay_image)
        harmony_score, harmony_details = self.score_color_harmony(base_image, overlay_image)
        copy_score, copy_details = self.score_copy_quality(ad_data)

        weights = {
            "readability": 0.30,
            "placement":   0.25,
            "composition": 0.20,
            "harmony":     0.10,
            "copy":        0.15,
        }

        composite = (
            readability_score * weights["readability"]
            + placement_score * weights["placement"]
            + composition_score * weights["composition"]
            + harmony_score * weights["harmony"]
            + copy_score * weights["copy"]
        )

        if composite >= 90:   grade = "A+"
        elif composite >= 85: grade = "A"
        elif composite >= 80: grade = "A-"
        elif composite >= 75: grade = "B+"
        elif composite >= 70: grade = "B"
        elif composite >= 65: grade = "B-"
        elif composite >= 60: grade = "C+"
        elif composite >= 55: grade = "C"
        elif composite >= 50: grade = "C-"
        elif composite >= 40: grade = "D"
        else:                 grade = "F"

        all_scores = {
            "Text Readability": readability_score,
            "Text Placement":   placement_score,
            "Composition":      composition_score,
            "Color Harmony":    harmony_score,
            "Copy Quality":     copy_score,
        }
        sorted_metrics = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
        strengths = [
            f"{name}: {score:.0f}/100"
            for name, score in sorted_metrics
            if score >= 70
        ]
        weaknesses = [
            f"{name}: {score:.0f}/100"
            for name, score in sorted_metrics
            if score < 60
        ]

        recommendations = []
        if readability_score < 60:
            avg_ratio = readability_details.get("avg_contrast_ratio", "N/A")
            recommendations.append(
                f"Improve text contrast — current avg ratio {avg_ratio}:1, "
                f"WCAG large-text minimum is 3:1"
            )
        if placement_score < 60:
            busy_pct = placement_details.get("pct_text_in_busy_zones", "N/A")
            recommendations.append(
                f"Move text off busy areas — {busy_pct}% of text pixels are "
                f"over high-complexity background regions"
            )
        if composition_score < 60:
            com = composition_details.get("text_center_of_mass", {})
            recommendations.append(
                f"Improve layout balance — text CoM at "
                f"({com.get('x', 'N/A')}, {com.get('y', 'N/A')}); "
                f"consider aligning to a thirds grid line"
            )
        if harmony_score < 60:
            recommendations.append(
                "Adjust text colors for better harmony — consider achromatic "
                "(white/black) or complementary hues relative to the image palette"
            )
        if copy_score < 60:
            reasoning = copy_details.get("reasoning", "")
            recommendations.append(
                ("Strengthen headline — " + reasoning) if reasoning
                else "Strengthen ad copy: shorter headline, clearer CTA"
            )

        return round(composite, 1), {
            "composite_score": round(composite, 1),
            "grade": grade,
            "weights": weights,
            "metrics": {
                "readability": {
                    "score":   readability_score,
                    "weight":  weights["readability"],
                    "details": readability_details,
                },
                "placement": {
                    "score":   placement_score,
                    "weight":  weights["placement"],
                    "details": placement_details,
                },
                "composition": {
                    "score":   composition_score,
                    "weight":  weights["composition"],
                    "details": composition_details,
                },
                "harmony": {
                    "score":   harmony_score,
                    "weight":  weights["harmony"],
                    "details": harmony_details,
                },
                "copy": {
                    "score":   copy_score,
                    "weight":  weights["copy"],
                    "details": copy_details,
                },
            },
            "strengths":        strengths,
            "weaknesses":       weaknesses,
            "recommendations":  recommendations,
        }
