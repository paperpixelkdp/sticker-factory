import streamlit as st
import io
import time
from image_gen import generate_sticker_image
from image_processor import process_sticker
from layout_manager import create_custom_sheets, export_to_zip
from guide import show_guide # Yeni modül
from donation import show_donation # Yeni modül

# --- CONFIG ---
st.set_page_config(page_title="Paper Pixel | Sticker Factory", layout="wide", initial_sidebar_state="collapsed")

# Secrets
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"].strip()
else:
    st.error("⚠️ HF_TOKEN missing!")
    st.stop()

# --- ULTRA PROFESSIONAL CSS ---
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* SEKME AYARLARI (Heybetli ve Geniş) */
    div[data-baseweb="tab-list"] {
        display: flex;
        justify-content: space-between;
        width: 100%;
        gap: 10px;
    }
    div[data-baseweb="tab"] {
        flex: 1; /* Tüm genişliğe yay */
        text-align: center;
        height: 70px;
        background-color: #161b22 !important;
        border-radius: 10px 10px 0 0;
        margin: 0 5px;
        border: 1px solid #30363d;
    }
    div[data-baseweb="tab"] p {
        font-size: 1.5em !important;
        font-weight: bold;
        padding-top: 10px;
    }
    div[data-baseweb="tab"][aria-selected="true"] {
        background-color: #21262d !important;
        border-bottom: 3px solid #ffffff !important;
    }

    /* Başlık Ortalama */
    .centered-title { text-align: center; margin-bottom: 20px; font-weight: bold; font-size: 3em; color: #ffffff; }

    /* PROMPT ALANI */
    .stTextArea textarea { 
        background-color: #161b22 !important; 
        color: #ffffff !important; 
        border: 1px solid #30363d !important; 
        border-radius: 12px; 
        font-size: 1.2em;
    }
    .stTextArea textarea::placeholder { font-style: italic; opacity: 0.6; }
    
    /* SAYISAL GİRDİLER VE SELECTBOX */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #161b22 !important;
        border-radius: 8px !important;
    }

    /* BUTONLAR (Devasa ve Yan Yana) */
    .stButton > button, .stDownloadButton > button {
        width: 100% !important;
        height: 4.5em !important;
        font-size: 1.3em !important;
        border-radius: 12px !important;
        font-weight: 2000 !important; /* En kalın yazı */
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Run Factory (Beyaz Tema) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: none !important;
    }
    /* Download (Koyu Tema) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        background-color: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #464646 !important;
    }

    /* Reklam Alanları */
    .ad-sidebar { min-height: 80vh; }
    .ad-footer { height: 100px; margin-top: 50px; border-top: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- ANA DÜZEN ---
left_ad, main_container, right_ad = st.columns([1, 5, 1]) # İçeriği biraz daha genişlettik

with main_container:
    st.markdown('<h1 class="centered-title">PAPER PIXEL STUDIO</h1>', unsafe_allow_html=True)
    
    tab_factory, tab_guide, tab_donate = st.tabs(["🏭 FACTORY", "📘 HOW IT WORKS", "☕ DONATION"])

    with tab_factory:
        # 1. Prompt Alanı
        placeholder_txt = "Enter up to 12 prompts here (one per line). Click here to start typing..."
        prompts_raw = st.text_area("FACTORY_INPUT", height=250, placeholder=placeholder_txt, label_visibility="collapsed")

        # 2. Settings (PX ve Layout)
        st.markdown("<br>", unsafe_allow_html=True)
        col_px, col_lay = st.columns([2, 1])
        
        with col_px:
            px_w, px_h = st.columns(2)
            width = px_w.number_input("WIDTH (PX)", value=4500, step=100)
            height = px_h.number_input("HEIGHT (PX)", value=5400, step=100)
            
        with col_lay:
            layout_mode = st.selectbox("LAYOUT GRID", [1, 2, 4, 6, 9, 12], index=3)

        # 3. Butonlar (Heybetli ve Bitişik)
        st.markdown("<br>", unsafe_allow_html=True)
        col_run, col_dl = st.columns(2, gap="medium")
        
        if 'zip_data' not in st.session_state:
            st.session_state['zip_data'] = None

        with col_run:
            run_factory = st.button("RUN FACTORY", use_container_width=True)

        with col_dl:
            if st.session_state['zip_data']:
                st.download_button(label="DOWNLOAD", data=st.session_state['zip_data'], file_name="PaperPixel_Pack.zip", mime="application/zip", use_container_width=True)
            else:
                st.button("DOWNLOAD", disabled=True, use_container_width=True)

        # --- MOTOR MANTIĞI ---
        if run_factory:
            prompts = [p.strip() for p in prompts_raw.split("\n") if p.strip()]
            if not prompts:
                st.error("Engine Error: No prompts detected.")
            elif len(prompts) > 12:
                st.error("🚨 Safety Limit: Maximum 12 prompts allowed.")
            else:
                with st.status("🚀 FACTORY LINE ACTIVE...", expanded=True) as status:
                    all_processed_stickers = []
                    for i, p in enumerate(prompts):
                        st.write(f"⚙️ **Processing {i+1}/{len(prompts)}:** {p}")
                        raw_img = generate_sticker_image(p, HF_TOKEN, st.empty())
                        
                        if raw_img and raw_img != "TOKEN_ERROR":
                            processed_sticker = process_sticker(raw_img, outline_thickness=30)
                            all_processed_stickers.append(processed_sticker)
                        else:
                            st.error(f"Failed: {p}")

                    if all_processed_stickers:
                        st.write("📦 **Finalizing Production Pack...**")
                        final_sheets = create_custom_sheets(all_processed_stickers, width, height, layout_mode)
                        zip_bytes = export_to_zip(all_processed_stickers, final_sheets)
                        st.session_state['zip_data'] = zip_bytes
                        status.update(label="✅ PRODUCTION COMPLETE!", state="complete", expanded=False)
                        time.sleep(1)
                        st.rerun()

    with tab_guide:
        show_guide() # Dışarıdan çağırdık

    with tab_donate:
        show_donation() # Dışarıdan çağırdık

# Sol ve Sağ Reklam Alanları İçin Görünmez Doldurma
with left_ad: st.markdown('<div class="ad-sidebar"></div>', unsafe_allow_html=True)
with right_ad: st.markdown('<div class="ad-sidebar"></div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="ad-footer"></div>', unsafe_allow_html=True)