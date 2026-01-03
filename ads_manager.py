import streamlit as st

# --- REKLAM AYARLARI ---
RB_LINK = "https://www.redbubble.com/people/paperpixelkdp/shop?asc=u"
RAW_BASE_URL = "https://raw.githubusercontent.com/paperpixelkdp/sticker-factory/main/assets/"

ADS_CONFIG = {
    "left_sidebar": [
        {"image_url": f"{RAW_BASE_URL}banner_1.png", "link": RB_LINK},
        {"image_url": f"{RAW_BASE_URL}banner_3.png", "link": RB_LINK}, # 2. görsel (Sol alt)
    ],
    "right_sidebar": [
        {"image_url": f"{RAW_BASE_URL}banner_2.png", "link": RB_LINK},
        {"image_url": f"{RAW_BASE_URL}banner_4.png", "link": RB_LINK}, # 2. görsel (Sağ alt)
    ]
}

def show_left_ad():
    for ad in ADS_CONFIG["left_sidebar"]:
        st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <a href="{ad['link']}" target="_blank">
                    <img src="{ad['image_url']}" style="width:100%; border-radius:10px; border:1px solid #30363d; transition:0.3s;" 
                    onmouseover="this.style.borderColor='#ffffff'; this.style.transform='scale(1.02)';" 
                    onmouseout="this.style.borderColor='#30363d'; this.style.transform='scale(1.0)';" >
                </a>
            </div>
        """, unsafe_allow_html=True)

def show_right_ad():
    for ad in ADS_CONFIG["right_sidebar"]:
        st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <a href="{ad['link']}" target="_blank">
                    <img src="{ad['image_url']}" style="width:100%; border-radius:10px; border:1px solid #30363d; transition:0.3s;" 
                    onmouseover="this.style.borderColor='#ffffff'; this.style.transform='scale(1.02)';" 
                    onmouseout="this.style.borderColor='#30363d'; this.style.transform='scale(1.0)';" >
                </a>
            </div>
        """, unsafe_allow_html=True)

def show_footer_ad():
    pass