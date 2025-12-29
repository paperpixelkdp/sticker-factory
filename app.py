import streamlit as st
import requests
from rembg import remove
from PIL import Image
import io
import time
import random
from urllib.parse import quote

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
    """, unsafe_allow_html=True)

# Application Header
st.title("Paper Pixel Studio")
st.subheader("Sticker Factory")

tab_app, tab_guide, tab_support = st.tabs(["Sticker Factory", "User Guide", "Support"])

with tab_guide:
    st.markdown("### Workflow\n1. Enter prompts line by line.\n2. Select platform/layout.\n3. Generate and wait.")

with tab_support:
    st.markdown("### Support the Project\nThis is a free-to-use professional tool for POD sellers.")

with tab_app:
    prompts_text = st.text_area("Enter Prompts (One per line):", placeholder="Example:\nCute crocodile drinking cola\nCyberpunk owl", height=200)
    
    col_plat, col_lay = st.columns(2)
    with col_plat:
        platform = st.selectbox("Target Platform", ["Redbubble (4500x5400)", "Amazon Merch (4500x5400)", "Etsy (3000x3000)", "Manual"])
    with col_lay:
        layout_choice = st.selectbox("Layout Selection", ["1x", "2x", "4x", "6x", "12x (A4)"])

    if st.button("Generate Stickers"):
        if not prompts_text.strip():
            st.error("Please enter at least one prompt.")
        else:
            prompts = [p.strip() for p in prompts_text.split("\n") if p.strip()]
            status_box = st.empty()
            
            for i, prompt in enumerate(prompts):
                image_data = None
                retries = 15  # İnatçılık dozunu artırdık
                
                for attempt in range(retries):
                    status_box.info(f"Processing {i+1}/{len(prompts)} | Attempt {attempt+1}: {prompt}")
                    try:
                        # Random seed ekleyerek sunucuyu taze görsel üretmeye zorluyoruz
                        seed = random.randint(1, 999999)
                        refined_prompt = quote(f"{prompt}, sticker style, white background, high resolution, clean edges")
                        api_url = f"https://pollinations.ai/p/{refined_prompt}?seed={seed}&width=1024&height=1024&nologo=true"
                        
                        response = requests.get(api_url, timeout=30)
                        
                        if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                            image_data = response.content
                            break
                        else:
                            time.sleep(3) # Sunucuya nefes aldır
                    except Exception:
                        time.sleep(3)
                
                if image_data:
                    try:
                        status_box.info(f"Removing Background: {prompt}")
                        input_img = Image.open(io.BytesIO(image_data))
                        output_img = remove(input_img)
                        st.image(output_img, caption=f"Result: {prompt}", width=400)
                    except Exception as e:
                        st.error(f"Post-processing error for: {prompt}")
                else:
                    st.error(f"Generation failed: {prompt}. The AI server is busy, please try again later.")

            status_box.success("Processing complete.")