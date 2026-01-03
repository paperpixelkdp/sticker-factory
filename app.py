import streamlit as st
import io
import time
from image_gen import generate_sticker_image
from image_processor import process_sticker
from layout_manager import create_custom_sheets, export_to_zip

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Paper Pixel | Sticker Factory", layout="wide", initial_sidebar_state="collapsed")

# Secrets Kontrolü
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"].strip()
else:
    st.error("⚠️ HF_TOKEN is missing in Streamlit Secrets!")
    st.stop()

# --- PROFESYONEL CSS (Karanlık Tema ve Reklam Alanları) ---
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* Sekmeleri Ortala */
    div[data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        gap: 50px;
        border-bottom: 1px solid #30363d;
    }
    div[data-baseweb="tab"] { color: #8b949e; font-size: 1.2em; }
    div[data-baseweb="tab"][aria-selected="true"] { color: #ffffff; border-bottom-color: #ffffff; }

    /* Buton Tasarımları */
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; font-weight: bold; transition: 0.3s; }
    .gen-btn>div>button { background-color: #262730; color: white; border: 1px solid #464646; }
    .gen-btn>div>button:hover { background-color: #ffffff; color: black; }
    .dl-btn>div>button { background-color: #00ff00; color: black; border: none; }
    .dl-btn>div>button:hover { background-color: #00cc00; }

    /* Metin Alanları */
    .stTextArea textarea { background-color: #161b22 !important; color: #ffffff !important; border: 1px solid #30363d !important; text-align: center; }
    
    /* Reklam Alanı Sınırları (Görünmez ama yer tutar) */
    .ad-space { min-height: 500px; display: flex; align-items: center; justify-content: center; color: #30363d; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

# --- REKLAM ALANLI ANA DÜZEN ---
# Sol Reklam (1) | Ana İçerik (4) | Sağ Reklam (1)
left_ad, main_content, right_ad = st.columns([1, 4, 1])

with left_ad:
    st.markdown('<div class="ad-space"></div>', unsafe_allow_html=True) # Reklam Alanı (Sol)

with right_ad:
    st.markdown('<div class="ad-space"></div>', unsafe_allow_html=True) # Reklam Alanı (Sağ)

with main_content:
    st.title("Paper Pixel Studio")
    
    # ÜST SEKME NAVİGASYONU
    tab_factory, tab_guide, tab_donate = st.tabs(["🏭 Factory", "📘 How To Work", "☕ Donation"])

    with tab_factory:
        # 1. Prompt Yazma Alanı (Ortalı)
        prompts_raw = st.text_area(
            "Enter Sticker Prompts (Max 6, one per line)", 
            height=200, 
            placeholder="A cute dragon drinking coffee\nNeon cyberpunk skull"
        )

        # 2. Work Flow (Görsel Durum Göstergesi)
        workflow_area = st.empty()
        
        # 3. Manuel PX ve Layout Seçimi (Yan Yana)
        st.markdown("---")
        col_px_w, col_px_h, col_layout = st.columns(3)
        with col_px_w:
            width = st.number_input("Width (px)", value=4500, step=100)
        with col_px_h:
            height = st.number_input("Height (px)", value=5400, step=100)
        with col_layout:
            layout_mode = st.selectbox("Layout Mode", [1, 2, 4, 6, 9, 12], index=3)

        # 4. Generate ve Download Butonları (İkiye Bölünmüş)
        st.markdown("<br>", unsafe_allow_html=True)
        col_gen, col_dl = st.columns(2)
        
        # Session State (Verileri Hafızada Tutmak İçin)
        if 'zip_data' not in st.session_state:
            st.session_state['zip_data'] = None

        with col_gen:
            st.markdown('<div class="gen-btn">', unsafe_allow_html=True)
            generate_clicked = st.button("🚀 GENERATE FACTORY")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_dl:
            st.markdown('<div class="dl-btn">', unsafe_allow_html=True)
            # Eğer ZIP dosyası üretilmediyse butonu pasif gösteriyoruz (Streamlit kuralı)
            if st.session_state['zip_data']:
                st.download_button(
                    label="📥 DOWNLOAD PACK",
                    data=st.session_state['zip_data'],
                    file_name="PaperPixel_StickerPack.zip",
                    mime="application/zip"
                )
            else:
                st.button("📥 DOWNLOAD PACK (Waiting...)", disabled=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- MOTORU ÇALIŞTIRMA ---
        if generate_clicked:
            prompts = [p.strip() for p in prompts_raw.split("\n") if p.strip()]
            if not prompts:
                st.error("Engine Error: No prompts detected.")
            elif len(prompts) > 6:
                st.error("Safety Limit: Max 6 prompts at a time.")
            else:
                all_processed_stickers = []
                preview_cols = st.columns(3) # Önizleme için 3'lü kolon

                for i, p in enumerate(prompts):
                    # Step 1: Generation
                    workflow_area.info(f"🔄 **Workflow:** {i+1}/{len(prompts)} - Producing Art for '{p}'...")
                    raw_img = generate_sticker_image(p, HF_TOKEN, workflow_area)
                    
                    if raw_img:
                        # Step 2: Processing
                        workflow_area.info(f"✂️ **Workflow:** {i+1}/{len(prompts)} - Removing Background & Sharpening...")
                        # image_processor modülümüzdeki fonksiyonu çağırıyoruz
                        # Kalınlık 30, Büyütme 4x sabit ayarladık
                        processed_sticker = process_sticker(raw_img, outline_thickness=30)
                        all_processed_stickers.append(processed_sticker)
                        
                        # Önizleme
                        with preview_cols[i % 3]:
                            st.image(processed_sticker, caption=f"Sticker {i+1}", use_container_width=True)
                    else:
                        st.error(f"Failed to generate: {p}")

                if all_processed_stickers:
                    workflow_area.info("📦 **Workflow:** Packing everything into a ZIP file...")
                    
                    # Step 3: Layout & ZIP
                    # layout_manager modülümüzdeki fonksiyonları çağırıyoruz
                    final_sheets = create_custom_sheets(all_processed_stickers, width, height, layout_mode)
                    zip_bytes = export_to_zip(all_processed_stickers, final_sheets)
                    
                    # Veriyi sakla ve sayfayı yenile (Download butonunun aktifleşmesi için)
                    st.session_state['zip_data'] = zip_bytes
                    workflow_area.success("🎯 **Workflow:** Production Complete! Click Download.")
                    time.sleep(1)
                    st.rerun()

    with tab_guide:
        st.markdown("""
        ### User Guide
        1. **Write:** Put each sticker idea on a new line.
        2. **Configure:** Set your canvas size (e.g., 4500x5400 for Redbubble).
        3. **Execute:** Click Generate and watch the workflow.
        4. **Collect:** Download your ZIP which contains both individual stickers and ready-to-print sheets.
        """)

    with tab_donate:
        st.markdown("### Donation\nSupport Paper Pixel Studio to keep this tool 100% free.")
        st.write("Buy us a coffee! ☕")

# --- FOOTER (REKLAM ALANI) ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown('<div class="ad-space" style="min-height: 100px;"></div>', unsafe_allow_html=True) # Reklam Alanı (Alt)