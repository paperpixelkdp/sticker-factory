import streamlit as st
import requests
import numpy as np
import cv2
from PIL import Image, ImageFilter
from rembg import remove
import io
import time
from huggingface_hub import InferenceClient
import zipfile
import math

# --- CONFIG ---
st.set_page_config(page_title="Paper Pixel | Sticker Cloud", layout="wide", initial_sidebar_state="collapsed")

if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"].strip()
else:
    st.error("⚠️ HF_TOKEN is missing!")
    st.stop()

MODEL_POOL = [
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5",
    "prompthero/openjourney",
    "CompVis/stable-diffusion-v1-4",
    "stabilityai/sd-turbo"
]

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; background-color: #262730; color: white; border: 1px solid #464646; font-weight: bold; }
    .status-log { font-family: 'Courier New', monospace; color: #00ff00; font-size: 0.85em; margin: 0; }
    .stTextArea textarea { background-color: #161b22 !important; color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- MASTER JİLET KONTUR MOTORU ---

def process_sticker_master(img, outline_thickness=40):
    """Gri çizgileri yok eder, görseli büyütür ve pürüzsüz kontur ekler."""
    
    # 1. ADIM: Ham temizlik (rembg sonrası kalan gri pikselleri bıçakla kesiyoruz)
    img_array = np.array(img)
    alpha = img_array[:, :, 3]
    # 127'nin altındaki tüm şeffaflıkları 0 yap (Gri pusluluğu öldürür)
    _, alpha_clean = cv2.threshold(alpha, 127, 255, cv2.THRESH_BINARY)
    img_array[:, :, 3] = alpha_clean
    clean_img = Image.fromarray(img_array)

    # 2. ADIM: Önce Büyütme (Upscale)
    # Konturu büyük resimde atarsak piksellik olmaz
    w, h = clean_img.size
    upscaled_img = clean_img.resize((w*4, h*4), resample=Image.LANCZOS)
    
    # 3. ADIM: OpenCV ile Pürüzsüz Kontur
    img_arr_big = np.array(upscaled_img)
    alpha_big = img_arr_big[:, :, 3]
    
    # Kalınlığı ölçeğe göre ayarla
    kernel_size = outline_thickness
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    
    # Genişlet (Dilate)
    dilated = cv2.dilate(alpha_big, kernel, iterations=1)
    
    # 4. ADIM: Anti-Aliasing (Kenar Yumuşatma Sanatı)
    # Büyük bir Blur atıp sonra sert bir threshold ile pürüzsüzleştiriyoruz
    blur_amount = 15
    smoothed = cv2.GaussianBlur(dilated, (blur_amount, blur_amount), 0)
    _, final_mask = cv2.threshold(smoothed, 120, 255, cv2.THRESH_BINARY)
    
    # 5. ADIM: Beyaz Katmanı Oluştur
    outline_layer = np.zeros_like(img_arr_big)
    outline_layer[final_mask > 0] = [255, 255, 255, 255]
    
    # 6. ADIM: Birleştirme
    final_outline_img = Image.fromarray(outline_layer)
    final_outline_img.paste(upscaled_img, (0, 0), upscaled_img)
    
    return final_outline_img

def generate_image(prompt, status_placeholder):
    refined_prompt = f"sticker design of {prompt}, isolated on white background, white border, vector art, high contrast, 8k"
    for attempt in range(2):
        for model_id in MODEL_POOL:
            status_placeholder.markdown(f"<p class='status-log'>🔄 Node: {model_id.split('/')[-1]}...</p>", unsafe_allow_html=True)
            try:
                client = InferenceClient(model=model_id, token=HF_TOKEN)
                image = client.text_to_image(refined_prompt)
                return image
            except Exception:
                time.sleep(15)
                continue 
    return None

def create_sticker_sheet(images, canvas_size=(4500, 5400), layout=6):
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    cols = 2 if layout >= 2 else 1
    rows = math.ceil(layout / cols)
    cell_w, cell_h = canvas_size[0] // cols, canvas_size[1] // rows
    
    for idx, img in enumerate(images[:layout]):
        img.thumbnail((cell_w - 400, cell_h - 400), Image.LANCZOS)
        x = (idx % cols) * cell_w + (cell_w - img.width) // 2
        y = (idx // cols) * cell_h + (cell_h - img.height) // 2
        canvas.paste(img, (x, y), img)
    return canvas

# --- UI ---
st.title("Paper Pixel Studio")
st.caption("Version 3.2 - Ultra Smooth Edge (Jilet) Mode")

tab_factory, tab_guide = st.tabs(["🏭 Factory", "📘 Guide"])

with tab_factory:
    col_in, col_pre = st.columns([1, 1], gap="large")
    with col_in:
        prompts_raw = st.text_area("Enter Prompts (Max 6):", height=150)
        platform = st.selectbox("Platform", ["Redbubble/Amazon (4500x5400)", "Etsy A4"])
        layout_mode = st.selectbox("Layout Mode", [1, 2, 4, 6])
        btn_start = st.button("EXECUTE PRODUCTION")

    with col_pre:
        monitor = st.empty()
        preview_container = st.container()

    if btn_start:
        prompts = [p.strip() for p in prompts_raw.split("\n") if p.strip()][:6]
        if not prompts: st.error("No input!")
        else:
            all_stickers = []
            for i, p in enumerate(prompts):
                raw_img = generate_image(p, monitor)
                if raw_img:
                    monitor.markdown(f"<p class='status-log'>🔬 High-Precision Processing: {p}</p>", unsafe_allow_html=True)
                    # Arka plan sil
                    no_bg = remove(raw_img)
                    # Master Jilet İşlemi (Kontur ve Büyütme burada yapılıyor)
                    final_sticker = process_sticker_master(no_bg, outline_thickness=50)
                    
                    all_stickers.append(final_sticker)
                    with preview_container:
                        st.image(final_sticker, caption=f"Jilet Ready: {p}", width=300)
                else:
                    st.error(f"Failed: {p}")

            if all_stickers:
                c_size = (4500, 5400) if "Redbubble" in platform else (2480, 3508)
                sheet = create_sticker_sheet(all_stickers, canvas_size=c_size, layout=layout_mode)
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_f:
                    for idx, s in enumerate(all_stickers):
                        buf = io.BytesIO(); s.save(buf, format="PNG")
                        zip_f.writestr(f"individual/sticker_{idx+1}.png", buf.getvalue())
                    buf = io.BytesIO(); sheet.save(buf, format="PNG")
                    zip_f.writestr(f"sheets/full_sheet.png", buf.getvalue())
                
                st.success("Production Finished!")
                st.download_button("📥 DOWNLOAD JİLET PACK (ZIP)", zip_buffer.getvalue(), "Jilet_Sticker_Pack.zip", "application/zip")