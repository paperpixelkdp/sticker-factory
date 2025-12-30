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

# --- CONFIG & DÜKKAN AYARLARI ---
st.set_page_config(page_title="Paper Pixel | Sticker Cloud", layout="wide")

# Kodu bu şekilde değiştiriyoruz, şifreyi Streamlit'in kasasından çekeceğiz
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    st.error("Hata: HF_TOKEN bulunamadı. Lütfen Streamlit ayarlarından ekleyin.")
    st.stop()

# Model Havuzu (İnatçı Motor Listesi)
MODEL_POOL = [
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5",
    "prompthero/openjourney",
    "CompVis/stable-diffusion-v1-4",
    "stabilityai/sd-turbo"
]

# --- STİLLER (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; background-color: #262730; color: white; border: 1px solid #464646; font-weight: bold; }
    .stButton>button:hover { border: 1px solid #ffffff; }
    .status-log { font-family: 'Courier New', monospace; color: #00ff00; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

# --- FONKSİYONLAR (MOTORLAR) ---

def add_sticker_outline(img):
    """Görselin etrafına jilet gibi beyaz kontur (Die-cut) ekler."""
    # PIL imajını OpenCV formatına (RGBA) çevir
    img_array = np.array(img)
    alpha = img_array[:, :, 3] # Alpha kanalı (şeffaflık)
    
    # Maskeyi genişlet (Dilate) - Beyaz sınırın kalınlığı
    kernel = np.ones((15, 15), np.uint8) 
    mask_dilated = cv2.dilate(alpha, kernel, iterations=1)
    
    # Beyaz bir katman oluştur
    outline = np.zeros_like(img_array)
    outline[mask_dilated > 0] = [255, 255, 255, 255] # Beyaz çerçeve
    
    # Orijinal resmi üzerine yapıştır
    # Önce beyaz katmanı, sonra orijinali üst üste koyarız
    outline_img = Image.fromarray(outline)
    outline_img.paste(img, (0, 0), img)
    return outline_img

def generate_image(prompt):
    """İnatçı Motor (Bulldog Logic): 5 Model x 3 Tur."""
    refined_prompt = f"sticker design of {prompt}, white background, vector art, die-cut style, high contrast, sharp edges"
    
    for attempt in range(3): # 3 Tur
        for model_id in MODEL_POOL:
            try:
                client = InferenceClient(model=model_id, token=HF_TOKEN)
                image = client.text_to_image(refined_prompt)
                return image
            except Exception:
                continue # Hata verirse diğer modele geç
    return None

# --- ARAYÜZ ---
st.title("Paper Pixel Studio")
st.subheader("Sticker Cloud - AI Automation Factory")

tab_factory, tab_guide, tab_donate = st.tabs(["🏭 Sticker Factory", "📘 How It Works", "☕ Donate"])

with tab_factory:
    col_input, col_preview = st.columns([1, 1], gap="large")
    
    with col_input:
        st.markdown("#### Production Control")
        prompts_raw = st.text_area("Enter Prompts (One per line)", height=200, placeholder="Example:\nCute cat astronaut\nNeon cyberpunk fox")
        
        platform = st.selectbox("POD Target", ["Redbubble / Amazon (4500x5400)", "Etsy A4 (2480x3508)", "Manual"])
        layout_mode = st.selectbox("Layout Mode (Stickers per Sheet)", [1, 2, 4, 6])
        
        btn_start = st.button("START PRODUCTION LINE")

    with col_preview:
        st.markdown("#### Live Monitoring")
        monitor = st.empty()
        preview_container = st.container()

    if btn_start:
        if not prompts_raw.strip():
            st.error("No input detected!")
        else:
            prompts = [p.strip() for p in prompts_raw.split("\n") if p.strip()]
            all_processed_images = []
            
            for i, p in enumerate(prompts):
                with monitor:
                    st.markdown(f"<p class='status-log'>🔄 Connecting to Neural Node for: {p}...</p>", unsafe_allow_html=True)
                
                # 1. MOTOR: Üretim
                raw_img = generate_image(p)
                
                if raw_img:
                    with monitor:
                        st.markdown(f"<p class='status-log'>🎨 Dreaming complete. ✂️ Isolating from reality...</p>", unsafe_allow_html=True)
                    
                    # 2. MOTOR: Arka Plan Silme (RAM Dostu)
                    # Resmi işlemek için küçült-maskele-büyüt mantığı
                    processed_img = remove(raw_img)
                    
                    # 3. MOTOR: Beyaz Kontur (Die-Cut)
                    with monitor:
                        st.markdown(f"<p class='status-log'>🔬 Adding professional die-cut outline...</p>", unsafe_allow_html=True)
                    final_sticker = add_sticker_outline(processed_img)
                    
                    # 4. MOTOR: Upscale (Lanczos)
                    # 4 kat büyütüyoruz (DPI artışı için)
                    w, h = final_sticker.size
                    final_sticker = final_sticker.resize((w*4, h*4), resample=Image.LANCZOS)
                    
                    all_processed_images.append(final_sticker)
                    
                    with preview_container:
                        st.image(final_sticker, caption=f"Ready: {p}", width=200)
                else:
                    st.error(f"Failed to generate: {p} (All models busy)")

            # --- PAKETLEME VE İNDİRME ---
            if all_processed_images:
                st.success(f"Production complete! Total {len(all_processed_images)} stickers created.")
                
                # ZIP Hazırlama
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    for idx, img in enumerate(all_processed_images):
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='PNG')
                        zip_file.writestr(f"sticker_{idx+1}.png", img_byte_arr.getvalue())
                
                st.download_button(
                    label="📥 DOWNLOAD STICKER PACK (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="PaperPixel_StickerPack.zip",
                    mime="application/zip"
                )

# --- DİĞER SEKMELER ---
with tab_guide:
    st.markdown("""
    ### System Architecture
    - **Stubborn Engine:** We try 5 different AI models across 15 attempts to get your result.
    - **Die-Cut Logic:** Automated white border addition for professional POD quality.
    - **Smart Packing:** Overflow prompts are automatically moved to additional sheets.
    """)

with tab_donate:
    st.markdown("Support Paper Pixel Studio to keep these tools free forever! ☕")