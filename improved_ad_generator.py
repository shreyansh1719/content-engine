"""
ImprovedAdGenerator — fine-tuned model + A/B testing wrapper.

Uses the fine-tuned GPT-3.5 model for ad copy generation and wraps
AdGenerator for image generation. Supports A/B variant generation.

Fine-tuned model: ft:gpt-3.5-turbo-0125:shreyansh::BLDyTfqs
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from ad_generator.generator import AdGenerator, DEV_MODE

FINE_TUNED_MODEL = os.getenv("FINE_TUNED_MODEL", "ft:gpt-3.5-turbo-0125:shreyansh::BLDyTfqs")


class ImprovedAdGenerator(AdGenerator):
    """
    Extended ad generator that uses the fine-tuned model for copywriting
    and supports A/B variant generation.

    Falls back gracefully to the base AdGenerator when the fine-tuned model
    is unavailable or the API key is absent.
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        super().__init__(openai_api_key=openai_api_key)
        self.fine_tuned_model = FINE_TUNED_MODEL
        self.logger = logging.getLogger("ImprovedAdGenerator")
        self.logger.info(f"ImprovedAdGenerator initialised (fine-tuned model: {self.fine_tuned_model})")

    # ------------------------------------------------------------------
    # Fine-tuned copy generation
    # ------------------------------------------------------------------

    def generate_fine_tuned_copy(self, prompt: str, brand_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate ad copy using the fine-tuned model.
        Falls back to base generate_ad_copy on any error.
        """
        if DEV_MODE or not self.openai_client:
            self.logger.warning("DEV MODE / no client — using base copy generation")
            return self._generate_default_ad_copy(prompt, brand_analysis)

        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        f"You are an expert ad copywriter for {brand_analysis.get('industry', 'general')} brands. "
                        f"Brand level: {brand_analysis.get('brand_level', 'premium')}. "
                        f"Tone: {brand_analysis.get('tone', 'professional')}."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Write a high-converting advertisement for: {prompt}\n"
                        f"Key benefits: {', '.join(brand_analysis.get('key_benefits', []))}\n"
                        f"Target market: {brand_analysis.get('target_market', 'general consumers')}\n\n"
                        "Return JSON with keys: headline, subheadline, body_text, call_to_action, image_description"
                    ),
                },
            ]

            response = self.openai_client.chat.completions.create(
                model=self.fine_tuned_model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.75,
            )
            result = json.loads(response.choices[0].message.content)
            self.logger.info("Fine-tuned copy generated successfully")
            return self._validate_ad_copy(result, prompt, brand_analysis)

        except Exception as e:
            self.logger.warning(f"Fine-tuned model failed ({e}), falling back to base copy")
            return self.generate_ad_copy(prompt, brand_analysis)

    # ------------------------------------------------------------------
    # A/B variant generation
    # ------------------------------------------------------------------

    def generate_ab_variants(
        self,
        prompt: str,
        n_variants: int = 2,
        use_fine_tuned: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Generate N ad copy variants for A/B testing.

        Args:
            prompt: Product/campaign description
            n_variants: Number of variants to generate (1-4)
            use_fine_tuned: Whether to use the fine-tuned model for copy

        Returns:
            List of ad data dictionaries, one per variant
        """
        n_variants = max(1, min(n_variants, 4))
        self.logger.info(f"Generating {n_variants} A/B variants for: {prompt}")

        brand_info = self.extract_brand_info(prompt)
        brand_analysis = self.analyze_brand(brand_info)

        variants = []
        for i in range(n_variants):
            self.logger.info(f"Generating variant {i + 1}/{n_variants}")
            try:
                if use_fine_tuned:
                    ad_copy = self.generate_fine_tuned_copy(prompt, brand_analysis)
                else:
                    ad_copy = self.generate_ad_copy(prompt, brand_analysis)

                # Generate image only for first variant (saves cost in A/B)
                if i == 0:
                    image_result = self.image_generator.create_studio_ad(
                        product=brand_info["product"],
                        brand_name=brand_info["brand"],
                        headline=ad_copy["headline"],
                        subheadline=ad_copy.get("subheadline"),
                        call_to_action=ad_copy.get("call_to_action"),
                        industry=brand_analysis.get("industry"),
                        brand_level=brand_analysis.get("brand_level"),
                        image_description=ad_copy.get("image_description"),
                    )
                else:
                    image_result = {"final_path": variants[0].get("final_path", ""), "image_path": ""}

                variant = {
                    **ad_copy,
                    **brand_analysis,
                    **image_result,
                    "product": brand_info["product"],
                    "brand_name": brand_info["brand"],
                    "variant_index": i + 1,
                    "generation_time": datetime.now().isoformat(),
                }
                variants.append(variant)

            except Exception as e:
                self.logger.error(f"Variant {i + 1} failed: {e}")
                variants.append(self._generate_mock_ad(prompt))

        return variants

    # ------------------------------------------------------------------
    # Convenience: create_ad with fine-tuned copy
    # ------------------------------------------------------------------

    def create_ad(self, prompt: str, product_image_path: str = None, use_fine_tuned: bool = True) -> Dict[str, Any]:
        """
        Create an ad, optionally using the fine-tuned model for copywriting.
        Wraps base create_ad with fine-tuned copy generation.
        """
        if DEV_MODE or not self.openai_client:
            return self._generate_mock_ad(prompt)

        brand_info = self.extract_brand_info(prompt)
        brand_analysis = self.analyze_brand(brand_info)

        if use_fine_tuned:
            ad_copy = self.generate_fine_tuned_copy(prompt, brand_analysis)
        else:
            ad_copy = self.generate_ad_copy(prompt, brand_analysis)

        if product_image_path:
            image_result = self.image_generator.create_ad_with_user_product(
                product_image_path=product_image_path,
                product=brand_info["product"],
                brand_name=brand_info["brand"],
                headline=ad_copy["headline"],
                subheadline=ad_copy.get("subheadline"),
                call_to_action=ad_copy.get("call_to_action"),
                industry=brand_analysis.get("industry"),
                brand_level=brand_analysis.get("brand_level"),
            )
        else:
            image_result = self.image_generator.create_studio_ad(
                product=brand_info["product"],
                brand_name=brand_info["brand"],
                headline=ad_copy["headline"],
                subheadline=ad_copy.get("subheadline"),
                call_to_action=ad_copy.get("call_to_action"),
                industry=brand_analysis.get("industry"),
                brand_level=brand_analysis.get("brand_level"),
                image_description=ad_copy.get("image_description"),
            )

        return {
            **ad_copy,
            **brand_analysis,
            **image_result,
            "product": brand_info["product"],
            "brand_name": brand_info["brand"],
            "generation_time": datetime.now().isoformat(),
        }
