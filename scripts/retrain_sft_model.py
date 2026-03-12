"""
Step 1: Retrain SFT model on gpt-4.1-mini.

Migrates from deprecated ft:gpt-4o-mini-2024-07-18:shreyansh::DHRbE3oW to
gpt-4.1-mini-2025-04-14 using the same 421 training examples.

Usage:
    python scripts/retrain_sft_model.py
"""
import json
import os
import sys
import time
import shutil
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed. Run: pip install openai")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TRAINING_FILE = "fine_tuning_dataset_v2.jsonl"
BASE_MODEL = "gpt-4.1-mini-2025-04-14"
N_EPOCHS = 3
POLL_INTERVAL_SECS = 60

CREATIVE_BRIEF_SYSTEM_PROMPT = (
    "You are an expert advertising creative director. Given a brand and product, "
    "generate a complete ad creative brief including copy and visual direction. "
    "Respond only in JSON."
)

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_training_file(path: str) -> tuple[bool, dict]:
    """
    Validate the training JSONL before uploading.
    Returns (is_valid, stats_dict).
    """
    print(f"\n[validate] Validating {path} ...")
    errors = []
    valid_count = 0
    system_prompts = set()

    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"  Line {lineno}: JSON parse error: {e}")
                continue

            msgs = entry.get("messages")
            if not isinstance(msgs, list) or len(msgs) < 2:
                errors.append(f"  Line {lineno}: missing or short 'messages' array")
                continue

            roles = [m.get("role") for m in msgs]
            allowed = {"system", "user", "assistant"}
            bad_roles = [r for r in roles if r not in allowed]
            if bad_roles:
                errors.append(f"  Line {lineno}: unknown roles {bad_roles}")
                continue

            sys_msg = next((m["content"] for m in msgs if m["role"] == "system"), None)
            if sys_msg:
                system_prompts.add(sys_msg)

            valid_count += 1

    total_lines = valid_count + len(errors)
    is_valid = len(errors) == 0

    stats = {
        "total_entries": total_lines,
        "valid_entries": valid_count,
        "malformed_entries": len(errors),
        "unique_system_prompts": len(system_prompts),
        "system_prompts": list(system_prompts),
    }

    print(f"  Total entries : {total_lines}")
    print(f"  Valid entries : {valid_count}")
    print(f"  Malformed     : {len(errors)}")
    if errors:
        for e in errors[:10]:
            print(e)
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")

    # Verify system prompt consistency
    if len(system_prompts) != 1:
        print(f"  WARNING: {len(system_prompts)} unique system prompts found (expected 1)")
        for p in system_prompts:
            print(f"    -> {repr(p)}")
    else:
        actual = list(system_prompts)[0]
        if actual == CREATIVE_BRIEF_SYSTEM_PROMPT:
            print(f"  System prompt: MATCHES prompts.py ✓")
        else:
            print(f"  WARNING: Training data prompt does NOT match CREATIVE_BRIEF_SYSTEM_PROMPT")
            print(f"  Training data: {repr(actual)}")
            print(f"  prompts.py   : {repr(CREATIVE_BRIEF_SYSTEM_PROMPT)}")
            print(f"  -> prompts.py has been authored to match the training data.")

    return is_valid, stats


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

def smoke_test_model(client: OpenAI, model_id: str) -> bool:
    """
    Smoke test: generate a creative brief for Nike Air Jordan 1.
    Verifies the response parses and contains expected fields.
    Returns True if test passes.
    """
    print(f"\n[smoke_test] Testing model {model_id} ...")

    required_fields = ["headline", "caption", "tone", "visual_style",
                       "conceptual_technique", "call_to_action", "emotion"]

    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": CREATIVE_BRIEF_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Create an ad for:\n"
                        "Brand: Nike\n"
                        "Product type: Nike Air Jordan 1 streetwear sneakers\n"
                        "Tone: Bold\n"
                        "Visual style: Urban & Street\n"
                        "Conceptual technique: Athlete empowerment\n"
                        "Format: image"
                    ),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.75,
        )

        content = response.choices[0].message.content
        result = json.loads(content)

        print(f"\n  Full response:")
        print(json.dumps(result, indent=4))

        missing = [f for f in required_fields if not result.get(f)]
        if missing:
            print(f"\n  WARN: Missing/empty fields: {missing}")
        else:
            print(f"\n  All {len(required_fields)} required fields present ✓")

        return len(missing) == 0

    except Exception as e:
        print(f"  Smoke test FAILED: {e}")
        return False


# ---------------------------------------------------------------------------
# .env update helpers
# ---------------------------------------------------------------------------

def backup_and_update_env(new_model_id: str):
    """Back up .env, then update FINE_TUNED_MODEL_ID."""
    env_path = Path(".env")
    backup_path = Path(".env.backup")

    if env_path.exists():
        shutil.copy(env_path, backup_path)
        print(f"\n  .env backed up to {backup_path}")

    if not env_path.exists():
        env_path.write_text("")

    content = env_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    updated = []
    found_main = False
    found_v1 = False
    old_model = os.getenv("FINE_TUNED_MODEL_ID", "")

    for line in lines:
        if line.startswith("FINE_TUNED_MODEL_ID=") and not line.startswith("FINE_TUNED_MODEL_ID_V1="):
            updated.append(f"FINE_TUNED_MODEL_ID={new_model_id}\n")
            found_main = True
        elif line.startswith("FINE_TUNED_MODEL_ID_V1="):
            updated.append(line)
            found_v1 = True
        else:
            updated.append(line)

    if not found_main:
        updated.append(f"FINE_TUNED_MODEL_ID={new_model_id}\n")

    if not found_v1 and old_model and old_model != new_model_id:
        updated.append(f"FINE_TUNED_MODEL_ID_V1={old_model}\n")

    env_path.write_text("".join(updated), encoding="utf-8")
    print(f"  FINE_TUNED_MODEL_ID  = {new_model_id}")
    if old_model:
        print(f"  FINE_TUNED_MODEL_ID_V1 preserved: {old_model}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # ── 1. Validate training data ──
    if not Path(TRAINING_FILE).exists():
        print(f"ERROR: Training file not found: {TRAINING_FILE}")
        sys.exit(1)

    is_valid, stats = validate_training_file(TRAINING_FILE)
    if not is_valid:
        print(f"\nERROR: Training file has {stats['malformed_entries']} malformed entries. Fix before uploading.")
        sys.exit(1)

    print(f"\n  Validation passed: {stats['valid_entries']} valid entries ✓")

    # ── 2. Upload training file ──
    print(f"\n[upload] Uploading {TRAINING_FILE} to OpenAI Files API ...")
    with open(TRAINING_FILE, "rb") as f:
        upload_result = client.files.create(file=f, purpose="fine-tune")

    file_id = upload_result.id
    print(f"  File uploaded: {file_id}")

    # ── 3. Create fine-tuning job ──
    print(f"\n[finetune] Creating SFT job on {BASE_MODEL} (n_epochs={N_EPOCHS}) ...")
    job = client.fine_tuning.jobs.create(
        training_file=file_id,
        model=BASE_MODEL,
        hyperparameters={"n_epochs": N_EPOCHS},
    )
    job_id = job.id
    print(f"  Job created: {job_id}")
    print(f"  Status: {job.status}")
    print(f"  Model: {job.model}")

    # ── 4. Poll until complete ──
    print(f"\n[poll] Polling every {POLL_INTERVAL_SECS}s until job completes ...")
    terminal_states = {"succeeded", "failed", "cancelled"}

    while True:
        time.sleep(POLL_INTERVAL_SECS)
        job = client.fine_tuning.jobs.retrieve(job_id)
        ts = datetime.now().strftime("%H:%M:%S")
        status = job.status

        metrics_str = ""
        if hasattr(job, "training_file") and job.result_files:
            pass  # metrics in result files

        print(f"  [{ts}] status={status}  trained_tokens={getattr(job, 'trained_tokens', 'N/A')}")

        # Print events for live metrics
        try:
            events = client.fine_tuning.jobs.list_events(job_id, limit=5)
            for ev in reversed(list(events.data)):
                if ev.message and "step" in ev.message.lower():
                    print(f"    event: {ev.message}")
        except Exception:
            pass

        if status in terminal_states:
            break

    # ── 5. Handle result ──
    if job.status != "succeeded":
        print(f"\nERROR: Fine-tuning job {job_id} ended with status '{job.status}'")
        if job.error:
            print(f"  Error: {job.error}")
        sys.exit(1)

    new_model_id = job.fine_tuned_model
    print(f"\n{'='*60}")
    print(f"  NEW MODEL ID: {new_model_id}")
    print(f"{'='*60}")

    # ── 6. Update .env ──
    backup_and_update_env(new_model_id)

    # ── 7. Smoke test ──
    passed = smoke_test_model(client, new_model_id)
    if passed:
        print(f"\n[smoke_test] PASSED ✓ — model is producing valid structured output")
    else:
        print(f"\n[smoke_test] WARN — model output missing some fields; inspect response above")

    print(f"\n[done] SFT retraining complete.")
    print(f"  Model: {new_model_id}")
    print(f"  Next step: run scripts/generate_preference_data.py")


if __name__ == "__main__":
    main()
