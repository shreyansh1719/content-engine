# AdCraft Pro

AI-powered advertisement generation platform. Paste in a product brief, get back a studio-quality ad image and copy — powered by GPT-4o + DALL-E 3.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Streamlit UI (frontend_app.py)  :8501               │
│  • Form → POST /generate_ad                         │
│  • Shows image (served via /static/...)             │
│  • DEV MODE banner when no API key                  │
└───────────────────┬─────────────────────────────────┘
                    │ HTTP
┌───────────────────▼─────────────────────────────────┐
│  FastAPI Backend (api.py)  :8000                     │
│  GET  /health         — liveness + config check     │
│  GET  /api-info        — dropdown options            │
│  POST /generate_ad     — main generation endpoint   │
│  POST /submit_feedback — store user feedback        │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│  ad_generator/                                       │
│  ├── generator.py          AdGenerator (GPT-4o)     │
│  ├── image_maker.py        ModernStudioImageGenerator│
│  ├── product_integration.py  EnhancedProductIntegr. │
│  ├── analytics.py          AdMetricsAnalyzer        │
│  ├── social_media/         Reddit API insights      │
│  └── typography/           10-module text system    │
│                                                     │
│  improved_ad_generator.py  Fine-tuned + A/B testing │
└─────────────────────────────────────────────────────┘
```

---

## Setup

### Prerequisites

- Python 3.12+ (3.14 works; 3.12 recommended for Docker)
- An OpenAI API key (optional — runs in dev/mock mode without it)

### Installation

```bash
git clone https://github.com/shreyansh1719/content-engine
cd content-engine-backup

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...your-key-here...

# Optional
FINE_TUNED_MODEL=ft:gpt-3.5-turbo-0125:shreyansh::BLDyTfqs
```

> **Dev mode**: If `OPENAI_API_KEY` is absent, the app runs in dev/mock mode — all endpoints work, ads return template copy and a placeholder image. Activate a real key to get live DALL-E + GPT-4o generation.

---

## Running

### Quick start (Windows)

```bat
run.bat
```

This starts both the API (port 8000) and the Streamlit UI (port 8501).

### Manual start

```bash
# Terminal 1 — API
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — UI
streamlit run frontend_app.py
```

### Docker

```bash
docker-compose up --build
```

Access:
- UI: http://localhost:8501
- API docs: http://localhost:8000/docs

---

## API Reference

### `GET /health`

Returns server liveness and API key configuration status.

```json
{"status": "ok", "api_key_configured": true, "dev_mode": false}
```

### `GET /api-info`

Returns all dropdown option lists for the frontend form.

### `POST /generate_ad`

Generate a complete ad (copy + image).

**Request body:**

```json
{
  "product_name": "Air Max 90",
  "brand_name": "Nike",
  "product_description": "Classic running shoes with Air cushioning",
  "industry": "Fitness",
  "platform": "Instagram",
  "tone": "Bold",
  "visual_style": "Modern Minimal",
  "principle": "Simple",
  "key_benefit": "Ultimate comfort over long distances",
  "audience_desc": "Amateur runners aged 20-35",
  "use_fine_tuned": false
}
```

**Response:**

```json
{
  "headline": "Run Beyond Limits",
  "subheadline": "Air cushioning that goes the distance.",
  "body_text": "...",
  "cta": "SHOP NOW",
  "image_url": "/static/images/final/ad_20260101_120000.png",
  "brand_name": "Nike",
  "product": "Air Max 90",
  "industry": "Fitness",
  "generation_time": "2026-01-01T12:00:00"
}
```

### `POST /submit_feedback`

Submit rating and feedback for a generated ad.

```json
{
  "ad_id": "ad_20260101_120000",
  "headline": "Run Beyond Limits",
  "rating": 4,
  "strengths": "Clear CTA, strong visual",
  "weaknesses": "Headline too generic",
  "corrections": "Use 'Air Max 90' in headline"
}
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| Frontend UI | Streamlit |
| Ad Copy | OpenAI GPT-4o / fine-tuned GPT-3.5 |
| Image Gen | OpenAI DALL-E 3 |
| Image Processing | Pillow, OpenCV, scikit-learn |
| Typography | Custom 10-module system (Montserrat, OpenSans, Oswald) |
| Background Removal | rembg / GrabCut / ML fallback chain |
| Scraping | Selenium, PRAW (Reddit) |
| Testing | pytest + FastAPI TestClient |
| Containerisation | Docker + docker-compose |

---

## Project Structure

```
content-engine-backup/
├── api.py                      # FastAPI backend
├── frontend_app.py             # Streamlit UI
├── improved_ad_generator.py    # Fine-tuned model + A/B testing
├── main.py                     # CLI entry point
├── requirements.txt
├── run.bat                     # Windows quick-start script
├── Dockerfile
├── docker-compose.yml
├── ad_generator/
│   ├── generator.py            # AdGenerator (GPT-4o)
│   ├── image_maker.py          # ModernStudioImageGenerator (DALL-E 3)
│   ├── product_integration.py  # EnhancedProductIntegrator
│   ├── analytics.py            # AdMetricsAnalyzer
│   ├── social_media/           # Reddit insights (PRAW)
│   └── typography/             # 10-module typography system
│       ├── typography_system.py
│       ├── font_pairing.py
│       ├── typography_effects.py
│       ├── enhanced_typography.py
│       └── ...
├── ad_insights_scraper/        # Selenium + PRAW scrapers
├── fonts/                      # Bundled TTF fonts (Montserrat, OpenSans, etc.)
├── output/                     # Generated images and data
├── tests/                      # pytest test suite
└── data/                       # Training data, feedback, insights
```

---

## Running Tests

```bash
pytest tests/ -v
```

All 14 tests pass in dev/mock mode (no API key required).

---

## Notes

- **CORS**: Currently `allow_origins=["*"]` — restrict this in production.
- **Fine-tuned model**: `ft:gpt-3.5-turbo-0125:shreyansh::BLDyTfqs` — set via `FINE_TUNED_MODEL` env var or in `.env`.
- **Fonts**: Bundled in `fonts/` (display, sans, serif, mono, variable subdirs + `font_mapping.json`).
- **Logs**: Rotating log at `logs/adcraft.log` (5 MB max, 3 backups).
