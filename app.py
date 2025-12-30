import streamlit as st
import requests
import numpy as np
import cv2
from PIL import Image, ImageOps
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

# --- JİLET GİBİ KONTUR MOTORU ---

def add_sticker_outline(img, thickness=25):
    """Pikselliği gideren ve gri çizgileri yok eden jilet gibi beyaz kontur ekler."""
    # PIL -> OpenCV (RGBA)
    img_array = np.array(img)
    
    # 1. Gri çizgileri yok etmek için Alpha kanalını temizle (Thresholding)
    alpha = img_array[:, :, 3]
    _, alpha_clean = cv2.threshold(alpha, 127, 255, cv2.THRESH_BINARY)
    
    # 2. Maskeyi dairesel bir kernel ile genişlet (Daha yuvarlak hatlar için)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (thickness, thickness))
    mask_dilated = cv2.dilate(alpha_clean, kernel, iterations=1)
    
    # 3. KENAR YUMUŞATMA (Anti-Aliasing Hilesi)
    # Genişletilmiş maskeyi hafifçe bulandırıp tekrar keskinleştiriyoruz
    mask_blurred = cv2.GaussianBlur(mask_dilated, (11, 11), 0)
    _, mask_final = cv2.threshold(mask_blurred, 127, 255, cv2.THRESH_BINARY)
    
    # 4. Beyaz çerçeve katmanını oluştur
    outline = np.zeros_like(img_array)
    outline[mask_final > 0] = [255, 255, 255, 255]
    
    # 5. Orijinal resmi pürüzsüz çerçeve üzerine yapıştır
    outline_img = Image.fromarray(outline)
    # Orijinal resmin kenarlarındaki o pislikleri (gri pikselleri) temizlemek için maskesini de temizliyoruz
    img_clean_alpha = Image.fromarray(cv2.bitwise_and(img_array, img_array, mask=alpha_clean))
    outline_img.paste(img_clean_alpha, (0, 0), img_clean_alpha)
    
    return outline_img

def generate_image(prompt, status_placeholder):
    refined_prompt = f"sticker design of {prompt}, isolated on white background, white border, vector art, high contrast, sharp edges, 300 dpi"
    for attempt in range(2):
        for model_id in MODEL_POOL:
            status_placeholder.markdown(f"<p class='status-log'>🔄 Node: {model_id.split('/')[-1]}...</p>", unsafe_allow_html=True)
            try:
                client = InferenceClient(model=model_id, token=HF_TOKEN)
                image = client.text_to_image(refined_prompt)
                return image
            except Exception:
                time.sleep(10)
                continue 
    return None

def create_sticker_sheet(images, canvas_size=(4500, 5400), layout=6):
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    cols = 2 if layout >= 2 else 1
    rows = math.ceil(layout / cols)
    cell_w, cell_h = canvas_size[0] // cols, canvas_size[1] // rows
    
    for idx, img in enumerate(images[:layout]):
        # Sayfaya dizerken küçült ama jiletliği koru
        img.thumbnail((cell_w - 300, cell_h - 300), Image.LANCZOS)
        x = (idx % cols) * cell_w + (cell_w - img.width) // 2
        y = (idx // cols) * cell_h + (cell_h - img.height) // 2
        canvas.paste(img, (x, y), img)
    return canvas

# --- UI ---
st.title("Paper Pixel Studio")
st.subheader("Sticker Cloud - Jilet Mode Active 🚀")

tab_factory, tab_guide = st.tabs(["🏭 Factory", "📘 Guide"])

with tab_factory:
    col_in, col_pre = st.columns([1, 1], gap="large")
    with col_in:
        prompts_raw = st.text_area("Enter Prompts (Max 6):", height=150)
        platform = st.selectbox("Platform", ["Redbubble/Amazon (4500x5400)", "Etsy A4 (2480x3508)"])
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
                    monitor.markdown(f"<p class='status-log'>🔬 Jilet Kontur & BG Removal: {p}</p>", unsafe_allow_html=True)
                    processed = remove(raw_img)
                    # Buradaki kalınlığı 25 yaptım, idealdir.
                    outlined = add_sticker_outline(processed, thickness=25)
                    # 4x Upscale (Lanczos)
                    w, h = outlined.size
                    upscaled = outlined.resize((w*4, h*4), resample=Image.LANCZOS)
                    all_stickers.append(upscaled)
                    with preview_container:
                        st.image(upscaled, caption=f"Sticker {i+1}", width=250)
                else: st.error(f"Failed: {p}")

            if all_stickers:
                c_size = (4500, 5400) if "Redbubble" in platform else (2480, 3508)
                sheet = create_sticker_sheet(all_stickers, canvas_size=c_size, layout=layout_mode)
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_f:
                    # Individual Stickers (Tekli şeffaf dosyalar)
                    for idx, s in enumerate(all_stickers):
                        buf = io.BytesIO()
                        s.save(buf, format="PNG")
                        zip_f.writestr(f"individual/sticker_{idx+1}.png", buf.getvalue())
                    # Ready Sheets (Baskıya hazır sayfa)
                    buf = io.BytesIO()
                    sheet.save(buf, format="PNG")
                    zip_f.writestr(f"sheets/full_sheet.png", buf.getvalue())
                
                st.success("Production Finished!")
                st.download_button("📥 DOWNLOAD PRODUCTION PACK (ZIP)", zip_buffer.getvalue(), "PaperPixel_Pack.zip", "application/zip")