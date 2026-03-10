"""
Standalone Playwright renderer called via subprocess.

Accepts JSON from stdin:
  {"html": "...", "width": 1024, "height": 1024, "output": "/path/to/out.png"}

Prints JSON result to stdout:
  {"success": true} or {"success": false, "error": "..."}

Running in a subprocess guarantees no asyncio event loop conflicts.
"""
import sys
import os
import json
import tempfile
from pathlib import Path


def main():
    data = json.load(sys.stdin)
    html_content = data["html"]
    width        = data["width"]
    height       = data["height"]
    output_path  = data["output"]

    from playwright.sync_api import sync_playwright

    tmp_dir   = tempfile.mkdtemp(prefix="adcraft_")
    html_path = os.path.join(tmp_dir, "overlay.html")

    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                viewport={"width": width, "height": height},
                device_scale_factor=1,
            )
            page.goto(f"file:///{Path(html_path).as_posix()}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)
            page.screenshot(path=output_path, omit_background=True, type="png")
            browser.close()

        print(json.dumps({"success": True}))

    except Exception as exc:
        print(json.dumps({"success": False, "error": str(exc)}))

    finally:
        try:
            os.unlink(html_path)
        except OSError:
            pass
        try:
            os.rmdir(tmp_dir)
        except OSError:
            pass


if __name__ == "__main__":
    main()
