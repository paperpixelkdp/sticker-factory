import streamlit as st
import requests
import numpy as np
import cv2
from PIL import Image
from rembg import remove
import io
import time
from huggingface_hub import InferenceClient
import zipfile

# --- CONFIG ---
st.set_page_config(page_title="Paper Pixel | Sticker Cloud", layout="wide", initial_sidebar_state="collapsed")

# Secrets Kontrolü (GÜVENLİK)
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"].strip() # Boşlukları otomatik temizler
else:
    st.error("⚠️ HF_TOKEN is missing in Streamlit Secrets!")
    st.stop()

# Model Havuzu
MODEL_POOL = [
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5",
    "prompthero/openjourney",
    "CompVis/stable-diffusion-v1-4",
    "stabilityai/sd-turbo"
]

# --- CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; background-color: #262730; color: white; border: 1px solid #464646; font-weight: bold; }
    .status-log { font-family: 'Courier New', monospace; color: #00ff00; font-size: 0.85em; margin: 0; }
    .error-log { font-family: 'Courier New', monospace; color: #ff4b4b; font-size: 0.85em; margin: 0; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORLAR ---

def add_sticker_outline(img):
    img_array = np.array(img)
    alpha = img_array[:, :, 3]
    kernel = np.ones((15, 15), np.uint8) 
    mask_dilated = cv2.dilate(alpha, kernel, iterations=1)
    outline = np.zeros_like(img_array)
    outline[mask_dilated > 0] = [255, 255, 255, 255]
    outline_img = Image.fromarray(outline)
    outline_img.paste(img, (0, 0), img)
    return outline_img

def generate_image(prompt, status_placeholder):
    refined_prompt = f"sticker design of {prompt}, white background, vector art, die-cut style, high contrast, sharp edges"
    
    # 20 saniyelik inatçı döngü
    for attempt in range(2): # 2 Tur
        for model_id in MODEL_POOL:
            status_placeholder.markdown(f"<p class='status-log'>🔄 Trying Model: {model_id.split('/')[-1]}...</p>", unsafe_allow_html=True)
            try:
                client = InferenceClient(model=model_id, token=HF_TOKEN)
                image = client.text_to_image(refined_prompt)
                return image
            except Exception as e:
                error_msg = str(e)
                if "401" in error_msg:
                    status_placeholder.markdown(f"<p class='error-log'>❌ ERROR: YOUR TOKEN IS INVALID (401). Check Secrets!</p>", unsafe_allow_html=True)
                    st.stop() # Yanlış şifreyle denemeye devam etme
                
                status_placeholder.markdown(f"<p class='error-log'>⚠️ Busy. Waiting 20 seconds for next attempt...</p>", unsafe_allow_html=True)
                time.sleep(20) # Ustamın istediği 20 saniyelik mola
                continue 
    return None

# --- UI ---
st.title("Paper Pixel Studio")
st.subheader("Sticker Cloud Engine v2.1")

tab_factory, tab_guide = st.tabs(["🏭 Factory", "📘 Guide"])

with tab_factory:
    col_in, col_pre = st.columns([1, 1], gap="large")
    
    with col_in:
        prompts_raw = st.text_area("Enter Prompts:", height=150, placeholder="Example: Cute crocodile")
        btn_start = st.button("START PRODUCTION LINE")

    with col_pre:
        monitor = st.empty()
        preview_container = st.container()

    if btn_start:
        if not prompts_raw.strip():
            st.error("No prompts found.")
        else:
            prompts = [p.strip() for p in prompts_raw.split("\n") if p.strip()]
            all_imgs = []
            
            for i, p in enumerate(prompts):
                raw_img = generate_image(p, monitor)
                
                if raw_img:
                    monitor.markdown(f"<p class='status-log'>✂️ Removing Background...</p>", unsafe_allow_html=True)
                    processed_img = remove(raw_img)
                    final_sticker = add_sticker_outline(processed_img)
                    
                    # 4x Upscale
                    w, h = final_sticker.size
                    final_sticker = final_sticker.resize((w*4, h*4), resample=Image.LANCZOS)
                    
                    all_imgs.append(final_sticker)
                    with preview_container:
                        st.image(final_sticker, caption=f"Ready: {p}", width=250)
                else:
                    st.error(f"Failed to manifest: {p} (All models failed after waiting)")

            if all_imgs:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    for idx, img in enumerate(all_imgs):
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='PNG')
                        zip_file.writestr(f"sticker_{idx+1}.png", img_byte_arr.getvalue())
                
                st.download_button("📥 DOWNLOAD ZIP PACK", zip_buffer.getvalue(), "Pack.zip", "application/zip")