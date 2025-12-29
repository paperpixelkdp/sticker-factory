import streamlit as st
import requests
from rembg import remove
from PIL import Image
import io
import time
import random

# Sayfa Yapılandırması
st.set_page_config(page_title="Paper Pixel | Sticker Factory", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; background-color: #262730; color: white; border: 1px solid #464646; font-weight: bold; }
    .stTextArea>div>div>textarea { background-color: #161b22; color: #ffffff; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("Paper Pixel Studio")
st.subheader("Sticker Factory - Debug Mode")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("Control Panel")
    prompts_text = st.text_area("Enter Prompts:", placeholder="Cute crocodile drinking cola", height=200)
    run_engine = st.button("RUN FACTORY ENGINE")

with col_right:
    st.subheader("Live Preview")
    status_area = st.empty()
    preview_area = st.container()

if run_engine:
    if not prompts_text.strip():
        st.error("No prompts found.")
    else:
        prompts = [p.strip() for p in prompts_text.split("\n") if p.strip()]
        
        # IP engeline karşı en sağlam başlıklar
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
        }

        for i, raw_prompt in enumerate(prompts):
            image_data = None
            
            # ADIM 1: GÖRSELİ ÜRETME (İnatçı Döngü)
            for attempt in range(20):
                status_area.info(f"Step 1: Generating Image (Attempt {attempt+1}/20)...")
                try:
                    seed = random.randint(1000, 999999)
                    # En sade ve çalışan URL yapısı (CMD'deki gibi)
                    encoded_prompt = requests.utils.quote(f"{raw_prompt}, sticker style, white background")
                    api_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true"
                    
                    # Debug: URL'yi ekrana yazdıralım ki tıklayıp kontrol edebilesin
                    st.write(f"Debug URL: {api_url}")
                    
                    response = requests.get(api_url, headers=headers, timeout=60)
                    
                    if response.status_code == 200 and len(response.content) > 5000:
                        image_data = response.content
                        break
                    time.sleep(3)
                except Exception as e:
                    st.warning(f"Connection error: {e}")
                    time.sleep(3)

            if image_data:
                # Önce HAM resmi gösterelim (Sorun burada mı anlayalım)
                raw_img = Image.open(io.BytesIO(image_data))
                with preview_area:
                    st.image(raw_img, caption="RAW IMAGE (Background not removed yet)", width=300)
                
                # ADIM 2: ARKA PLAN SİLME
                try:
                    status_area.info("Step 2: Removing Background...")
                    # rembg'nin bazen çökmesine karşı koruma
                    output_img = remove(raw_img)
                    with preview_area:
                        st.success(f"Final Sticker: {raw_prompt}")
                        st.image(output_img, caption="FINAL STICKER", width=300)
                        st.divider()
                except Exception as e:
                    st.error(f"Background removal failed: {e}")
            else:
                st.error(f"Failed to fetch image from Pollinations: {raw_prompt}")

        status_area.success("Process finished.")