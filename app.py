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

# --- PROFESYONEL CSS (v6.0 Güncellemeleri) ---
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* SEKME AYARLARI (Büyütülmüş ve Ortalanmış) */
    div[data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        width: 100%;
        gap: 20px;
    }
    div[data-baseweb="tab"] {
        flex: 1;
        text-align: center;
        height: 60px;
        background-color: transparent;
    }
    div[data-baseweb="tab"] p {
        font-size: 1.4em !important; /* Yazıları büyüttük */
        font-weight: bold;
        color: #8b949e;
    }
    div[data-baseweb="tab"][aria-selected="true"] p {
        color: #ffffff !important;
    }

    /* Başlık Ortalama */
    .centered-title { text-align: center; margin-bottom: 20px; font-weight: bold; font-size: 2.5em; color: #ffffff; }

    /* PROMPT ALANI (İtalik Placeholder) */
    .stTextArea textarea { 
        background-color: #161b22 !important; 
        color: #ffffff !important; 
        border: 1px solid #30363d !important; 
        border-radius: 10px; 
        font-size: 1.1em;
    }
    .stTextArea textarea::placeholder {
        font-style: italic;
        opacity: 0.7;
    }
    
    /* BUTONLAR (Geniş ve Bitişik Görünümlü) */
    .stButton>button {
        width: 100%;
        height: 4em !important;
        font-size: 1.2em !important;
        border-radius: 8px;
        font-weight: bold;
        transition: 0.3s;
    }
    /* Run Factory Butonu (Beyaz) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: none;
    }
    /* Download Butonu (Koyu) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        background-color: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #464646;
    }

    /* Reklam Alanları */
    .ad-sidebar { min-height: 80vh; display: flex; align-items: center; justify-content: center; }
    .ad-footer { height: 100px; margin-top: 50px; border-top: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- ANA DÜZEN ---
left_ad, main_container, right_ad = st.columns([1, 4, 1])

with left_ad:
    st.markdown('<div class="ad-sidebar"></div>', unsafe_allow_html=True)

with right_ad:
    st.markdown('<div class="ad-sidebar"></div>', unsafe_allow_html=True)

with main_container:
    st.markdown('<h1 class="centered-title">Paper Pixel Studio | Sticker Factory</h1>', unsafe_allow_html=True)
    
    tab_factory, tab_guide, tab_donate = st.tabs(["🏭 Factory", "📘 How To Work", "☕ Donation"])

    with tab_factory:
        # 1. Prompt Alanı (12 Prompt Sınırı ve İtalik Placeholder)
        placeholder_text = "Enter up to 12 prompts here (one per line). Example: \n- Cyberpunk neon cat \n- Vintage forest bear"
        prompts_raw = st.text_area("Sticker Prompts", height=200, placeholder=placeholder_text, label_visibility="collapsed")

        # 2. Settings (Manuel PX ve Layout - Yan Yana)
        st.markdown("<br>", unsafe_allow_html=True)
        col_set1, col_set2 = st.columns(2)
        
        with col_set1:
            px_col1, px_col2 = st.columns(2)
            width = px_col1.number_input("Width (px)", value=4500, step=100)
            height = px_col2.number_input("Height (px)", value=5400, step=100)
            
        with col_set2:
            layout_mode = st.selectbox("Layout Mode", [1, 2, 4, 6, 9, 12], index=3)

        # 3. Butonlar (Run Factory ve Download)
        st.markdown("<br>", unsafe_allow_html=True)
        col_run, col_download = st.columns(2, gap="small") # Butonları birbirine yaklaştırdık
        
        if 'zip_data' not in st.session_state:
            st.session_state['zip_data'] = None

        with col_run:
            run_factory = st.button("Run Factory")

        with col_download:
            if st.session_state['zip_data']:
                st.download_button(label="Download", data=st.session_state['zip_data'], file_name="PaperPixel_Pack.zip", mime="application/zip")
            else:
                st.button("Download", disabled=True, help="Run the factory first to enable download.")

        # --- MOTOR ÇALIŞMA MANTIĞI ---
        if run_factory:
            prompts = [p.strip() for p in prompts_raw.split("\n") if p.strip()]
            
            # 12 PROMPT SINIRI KONTROLÜ
            if not prompts:
                st.error("Engine Error: No prompts detected.")
            elif len(prompts) > 12:
                st.error("🚨 Safety Limit Exceeded: Please enter a maximum of 12 prompts.")
            else:
                # 4. Work Flow Alanı (Otomatik Açılan Statü Paneli)
                with st.status("🚀 Production Line Active...", expanded=True) as status:
                    all_processed_stickers = []
                    
                    for i, p in enumerate(prompts):
                        st.write(f"🔍 **Step 1:** Requesting art for '{p}'...")
                        raw_img = generate_sticker_image(p, HF_TOKEN, st.empty())
                        
                        if raw_img and raw_img != "TOKEN_ERROR":
                            st.write(f"✂️ **Step 2:** Processing background & Jilet-outline...")
                            processed_sticker = process_sticker(raw_img, outline_thickness=30)
                            all_processed_stickers.append(processed_sticker)
                        else:
                            st.error(f"Failed to generate: {p}")

                    if all_processed_stickers:
                        st.write("📦 **Step 3:** Packing sheets into ZIP...")
                        final_sheets = create_custom_sheets(all_processed_stickers, width, height, layout_mode)
                        zip_bytes = export_to_zip(all_processed_stickers, final_sheets)
                        
                        st.session_state['zip_data'] = zip_bytes
                        status.update(label="✅ Production Complete! Shipment Ready.", state="complete", expanded=False)
                        time.sleep(1)
                        st.rerun()

    with tab_guide:
        st.markdown("""
        <div style="text-align: center; font-size: 1.2em;">
        <h3>How It Works</h3>
        <p>1. Enter up to <b>12 prompts</b> in the text area.</p>
        <p>2. Set your <b>Canvas Size</b> and <b>Layout</b>.</p>
        <p>3. Click <b>Run Factory</b> to start the neural engines.</p>
        <p>4. Once complete, your <b>Download</b> button will activate.</p>
        </div>
        """, unsafe_allow_html=True)

    with tab_donate:
        st.markdown("<div style='text-align: center;'><h3>Support Paper Pixel Studio</h3><p>Help us keep these tools free! ☕</p></div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown('<div class="ad-footer"></div>', unsafe_allow_html=True)