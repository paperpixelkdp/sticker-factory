import streamlit as st
import requests
from rembg import remove
from PIL import Image
import io
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Paper Pixel - Sticker Factory", layout="wide")

# --- SIDEBAR (YAN MENÜ) ---
with st.sidebar:
    st.title("🎨 Paper Pixel Studio")
    menu = st.radio("Menü", ["🚀 Sticker Factory", "📖 How to Work", "☕ Support Us"])
    st.info("Sürüm: 1.0 - Alpha")

# --- HOW TO WORK SAYFASI ---
if menu == "📖 How to Work":
    st.header("Nasıl Çalışır?")
    st.write("1. Promptlarını her satıra bir tane gelecek şekilde yaz.")
    st.write("2. Platformunu ve paket düzenini seç.")
    st.write("3. 'Generate' butonuna bas ve arkana yaslan!")

# --- SUPPORT US SAYFASI ---
elif menu == "☕ Support Us":
    st.header("Bize Destek Olun")
    st.write("Bu araç tamamen ücretsizdir. Eğer işinize yaradıysa bir kahve ısmarlayabilirsiniz!")
    st.button("Bağış Yap (Simbolik)")

# --- ANA UYGULAMA (STICKER FACTORY) ---
elif menu == "🚀 Sticker Factory":
    st.header("Sticker Factory 🚀")
    
    # Girdi Alanı
    prompts_text = st.text_area("Sticker Promptlarını Gir (Her satıra bir adet):", placeholder="Örn: Cute galaxy cat\nNeon cyberpunk wolf", height=200)
    
    col1, col2 = st.columns(2)
    with col1:
        platform = st.selectbox("Hedef Platform", ["Redbubble & Amazon (4500x5400)", "Etsy (3000x3000)", "WhatsApp (512x512)", "Manual"])
    with col2:
        layout_choice = st.selectbox("Paket Düzeni", ["1x (Tekli)", "2x", "4x", "6x", "12x (A4)"])

    if st.button("STİKERLARI ÜRET VE HAZIRLA 🔥"):
        if not prompts_text.strip():
            st.warning("Lütfen en az bir prompt girin!")
        else:
            prompts = [p.strip() for p in prompts_text.split("\n") if p.strip()]
            
            # İşlem Durumu
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            for i, prompt in enumerate(prompts):
                status_text.info(f"İşleniyor: {i+1}/{len(prompts)} - {prompt}")
                
                # --- İNATÇI DÖNGÜ (RETRY LOGIC) ---
                image_data = None
                retries = 20
                for attempt in range(retries):
                    try:
                        # Promptu güçlendiriyoruz
                        final_prompt = f"{prompt}, isolated on white background, professional sticker art, white border, high resolution, 300 dpi"
                        api_url = f"https://pollinations.ai/p/{final_prompt.replace(' ', '%20')}"
                        
                        response = requests.get(api_url, timeout=30)
                        if response.status_code == 200:
                            image_data = response.content
                            break
                    except:
                        time.sleep(1) # Hata olursa 1 saniye bekle tekrar dene
                
                if image_data:
                    # --- ARKA PLAN SİLME ---
                    status_text.info(f"Arka plan siliniyor: {prompt}...")
                    input_image = Image.open(io.BytesIO(image_data))
                    output_image = remove(input_image)
                    
                    # Önizleme (Düşük çözünürlüklü)
                    st.image(output_image, caption=f"Tamamlandı: {prompt}", width=200)
                    
                    # Buraya ileride Upscale ve Paketleme mantığını ekleyeceğiz.
                else:
                    st.error(f"Maalesef üretilemedi: {prompt}")
                
                progress_bar.progress((i + 1) / len(prompts))
            
            status_text.success("Tüm stickerlar hazırlandı! (Paketleme ve indirme özelliği bir sonraki adımda eklenecek)")