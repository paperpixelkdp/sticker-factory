import streamlit as st
import io
import time
from image_gen import generate_sticker_image
from image_processor import process_sticker
from layout_manager import create_custom_sheets, export_to_zip

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Paper Pixel | Sticker Factory", layout="wide")

# 1. ADIM: TOKEN'I KASADAN ÇEK
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"].strip()
else:
    st.error("❌ ERROR: HF_TOKEN not found in Secrets! Please add it to Streamlit Cloud settings.")
    st.stop()

# --- CSS (Basit ve Şık) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    div[data-baseweb="tab-list"] { display: flex; justify-content: center; gap: 50px; }
    .stTextArea textarea { background-color: #161b22 !important; color: #ffffff !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- REKLAM ALANLI DÜZEN ---
left_ad, main_content, right_ad = st.columns([1, 4, 1])

with main_content:
    st.title("Paper Pixel Studio")
    tab_factory, tab_guide, tab_donate = st.tabs(["🏭 Factory", "📘 How To Work", "☕ Donation"])

    with tab_factory:
        prompts_raw = st.text_area("Enter Prompts (Max 6):", height=150)
        workflow_area = st.empty()
        
        col_w, col_h, col_l = st.columns(3)
        width = col_w.number_input("Width (px)", value=4500)
        height = col_h.number_input("Height (px)", value=5400)
        layout_mode = col_l.selectbox("Layout Mode", [1, 2, 4, 6, 9, 12], index=3)

        btn_gen = st.button("🚀 GENERATE")

        if btn_gen:
            prompts = [p.strip() for p in prompts_raw.split("\n") if p.strip()][:6]
            if not prompts:
                st.error("Please enter a prompt.")
            else:
                all_stickers = []
                for p in prompts:
                    # 2. ADIM: TOKEN'I MOTORA GÖNDER (HF_TOKEN burada motora iletiliyor)
                    raw_img = generate_sticker_image(p, HF_TOKEN, workflow_area)
                    
                    if raw_img and raw_img != "TOKEN_ERROR":
                        workflow_area.info(f"✂️ Processing: {p}")
                        processed = process_sticker(raw_img)
                        all_stickers.append(processed)
                        st.image(processed, width=200)
                    elif raw_img == "TOKEN_ERROR":
                        st.error("Stopping due to Token Error.")
                        break

                if all_stickers:
                    # ZIP ve Layout işlemleri
                    sheets = create_custom_sheets(all_stickers, width, height, layout_mode)
                    zip_data = export_to_zip(all_stickers, sheets)
                    st.download_button("📥 DOWNLOAD PACK", zip_data, "Pack.zip", "application/zip")