import streamlit as st
import io
import time
import base64
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

# --- AUTO-DOWNLOAD JAVASCRIPT ---
def trigger_auto_download(bin_data, file_name):
    """İşlem bittiğinde dosyayı otomatik indirmek için JS tetikleyici."""
    b64 = base64.b64encode(bin_data).decode()
    js_code = f"""
        <script>
        var a = document.createElement('a');
        a.href = 'data:application/zip;base64,{b64}';
        a.download = '{file_name}';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

# --- ULTRA PROFESSIONAL CSS (v12.0) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .centered-title { text-align: center; margin-bottom: 30px; font-weight: 800; font-size: 2.8em; color: #ffffff; }

    /* SEKMELER (TABS) - HEYBETLİ */
    div[data-baseweb="tab-list"] { display: flex; justify-content: center; width: 100%; gap: 10px; }
    button[data-baseweb="tab"] {
        flex: 1; height: 80px !important;
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 12px 12px 0 0 !important;
    }
    button[data-baseweb="tab"] div p { font-size: 1.3em !important; font-weight: 800 !important; color: #8b949e !important; }
    button[data-baseweb="tab"][aria-selected="true"] { background-color: #21262d !important; border-bottom: 4px solid #ffffff !important; }
    button[data-baseweb="tab"][aria-selected="true"] div p { color: #ffffff !important; }

    /* PROMPT ALANI */
    .stTextArea textarea { 
        background-color: #161b22 !important; color: #ffffff !important; 
        border: 1px solid #30363d !important; border-radius: 12px; 
        font-size: 1.2em; padding: 15px; text-align: center;
    }

    /* RUN FACTORY BUTONU (HEYBETLİ) */
    .stButton > button {
        width: 100% !important;
        height: 5em !important; /* Daha da heybetli yaptık */
        border-radius: 15px !important;
        font-size: 1.4em !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        background-color: #ffffff !important;
        color: #000000 !important;
        border: none !important;
        transition: 0.3s;
        box-shadow: 0px 4px 15px rgba(255, 255, 255, 0.1);
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0px 6px 20px rgba(255, 255, 255, 0.2);
    }

    /* Reklam Placeholder */
    .ad-sidebar { min-height: 80vh; display: flex; align-items: center; justify-content: center; border: 1px dashed #30363d; color: #30363d; font-size: 0.8em; text-align: center; }
    .ad-footer { height: 100px; margin-top: 50px; border: 1px dashed #30363d; display: flex; align-items: center; justify-content: center; color: #30363d; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

# --- ANA DÜZEN ---
left_col, main_col, right_col = st.columns([1, 5, 1])

with left_col: ads_manager.show_left_ad()
with right_col: ads_manager.show_right_ad()

with main_col:
    st.markdown('<h1 class="centered-title">PAPER PIXEL STUDIO | STICKER FACTORY</h1>', unsafe_allow_html=True)
    tab_factory, tab_guide, tab_donate = st.tabs(["🏭 FACTORY", "📘 HOW IT WORKS", "☕ DONATION"])

    with tab_factory:
        # 1. Prompt Kutusu
        prompts_raw = st.text_area("FACTORY_INPUT", height=250, placeholder="Enter up to 12 prompts (one per line)...\nItalicized hint: Be descriptive for best results.", label_visibility="collapsed")

        # 2. Ayarlar
        st.markdown("<br>", unsafe_allow_html=True)
        set_col1, set_col2 = st.columns([2, 1])
        with set_col1:
            px_cols = st.columns(2)
            width = px_cols[0].number_input("WIDTH (PX)", value=4500, step=100)
            height = px_cols[1].number_input("HEIGHT (PX)", value=5400, step=100)
        with set_col2:
            layout_mode = st.selectbox("LAYOUT GRID", [1, 2, 4, 6, 9, 12], index=3)

        # 3. RUN FACTORY BUTONU (2/3 GENİŞLİK VE MERKEZLENMİŞ)
        st.markdown("<br>", unsafe_allow_html=True)
        # [1, 4, 1] oranı butonun 4/6 yani tam olarak 2/3 genişlikte olmasını sağlar.
        btn_center_col1, btn_center_col2, btn_center_col3 = st.columns([1, 4, 1])

        with btn_center_col2:
            run_factory = st.button("RUN FACTORY")

        # --- ÜRETİM MOTORU ---
        if run_factory:
            prompts = [p.strip() for p in prompts_raw.split("\n") if p.strip()]
            if not prompts:
                st.error("Engine Error: No prompts detected.")
            elif len(prompts) > 12:
                st.error("🚨 Safety Limit: Max 12 prompts allowed!")
            else:
                with st.status("🚀 FACTORY LINE ACTIVE...", expanded=True) as status:
                    all_processed_stickers = []
                    for i, p in enumerate(prompts):
                        st.write(f"⚙️ **Step {i+1}:** neural dreaming for '{p}'...")
                        raw_img = generate_sticker_image(p, HF_TOKEN, st.empty())
                        if raw_img and raw_img != "TOKEN_ERROR":
                            processed = process_sticker(raw_img)
                            all_processed_stickers.append(processed)
                        else:
                            st.error(f"Failed to generate: {p}")

                    if all_stickers_count := len(all_processed_stickers):
                        st.write("📦 **Finalizing & Exporting...**")
                        final_sheets = create_custom_sheets(all_processed_stickers, width, height, layout_mode)
                        zip_bytes = export_to_zip(all_processed_stickers, final_sheets)
                        
                        # BAŞARILI BİTİŞ VE OTOMATİK İNDİRME TETİĞİ
                        status.update(label="✅ PRODUCTION COMPLETE! AUTO-DOWNLOADING...", state="complete", expanded=False)
                        
                        # İşte o sihirli an:
                        trigger_auto_download(zip_bytes, "PaperPixel_Production_Pack.zip")
                        st.success(f"Success! {all_stickers_count} stickers produced and exported.")

    with tab_guide:
        show_guide()

    with tab_donate:
        show_donation()

# FOOTER
st.markdown("<br>", unsafe_allow_html=True)
ads_manager.show_footer_ad()