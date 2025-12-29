import streamlit as st
import requests
from rembg import remove
from PIL import Image
import io
import time
import random

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Paper Pixel | Sticker Factory", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Profesyonel Karanlık Tema ve Split Screen Düzeni (CSS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; background-color: #262730; color: white; border: 1px solid #464646; font-weight: bold; margin-top: 10px; }
    .stButton>button:hover { background-color: #1c1c24; border: 1px solid #ffffff; }
    .stTextArea>div>div>textarea { background-color: #161b22; color: #ffffff; border: 1px solid #30363d; font-family: monospace; }
    div[data-baseweb="tab-list"] { gap: 20px; border-bottom: 1px solid #30363d; }
    div[data-baseweb="tab"] { color: #8b949e; }
    div[data-baseweb="tab"][aria-selected="true"] { color: #ffffff; border-bottom-color: #ffffff; }
    /* Sağ sütun (Önizleme) için stil */
    .preview-container { border-left: 1px solid #30363d; padding-left: 20px; min-height: 500px; }
    </style>
    """, unsafe_allow_html=True)

# Başlık
st.title("Paper Pixel Studio")
st.caption("Advanced AI Sticker Factory - High-Speed Production Line")

# Üst Sekmeler
tab_app, tab_guide, tab_support = st.tabs(["🚀 Engine", "📖 User Guide", "☕ Support"])

with tab_guide:
    st.markdown("### How it works:\n1. Write prompts on the left.\n2. Choose platform.\n3. Watch previews on the right.")

with tab_support:
    st.markdown("### Support our work\nFree tools for the POD community.")

with tab_app:
    # EKRANI İKİYE BÖLÜYORUZ
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.subheader("Control Panel")
        prompts_text = st.text_area(
            "Enter Prompts (One per line):", 
            placeholder="Example:\nCute crocodile drinking cola\nGalaxy cat sticker", 
            height=300
        )
        
        platform = st.selectbox("POD Platform Optimization", [
            "Redbubble (4500x5400 px)", 
            "Amazon Merch (4500x5400 px)", 
            "Etsy (3000x3000 px)", 
            "Manual Mode"
        ])
        
        layout = st.selectbox("Sheet Layout", ["1x (Single)", "2x", "4x", "6x", "12x"])
        
        run_engine = st.button("RUN FACTORY ENGINE")

    with col_right:
        st.subheader("Live Preview")
        preview_area = st.container() # Görseller buraya dolacak
        status_area = st.empty()     # Durum mesajları burada görünecek

    # MOTOR ÇALIŞMA MANTIĞI
    if run_engine:
        if not prompts_text.strip():
            st.error("Engine Error: No prompts found.")
        else:
            prompts = [p.strip() for p in prompts_text.split("\n") if p.strip()]
            
            # İnsan taklidi yapan headers (IP Bloğunu aşmak için)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            }
            
            for i, raw_prompt in enumerate(prompts):
                image_data = None
                
                # İnatçı Döngü (Retry Logic)
                for attempt in range(50):
                    status_area.info(f"⚡ Processing {i+1}/{len(prompts)} | Attempt {attempt+1}: {raw_prompt}")
                    try:
                        seed = random.randint(100000, 9999999)
                        # Senin çalışan CMD motoru URL'i
                        sticker_prompt = f"{raw_prompt}, sticker style, white border, isolated on white background, 4k, high resolution"
                        encoded_prompt = requests.utils.quote(sticker_prompt)
                        api_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true&model=flux"
                        
                        response = requests.get(api_url, headers=headers, timeout=120)
                        
                        if response.status_code == 200 and len(response.content) > 1000:
                            image_data = response.content
                            break
                        
                        time.sleep(attempt % 5 + 2)
                    except:
                        time.sleep(5)
                
                if image_data:
                    status_area.info(f"✂️ Removing Background: {raw_prompt}")
                    try:
                        input_img = Image.open(io.BytesIO(image_data))
                        output_img = remove(input_img)
                        
                        # SAĞ TARAFA GÖRSELİ EKLE
                        with preview_area:
                            st.success(f"Finished: {raw_prompt}")
                            st.image(output_img, caption=f"Result: {raw_prompt}", use_container_width=True)
                            st.divider() # Araya çizgi çek
                    except Exception as e:
                        st.error(f"Post-processing error: {e}")
                else:
                    st.error(f"Failed to generate: {raw_prompt}")

            status_area.success("Factory Operation Complete.")