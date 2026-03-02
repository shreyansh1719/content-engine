"""
AdCraft Pro — Streamlit Frontend
Professional UI for AI-powered ad generation.

Run with:
    streamlit run frontend_app.py
"""
import json
import time
from datetime import datetime
from io import BytesIO

import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BACKEND_URL = "http://localhost:8000"
APP_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Page config — must be the first Streamlit call
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AdCraft Pro",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS — premium dark-compatible styling
# ---------------------------------------------------------------------------

st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');

/* ── Root tokens ── */
:root {
    --accent: #7C6AF7;
    --accent-light: #9D8FF9;
    --accent-dim: rgba(124, 106, 247, 0.15);
    --success: #22c55e;
    --warning: #f59e0b;
    --danger: #ef4444;
    --surface: rgba(255,255,255,0.04);
    --border: rgba(255,255,255,0.08);
    --text-muted: rgba(255,255,255,0.45);
    --radius: 12px;
    --radius-sm: 8px;
}

/* ── Global type ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 3rem !important; }

/* ── App header ── */
.app-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 0 0 2rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.app-header-icon {
    font-size: 2.2rem;
    line-height: 1;
}
.app-header-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #fff 0%, var(--accent-light) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.2;
}
.app-header-sub {
    font-size: 0.78rem;
    color: var(--text-muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 0;
    font-weight: 500;
}

/* ── Sidebar branding ── */
.sidebar-brand {
    text-align: center;
    padding: 1.2rem 0.5rem 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.2rem;
}
.sidebar-brand-name {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.35rem;
    font-weight: 700;
    background: linear-gradient(135deg, #fff 0%, var(--accent-light) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sidebar-brand-tagline {
    font-size: 0.7rem;
    color: var(--text-muted);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    font-weight: 500;
}
.sidebar-version {
    font-size: 0.65rem;
    color: var(--text-muted);
    margin-top: 4px;
}

/* ── Health indicator ── */
.health-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}
.health-ok   { background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
.health-warn { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
.health-err  { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
.dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
.dot-ok   { background: #22c55e; box-shadow: 0 0 6px #22c55e; }
.dot-warn { background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }
.dot-err  { background: #ef4444; box-shadow: 0 0 6px #ef4444; }

/* ── Section labels ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.8rem;
    margin-top: 1.4rem;
}

/* ── Form card ── */
.form-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.8rem;
    margin-bottom: 1.5rem;
}
.form-card-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: rgba(255,255,255,0.85);
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Generate button ── */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent) 0%, #5b4de0 100%) !important;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: 0.75rem 2.5rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    color: white !important;
    transition: opacity 0.2s, transform 0.15s !important;
    box-shadow: 0 4px 20px rgba(124, 106, 247, 0.4) !important;
    width: 100% !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

/* ── Ad copy result card ── */
.copy-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 2rem;
    height: 100%;
}
.copy-headline {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.9rem;
    font-weight: 700;
    line-height: 1.2;
    color: #ffffff;
    margin-bottom: 0.6rem;
}
.copy-subheadline {
    font-size: 1.05rem;
    font-weight: 500;
    color: var(--accent-light);
    margin-bottom: 1.2rem;
    line-height: 1.5;
}
.copy-body {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.7);
    line-height: 1.7;
    margin-bottom: 1.8rem;
}
.copy-divider {
    height: 1px;
    background: var(--border);
    margin: 1.4rem 0;
}
.cta-button {
    display: inline-block;
    background: linear-gradient(135deg, var(--accent), #5b4de0);
    color: white !important;
    padding: 12px 28px;
    border-radius: var(--radius-sm);
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    text-decoration: none;
    box-shadow: 0 4px 16px rgba(124,106,247,0.4);
}
.copy-meta {
    margin-top: 1.4rem;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}
.meta-tag {
    background: var(--accent-dim);
    color: var(--accent-light);
    border: 1px solid rgba(124,106,247,0.25);
    border-radius: 999px;
    padding: 3px 10px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
}

/* ── Image result card ── */
.image-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem;
    height: 100%;
}
.image-card-title {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 1rem;
}

/* ── History item ── */
.history-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 10px 12px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: border-color 0.2s;
}
.history-item:hover { border-color: var(--accent); }
.history-headline {
    font-size: 0.82rem;
    font-weight: 600;
    color: rgba(255,255,255,0.85);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.history-meta {
    font-size: 0.68rem;
    color: var(--text-muted);
    margin-top: 2px;
}

/* ── Success banner ── */
.success-banner {
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.3);
    border-radius: var(--radius-sm);
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.85rem;
    color: #22c55e;
    font-weight: 500;
    margin-bottom: 1.5rem;
}

/* ── Error / warning banners ── */
.warn-banner {
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.3);
    border-radius: var(--radius-sm);
    padding: 14px 18px;
    font-size: 0.85rem;
    color: #fbbf24;
    margin-bottom: 1rem;
}
.err-banner {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: var(--radius-sm);
    padding: 14px 18px;
    font-size: 0.85rem;
    color: #f87171;
    margin-bottom: 1rem;
}

/* ── Info box ── */
.info-box {
    background: rgba(124,106,247,0.08);
    border: 1px solid rgba(124,106,247,0.25);
    border-radius: var(--radius-sm);
    padding: 14px 18px;
    font-size: 0.83rem;
    color: rgba(255,255,255,0.7);
    line-height: 1.6;
}
.info-box code {
    background: rgba(255,255,255,0.08);
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 0.82rem;
    color: var(--accent-light);
}

/* ── Streamlit widget overrides ── */
.stTextInput > label, .stTextArea > label,
.stSelectbox > label { font-size: 0.8rem !important; font-weight: 500 !important; color: rgba(255,255,255,0.65) !important; }

div[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    background: var(--surface) !important;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []           # list of result dicts
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "form_values" not in st.session_state:
    st.session_state.form_values = {}


# ---------------------------------------------------------------------------
# Backend helpers
# ---------------------------------------------------------------------------

def check_health() -> dict:
    """Return health dict or None on connection failure."""
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def fetch_api_info() -> dict:
    """Fetch dropdown options from the API. Falls back to hardcoded defaults."""
    try:
        r = requests.get(f"{BACKEND_URL}/api-info", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {
        "industries": ["Technology","Fashion","Beauty","Automotive","Luxury",
                        "Food & Beverage","Fitness","Home & Living","Healthcare",
                        "Entertainment","Finance","Education"],
        "platforms":  ["Instagram","Facebook","LinkedIn","Twitter/X","Pinterest",
                        "Google Ads","TikTok","YouTube"],
        "tones":      ["Professional","Playful","Luxurious","Bold","Minimalist",
                        "Emotional","Urgent","Inspirational"],
        "visual_styles": ["Modern Minimal","Bold & Vibrant","Luxury & Elegant",
                          "Tech-Forward","Natural & Organic","Urban & Street",
                          "Classic & Timeless"],
        "principles": ["Simple","Unexpected","Concrete","Credible","Emotional","Story-driven"],
    }


def download_image_bytes(image_url: str) -> bytes | None:
    """Fetch image bytes from a URL for the download button."""
    try:
        url = image_url if image_url.startswith("http") else f"{BACKEND_URL}{image_url}"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.content
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    # Brand block
    st.markdown("""
    <div class="sidebar-brand">
        <div style="font-size:2rem;margin-bottom:6px;">✦</div>
        <div class="sidebar-brand-name">AdCraft Pro</div>
        <div class="sidebar-brand-tagline">AI-Powered Ad Engine</div>
        <div class="sidebar-version">v""" + APP_VERSION + """</div>
    </div>
    """, unsafe_allow_html=True)

    # Health check
    st.markdown('<div class="section-label">System Status</div>', unsafe_allow_html=True)
    health = check_health()
    if health is None:
        st.markdown("""
        <div class="health-pill health-err">
            <span class="dot dot-err"></span> API Offline
        </div>""", unsafe_allow_html=True)
        st.markdown("""
        <div class="warn-banner" style="margin-top:10px;">
            ⚠ Backend not reachable.<br>
            Run <code style="font-size:0.8rem;background:rgba(255,255,255,0.1);padding:2px 6px;border-radius:4px;">run.bat</code>
            to start both services.
        </div>""", unsafe_allow_html=True)
    elif not health.get("api_key_configured"):
        st.markdown("""
        <div class="health-pill health-warn">
            <span class="dot dot-warn"></span> No API Key
        </div>""", unsafe_allow_html=True)
        st.markdown("""
        <div class="warn-banner" style="margin-top:10px;">
            ⚠ Add <code style="font-size:0.8rem;background:rgba(255,255,255,0.1);padding:2px 6px;border-radius:4px;">OPENAI_API_KEY</code>
            to your <code style="font-size:0.8rem;background:rgba(255,255,255,0.1);padding:2px 6px;border-radius:4px;">.env</code>
            file and restart the API.
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="health-pill health-ok">
            <span class="dot dot-ok"></span> API Ready
        </div>""", unsafe_allow_html=True)

    # Generation history
    st.markdown('<div class="section-label">Recent Generations</div>', unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown('<div style="font-size:0.78rem;color:rgba(255,255,255,0.3);padding:6px 0;">No ads generated yet.</div>',
                    unsafe_allow_html=True)
    else:
        for i, item in enumerate(reversed(st.session_state.history[-8:])):
            headline_short = (item["headline"][:34] + "…") if len(item["headline"]) > 35 else item["headline"]
            st.markdown(f"""
            <div class="history-item">
                <div class="history-headline">{headline_short}</div>
                <div class="history-meta">{item['brand']} · {item['timestamp']}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f'<div style="font-size:0.65rem;color:rgba(255,255,255,0.25);text-align:center;">© 2025 AdCraft Pro</div>',
                unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Fetch API options (cached for the session)
# ---------------------------------------------------------------------------

if "api_info" not in st.session_state:
    st.session_state.api_info = fetch_api_info()

api_info = st.session_state.api_info


# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------

st.markdown("""
<div class="app-header">
    <div class="app-header-icon">✦</div>
    <div>
        <p class="app-header-title">AdCraft Pro</p>
        <p class="app-header-sub">Craft Premium Ads with AI Precision</p>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Results view (shown after a successful generation)
# ---------------------------------------------------------------------------

if st.session_state.show_result and st.session_state.last_result:
    result = st.session_state.last_result

    st.markdown("""
    <div class="success-banner">
        ✓ &nbsp;Ad generated successfully!
    </div>""", unsafe_allow_html=True)

    col_copy, col_img = st.columns([1, 1], gap="large")

    # ── Left: ad copy ────────────────────────────────────────────────────────
    with col_copy:
        st.markdown(f"""
        <div class="copy-card">
            <div style="font-size:0.72rem;font-weight:700;letter-spacing:0.14em;
                        text-transform:uppercase;color:rgba(255,255,255,0.3);
                        margin-bottom:1.2rem;">Ad Copy</div>

            <div class="copy-headline">{result.get('headline', '')}</div>
            <div class="copy-subheadline">{result.get('subheadline', '')}</div>
            <div class="copy-divider"></div>
            <div class="copy-body">{result.get('body_text', '')}</div>

            <a class="cta-button">{result.get('cta', 'SHOP NOW')}</a>

            <div class="copy-meta">
                <span class="meta-tag">{result.get('industry', '')}</span>
                <span class="meta-tag">{result.get('brand_name', '')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Right: generated image ────────────────────────────────────────────────
    with col_img:
        st.markdown('<div class="image-card">', unsafe_allow_html=True)
        st.markdown('<div class="image-card-title">Generated Visual</div>', unsafe_allow_html=True)

        image_url = result.get("image_url", "")
        if image_url:
            full_url = image_url if image_url.startswith("http") else f"{BACKEND_URL}{image_url}"
            st.image(full_url, use_container_width=True)

            img_bytes = download_image_bytes(image_url)
            if img_bytes:
                fname = f"adcraft_{result.get('brand_name','ad').lower().replace(' ','_')}.png"
                st.download_button(
                    label="⬇ Download Image",
                    data=img_bytes,
                    file_name=fname,
                    mime="image/png",
                    use_container_width=True,
                )
        else:
            st.markdown('<div style="color:rgba(255,255,255,0.3);font-size:0.85rem;'
                        'padding:3rem 0;text-align:center;">No image generated.</div>',
                        unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Debug expander ────────────────────────────────────────────────────────
    with st.expander("🔍 Full API Response (debug)"):
        st.code(json.dumps(result, indent=2), language="json")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✦ Generate Another Ad", type="primary"):
        st.session_state.show_result = False
        st.rerun()

    st.stop()


# ---------------------------------------------------------------------------
# Form view
# ---------------------------------------------------------------------------

# API offline banner above form
if health is None:
    st.markdown("""
    <div class="err-banner">
        ✗ &nbsp;Cannot reach the backend API at <strong>localhost:8000</strong>.
        Run <code>run.bat</code> to start both services, then refresh this page.
    </div>""", unsafe_allow_html=True)
elif not health.get("api_key_configured"):
    st.markdown("""
    <div class="warn-banner">
        ⚠ &nbsp;Backend is running but <strong>OPENAI_API_KEY</strong> is not configured.<br>
        Add it to your <code>.env</code> file and restart the API server.
    </div>""", unsafe_allow_html=True)

with st.form("ad_form", clear_on_submit=False):

    # ── Product block ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">📦 Product Details</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        product_name = st.text_input(
            "Product Name *",
            value=st.session_state.form_values.get("product_name", ""),
            placeholder="e.g., Bombay Musk Coolwater Perfume",
        )
    with c2:
        brand_name = st.text_input(
            "Brand Name *",
            value=st.session_state.form_values.get("brand_name", ""),
            placeholder="e.g., Bombay Musk",
        )

    product_description = st.text_area(
        "Product Description *",
        value=st.session_state.form_values.get("product_description", ""),
        placeholder="Describe your product, its features, materials, and what makes it unique...",
        height=100,
    )

    # ── Targeting block ───────────────────────────────────────────────────────
    st.markdown('<div class="section-label">🎯 Targeting</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        industry_opts = api_info.get("industries", [])
        saved_industry = st.session_state.form_values.get("industry", industry_opts[0] if industry_opts else "")
        industry_idx = industry_opts.index(saved_industry) if saved_industry in industry_opts else 0
        industry = st.selectbox("Industry *", industry_opts, index=industry_idx)

    with c4:
        platform_opts = api_info.get("platforms", [])
        saved_platform = st.session_state.form_values.get("platform", platform_opts[0] if platform_opts else "")
        platform_idx = platform_opts.index(saved_platform) if saved_platform in platform_opts else 0
        platform = st.selectbox("Target Platform *", platform_opts, index=platform_idx)

    key_benefit = st.text_input(
        "Key Benefit",
        value=st.session_state.form_values.get("key_benefit", ""),
        placeholder="e.g., Long-lasting scent that stays for 12 hours",
    )
    audience_desc = st.text_input(
        "Target Audience",
        value=st.session_state.form_values.get("audience_desc", ""),
        placeholder="e.g., Style-conscious professionals aged 25–40",
    )

    # ── Creative direction block ───────────────────────────────────────────────
    st.markdown('<div class="section-label">🎨 Creative Direction</div>', unsafe_allow_html=True)
    c5, c6, c7 = st.columns(3)
    with c5:
        tone_opts = api_info.get("tones", [])
        saved_tone = st.session_state.form_values.get("tone", tone_opts[0] if tone_opts else "")
        tone_idx = tone_opts.index(saved_tone) if saved_tone in tone_opts else 0
        tone = st.selectbox("Tone", tone_opts, index=tone_idx)

    with c6:
        style_opts = api_info.get("visual_styles", [])
        saved_style = st.session_state.form_values.get("visual_style", style_opts[0] if style_opts else "")
        style_idx = style_opts.index(saved_style) if saved_style in style_opts else 0
        visual_style = st.selectbox("Visual Style", style_opts, index=style_idx)

    with c7:
        principle_opts = api_info.get("principles", [])
        saved_principle = st.session_state.form_values.get("principle", principle_opts[0] if principle_opts else "")
        principle_idx = principle_opts.index(saved_principle) if saved_principle in principle_opts else 0
        principle = st.selectbox("Made to Stick Principle", principle_opts, index=principle_idx)

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("✦  Generate Ad", type="primary", use_container_width=True)


# ---------------------------------------------------------------------------
# Form submission
# ---------------------------------------------------------------------------

if submitted:
    # Persist values to session state
    st.session_state.form_values = {
        "product_name": product_name,
        "brand_name": brand_name,
        "product_description": product_description,
        "industry": industry,
        "platform": platform,
        "key_benefit": key_benefit,
        "audience_desc": audience_desc,
        "tone": tone,
        "visual_style": visual_style,
        "principle": principle,
    }

    # Validation
    missing = []
    if not product_name.strip():
        missing.append("Product Name")
    if not brand_name.strip():
        missing.append("Brand Name")
    if not product_description.strip():
        missing.append("Product Description")

    if missing:
        st.markdown(f"""
        <div class="err-banner">
            ✗ &nbsp;Please fill in the required fields: <strong>{", ".join(missing)}</strong>
        </div>""", unsafe_allow_html=True)
        st.stop()

    if health is None:
        st.markdown("""
        <div class="err-banner">
            ✗ &nbsp;Cannot connect to the backend. Start it with <code>run.bat</code> then try again.
        </div>""", unsafe_allow_html=True)
        st.stop()

    payload = {
        "product_name": product_name.strip(),
        "brand_name": brand_name.strip(),
        "product_description": product_description.strip(),
        "industry": industry,
        "platform": platform,
        "tone": tone,
        "visual_style": visual_style,
        "principle": principle,
        "key_benefit": key_benefit.strip(),
        "audience_desc": audience_desc.strip(),
    }

    with st.spinner("✦  Generating your ad — this takes ~30–60 seconds…"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/generate_ad",
                json=payload,
                timeout=120,
            )

            if response.status_code == 200:
                result = response.json()
                st.session_state.last_result = result
                st.session_state.show_result = True

                # Save to history
                st.session_state.history.append({
                    "headline":  result.get("headline", ""),
                    "brand":     result.get("brand_name", brand_name),
                    "timestamp": datetime.now().strftime("%H:%M"),
                })

                st.rerun()

            elif response.status_code == 503:
                detail = response.json().get("detail", "Service unavailable.")
                st.markdown(f"""
                <div class="err-banner">
                    ✗ &nbsp;<strong>API key not configured:</strong> {detail}
                </div>""", unsafe_allow_html=True)

            elif response.status_code == 422:
                detail = response.json().get("detail", "Validation error.")
                st.markdown(f"""
                <div class="err-banner">
                    ✗ &nbsp;<strong>Validation error:</strong> {detail}
                </div>""", unsafe_allow_html=True)

            else:
                detail = ""
                try:
                    detail = response.json().get("detail", response.text)
                except Exception:
                    detail = response.text
                st.markdown(f"""
                <div class="err-banner">
                    ✗ &nbsp;<strong>Generation failed (HTTP {response.status_code}):</strong><br>
                    {detail}
                </div>""", unsafe_allow_html=True)

        except requests.exceptions.ConnectionError:
            st.markdown("""
            <div class="err-banner">
                ✗ &nbsp;Lost connection to the backend. Make sure <code>run.bat</code> is running.
            </div>""", unsafe_allow_html=True)

        except requests.exceptions.Timeout:
            st.markdown("""
            <div class="err-banner">
                ✗ &nbsp;Request timed out after 120 seconds. The API may be overloaded — please try again.
            </div>""", unsafe_allow_html=True)

        except Exception as exc:
            st.markdown(f"""
            <div class="err-banner">
                ✗ &nbsp;<strong>Unexpected error:</strong> {exc}
            </div>""", unsafe_allow_html=True)
