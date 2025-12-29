import streamlit as st
import requests
from rembg import remove
from PIL import Image
import io
import time
import random

# Sayfa Yapılandırması
st.set_page_config(page_title="Paper Pixel | Sticker Factory", layout="wide", initial_sidebar_state="collapsed")

# Profesyonel Karanlık Tema (CSS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; background-color: #262730; color: white; border: 1px solid #464646; font-weight: bold; }
    .stButton>button:hover { background-color: #1c1c24; border: 1px solid #ffffff; }
    .stTextArea>div>div>textarea { background-color: #161b22; color: #ffffff; border: 1px solid #30363d; font-family: monospace; }
    div[data-baseweb="tab-list"] { gap: 20px; border-bottom: 1px solid #30363d; }
    div[data-baseweb="tab"] { color: #8b949e; }
    div[data-baseweb="tab"][aria-selected="true"] { color: #ffffff; border-bottom-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("Paper Pixel Studio")
st.subheader("Sticker Factory - Professional Edition")

tab_app, tab_guide, tab_support = st.tabs(["🚀 Engine", "📖 User Guide", "☕ Support"])

with tab_app:
    # EKRANI İKİYE BÖLÜYORUZ
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.subheader("Control Panel")
        prompts_text = st.text_area("Enter Prompts (One per line):", placeholder="Example: Cute crocodile drinking cola", height=250)
        
        platform = st.selectbox("POD Platform", ["Redbubble (4500x5400)", "Amazon Merch", "Etsy", "Manual"])
        layout = st.selectbox("Layout", ["1x", "2x", "4x", "6x", "12x"])
        
        run_engine = st.button("RUN STICKER FACTORY")

    with col_right:
        st.subheader("Live Preview")
        status_area = st.empty()
        preview_area = st.container()

    if run_engine:
        if not prompts_text.strip():
            st.error("Engine Error: No prompts found.")
        else:
            prompts = [p.strip() for p in prompts_text.split("\n") if p.strip()]
            
            # Bot korumasını aşan headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            for i, raw_prompt in enumerate(prompts):
                image_data = None
                
                # İnatçı Döngü
                for attempt in range(30):
                    status_area.info(f"⚡ Generating {i+1}/{len(prompts)} | Attempt {attempt+1}/30: {raw_prompt}")
                    try:
                        seed = random.randint(100000, 9999999)
                        # HATA ÇÖZÜMÜ: model=flux kısmını kaldırıp sunucunun insafına bırakıyoruz
                        # 'sticker style, white background' ekleyerek sticker kalitesini garanti ediyoruz
                        sticker_prompt = requests.utils.quote(f"{raw_prompt}, sticker style, white border, isolated on white background, 4k resolution")
                        
                        # En stabil URL yapısına döndük
                        api_url = f"https://image.pollinations.ai/prompt/{sticker_prompt}?width=1024&height=1024&seed={seed}&nologo=true"
                        
                        response = requests.get(api_url, headers=headers, timeout=60)
                        
                        # Resim geldiyse ve hata mesajı değilse (5000 byte'tan büyükse resimdir)
                        if response.status_code == 200 and len(response.content) > 5000:
                            image_data = response.content
                            break
                        
                        # Sunucu meşgulse biraz bekle ve tekrar dene
                        time.sleep(3)
                    except:
                        time.sleep(3)
                
                if image_data:
                    status_area.info(f"✂️ Background Removal: {raw_prompt}")
                    try:
                        input_img = Image.open(io.BytesIO(image_data))
                        # rembg ile arka plan silme
                        output_img = remove(input_img)
                        
                        with preview_area:
                            st.success(f"Generated: {raw_prompt}")
                            st.image(output_img, caption=f"Sticker: {raw_prompt}", use_container_width=True)
                            st.divider()
                    except Exception as e:
                        st.error(f"Image processing error: {e}")
                else:
                    st.error(f"Server Overload: Failed to generate '{raw_prompt}' after 30 attempts. Try again later.")

            status_area.success("All tasks completed.")