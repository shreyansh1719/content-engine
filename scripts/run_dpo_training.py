"""
Step 3: DPO training on preference pairs.

Converts preference pairs to OpenAI DPO format, validates, uploads, and
creates a DPO fine-tuning job on top of the SFT model from Step 1.

Usage:
    python scripts/run_dpo_training.py
"""
import json
import os
import sys
import time
import shutil
from datetime import datetime
from pathlib import Path

# Ensure project root is on sys.path when running as script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed")
    sys.exit(1)

DPO_OUTPUT_PATH = "data/dpo_training_dataset.jsonl"
POLL_INTERVAL_SECS = 60


# ---------------------------------------------------------------------------
# .env helpers
# ---------------------------------------------------------------------------

def update_env_for_dpo(dpo_model_id: str, sft_model_id: str):
    """Promote DPO model to production, demote SFT to SFT_MODEL_ID."""
    env_path = Path(".env")
    if not env_path.exists():
        env_path.write_text("")

    # Backup
    shutil.copy(env_path, Path(".env.backup"))

    content = env_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    updated = []
    found_main = found_sft = False

    for line in lines:
        if line.startswith("FINE_TUNED_MODEL_ID=") and not line.startswith("FINE_TUNED_MODEL_ID_V"):
            updated.append(f"FINE_TUNED_MODEL_ID={dpo_model_id}\n")
            found_main = True
        elif line.startswith("SFT_MODEL_ID="):
            updated.append(f"SFT_MODEL_ID={sft_model_id}\n")
            found_sft = True
        else:
            updated.append(line)

    if not found_main:
        updated.append(f"FINE_TUNED_MODEL_ID={dpo_model_id}\n")
    if not found_sft:
        updated.append(f"SFT_MODEL_ID={sft_model_id}\n")

    env_path.write_text("".join(updated), encoding="utf-8")
    print(f"  FINE_TUNED_MODEL_ID = {dpo_model_id}  (production)")
    print(f"  SFT_MODEL_ID        = {sft_model_id}   (preserved)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set")
        sys.exit(1)

    sft_model_id = os.getenv("FINE_TUNED_MODEL_ID", "").strip()
    if not sft_model_id:
        print("ERROR: FINE_TUNED_MODEL_ID not set. Run retrain_sft_model.py first.")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # ── 1. Build DPO dataset ──
    print("\n[build] Building DPO dataset from preference pairs ...")
    from ad_generator.feedback_loop import FeedbackLoop
    from ad_generator.dpo_dataset_builder import DPODatasetBuilder

    feedback_loop = FeedbackLoop()
    builder = DPODatasetBuilder(feedback_loop=feedback_loop)

    stats = feedback_loop.get_stats()
    total_pairs = stats.get("total_preference_pairs", 0)
    print(f"  Preference pairs available: {total_pairs}")

    if total_pairs < 15:
        print(f"  WARN: Only {total_pairs} pairs. DPO training with few examples has limited signal.")
        print(f"  Proceeding anyway — wide-gap pairs are still useful.")

    result = builder.build_dataset(output_path=DPO_OUTPUT_PATH)
    print(f"  Dataset build status: {result['status']}")

    if result["status"] not in ("success",):
        print(f"  ERROR: Dataset build failed: {result}")
        sys.exit(1)

    num_examples = result["num_examples"]
    print(f"  DPO examples written: {num_examples} -> {DPO_OUTPUT_PATH}")

    if num_examples == 0:
        print("  ERROR: No DPO examples produced. Check preference pairs.")
        sys.exit(1)

    # ── 2. Validate DPO dataset ──
    print(f"\n[validate] Validating {DPO_OUTPUT_PATH} ...")
    from ad_generator.prompts import CREATIVE_BRIEF_SYSTEM_PROMPT

    errors = []
    valid_count = 0
    with open(DPO_OUTPUT_PATH, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"Line {lineno}: {e}")
                continue

            # Check structure
            assert "input" in entry and "messages" in entry["input"], f"Line {lineno}: missing input.messages"
            assert "preferred_output" in entry, f"Line {lineno}: missing preferred_output"
            assert "non_preferred_output" in entry, f"Line {lineno}: missing non_preferred_output"

            # Check system prompt matches
            sys_content = entry["input"]["messages"][0].get("content", "")
            if sys_content != CREATIVE_BRIEF_SYSTEM_PROMPT:
                errors.append(f"Line {lineno}: system prompt mismatch")

            valid_count += 1

    if errors:
        print(f"  ERRORS ({len(errors)}):")
        for e in errors[:5]:
            print(f"    {e}")
        sys.exit(1)

    print(f"  {valid_count} entries valid, system prompts all match [OK]")

    # ── 3. Upload DPO dataset ──
    print(f"\n[upload] Uploading DPO dataset ...")
    with open(DPO_OUTPUT_PATH, "rb") as f:
        upload_result = client.files.create(file=f, purpose="fine-tune")

    dpo_file_id = upload_result.id
    print(f"  Uploaded: {dpo_file_id}")

    # ── 4. Create DPO fine-tuning job ──
    print(f"\n[dpo] Creating DPO job on {sft_model_id} (beta=0.1) ...")
    job = client.fine_tuning.jobs.create(
        training_file=dpo_file_id,
        model=sft_model_id,
        method={
            "type": "dpo",
            "dpo": {
                "hyperparameters": {"beta": 0.1}
            },
        },
    )
    job_id = job.id
    print(f"  Job created: {job_id}")
    print(f"  Status: {job.status}")

    # ── 5. Poll until complete ──
    print(f"\n[poll] Polling every {POLL_INTERVAL_SECS}s ...")
    terminal_states = {"succeeded", "failed", "cancelled"}

    while True:
        time.sleep(POLL_INTERVAL_SECS)
        job = client.fine_tuning.jobs.retrieve(job_id)
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  [{ts}] status={job.status}  trained_tokens={getattr(job, 'trained_tokens', 'N/A')}")

        try:
            events = client.fine_tuning.jobs.list_events(job_id, limit=5)
            for ev in reversed(list(events.data)):
                if ev.message and "step" in ev.message.lower():
                    print(f"    event: {ev.message}")
        except Exception:
            pass

        if job.status in terminal_states:
            break

    # ── 6. Handle result ──
    if job.status != "succeeded":
        print(f"\nERROR: DPO job {job_id} ended with status '{job.status}'")
        if job.error:
            print(f"  Error: {job.error}")
        sys.exit(1)

    dpo_model_id = job.fine_tuned_model
    print(f"\n{'='*60}")
    print(f"  DPO MODEL ID: {dpo_model_id}")
    print(f"{'='*60}")

    # ── 7. Update .env ──
    update_env_for_dpo(dpo_model_id, sft_model_id)

    # ── 8. Smoke test ──
    print(f"\n[smoke_test] Testing DPO model ...")
    from ad_generator.prompts import CREATIVE_BRIEF_SYSTEM_PROMPT

    try:
        response = client.chat.completions.create(
            model=dpo_model_id,
            messages=[
                {"role": "system", "content": CREATIVE_BRIEF_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Create an ad for:\n"
                        "Brand: Rolex\n"
                        "Product type: Rolex Submariner luxury dive watch\n"
                        "Tone: Premium\n"
                        "Visual style: Luxury & Elegant\n"
                        "Conceptual technique: Heritage craftsmanship\n"
                        "Format: image"
                    ),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.75,
        )
        result = json.loads(response.choices[0].message.content)
        print(f"  DPO response:")
        print(json.dumps(result, indent=4))
        required = ["headline", "caption", "tone", "visual_style", "call_to_action", "emotion"]
        missing = [f for f in required if not result.get(f)]
        if missing:
            print(f"  WARN: missing fields: {missing}")
        else:
            print(f"  All required fields present [OK]")
    except Exception as e:
        print(f"  Smoke test error: {e}")

    print(f"\n[done] DPO training complete. Production model: {dpo_model_id}")
    print(f"  Next step: run scripts/run_evaluation.py")


if __name__ == "__main__":
    main()
