"""
DPO Dataset Builder: Converts preference pairs into OpenAI's DPO training format.

OpenAI DPO format:
{
    "input": {
        "messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."}
        ]
    },
    "preferred_output": [{"role": "assistant", "content": "..."}],
    "non_preferred_output": [{"role": "assistant", "content": "..."}]
}

The system/user messages must match EXACTLY what the fine-tuned model receives
during inference. The preferred/non_preferred outputs are the creative briefs
that led to higher/lower quality ads.
"""
import os
import json
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class DPODatasetBuilder:
    """
    Builds DPO training datasets from preference pairs.

    Critical requirements:
    - System prompt must match what the model sees during inference
    - User prompt format must match the inference format
    - Preferred/non-preferred outputs must be valid JSON creative briefs
    - Minimum 20 pairs recommended, 50+ for meaningful improvement
    """

    # This MUST match the system prompt used in generator.py's _get_creative_brief()
    SYSTEM_PROMPT = (
        "You are an expert advertising creative director. "
        "Given a brand and product, output a complete creative brief as JSON with keys: "
        "headline, caption, tone, visual_style, conceptual_technique, "
        "call_to_action, emotion."
    )

    def __init__(self, feedback_loop):
        """
        Args:
            feedback_loop: FeedbackLoop instance with collected preference pairs
        """
        self.feedback_loop = feedback_loop

    def build_dataset(self, output_path: str = "data/dpo_training_dataset.jsonl") -> Dict:
        """
        Convert all preference pairs into OpenAI DPO format.

        Returns:
            {
                "status": "success" | "insufficient_data",
                "output_path": str,
                "num_examples": int,
                "validation": { valid: int, invalid: int, errors: [...] }
            }
        """
        pairs = self.feedback_loop.preference_pairs

        if len(pairs) < 10:
            return {
                "status": "insufficient_data",
                "message": f"Only {len(pairs)} pairs available. Need at least 10, recommend 50+.",
                "num_examples": len(pairs),
            }

        examples = []
        errors = []

        for pair in pairs:
            try:
                example = self._convert_pair(pair)
                if example:
                    examples.append(example)
            except Exception as e:
                errors.append({"pair_id": pair.get("pair_id"), "error": str(e)})

        if not examples:
            return {
                "status": "no_valid_examples",
                "message": "No pairs could be converted to DPO format",
                "errors": errors,
            }

        valid, invalid, validation_errors = self._validate_dataset(examples)

        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        with open(output_path, "w") as f:
            for ex in valid:
                f.write(json.dumps(ex) + "\n")

        logger.info(f"DPO dataset built: {len(valid)} valid examples written to {output_path}")

        return {
            "status": "success",
            "output_path": output_path,
            "num_examples": len(valid),
            "num_invalid": len(invalid),
            "validation_errors": validation_errors[:5],
            "dataset_stats": self._compute_stats(valid),
        }

    def _convert_pair(self, pair: Dict) -> Dict:
        """Convert a single preference pair to OpenAI DPO format."""
        product_prompt = pair.get("product_prompt", "")
        preferred_brief = pair.get("preferred", {}).get("creative_brief", {})
        non_preferred_brief = pair.get("non_preferred", {}).get("creative_brief", {})

        if not product_prompt or not preferred_brief or not non_preferred_brief:
            return None

        # Build user message matching inference format
        if " by " in product_prompt:
            brand = product_prompt.split(" by ")[-1]
        else:
            brand = product_prompt.split()[0]
        user_message = f"Create an ad for:\nBrand: {brand}\nProduct type: {product_prompt}"

        return {
            "input": {
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ]
            },
            "preferred_output": [
                {"role": "assistant", "content": json.dumps(preferred_brief)}
            ],
            "non_preferred_output": [
                {"role": "assistant", "content": json.dumps(non_preferred_brief)}
            ],
        }

    def _validate_dataset(self, examples: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Validate all examples against OpenAI's DPO format requirements."""
        valid = []
        invalid = []
        errors = []

        for i, ex in enumerate(examples):
            try:
                assert "input" in ex, "Missing 'input'"
                assert "messages" in ex["input"], "Missing 'input.messages'"
                assert len(ex["input"]["messages"]) >= 2, "Need at least 2 messages (system + user)"
                assert ex["input"]["messages"][0]["role"] == "system", "First message must be system"
                assert ex["input"]["messages"][1]["role"] == "user", "Second message must be user"

                assert "preferred_output" in ex, "Missing 'preferred_output'"
                assert "non_preferred_output" in ex, "Missing 'non_preferred_output'"
                assert len(ex["preferred_output"]) == 1, "preferred_output must have exactly 1 message"
                assert len(ex["non_preferred_output"]) == 1, "non_preferred_output must have exactly 1 message"
                assert ex["preferred_output"][0]["role"] == "assistant", "preferred must be assistant"
                assert ex["non_preferred_output"][0]["role"] == "assistant", "non_preferred must be assistant"

                # Verify outputs are valid JSON
                json.loads(ex["preferred_output"][0]["content"])
                json.loads(ex["non_preferred_output"][0]["content"])

                # Verify outputs are different
                assert ex["preferred_output"][0]["content"] != ex["non_preferred_output"][0]["content"], \
                    "Preferred and non-preferred outputs must be different"

                valid.append(ex)
            except Exception as e:
                invalid.append(ex)
                errors.append({"index": i, "error": str(e)})

        return valid, invalid, errors

    def _compute_stats(self, examples: List[Dict]) -> Dict:
        """Compute statistics about the dataset."""
        if not examples:
            return {"total_examples": 0}
        return {
            "total_examples": len(examples),
            "avg_preferred_length": round(
                sum(len(ex["preferred_output"][0]["content"]) for ex in examples) / len(examples)
            ),
            "avg_non_preferred_length": round(
                sum(len(ex["non_preferred_output"][0]["content"]) for ex in examples) / len(examples)
            ),
        }

    def get_training_command(self, dataset_path: str, base_model: str = None) -> str:
        """
        Generate the Python code to run the DPO training job.

        This doesn't execute the training (costs money) — it returns
        the exact code that would run it, ready to paste when budget allows.
        """
        if base_model is None:
            base_model = "gpt-4.1-mini-2025-04-14"

        return f'''
# DPO Training — Run when ready (costs ~$2-3)
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Upload DPO dataset
file_result = client.files.create(
    file=open("{dataset_path}", "rb"),
    purpose="fine-tune"
)
print(f"File uploaded: {{file_result.id}}")

# Create DPO fine-tuning job
# Base model should be the SFT model or a supported base model
job = client.fine_tuning.jobs.create(
    training_file=file_result.id,
    model="{base_model}",
    method={{
        "type": "dpo",
        "dpo": {{
            "hyperparameters": {{"beta": 0.1}}
        }}
    }}
)
print(f"DPO job created: {{job.id}}")
print(f"Status: {{job.status}}")
'''
