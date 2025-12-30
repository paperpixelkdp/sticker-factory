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
import math

# --- CONFIG ---
st.set_page_config(page_title="Paper Pixel | Sticker Cloud", layout="wide", initial_sidebar_state="collapsed")

# Secrets Check
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"].strip()
else:
    st.error("⚠️ HF_TOKEN is missing!")
    st.stop()

# Model Pool
MODEL_POOL = [
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5",
    "prompthero/openjourney",
    "CompVis/stable-diffusion-v1-4",
    "stabilityai/sd-turbo"
]

# --- CSS (Professional Dark) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; background-color: #262730; color: white; border: 1px solid #464646; font-weight: bold; }
    .status-log { font-family: 'Courier New', monospace; color: #00ff00; font-size: 0.85em; margin: 0; }
    .error-log { font-family: 'Courier New', monospace; color: #ff4b4b; font-size: 0.85em; margin: 0; }
    .stTextArea textarea { background-color: #161b22 !important; color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE MOTORS ---

def add_sticker_outline(img, thickness=30):
    """Adds a thick, professional white die-cut outline."""
    img_array = np.array(img)
    alpha = img_array[:, :, 3]
    kernel = np.ones((thickness, thickness), np.uint8) 
    mask_dilated = cv2.dilate(alpha, kernel, iterations=1)
    outline = np.zeros_like(img_array)
    outline[mask_dilated > 0] = [255, 255, 255, 255]
    outline_img = Image.fromarray(outline)
    outline_img.paste(img, (0, 0), img)
    return outline_img

def generate_image(prompt, status_placeholder):
    refined_prompt = f"sticker design of {prompt}, white background, vector art, die-cut style, high contrast, sharp edges, 300 dpi"
    for attempt in range(2):
        for model_id in MODEL_POOL:
            status_placeholder.markdown(f"<p class='status-log'>🔄 Using Node: {model_id.split('/')[-1]}...</p>", unsafe_allow_html=True)
            try:
                client = InferenceClient(model=model_id, token=HF_TOKEN)
                image = client.text_to_image(refined_prompt)
                return image
            except Exception:
                status_placeholder.markdown(f"<p class='error-log'>⚠️ Node busy. Retrying in 20s...</p>", unsafe_allow_html=True)
                time.sleep(20)
                continue 
    return None

def create_sticker_sheet(images, canvas_size=(4500, 5400), layout=6):
    """Packs stickers into a high-res POD ready canvas."""
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    cols = 2 if layout >= 2 else 1
    rows = math.ceil(layout / cols)
    
    cell_w = canvas_size[0] // cols
    cell_h = canvas_size[1] // rows
    
    for idx, img in enumerate(images[:layout]):
        # Resize sticker to fit cell with padding
        img.thumbnail((cell_w - 200, cell_h - 200), Image.LANCZOS)
        
        x = (idx % cols) * cell_w + (cell_w - img.width) // 2
        y = (idx // cols) * cell_h + (cell_h - img.height) // 2
        canvas.paste(img, (x, y), img)
    return canvas

# --- UI ---
st.title("Paper Pixel Studio")
st.subheader("Sticker Cloud Automation v3.0")

tab_factory, tab_guide, tab_about, tab_support = st.tabs(["🏭 Factory", "📘 Guide", "ℹ️ About", "☕ Support"])

with tab_factory:
    col_in, col_pre = st.columns([1, 1], gap="large")
    
    with col_in:
        st.markdown("#### Production Line")
        prompts_raw = st.text_area("Enter Prompts (Max 6 per batch):", height=150, placeholder="Example: Cute coffee mug\nVintage astronaut")
        
        platform = st.selectbox("POD Presets", ["Redbubble/Amazon (4500x5400)", "Etsy A4 (2480x3508)"])
        layout_mode = st.selectbox("Layout Mode", [1, 2, 4, 6])
        
        btn_start = st.button("EXECUTE PRODUCTION")

    with col_pre:
        monitor = st.empty()
        preview_container = st.container()

    if btn_start:
        prompts = [p.strip() for p in prompts_raw.split("\n") if p.strip()]
        if not prompts:
            st.error("No input detected.")
        elif len(prompts) > 6:
            st.error("Safety Limit: Please enter maximum 6 prompts at a time.")
        else:
            all_stickers = []
            for i, p in enumerate(prompts):
                raw_img = generate_image(p, monitor)
                if raw_img:
                    monitor.markdown(f"<p class='status-log'>✂️ Removing Background & Adding Outline...</p>", unsafe_allow_html=True)
                    processed = remove(raw_img)
                    outlined = add_sticker_outline(processed, thickness=30)
                    # 4x Upscale
                    w, h = outlined.size
                    upscaled = outlined.resize((w*4, h*4), resample=Image.LANCZOS)
                    all_stickers.append(upscaled)
                    
                    with preview_container:
                        st.image(upscaled, caption=f"Sticker {i+1}", width=200)
                else:
                    st.error(f"Failed to generate: {p}")

            if all_stickers:
                monitor.markdown(f"<p class='status-log'>📦 Packing high-res sheets...</p>", unsafe_allow_html=True)
                
                # Canvas size based on platform
                c_size = (4500, 5400) if "Redbubble" in platform else (2480, 3508)
                
                # Generate sheets
                num_sheets = math.ceil(len(all_stickers) / layout_mode)
                final_sheets = []
                for s in range(num_sheets):
                    start = s * layout_mode
                    end = start + layout_mode
                    sheet = create_sticker_sheet(all_stickers[start:end], canvas_size=c_size, layout=layout_mode)
                    final_sheets.append(sheet)

                # ZIP
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_f:
                    # Save individual stickers
                    for idx, s in enumerate(all_stickers):
                        buf = io.BytesIO()
                        s.save(buf, format="PNG")
                        zip_f.writestr(f"individual_stickers/sticker_{idx+1}.png", buf.getvalue())
                    # Save sheets
                    for idx, sheet in enumerate(final_sheets):
                        buf = io.BytesIO()
                        sheet.save(buf, format="PNG")
                        zip_f.writestr(f"print_ready_sheets/sheet_{idx+1}.png", buf.getvalue())
                
                st.success("All stickers and sheets are ready!")
                st.download_button("📥 DOWNLOAD PRODUCTION PACK (ZIP)", zip_buffer.getvalue(), "PaperPixel_Pack.zip", "application/zip")

# --- OTHER TABS ---
with tab_guide:
    st.markdown("Enter up to 6 prompts. Our engine tries 5 models x 2 rounds with 20s cooldown. Best results for POD.")

with tab_about:
    st.markdown("Paper Pixel Studio: AI-powered automation for creative entrepreneurs.")

with tab_support:
    st.markdown("Help us keep this tool free! ☕")