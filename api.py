"""
AdCraft Pro - FastAPI Backend
Serves the ad generation engine via REST API for the Streamlit frontend.

Run with:
    python api.py
    or
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload
"""
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AdCraft Pro API", version="1.0.0")

# Allow the Streamlit frontend (port 8501) and any other localhost origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve everything inside output/ as /static/...
# e.g. output/images/final/ad_123.png → /static/images/final/ad_123.png
Path("output").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="output"), name="static")


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class AdRequest(BaseModel):
    product_name: str
    brand_name: str
    product_description: str
    key_benefit: str
    tone: str
    visual_style: str
    principle: str
    industry: str
    platform: str
    project_name: Optional[str] = ""
    campaign_name: Optional[str] = ""
    audience_desc: Optional[str] = ""


class AdResponse(BaseModel):
    headline: str
    subheadline: str
    body_text: str
    cta: str
    image_url: str
    brand_name: str
    product: str
    industry: str
    generation_time: str


# ---------------------------------------------------------------------------
# Lazy-load the generator so startup is instant
# ---------------------------------------------------------------------------

_generator = None


def get_generator():
    global _generator
    if _generator is None:
        from ad_generator import AdGenerator
        _generator = AdGenerator()
    return _generator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _local_path_to_url(local_path: str) -> str:
    """Convert output/images/final/foo.png → /static/images/final/foo.png."""
    if not local_path:
        return ""
    p = Path(local_path)
    try:
        rel = p.relative_to("output")
        return f"/static/{rel.as_posix()}"
    except ValueError:
        # Path not under output/ — return as-is and let the client deal with it
        return local_path


def _build_prompt(req: AdRequest) -> str:
    """
    Combine the structured frontend fields into a single rich prompt string
    that AdGenerator.create_ad() can parse with GPT-4o.
    """
    parts = [f"{req.product_name} by {req.brand_name}"]

    if req.product_description:
        parts.append(req.product_description)
    if req.key_benefit:
        parts.append(f"Key benefit: {req.key_benefit}")
    if req.audience_desc:
        parts.append(f"Target audience: {req.audience_desc}")
    if req.tone:
        parts.append(f"Tone: {req.tone}")
    if req.visual_style:
        parts.append(f"Visual style: {req.visual_style}")
    if req.principle:
        parts.append(f"Made to Stick principle: {req.principle}")
    if req.industry:
        parts.append(f"Industry: {req.industry}")
    if req.platform:
        parts.append(f"Platform: {req.platform}")

    return ". ".join(parts)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Quick liveness check."""
    return {"status": "ok"}


@app.post("/generate_ad", response_model=AdResponse)
def generate_ad(req: AdRequest):
    """
    Generate a complete ad (copy + image) from structured product information.
    Returns ad copy and a URL to the generated image served by this API.
    """
    if not req.product_name or not req.brand_name:
        raise HTTPException(status_code=422, detail="product_name and brand_name are required.")

    prompt = _build_prompt(req)

    try:
        generator = get_generator()
        ad_data = generator.create_ad(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ad generation failed: {str(e)}")

    # The generator may return image_path or final_path depending on the code path taken
    image_path = ad_data.get("final_path") or ad_data.get("image_path") or ""
    image_url = _local_path_to_url(image_path)

    return AdResponse(
        headline=ad_data.get("headline", ""),
        subheadline=ad_data.get("subheadline", ""),
        body_text=ad_data.get("body_text", ""),
        cta=ad_data.get("call_to_action", ""),
        image_url=image_url,
        brand_name=ad_data.get("brand_name", req.brand_name),
        product=ad_data.get("product", req.product_name),
        industry=ad_data.get("industry", req.industry),
        generation_time=ad_data.get("generation_time", ""),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
