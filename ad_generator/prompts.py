"""
Single source of truth for all prompts used in training and inference.

CRITICAL: CREATIVE_BRIEF_SYSTEM_PROMPT must match exactly what was used to
train fine_tuning_dataset_v2.jsonl (421 examples). This was verified by
checking all 421 entries — they use a single unique system prompt, copied
verbatim below. Any divergence here will cause silent DPO training failure.
"""

CREATIVE_BRIEF_SYSTEM_PROMPT = (
    "You are an expert advertising creative director. Given a brand and product, "
    "generate a complete ad creative brief including copy and visual direction. "
    "Respond only in JSON."
)
