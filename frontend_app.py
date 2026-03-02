import streamlit as st
import requests
import json
import os

# Backend URL (replace with your own backend URL if needed)
BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AdCraft Pro",
    page_icon="\U0001F4F0",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("\U0001F4F0 AdCraft Pro")
st.caption("Craft Premium Ads with AI Precision")

# --- Sidebar for Project and Campaign Management ---
with st.sidebar:
    st.header("Manage Workflow")

    # Project Section
    st.subheader("\U0001F4C4 Project")
    project_name = st.text_input("Project Name", placeholder="e.g., Bombay Musk")
    industry = st.selectbox("Industry", ["Fragrance", "Technology", "Fashion", "Food", "Other"])
    platform = st.selectbox("Platform", ["Instagram", "Facebook", "Google", "LinkedIn", "Other"])

    if st.button("Create Project"):
        if project_name:
            st.success(f"Project '{project_name}' created!")
        else:
            st.error("Project name required.")

    # Campaign Section
    st.subheader("\U0001F3AF Campaign")
    campaign_name = st.text_input("Campaign Name", placeholder="e.g., Summer Launch")
    ad_type = st.selectbox("Ad Type", ["Feed", "Story", "Other"])
    audience_desc = st.text_area("Target Audience", placeholder="e.g., Car enthusiasts under 40")

    if st.button("Create Campaign"):
        if campaign_name:
            st.success(f"Campaign '{campaign_name}' created!")
        else:
            st.error("Campaign name required.")

st.divider()

# --- Main Ad Creation Workflow ---
st.header("\U0001F58C\ufe0f Ad Creation")

col1, col2 = st.columns(2)

with col1:
    product_name = st.text_input("Product Name", placeholder="e.g., BOMBAY MUSK Coolwater Perfume")
    brand_name = st.text_input("Brand Name", placeholder="e.g., Bombay Musk")
    product_desc = st.text_area("Product Description", placeholder="Describe your product...")
    benefit_desc = st.text_area("Key Benefit", placeholder="e.g., Affordable luxury fragrance")

with col2:
    tone = st.selectbox("Ad Tone", ["Luxury", "Playful", "Bold", "Minimalistic", "Emotional", "Logical"])
    visual_style = st.selectbox("Visual Style", ["Minimalist", "Vibrant", "Dark", "Light", "Other"])
    made_to_stick = st.selectbox("Made to Stick Principle", ["Emotional", "Credible", "Simple", "Concrete", "Unexpected", "Story-driven"])
    submit = st.button("\U0001F680 Generate Ad")

# --- Generate Ad ---
if submit:
    if not all([product_name, brand_name, product_desc, benefit_desc]):
        st.error("Please fill out all required fields.")
    else:
        with st.spinner("Generating your ad..."):
            payload = {
                "product_name": product_name,
                "brand_name": brand_name,
                "product_description": product_desc,
                "key_benefit": benefit_desc,
                "tone": tone,
                "visual_style": visual_style,
                "principle": made_to_stick,
                "industry": industry,
                "platform": platform,
                "project_name": project_name,
                "campaign_name": campaign_name,
                "audience_desc": audience_desc
            }
            try:
                res = requests.post(f"{BACKEND_URL}/generate_ad", json=payload, timeout=60)
                if res.status_code == 200:
                    ad_data = res.json()

                    st.success("Ad Generated Successfully!")

                    st.subheader("Generated Ad")
                    
                    # FIXED IMAGE HANDLING CODE
                    # Handle image URL from backend
                    image_url = ad_data["image_url"]
    
# If it's a relative URL, prepend the backend base URL
                    if image_url.startswith("/"):
                        image_url = f"{BACKEND_URL}{image_url}"
    
# Display the DALL-E generated image
                    st.image(image_url, use_container_width=True)

                    st.markdown(f"**Headline:** {ad_data['headline']}")
                    st.markdown(f"**Subheadline:** {ad_data['subheadline']}")
                    st.markdown(f"**Body Text:** {ad_data['body_text']}")
                    st.markdown(f"**Call to Action:** {ad_data['cta']}")

                    with st.expander("\U0001F4DD Feedback on this Ad"):
                        feedback = st.text_area("Your thoughts:")
                        if st.button("Submit Feedback"):
                            st.success("Feedback submitted! (mock)")
                else:
                    st.error("Failed to generate ad. Please retry.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.divider()

st.caption("\u00a9 2025 AdCraft Pro. Built for Creative Professionals.")