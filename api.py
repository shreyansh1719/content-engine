"""
AdCraft Pro — FastAPI Backend
Serves the ad generation engine via REST API for the Streamlit frontend.

Run with:
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload
or:
    python api.py
"""
import os
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AdCraft Pro API",
    version="1.0.0",
    description="AI-powered ad generation engine. POST to /generate_ad to create a complete ad.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve output/ directory as /static/
# e.g. output/images/final/ad_123.png → /static/images/final/ad_123.png
Path("output/images/final").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="output"), name="static")


# ---------------------------------------------------------------------------
# Enums / option lists (single source of truth for frontend dropdowns)
# ---------------------------------------------------------------------------

INDUSTRIES: List[str] = [
    "Technology",
    "Fashion",
    "Beauty",
    "Automotive",
    "Luxury",
    "Food & Beverage",
    "Fitness",
    "Home & Living",
    "Healthcare",
    "Entertainment",
    "Finance",
    "Education",
]

PLATFORMS: List[str] = [
    "Instagram",
    "Facebook",
    "LinkedIn",
    "Twitter/X",
    "Pinterest",
    "Google Ads",
    "TikTok",
    "YouTube",
]

TONES: List[str] = [
    "Professional",
    "Playful",
    "Luxurious",
    "Bold",
    "Minimalist",
    "Emotional",
    "Urgent",
    "Inspirational",
]

VISUAL_STYLES: List[str] = [
    "Modern Minimal",
    "Bold & Vibrant",
    "Luxury & Elegant",
    "Tech-Forward",
    "Natural & Organic",
    "Urban & Street",
    "Classic & Timeless",
]

PRINCIPLES: List[str] = [
    "Simple",
    "Unexpected",
    "Concrete",
    "Credible",
    "Emotional",
    "Story-driven",
]


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class AdRequest(BaseModel):
    product_name: str
    brand_name: str
    product_description: str
    industry: str
    platform: str
    tone: str
    visual_style: str
    principle: str
    key_benefit: Optional[str] = ""
    audience_desc: Optional[str] = ""
    project_name: Optional[str] = ""
    campaign_name: Optional[str] = ""


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


class HealthResponse(BaseModel):
    status: str
    api_key_configured: bool


class ApiInfoResponse(BaseModel):
    industries: List[str]
    platforms: List[str]
    tones: List[str]
    visual_styles: List[str]
    principles: List[str]


# ---------------------------------------------------------------------------
# Lazy-loaded generator (startup stays instant)
# ---------------------------------------------------------------------------

_generator = None


def get_generator():
    """Return singleton AdGenerator, raising 503 if OpenAI key is absent."""
    global _generator
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "OPENAI_API_KEY is not configured. "
                "Add it to your .env file and restart the server."
            ),
        )
    if _generator is None:
        from ad_generator import AdGenerator
        _generator = AdGenerator(openai_api_key=api_key)
    return _generator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _local_path_to_url(local_path: str) -> str:
    """Convert output/images/final/foo.png  →  /static/images/final/foo.png."""
    if not local_path:
        return ""
    p = Path(local_path)
    try:
        rel = p.relative_to("output")
        return f"/static/{rel.as_posix()}"
    except ValueError:
        return local_path


def _build_prompt(req: AdRequest) -> str:
    """
    Combine all structured frontend fields into one rich prompt string for
    AdGenerator.create_ad(), which feeds it to GPT-4o for analysis.
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

@app.get("/health", response_model=HealthResponse, tags=["Meta"])
def health():
    """Liveness + config check. Safe to call without an API key."""
    api_key_present = bool(os.getenv("OPENAI_API_KEY", "").strip())
    return HealthResponse(
        status="ok",
        api_key_configured=api_key_present,
    )


@app.get("/api-info", response_model=ApiInfoResponse, tags=["Meta"])
def api_info():
    """Return all available dropdown options for the frontend form."""
    return ApiInfoResponse(
        industries=INDUSTRIES,
        platforms=PLATFORMS,
        tones=TONES,
        visual_styles=VISUAL_STYLES,
        principles=PRINCIPLES,
    )


@app.post("/generate_ad", response_model=AdResponse, tags=["Generation"])
def generate_ad(req: AdRequest):
    """
    Generate a complete ad (copy + image) from structured product information.

    - Calls GPT-4o for brand analysis and copywriting.
    - Calls DALL-E 3 for image generation.
    - Returns ad copy fields and a /static/... URL to the generated image.
    - Returns 503 if OPENAI_API_KEY is missing.
    - Returns 422 if required fields are empty.
    """
    if not req.product_name.strip() or not req.brand_name.strip():
        raise HTTPException(
            status_code=422,
            detail="product_name and brand_name are required and cannot be blank.",
        )

    prompt = _build_prompt(req)

    # get_generator() raises 503 if no API key
    generator = get_generator()

    try:
        ad_data = generator.create_ad(prompt)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Ad generation failed: {exc}",
        )

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


# ---------------------------------------------------------------------------
# Dev entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
