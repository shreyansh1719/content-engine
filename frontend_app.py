"""
AdCraft Pro — Premium Streamlit Frontend
Dark luxury aesthetic inspired by Apple.com, Linear, Vercel.

Run with:
    streamlit run frontend_app.py
"""
import requests
from datetime import datetime

import streamlit as st

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BACKEND_URL = "http://localhost:8000"

# ---------------------------------------------------------------------------
# Page config — must be the first Streamlit call
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AdCraft Pro",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS — complete override of Streamlit defaults
# ---------------------------------------------------------------------------

st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,300;1,9..40,400&family=DM+Serif+Display&display=swap');

/* ── Global reset ── */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background-color: #080808;
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #E8E8E8;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], .stDeployButton { display: none !important; }

/* Custom scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #080808; }
::-webkit-scrollbar-thumb { background: #2A2A2A; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3A3A3A; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #0D0D0D !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Sidebar labels */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stTextArea label {
    color: #555 !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    font-weight: 500 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Sidebar markdown section headers */
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #333 !important;
    font-size: 0.65rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.15em !important;
    font-weight: 600 !important;
    margin: 1.5rem 0 0.5rem 0 !important;
    padding-bottom: 0.5rem !important;
    border-bottom: 1px solid rgba(255,255,255,0.04) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Input fields */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
    background-color: #151515 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 8px !important;
    color: #D0D0D0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color 0.2s ease !important;
}

[data-testid="stSidebar"] input:focus,
[data-testid="stSidebar"] textarea:focus {
    border-color: rgba(255,255,255,0.18) !important;
    box-shadow: 0 0 0 2px rgba(255,255,255,0.04) !important;
    outline: none !important;
}

[data-testid="stSidebar"] input::placeholder,
[data-testid="stSidebar"] textarea::placeholder {
    color: #3A3A3A !important;
}

/* Selectbox */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #151515 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 8px !important;
    color: #D0D0D0 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] span {
    color: #D0D0D0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
}

/* Dropdown list */
[data-baseweb="popover"] { background: #1A1A1A !important; }
[data-baseweb="menu"] { background: #1A1A1A !important; border: 1px solid rgba(255,255,255,0.08) !important; }
[role="option"] { background: #1A1A1A !important; color: #C0C0C0 !important; }
[role="option"]:hover { background: #222 !important; }

/* Generate button */
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: #FFFFFF !important;
    color: #080808 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.8rem 1.5rem !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.03em !important;
    font-family: 'DM Sans', sans-serif !important;
    cursor: pointer !important;
    transition: all 0.25s ease !important;
    margin-top: 0.75rem !important;
    box-shadow: 0 1px 0 rgba(255,255,255,0.1), 0 4px 16px rgba(255,255,255,0.06) !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: #E8E8E8 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(255,255,255,0.12) !important;
}

[data-testid="stSidebar"] .stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Main content ── */
.main .block-container {
    padding: 2.5rem 3rem 3rem 3rem;
    max-width: 1100px;
}

/* ── Typography ── */
.hero-title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.6rem;
    font-weight: 400;
    color: #F0F0F0;
    letter-spacing: -0.025em;
    line-height: 1.05;
    margin: 0 0 0.4rem 0;
}

.hero-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    color: #444;
    font-weight: 300;
    letter-spacing: 0.01em;
    line-height: 1.5;
}

/* ── Status badge ── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
    font-family: 'DM Sans', sans-serif;
}

.status-online {
    background: rgba(52, 199, 89, 0.08);
    color: #30D158;
    border: 1px solid rgba(52, 199, 89, 0.18);
}

.status-devmode {
    background: rgba(255, 159, 10, 0.08);
    color: #FF9F0A;
    border: 1px solid rgba(255, 159, 10, 0.18);
}

.status-offline {
    background: rgba(255, 69, 58, 0.08);
    color: #FF453A;
    border: 1px solid rgba(255, 69, 58, 0.18);
}

/* ── Divider ── */
.subtle-divider {
    height: 1px;
    background: rgba(255,255,255,0.04);
    margin: 2.5rem 0;
    border: none;
}

/* ── Empty state ── */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
    text-align: center;
    padding: 4rem 2rem;
}

.empty-state-diamond {
    font-size: 2.5rem;
    color: #1E1E1E;
    margin-bottom: 1.5rem;
    line-height: 1;
}

.empty-state-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: #2A2A2A;
    margin-bottom: 0.6rem;
}

.empty-state-text {
    font-size: 0.85rem;
    color: #383838;
    max-width: 360px;
    line-height: 1.65;
}

.empty-state-steps {
    display: flex;
    gap: 2rem;
    margin-top: 2.5rem;
    flex-wrap: wrap;
    justify-content: center;
}

.empty-state-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
    width: 100px;
}

.step-num {
    width: 28px; height: 28px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem;
    color: #3A3A3A;
    font-weight: 600;
    font-family: 'DM Sans', sans-serif;
}

.step-text {
    font-size: 0.7rem;
    color: #2E2E2E;
    text-align: center;
    line-height: 1.4;
    font-family: 'DM Sans', sans-serif;
}

/* ── Ad result layout ── */
.ad-image-wrapper {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06);
    background: #0D0D0D;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 1px 0 rgba(255,255,255,0.05);
}

.ad-copy-card {
    background: #0D0D0D;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 2rem;
    height: 100%;
}

.ad-headline-display {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.55rem;
    color: #F0F0F0;
    line-height: 1.2;
    margin-bottom: 0.75rem;
    letter-spacing: -0.01em;
}

.ad-subheadline-display {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    color: #777;
    font-style: italic;
    margin-bottom: 1rem;
    line-height: 1.5;
    font-weight: 300;
}

.ad-body-display {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.82rem;
    color: #555;
    line-height: 1.7;
    margin-bottom: 1.5rem;
}

.ad-cta-pill {
    display: inline-block;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #E0E0E0;
    padding: 7px 18px;
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 6px;
}

/* ── Metadata pills ── */
.metadata-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 1.75rem;
    padding-top: 1.25rem;
    border-top: 1px solid rgba(255,255,255,0.04);
}

.meta-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 5px;
    font-size: 0.68rem;
    font-family: 'DM Sans', sans-serif;
}

.meta-pill-key {
    color: #3A3A3A;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}

.meta-pill-val {
    color: #777;
}

/* ── Download button ── */
.main .stDownloadButton > button {
    background: transparent !important;
    color: #666 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    padding: 0.55rem 1.25rem !important;
    transition: all 0.2s ease !important;
}

.main .stDownloadButton > button:hover {
    border-color: rgba(255,255,255,0.18) !important;
    color: #999 !important;
    background: rgba(255,255,255,0.03) !important;
}

/* ── Expander (feedback) ── */
.streamlit-expanderHeader {
    background: transparent !important;
    color: #3A3A3A !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 8px !important;
}

.streamlit-expanderContent {
    background: #0D0D0D !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 1rem !important;
}

/* Expander inner inputs */
.streamlit-expanderContent input,
.streamlit-expanderContent textarea {
    background: #151515 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 7px !important;
    color: #C0C0C0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
}

.streamlit-expanderContent .stButton > button {
    background: transparent !important;
    color: #555 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 7px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    transition: all 0.2s ease !important;
}

.streamlit-expanderContent .stButton > button:hover {
    border-color: rgba(255,255,255,0.15) !important;
    color: #888 !important;
}

/* Slider */
.stSlider { filter: brightness(0.7) saturate(0.3); }

/* ── History section ── */
.history-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #2E2E2E;
    font-weight: 600;
    margin-bottom: 0.75rem;
}

.history-thumb-wrapper {
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.05);
    transition: border-color 0.25s ease;
}

.history-thumb-wrapper:hover { border-color: rgba(255,255,255,0.12); }

.history-caption {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.68rem;
    color: #333;
    margin-top: 0.3rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* ── Error / warning override ── */
.stAlert {
    background: rgba(255,69,58,0.06) !important;
    border: 1px solid rgba(255,69,58,0.15) !important;
    border-radius: 8px !important;
    color: #FF6B6B !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.83rem !important;
}

.stSuccess {
    background: rgba(52,199,89,0.06) !important;
    border: 1px solid rgba(52,199,89,0.15) !important;
    border-radius: 8px !important;
    color: #4ADE80 !important;
}

/* Spinner */
.stSpinner > div { border-top-color: #333 !important; }

/* Columns gap */
[data-testid="column"] { padding: 0 0.5rem; }
[data-testid="column"]:first-child { padding-left: 0; }
[data-testid="column"]:last-child { padding-right: 0; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "current_ad" not in st.session_state:
    st.session_state.current_ad = None
if "history" not in st.session_state:
    st.session_state.history = []


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

col_title, col_status = st.columns([5, 1])

with col_title:
    st.markdown('<div class="hero-title">AdCraft Pro</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">AI-powered ad generation driven by fine-tuned creative intelligence</div>',
        unsafe_allow_html=True,
    )

with col_status:
    try:
        health = requests.get(f"{BACKEND_URL}/health", timeout=3).json()
        if health.get("api_key_valid"):
            badge_cls = "status-online"
            badge_label = "● Production"
        elif health.get("dev_mode"):
            badge_cls = "status-devmode"
            badge_label = "● Dev Mode"
        else:
            badge_cls = "status-offline"
            badge_label = "● No Key"
    except Exception:
        badge_cls = "status-offline"
        badge_label = "● API Offline"

    st.markdown(
        f'<div style="text-align:right; padding-top:0.6rem;">'
        f'<div class="status-badge {badge_cls}">{badge_label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar — input form
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        '<div style="font-family:\'DM Serif Display\',serif;font-size:1.15rem;'
        'color:#E8E8E8;letter-spacing:-0.01em;margin-bottom:0.25rem;">New Ad</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:0.72rem;color:#333;margin-bottom:1.5rem;">Fill in the brief, then generate.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Brand")
    brand_name = st.text_input("Brand Name", placeholder="Apple", key="brand")
    product_name = st.text_input("Product Name", placeholder="AirPods Pro 3", key="product")

    st.markdown("### Product")
    product_desc = st.text_area(
        "Description",
        placeholder="What makes this product special...",
        height=75,
        key="desc",
    )
    key_benefit = st.text_input("Key Benefit", placeholder="Spatial audio with hearing health", key="benefit")

    st.markdown("### Creative Direction")
    col1, col2 = st.columns(2)
    with col1:
        industry = st.selectbox(
            "Industry",
            ["Technology", "Luxury", "Fashion", "Food & Beverage", "Beauty",
             "Automotive", "Gaming", "Health & Fitness", "Finance", "Other"],
            key="industry",
        )
        tone = st.selectbox(
            "Tone",
            ["Premium", "Bold", "Playful", "Minimalist", "Emotional",
             "Technical", "Raw", "Cinematic", "Direct"],
            key="tone",
        )
    with col2:
        platform = st.selectbox(
            "Platform",
            ["Instagram", "Facebook", "LinkedIn", "TikTok",
             "Pinterest", "YouTube", "Google", "Other"],
            key="platform",
        )
        visual_style = st.selectbox(
            "Visual Style",
            ["Dramatic Lighting", "Minimalist", "Vibrant", "Vintage",
             "3D Render", "Monochrome", "Pastel", "Editorial", "Flat Lay"],
            key="vstyle",
        )

    audience = st.text_input(
        "Target Audience", placeholder="Tech-savvy professionals 25–45", key="audience"
    )

    generate = st.button("Generate Ad", use_container_width=True, key="gen_btn")

    # Sidebar footer
    st.markdown(
        '<div style="margin-top:3rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,0.04);">'
        '<div style="font-size:0.65rem;color:#222;line-height:1.7;">'
        'AdCraft Pro uses a fine-tuned GPT-4o-mini for creative briefs, '
        'GPT-4o for HTML/CSS overlays, and DALL-E 3 for product imagery.</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Generation logic
# ---------------------------------------------------------------------------

if generate:
    if not brand_name or not product_name:
        st.error("Brand name and product name are required.")
    else:
        payload = {
            "product_name": product_name,
            "brand_name": brand_name,
            "product_description": product_desc or "",
            "key_benefit": key_benefit or "",
            "tone": tone,
            "visual_style": visual_style,
            "principle": "Emotional",
            "industry": industry,
            "platform": platform,
            "audience_desc": audience or "",
        }

        with st.spinner(""):
            st.markdown(
                '<div style="text-align:center;padding:3rem 1rem;">'
                '<div style="font-family:\'DM Sans\',sans-serif;font-size:0.85rem;color:#333;">'
                'Generating your ad…'
                '</div>'
                '<div style="font-size:0.72rem;color:#222;margin-top:0.5rem;line-height:1.8;">'
                'Fine-tuned model&nbsp;→&nbsp;Creative brief&nbsp;→&nbsp;'
                'Copy + HTML/CSS&nbsp;→&nbsp;DALL-E image&nbsp;→&nbsp;Composite'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/generate_ad",
                    json=payload,
                    timeout=180,
                )
                if resp.status_code == 200:
                    ad = resp.json()
                    st.session_state.current_ad = ad
                    st.session_state.history.insert(0, {
                        "ad": ad,
                        "brand": brand_name,
                        "product": product_name,
                        "timestamp": datetime.now().strftime("%H:%M"),
                    })
                    st.session_state.history = st.session_state.history[:8]
                    st.rerun()
                else:
                    detail = resp.json().get("detail", resp.text) if resp.headers.get("content-type", "").startswith("application/json") else resp.text
                    st.error(f"Generation failed ({resp.status_code}): {detail}")
            except requests.exceptions.Timeout:
                st.error("Request timed out. The pipeline takes ~30–60 s — the server may still be working. Refresh after a minute.")
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach the API. Start it with: uvicorn api:app --port 8000")
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")


# ---------------------------------------------------------------------------
# Main display area
# ---------------------------------------------------------------------------

if st.session_state.current_ad:
    ad = st.session_state.current_ad

    image_url = ad.get("image_url", "")
    full_url = f"{BACKEND_URL}{image_url}" if image_url.startswith("/") else image_url

    # ── Two-column layout: image left, copy right ──
    img_col, copy_col = st.columns([5, 4], gap="large")

    with img_col:
        if full_url:
            st.markdown('<div class="ad-image-wrapper">', unsafe_allow_html=True)
            try:
                st.image(full_url, use_container_width=True)
            except Exception:
                st.markdown(
                    '<div style="height:400px;display:flex;align-items:center;'
                    'justify-content:center;color:#2A2A2A;font-size:0.8rem;">'
                    'Image unavailable</div>',
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

            # Download button under the image
            try:
                img_bytes = requests.get(full_url, timeout=30)
                if img_bytes.status_code == 200:
                    safe_brand = (brand_name or "ad").replace(" ", "_").lower()
                    safe_product = (product_name or "image").replace(" ", "_").lower()
                    st.download_button(
                        "↓  Download Image",
                        data=img_bytes.content,
                        file_name=f"adcraft_{safe_brand}_{safe_product}.png",
                        mime="image/png",
                    )
            except Exception:
                pass

    with copy_col:
        headline = ad.get("headline", "")
        subheadline = ad.get("subheadline", "")
        body_text = ad.get("body_text", "")
        cta = ad.get("call_to_action", "")
        tone_val = ad.get("tone", "")
        style_val = ad.get("visual_style", "")
        design_val = ad.get("design_approach", "")

        st.markdown(
            f'<div class="ad-copy-card">'
            f'<div class="ad-headline-display">{headline}</div>'
            f'<div class="ad-subheadline-display">{subheadline}</div>'
            f'{"<div class=ad-body-display>" + body_text + "</div>" if body_text else ""}'
            f'<div class="ad-cta-pill">{cta}</div>'
            f'<div class="metadata-row">'
            f'<div class="meta-pill"><span class="meta-pill-key">Tone</span><span class="meta-pill-val">{tone_val or "—"}</span></div>'
            f'<div class="meta-pill"><span class="meta-pill-key">Style</span><span class="meta-pill-val">{style_val or "—"}</span></div>'
            f'<div class="meta-pill"><span class="meta-pill-key">Layout</span><span class="meta-pill-val">{design_val or "—"}</span></div>'
            f'<div class="meta-pill"><span class="meta-pill-key">Platform</span><span class="meta-pill-val">{platform}</span></div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Feedback expander ──
    st.markdown('<div style="margin-top:1.5rem;"></div>', unsafe_allow_html=True)
    with st.expander("Submit Feedback"):
        fb_col1, fb_col2 = st.columns([1, 3])
        with fb_col1:
            rating = st.slider("Rating", 1, 5, 4, key="fb_rating")
        with fb_col2:
            fb_text = st.text_area(
                "Comments",
                placeholder="What worked well? What could be improved?",
                height=68,
                key="fb_text",
                label_visibility="collapsed",
            )
        if st.button("Submit Feedback", key="fb_submit"):
            try:
                fb_resp = requests.post(
                    f"{BACKEND_URL}/submit_feedback",
                    json={
                        "ad_id": ad.get("ad_id", "unknown"),
                        "headline": headline,
                        "rating": rating,
                        "strengths": fb_text if rating >= 4 else "",
                        "weaknesses": fb_text if rating < 4 else "",
                    },
                    timeout=10,
                )
                if fb_resp.status_code == 200:
                    st.success("Feedback saved — thank you.")
                else:
                    st.error("Could not save feedback.")
            except Exception:
                st.error("Could not reach the feedback endpoint.")

else:
    # ── Empty state ──
    st.markdown(
        '<div class="empty-state">'
        '<div class="empty-state-diamond">◆</div>'
        '<div class="empty-state-title">Create your first ad</div>'
        '<div class="empty-state-text">'
        'Enter your brand and product details in the sidebar, choose your creative direction, '
        'and let the AI pipeline craft a production-ready advertisement.'
        '</div>'
        '<div class="empty-state-steps">'
        '<div class="empty-state-step"><div class="step-num">1</div><div class="step-text">Brand & product</div></div>'
        '<div class="empty-state-step"><div class="step-num">2</div><div class="step-text">Creative brief</div></div>'
        '<div class="empty-state-step"><div class="step-num">3</div><div class="step-text">Generate</div></div>'
        '<div class="empty-state-step"><div class="step-num">4</div><div class="step-text">Download</div></div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# History strip
# ---------------------------------------------------------------------------

if st.session_state.history:
    st.markdown('<hr class="subtle-divider">', unsafe_allow_html=True)
    st.markdown('<div class="history-label">Recent</div>', unsafe_allow_html=True)

    visible = st.session_state.history[:6]
    cols = st.columns(len(visible))

    for i, item in enumerate(visible):
        with cols[i]:
            hist_url = item["ad"].get("image_url", "")
            if hist_url:
                full_hist = f"{BACKEND_URL}{hist_url}" if hist_url.startswith("/") else hist_url
                try:
                    st.markdown('<div class="history-thumb-wrapper">', unsafe_allow_html=True)
                    st.image(full_hist, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception:
                    st.markdown(
                        '<div style="height:80px;border:1px solid rgba(255,255,255,0.05);'
                        'border-radius:8px;"></div>',
                        unsafe_allow_html=True,
                    )
            st.markdown(
                f'<div class="history-caption">{item["brand"]} · {item["timestamp"]}</div>',
                unsafe_allow_html=True,
            )
