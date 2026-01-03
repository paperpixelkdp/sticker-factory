import streamlit as st
import io
import time
from image_gen import generate_sticker_image
from image_processor import process_sticker
from layout_manager import create_custom_sheets, export_to_zip
from guide import show_guide
from donation import show_donation
import ads_manager

# --- CONFIG ---
st.set_page_config(page_title="Paper Pixel | Sticker Factory", layout="wide", initial_sidebar_state="collapsed")

# Secrets Check
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"].strip()
else:
    st.error("⚠️ HF_TOKEN missing!")
    st.stop()

# --- CSS BALYOZU (MİLLİMETRİK AYARLAR) ---
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* BAŞLIK */
    .centered-title { text-align: center; margin-bottom: 25px; font-weight: 800; font-size: 2.8em; color: #ffffff; letter-spacing: -1px; }

    /* SEKMELER (TABS) - HEYBETLİ VE TAM GENİŞLİK */
    div[data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        width: 100%;
        gap: 8px;
    }
    button[data-baseweb="tab"] {
        flex: 1;
        height: 75px !important;
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 12px 12px 0 0 !important;
    }
    button[data-baseweb="tab"] div p { font-size: 1.3em !important; font-weight: 800 !important; color: #8b949e !important; }
    button[data-baseweb="tab"][aria-selected="true"] { background-color: #21262d !important; border-bottom: 4px solid #ffffff !important; }
    button[data-baseweb="tab"][aria-selected="true"] div p { color: #ffffff !important; }

    /* PROMPT ALANI */
    .stTextArea textarea { 
        background-color: #161b22 !important; 
        color: #ffffff !important; 
        border: 1px solid #30363d !important; 
        border-radius: 12px; 
        font-size: 1.2em;
        padding: 15px;
    }

    /* BUTON KAPSAYICI (ACTION ROW) */
    /* Bu kısım hem normal butonu hem download butonunu %100 genişliğe zorlar */
    div.row-widget.stButton, div.row-widget.stDownloadButton {
        width: 100% !important;
    }
    
    .stButton > button, .stDownloadButton > button {
        width: 100% !important;
        height: 4em !important;
        border-radius: 12px !important;
        font-size: 1.2em !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        margin: 0 !important;
    }

    /* Run Factory Renkleri */
    div[data-testid="column"]:nth-of-type(1) .stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: none !important;
    }

    /* Download Renkleri */
    div[data-testid="column"]:nth-of-type(2) .stDownloadButton > button, 
    div[data-testid="column"]:nth-of-type(2) .stButton > button {
        background-color: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #464646 !important;
    }

    /* Reklam Alanları */
    .ad-sidebar { min-height: 80vh; display: flex; align-items: center; justify-content: center; border: 1px dashed #30363d; color: #30363d; font-size: 0.8em; text-align: center; }
    .ad-footer { height: 100px; margin-top: 50px; border: 1px dashed #30363d; display: flex; align-items: center; justify-content: center; color: #30363d; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

# --- ANA DÜZEN ---
left_col, main_col, right_col = st.columns([1, 5, 1])

with left_col:
    ads_manager.show_left_ad()

with right_col:
    ads_manager.show_right_ad()

with main_col:
    # BAŞLIK
    st.markdown('<h1 class="centered-title">PAPER PIXEL STUDIO | STICKER FACTORY</h1>', unsafe_allow_html=True)
    
    # SEKMELER
    tab_factory, tab_guide, tab_donate = st.tabs(["🏭 FACTORY", "📘 HOW IT WORKS", "☕ DONATION"])

    with tab_factory:
        # 1. Prompt Kutusu
        prompts_raw = st.text_area("FACTORY_INPUT", height=250, placeholder="Enter up to 12 prompts (one per line)...", label_visibility="collapsed")

        # 2. Ayarlar Satırı
        st.markdown("<br>", unsafe_allow_html=True)
        set_col1, set_col2 = st.columns([2, 1])
        with set_col1:
            px_cols = st.columns(2)
            width = px_cols[0].number_input("WIDTH (PX)", value=4500, step=100)
            height = px_cols[1].number_input("HEIGHT (PX)", value=5400, step=100)
        with set_col2:
            layout_mode = st.selectbox("LAYOUT GRID", [1, 2, 4, 6, 9, 12], index=3)

        # 3. Butonlar Satırı (İşte burası jilet gibi olacak)
        st.markdown("<br>", unsafe_allow_html=True)
        btn_col1, btn_col2 = st.columns(2, gap="medium")
        
        if 'zip_data' not in st.session_state:
            st.session_state['zip_data'] = None

        with btn_col1:
            run_factory = st.button("RUN FACTORY", use_container_width=True)

        with btn_col2:
            if st.session_state['zip_data']:
                st.download_button(label="DOWNLOAD", data=st.session_state['zip_data'], file_name="PaperPixel_Pack.zip", mime="application/zip", use_container_width=True)
            else:
                st.button("DOWNLOAD", disabled=True, use_container_width=True)

        # --- MOTOR ---
        if run_factory:
            prompts = [p.strip() for p in prompts_raw.split("\n") if p.strip()]
            if not prompts:
                st.error("Engine Error: No prompts detected.")
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
ads_manager.show_footer_ad()