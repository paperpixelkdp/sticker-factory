import streamlit as st
import io
import time
from image_gen import generate_sticker_image
from image_processor import process_sticker
from layout_manager import create_custom_sheets, export_to_zip
from guide import show_guide
from donation import show_donation
import ads_manager # Yeni reklam modülü

# --- CONFIG ---
st.set_page_config(page_title="Paper Pixel | Sticker Factory", layout="wide", initial_sidebar_state="collapsed")

# Secrets
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"].strip()
else:
    st.error("⚠️ HF_TOKEN missing!")
    st.stop()

# --- ULTRA PROFESSIONAL CSS (v8.0 Jilet Sekmeler) ---
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* BAŞLIK ORTALAMA */
    .centered-title { text-align: center; margin-bottom: 30px; font-weight: bold; font-size: 3em; color: #ffffff; }

    /* SEKME (TAB) AYARLARI - BUTONLARLA AYNI GENİŞLİK VE HEYBETTE */
    div[data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        width: 100%;
        gap: 10px;
    }
    button[data-baseweb="tab"] {
        flex: 1; /* Hepsini eşit genişliğe zorla */
        height: 80px !important; /* Yüksekliği artır */
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 12px 12px 0 0 !important;
        transition: 0.3s;
    }
    button[data-baseweb="tab"] div p {
        font-size: 1.5em !important; /* Yazıları dev yap */
        font-weight: 900 !important;
        text-transform: uppercase;
        color: #8b949e !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #21262d !important;
        border-bottom: 4px solid #ffffff !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] div p {
        color: #ffffff !important;
    }

    /* PROMPT ALANI */
    .stTextArea textarea { 
        background-color: #161b22 !important; 
        color: #ffffff !important; 
        border: 1px solid #30363d !important; 
        border-radius: 12px; 
        font-size: 1.3em;
    }

    /* BUTONLAR (Devasa) */
    .stButton > button, .stDownloadButton > button {
        width: 100% !important;
        height: 4.5em !important;
        font-size: 1.4em !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        text-transform: uppercase;
    }
    
    /* Buton Renkleri */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { background-color: #ffffff !important; color: #000000 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { background-color: #262730 !important; color: #ffffff !important; border: 1px solid #464646 !important; }

    /* Reklam Alanı CSS'leri (Placeholder) */
    .ad-sidebar { 
        min-height: 80vh; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        border: 1px dashed #30363d; 
        color: #30363d;
        text-align: center;
        font-size: 0.8em;
    }
    .ad-footer { 
        height: 100px; 
        margin-top: 50px; 
        border: 1px dashed #30363d; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        color: #30363d;
        font-size: 0.8em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ANA DÜZEN (1-5-1 Reklam Yerleşimi) ---
left_col, main_col, right_col = st.columns([1, 5, 1])

with left_col:
    ads_manager.show_left_ad() # Modülden çek

with right_col:
    ads_manager.show_right_ad() # Modülden çek

with main_col:
    # YENİ BAŞLIK
    st.markdown('<h1 class="centered-title">PAPER PIXEL STUDIO | STICKER FACTORY</h1>', unsafe_allow_html=True)
    
    # SEKMELER
    tab_factory, tab_guide, tab_donate = st.tabs(["🏭 FACTORY", "📘 HOW IT WORKS", "☕ DONATION"])

    with tab_factory:
        # Prompt Alanı
        placeholder_txt = "Enter up to 12 prompts (one per line). Example: Cute crocodile drinking soda..."
        prompts_raw = st.text_area("FACTORY_INPUT", height=250, placeholder=placeholder_txt, label_visibility="collapsed")

        # Ayarlar
        st.markdown("<br>", unsafe_allow_html=True)
        col_px, col_lay = st.columns([2, 1])
        with col_px:
            px_w, px_h = st.columns(2)
            width = px_w.number_input("WIDTH (PX)", value=4500, step=100)
            height = px_h.number_input("HEIGHT (PX)", value=5400, step=100)
        with col_lay:
            layout_mode = st.selectbox("LAYOUT GRID", [1, 2, 4, 6, 9, 12], index=3)

        # Butonlar
        st.markdown("<br>", unsafe_allow_html=True)
        col_run, col_dl = st.columns(2, gap="medium")
        
        if 'zip_data' not in st.session_state:
            st.session_state['zip_data'] = None

        with col_run:
            run_factory = st.button("RUN FACTORY")

        with col_dl:
            if st.session_state['zip_data']:
                st.download_button(label="DOWNLOAD", data=st.session_state['zip_data'], file_name="PaperPixel_Pack.zip", mime="application/zip")
            else:
                st.button("DOWNLOAD", disabled=True)

        # --- MOTOR ---
        if run_factory:
            prompts = [p.strip() for p in prompts_raw.split("\n") if p.strip()]
            if not prompts:
                st.error("No input found!")
            elif len(prompts) > 12:
                st.error("Max 12 prompts allowed!")
            else:
                with st.status("🚀 FACTORY LINE ACTIVE...", expanded=True) as status:
                    all_stickers = []
                    for i, p in enumerate(prompts):
                        st.write(f"⚙️ **Processing {i+1}/{len(prompts)}:** {p}")
                        raw_img = generate_sticker_image(p, HF_TOKEN, st.empty())
                        if raw_img and raw_img != "TOKEN_ERROR":
                            processed = process_sticker(raw_img)
                            all_stickers.append(processed)
                        else:
                            st.error(f"Failed: {p}")

                    if all_stickers:
                        final_sheets = create_custom_sheets(all_stickers, width, height, layout_mode)
                        zip_bytes = export_to_zip(all_stickers, final_sheets)
                        st.session_state['zip_data'] = zip_bytes
                        status.update(label="✅ PRODUCTION COMPLETE!", state="complete", expanded=False)
                        time.sleep(1)
                        st.rerun()

    with tab_guide:
        show_guide()

    with tab_donate:
        show_donation()

# FOOTER REKLAM
st.markdown("<br>", unsafe_allow_html=True)
ads_manager.show_footer_ad() # Modülden çek