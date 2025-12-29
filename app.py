import streamlit as st
import requests
from rembg import remove
from PIL import Image
import io
import time
import random

# Sayfa Ayarları
st.set_page_config(page_title="Paper Pixel | Sticker Factory", layout="wide")

# Profesyonel Dark Tema
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #262730; color: white; border: 1px solid #464646; }
    .stButton>button:hover { background-color: #1c1c24; border: 1px solid #ffffff; }
    .stTextArea>div>div>textarea { background-color: #161b22; color: #ffffff; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("Paper Pixel Studio")
st.subheader("Sticker Factory")

# Sekmeler
tab_app, tab_guide = st.tabs(["🚀 Engine", "📖 Guide"])

with tab_app:
    prompts_text = st.text_area("Enter Prompts (One per line):", height=200)
    
    # Platform seçimleri (Arka planda boyutları biz ayarlayacağız)
    platform = st.selectbox("Platform", ["Redbubble", "Amazon Merch", "Etsy", "Manual"])
    
    if st.button("RUN FACTORY"):
        if not prompts_text.strip():
            st.error("Error: No prompts found.")
        else:
            prompts = [p.strip() for p in prompts_text.split("\n") if p.strip()]
            status_container = st.empty()
            
            # Sunucuyu kandırmak için 'İnsan' taklidi yapan başlıklar
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            }
            
            for i, raw_prompt in enumerate(prompts):
                image_data = None
                
                # Senin CMD'de çalışan o 'Sticker' takviyesi
                sticker_prompt = f"{raw_prompt}, sticker style, white border, isolated on white background, 4k, high resolution"
                # CMD'deki gibi güvenli kodlama
                encoded_prompt = requests.utils.quote(sticker_prompt)
                
                # İnatçı Döngü
                for attempt in range(50): # 100 çok uzun sürebilir, 50 ideal
                    status_container.info(f"Processing {i+1}/{len(prompts)} | Attempt {attempt+1}: {raw_prompt}")
                    try:
                        seed = random.randint(100000, 9999999)
                        # SENİN CMD'DEKİ ÇALIŞAN URL YAPISI (Birebir)
                        api_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true&model=flux"
                        
                        # Sunucuya "Ben insanım" diyerek giriyoruz (headers=headers)
                        response = requests.get(api_url, headers=headers, timeout=120)
                        
                        if response.status_code == 200:
                            # Gelen verinin gerçekten resim olduğunu doğrula
                            if len(response.content) > 1000: # 1KB'dan büyükse resimdir
                                image_data = response.content
                                break
                        
                        # Sunucu meşgulse bekleme süresini artırarak dene
                        time.sleep(attempt % 5 + 2) 
                    except:
                        time.sleep(5)
                
                if image_data:
                    status_container.info(f"Removing Background for: {raw_prompt}")
                    input_img = Image.open(io.BytesIO(image_data))
                    output_img = remove(input_img)
                    st.image(output_img, caption=f"Finished: {raw_prompt}", width=400)
                else:
                    st.error(f"Failed: {raw_prompt}. Server rejected the request.")

            status_container.success("Operation Finished.")