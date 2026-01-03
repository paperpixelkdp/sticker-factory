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
    st.error("⚠️ HF_TOKEN missing!")
    st.stop()

# --- PROFESYONEL CSS (Milimetrik Ölçüler) ---
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* Üst Sekmeleri Tam Üçe Böl ve Ortala */
    div[data-baseweb="tab-list"] {
        display: flex;
        justify-content: space-between;
        width: 100%;
        gap: 0px;
    }
    div[data-baseweb="tab"] {
        flex: 1;
        text-align: center;
        justify-content: center;
        color: #8b949e;
        font-size: 1.1em;
        border-bottom: 1px solid #30363d;
        height: 50px;
    }
    div[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff;
        border-bottom: 2px solid #ffffff;
    }

    /* Başlık Ortalama */
    .centered-title { text-align: center; margin-bottom: 30px; font-weight: bold; letter-spacing: 2px; }

    /* Metin Alanı ve Girdiler */
    .stTextArea textarea { background-color: #161b22 !important; color: #ffffff !important; border: 1px solid #30363d !important; border-radius: 10px; }
    
    /* Workflow Log Penceresi */
    .workflow-box {
        background-color: #000000;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 15px;
        font-family: 'Courier New', monospace;
        color: #00ff00;
        margin: 10px 0;
        min-height: 100px;
    }

    /* Butonlar */
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; font-weight: bold; }
    .gen-btn button { background-color: #ffffff !important; color: #000000 !important; }
    .dl-btn button { background-color: #262730 !important; color: #ffffff !important; border: 1px solid #464646 !important; }
    
    /* Reklam Alanları */
    .ad-sidebar { min-height: 80vh; display: flex; align-items: center; justify-content: center; background-color: transparent; }
    .ad-footer { height: 150px; margin-top: 50px; border-top: 1px solid #30363d; display: flex; align-items: center; justify-content: center; }
    </style>
    """, unsafe_allow_html=True)

# --- ANA DÜZEN (Sol Reklam | İÇERİK | Sağ Reklam) ---
left_ad, main_container, right_ad = st.columns([1, 4, 1])

with left_ad:
    st.markdown('<div class="ad-sidebar"></div>', unsafe_allow_html=True) # Sol Reklam Boşluk

with right_ad:
    st.markdown('<div class="ad-sidebar"></div>', unsafe_allow_html=True) # Sağ Reklam Boşluk

with main_container:
    # ORTALANMIŞ BAŞLIK
    st.markdown('<h1 class="centered-title">Paper Pixel Studio | Sticker Factory</h1>', unsafe_allow_html=True)
    
    # ÜST SEKME NAVİGASYONU (Tam üçe bölünmüş)
    tab_factory, tab_guide, tab_donate = st.tabs(["🏭 Factory", "📘 How To Work", "☕ Donation"])

    with tab_factory:
        # 1. Prompt Alanı
        prompts_raw = st.text_area("Sticker Production Prompts", height=200, placeholder="Example:\nCute cat astronaut\nVintage muscle car sticker", label_visibility="collapsed")

        # 2. Workflow (İş Akışı Bilgilendirme)
        st.markdown("**Production Workflow Status:**")
        workflow_area = st.empty()
        # Başlangıçtaki boş hali
        workflow_area.markdown('<div class="workflow-box">System idle. Waiting for prompts...</div>', unsafe_allow_html=True)
        
        # 3. Ayarlar (Manuel PX ve Layout - Yan Yana)
        st.markdown("<br>", unsafe_allow_html=True)
        col_settings_left, col_settings_right = st.columns(2)
        
        with col_settings_left:
            # PX Ayarlarını yan yana koyalım
            px_w, px_h = st.columns(2)
            width = px_w.number_input("Width (px)", value=4500, step=100)
            height = px_h.number_input("Height (px)", value=5400, step=100)
            
        with col_settings_right:
            layout_mode = st.selectbox("Sheet Layout Mode", [1, 2, 4, 6, 9, 12], index=3)

        # 4. Butonlar
        st.markdown("<br>", unsafe_allow_html=True)
        col_gen, col_dl = st.columns(2)
        
        # Session State for ZIP
        if 'zip_data' not in st.session_state:
            st.session_state['zip_data'] = None

        with col_gen:
            st.markdown('<div class="gen-btn">', unsafe_allow_html=True)
            generate_clicked = st.button("🚀 EXECUTE GENERATION")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_dl:
            st.markdown('<div class="dl-btn">', unsafe_allow_html=True)
            if st.session_state['zip_data']:
                st.download_button(label="📥 DOWNLOAD ZIP PACK", data=st.session_state['zip_data'], file_name="PaperPixel_Pack.zip", mime="application/zip")
            else:
                st.button("📥 DOWNLOAD PACK (Waiting...)", disabled=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- ÜRETİM MANTIĞI ---
        if generate_clicked:
            prompts = [p.strip() for p in prompts_raw.split("\n") if p.strip()][:6]
            if not prompts:
                st.error("Input required!")
            else:
                all_processed_stickers = []
                
                for i, p in enumerate(prompts):
                    # Workflow Güncelleme: Üretim aşaması
                    workflow_area.markdown(f'<div class="workflow-box">🔄 [{i+1}/{len(prompts)}] NEURAL ENGINE: Dreaming art for "{p}"...</div>', unsafe_allow_html=True)
                    
                    raw_img = generate_sticker_image(p, HF_TOKEN, workflow_area)
                    
                    if raw_img and raw_img != "TOKEN_ERROR":
                        # Workflow Güncelleme: İşleme aşaması
                        workflow_area.markdown(f'<div class="workflow-box">✂️ [{i+1}/{len(prompts)}] PROCESSOR: Removing background & adding Jilet outline for "{p}"...</div>', unsafe_allow_html=True)
                        
                        processed_sticker = process_sticker(raw_img, outline_thickness=30)
                        all_processed_stickers.append(processed_sticker)
                    elif raw_img == "TOKEN_ERROR":
                        st.error("Token failure.")
                        break

                if all_processed_stickers:
                    # Workflow Güncelleme: Paketleme aşaması
                    workflow_area.markdown('<div class="workflow-box">📦 PACKER: Arranging stickers into high-res sheets and compressing...</div>', unsafe_allow_html=True)
                    
                    final_sheets = create_custom_sheets(all_processed_stickers, width, height, layout_mode)
                    zip_bytes = export_to_zip(all_processed_stickers, final_sheets)
                    
                    st.session_state['zip_data'] = zip_bytes
                    workflow_area.markdown('<div class="workflow-box" style="color: #ffffff; border-color: #00ff00;">✅ SUCCESS: All assets are ready for shipment! Click Download.</div>', unsafe_allow_html=True)
                    time.sleep(1)
                    st.rerun()

    with tab_guide:
        st.markdown("""
        ### How It Works
        1. **Prompts:** Write up to 6 prompts. Our engine will try multiple models to get the best result.
        2. **Processing:** Each image undergoes background removal, 4x upscaling, and professional die-cut outlining.
        3. **Layout:** Stickers are packed into your custom pixel-sized sheets (e.g., 4500x5400 for Redbubble).
        4. **Download:** You get a single ZIP file containing everything.
        """)

    with tab_donate:
        st.markdown("### Support Paper Pixel\nHelp us keep the AI servers running! ☕")

# --- FOOTER REKLAM ALANI ---
st.markdown('<div class="ad-footer"></div>', unsafe_allow_html=True)