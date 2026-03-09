"""
Build fine_tuning_dataset_v2.jsonl from:
  - practical.jsonl          (21 high-quality real ad examples)
  - made_to_stick_400_final_dataset.jsonl  (399 style-pattern examples, captions regenerated)

Run:  python build_fine_tuning_dataset.py
"""
import json
import os

SYSTEM_PROMPT = (
    "You are an expert advertising creative director. Given a brand and product, "
    "generate a complete ad creative brief including copy and visual direction. "
    "Respond only in JSON."
)

OUT_PATH = "fine_tuning_dataset_v2.jsonl"


# ---------------------------------------------------------------------------
# practical.jsonl  (JSON array, 21 entries)
# ---------------------------------------------------------------------------

def load_practical(path="practical.jsonl"):
    with open(path, encoding="utf-8") as f:
        raw = f.read().strip()
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    # Fallback: try JSONL
    entries = []
    for line in raw.splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries


def practical_to_messages(entry):
    brand               = (entry.get("brand") or "").strip()
    product_type        = (entry.get("product_type") or "").strip()
    tone                = (entry.get("tone") or "").strip()
    visual_style        = (entry.get("visual_style") or "").strip()
    conceptual_technique= (entry.get("conceptual_technique") or "").strip()
    fmt                 = (entry.get("format") or "image").strip()
    headline            = (entry.get("headline") or "").strip()
    caption             = (entry.get("caption") or "").strip()
    emotion             = (entry.get("emotion") or "").strip()

    if not headline or not brand:
        return None

    # No call_to_action in practical — generate a sensible default
    cta = "Shop Now"

    user_content = (
        f"Create an ad for:\n"
        f"Brand: {brand}\n"
        f"Product type: {product_type}\n"
        f"Tone: {tone}\n"
        f"Visual style: {visual_style}\n"
        f"Conceptual technique: {conceptual_technique}\n"
        f"Format: {fmt}"
    )

    assistant_obj = {
        "headline":             headline,
        "caption":              caption if caption else f"{headline}. {brand} – {tone} and {visual_style}.",
        "tone":                 tone,
        "visual_style":         visual_style,
        "conceptual_technique": conceptual_technique,
        "call_to_action":       cta,
        "emotion":              emotion,
    }

    return {
        "messages": [
            {"role": "system",    "content": SYSTEM_PROMPT},
            {"role": "user",      "content": user_content},
            {"role": "assistant", "content": json.dumps(assistant_obj)},
        ]
    }


# ---------------------------------------------------------------------------
# made_to_stick_400_final_dataset.jsonl  (399 entries, synthetic captions)
# ---------------------------------------------------------------------------

def made_to_stick_to_messages(entry):
    brand                = (entry.get("brand") or "").strip()
    headline             = (entry.get("headline") or "").strip()
    tone                 = (entry.get("tone") or "").strip()
    visual_style         = (entry.get("visual_style") or "").strip()
    conceptual_technique = (entry.get("conceptual_technique") or "").strip()
    platform             = (entry.get("platform_context") or "").strip()
    core_principles      = entry.get("core_principles") or []
    cta                  = (entry.get("call_to_action") or "Shop Now").strip() or "Shop Now"

    if not headline or not brand:
        return None

    # Replace faker-generated caption with structured synthetic one
    technique_lc = conceptual_technique.lower() if conceptual_technique else "storytelling"
    tone_lc      = tone.lower()             if tone              else "professional"
    caption = (
        f"{headline}. Discover {brand}'s approach to {technique_lc} "
        f"with a {tone_lc} perspective."
    )

    user_content = (
        f"Create an ad for:\n"
        f"Brand: {brand}\n"
        f"Product type: {brand} product\n"
        f"Tone: {tone}\n"
        f"Visual style: {visual_style}\n"
        f"Conceptual technique: {conceptual_technique}\n"
        f"Format: image\n"
        f"Platform: {platform}"
    )

    assistant_obj = {
        "headline":             headline,
        "caption":              caption,
        "tone":                 tone,
        "visual_style":         visual_style,
        "conceptual_technique": conceptual_technique,
        "call_to_action":       cta,
        "core_principles":      core_principles,
        "platform_context":     platform,
    }

    return {
        "messages": [
            {"role": "system",    "content": SYSTEM_PROMPT},
            {"role": "user",      "content": user_content},
            {"role": "assistant", "content": json.dumps(assistant_obj)},
        ]
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    examples = []

    # --- practical.jsonl ---
    practical_entries = load_practical()
    practical_ok = 0
    for entry in practical_entries:
        msg = practical_to_messages(entry)
        if msg:
            examples.append(msg)
            practical_ok += 1
    print(f"practical.jsonl : {len(practical_entries)} loaded, {practical_ok} converted")

    # --- made_to_stick ---
    mts_total = 0
    mts_ok = 0
    with open("made_to_stick_400_final_dataset.jsonl", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            mts_total += 1
            try:
                entry = json.loads(line)
                msg = made_to_stick_to_messages(entry)
                if msg:
                    examples.append(msg)
                    mts_ok += 1
            except json.JSONDecodeError:
                pass
    print(f"made_to_stick   : {mts_total} lines, {mts_ok} converted")

    # --- Write ---
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")

    print(f"\nTotal examples  : {len(examples)}")
    print(f"Written to      : {OUT_PATH}")

    # --- Show 3 samples ---
    print("\n=== Sample entries ===")
    for idx in [0, len(examples) // 2, len(examples) - 1]:
        ex  = examples[idx]
        msgs = ex["messages"]
        print(f"\n--- Entry {idx} ---")
        print("USER     :", msgs[1]["content"][:180])
        print("ASSISTANT:", msgs[2]["content"][:300])


if __name__ == "__main__":
    main()
