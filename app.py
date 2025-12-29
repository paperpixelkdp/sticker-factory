import streamlit as st
import requests
from rembg import remove
from PIL import Image
import io
import time
import random

# Sayfa Yapılandırması
st.set_page_config(page_title="Paper Pixel | Sticker Factory", layout="wide", initial_sidebar_state="collapsed")

# Profesyonel Karanlık Tema (CSS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; background-color: #262730; color: white; border: 1px solid #464646; font-weight: bold; }
    .stButton>button:hover { background-color: #1c1c24; border: 1px solid #ffffff; }
    .stTextArea>div>div>textarea { background-color: #161b22; color: #ffffff; border: 1px solid #30363d; font-family: monospace; }
    div[data-baseweb="tab-list"] { gap: 20px; border-bottom: 1px solid #30363d; }
    div[data-baseweb="tab"] { color: #8b949e; }
    div[data-baseweb="tab"][aria-selected="true"] { color: #ffffff; border-bottom-color: #ffffff; }
    .model-info { background-color: #1c1c24; padding: 10px; border-radius: 5px; border-left: 3px solid #ffffff; font-size: 0.8em; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("Paper Pixel Studio")
st.caption("Professional AI Sticker Factory | Open-Source Logic")

# Üst Sekmeler (About Eklendi)
tab_app, tab_guide, tab_about, tab_support = st.tabs(["🚀 Engine", "📖 User Guide", "ℹ️ About", "☕ Support"])

with tab_guide:
    st.markdown("### How to Work\n1. Input your prompts.\n2. Choose your platform.\n3. The engine will auto-retry until the best image is fetched.")

with tab_about:
    st.markdown("""
    ### About Sticker Factory
    Paper Pixel Studio believes in transparency. 
    - **AI Engine:** This tool uses the **Pollinations.ai** open-source API.
    - **Models:** It dynamically switches between high-performance models (Flux, SDXL, Turbo) depending on server availability to ensure 100% up-time.
    - **Processing:** Background removal is processed locally via the **Rembg** library.
    - **Mission:** Our goal is to provide POD sellers with professional-grade automation tools for free.
    """)

with tab_support:
    st.markdown("### Support our Project\nIf this tool helps your business, consider supporting our journey to create more free AI tools.")

with tab_app:
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.subheader("Control Panel")
        prompts_text = st.text_area("Enter Prompts (One per line):", placeholder="Example: Vintage tiger head", height=250)
        platform = st.selectbox("POD Platform", ["Redbubble", "Amazon Merch", "Etsy", "Manual"])
        run_engine = st.button("RUN FACTORY ENGINE")

    with col_right:
        st.subheader("Live Preview & System Info")
        status_area = st.empty()
        preview_area = st.container()

    if run_engine:
        if not prompts_text.strip():
            st.error("Please enter a prompt.")
        else:
            prompts = [p.strip() for p in prompts_text.split("\n") if p.strip()]
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            
            for i, raw_prompt in enumerate(prompts):
                image_data = None
                used_seed = 0
                
                for attempt in range(25):
                    status_area.info(f"⚡ Generating {i+1}/{len(prompts)} | Attempt {attempt+1}")
                    try:
                        used_seed = random.randint(100000, 9999999)
                        sticker_prompt = requests.utils.quote(f"{raw_prompt}, sticker style, white background, high resolution")
                        # Sunucunun boşta ne varsa onu seçmesi için model belirtmiyoruz (Auto-select)
                        api_url = f"https://image.pollinations.ai/prompt/{sticker_prompt}?width=1024&height=1024&seed={used_seed}&nologo=true"
                        
                        response = requests.get(api_url, headers=headers, timeout=60)
                        
                        if response.status_code == 200 and len(response.content) > 5000:
                            image_data = response.content
                            break
                        time.sleep(2)
                    except:
                        time.sleep(2)
                
                if image_data:
                    status_area.info(f"✂️ Removing Background: {raw_prompt}")
                    try:
                        input_img = Image.open(io.BytesIO(image_data))
                        output_img = remove(input_img)
                        
                        with preview_area:
                            # SİSTEM BİLGİSİ GÖSTERİMİ
                            st.markdown(f"""
                                <div class="model-info">
                                <b>System Info:</b><br>
                                Prompt: {raw_prompt}<br>
                                Engine: Pollinations Dynamic (Best Available)<br>
                                Seed: {used_seed}
                                </div>
                                """, unsafe_allow_html=True)
                            st.image(output_img, use_container_width=True)
                            st.divider()
                    except Exception as e:
                        st.error(f"Processing error: {e}")
                else:
                    st.error(f"Server Overload for: {raw_prompt}")

            status_area.success("All tasks completed.")