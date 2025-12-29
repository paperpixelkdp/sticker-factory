import streamlit as st
import requests
from rembg import remove
from PIL import Image
import io
import time
import random
from urllib.parse import quote

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Paper Pixel | Sticker Factory", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Profesyonel Karanlık Tema CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #262730; color: white; border: 1px solid #464646; font-weight: bold; }
    .stButton>button:hover { background-color: #1c1c24; border: 1px solid #ffffff; }
    .stTextArea>div>div>textarea { background-color: #161b22; color: #ffffff; border: 1px solid #30363d; font-family: monospace; }
    div[data-baseweb="tab-list"] { gap: 20px; border-bottom: 1px solid #30363d; }
    div[data-baseweb="tab"] { color: #8b949e; }
    div[data-baseweb="tab"][aria-selected="true"] { color: #ffffff; border-bottom-color: #ffffff; }
    /* Durum kutularını sabitleme */
    .stInfo, .stSuccess, .stError { border-radius: 5px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# Başlık Bölümü
st.title("Paper Pixel Studio")
st.caption("Professional AI Sticker Generation Factory")

# Üst Sekmeli Navigasyon
tab_app, tab_guide, tab_support = st.tabs(["🚀 Sticker Factory", "📖 User Guide", "☕ Support Us"])

with tab_guide:
    st.markdown("""
    ### Professional Workflow
    1. **Input:** Enter your descriptive prompts line by line.
    2. **Configuration:** Select your target POD platform for optimization.
    3. **Generation:** The AI will attempt to generate each design up to 100 times until successful.
    4. **Processing:** Backgrounds are automatically removed with high precision.
    5. **Output:** High-resolution assets will be prepared for your selection.
    """)

with tab_support:
    st.markdown("### Support Paper Pixel Studio")
    st.write("This tool is provided free of charge for the POD community. Your support helps us keep the servers running and develop new automation tools.")

with tab_app:
    # Kullanıcı Girdileri
    prompts_text = st.text_area(
        "Enter Your Prompts (One per line):", 
        placeholder="Example:\nCute baby dragon with big eyes\nSteampunk mechanical owl\nCyberpunk neon cat", 
        height=250
    )
    
    col_plat, col_lay = st.columns(2)
    with col_plat:
        platform = st.selectbox("Target POD Platform", [
            "Redbubble (4500x5400 px)", 
            "Amazon Merch on Demand (4500x5400 px)", 
            "Etsy Digital (3000x3000 px)", 
            "Manual Configuration"
        ])
    with col_lay:
        layout_choice = st.selectbox("Sheet Layout", ["1x (Single)", "2x (Duo)", "4x (Quad)", "6x (Pack)", "12x (A4 Sheet)"])

    if st.button("START STICKER FACTORY ENGINE"):
        if not prompts_text.strip():
            st.error("Engine failure: No prompts detected. Please enter at least one prompt.")
        else:
            # Satırları temizleyip listeye alıyoruz
            prompts = [p.strip() for p in prompts_text.split("\n") if p.strip()]
            status_container = st.empty()
            progress_bar = st.progress(0)
            
            for i, raw_prompt in enumerate(prompts):
                image_data = None
                max_retries = 100 # Tam 100 kez deneyecek
                
                # Sticker için promptu zorunlu eklemelerle güçlendiriyoruz
                # Kullanıcı ne yazarsa yazsın sonuna bu teknik detaylar eklenecek
                refined_prompt = f"{raw_prompt}, sticker style, isolated on white background, professional sticker art, white border, high resolution, 300 dpi, sharp edges"
                encoded_prompt = quote(refined_prompt)
                
                for attempt in range(max_retries):
                    status_container.info(f"Processing {i+1}/{len(prompts)} | Attempt {attempt+1}/100: {raw_prompt}")
                    try:
                        seed = random.randint(1000000, 9999999)
                        # Senin çalışan CMD kodundaki 'image' kapısı
                        api_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true&model=flux"
                        
                        # Maksimum sabır: 300 saniye (5 dakika) bekliyoruz
                        response = requests.get(api_url, timeout=300)
                        
                        if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                            image_data = response.content
                            break # Görseli aldık, döngüden çık
                        else:
                            # Sunucu hatası veya boş cevap durumunda bekle ve tekrar dene
                            time.sleep(5)
                    except Exception:
                        # Bağlantı koparsa veya timeout olursa bekle ve tekrar dene
                        time.sleep(5)
                
                if image_data:
                    try:
                        status_container.info(f"Finalizing Art: Removing Background for '{raw_prompt}'...")
                        input_img = Image.open(io.BytesIO(image_data))
                        # Arka planı jilet gibi siliyoruz
                        output_img = remove(input_img)
                        
                        # Kullanıcının sağ tıkla indirmesini zorlaştıran düşük çözünürlüklü önizleme
                        st.image(output_img, caption=f"Preview: {raw_prompt}", width=400)
                        
                        # Not: Upscale ve Paketleme (ZIP) mantığı bir sonraki aşamada eklenecek
                    except Exception as e:
                        st.error(f"Post-processing failed for: {raw_prompt}")
                else:
                    st.error(f"Critical Failure: Could not generate '{raw_prompt}' after 100 attempts.")
                
                # İlerleme çubuğunu güncelle
                progress_bar.progress((i + 1) / len(prompts))

            status_container.success("Factory Operation Complete. High-resolution packaging features coming soon.")