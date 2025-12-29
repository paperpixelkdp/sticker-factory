import streamlit as st
import requests
from rembg import remove
from PIL import Image
import io
import time

# Page Configuration
st.set_page_config(page_title="Paper Pixel | Sticker Factory", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for Dark Professional Aesthetic
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #262730; color: white; border: 1px solid #464646; }
    .stButton>button:hover { background-color: #1c1c24; border: 1px solid #ffffff; }
    .stTextArea>div>div>textarea { background-color: #161b22; color: #ffffff; border: 1px solid #30363d; }
    div[data-baseweb="tab-list"] { gap: 20px; border-bottom: 1px solid #30363d; }
    div[data-baseweb="tab"] { color: #8b949e; }
    div[data-baseweb="tab"][aria-selected="true"] { color: #ffffff; border-bottom-color: #ffffff; }
    </style>
    """, unsafe_allow_stdio=True)

# Application Header
st.title("Paper Pixel Studio")
st.subheader("Sticker Factory")

# Top Navigation Tabs
tab_app, tab_guide, tab_support = st.tabs(["Sticker Factory", "User Guide", "Support"])

with tab_guide:
    st.markdown("""
    ### Workflow
    1. Enter your prompts line by line.
    2. Select your target platform and layout.
    3. Click generate and wait for the automated process.
    """)

with tab_support:
    st.markdown("""
    ### Support the Project
    This is a free-to-use professional tool. If it adds value to your business, consider supporting our development.
    """)

with tab_app:
    # Input Section
    prompts_text = st.text_area("Enter Prompts (One per line):", placeholder="Example:\nCute neon cat\nVintage forest landscape", height=200)
    
    col_plat, col_lay = st.columns(2)
    with col_plat:
        platform = st.selectbox("Target Platform", [
            "Redbubble (4500x5400)", 
            "Amazon Merch on Demand (4500x5400)", 
            "Etsy (3000x3000)", 
            "Manual"
        ])
    
    with col_lay:
        layout_choice = st.selectbox("Layout Selection", ["1x", "2x", "4x", "6x", "12x (A4)"])

    if st.button("Generate Stickers"):
        if not prompts_text.strip():
            st.error("Please enter at least one prompt.")
        else:
            prompts = [p.strip() for p in prompts_text.split("\n") if p.strip()]
            status_box = st.empty()
            
            for i, prompt in enumerate(prompts):
                status_box.info(f"Processing {i+1}/{len(prompts)}: {prompt}")
                
                # Robust Generation Logic (Inatçı Döngü)
                image_data = None
                retries = 10
                for attempt in range(retries):
                    try:
                        # Professional Prompt Enhancement
                        refined_prompt = f"{prompt}, isolated on white background, professional sticker art, high contrast, clean edges, 300 dpi"
                        api_url = f"https://pollinations.ai/p/{refined_prompt.replace(' ', '%20')}"
                        
                        response = requests.get(api_url, timeout=40)
                        
                        # Check if response is actually an image
                        if response.status_code == 200 and response.headers.get('content-type', '').startswith('image'):
                            image_data = response.content
                            break
                    except Exception:
                        time.sleep(2)
                
                if image_data:
                    try:
                        # Background Removal
                        status_box.info(f"Removing Background: {prompt}")
                        input_img = Image.open(io.BytesIO(image_data))
                        output_img = remove(input_img)
                        
                        # Clean Preview
                        st.image(output_img, caption=f"Result: {prompt}", width=300)
                        
                        # TODO: Future implementation for Upscaling and Sheet Layout
                        
                    except Exception as e:
                        st.error(f"Post-processing error for: {prompt}")
                else:
                    st.error(f"Generation failed after multiple attempts: {prompt}")

            status_box.success("Batch processing complete. Packaging features pending in next update.")