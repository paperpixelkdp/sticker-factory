import streamlit as st

# --- REKLAM AYARLARI ---
RB_LINK = "https://www.redbubble.com/people/paperpixelkdp/shop?asc=u"

# RAW (Ham) Görüntü Linkleri
LEFT_AD_RAW = "https://raw.githubusercontent.com/paperpixelkdp/sticker-factory/main/assets/SHOP%20NOW.png"
RIGHT_AD_RAW = "https://raw.githubusercontent.com/paperpixelkdp/sticker-factory/main/assets/SHOP%20NOW.png"

ADS_CONFIG = {
    "left_sidebar": [
        {"image_url": LEFT_AD_RAW, "link": RB_LINK},
    ],
    "right_sidebar": [
        {"image_url": RIGHT_AD_RAW, "link": RB_LINK},
    ]
}

def show_left_ad():
    for ad in ADS_CONFIG["left_sidebar"]:
        st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <a href="{ad['link']}" target="_blank">
                    <img src="{ad['image_url']}" style="width:100%; border-radius:10px; border:1px solid #30363d; transition:0.3s;" onmouseover="this.style.borderColor='#ffffff'" onmouseout="this.style.borderColor='#30363d'">
                </a>
            </div>
        """, unsafe_allow_html=True)

def show_right_ad():
    for ad in ADS_CONFIG["right_sidebar"]:
        st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <a href="{ad['link']}" target="_blank">
                    <img src="{ad['image_url']}" style="width:100%; border-radius:10px; border:1px solid #30363d; transition:0.3s;" onmouseover="this.style.borderColor='#ffffff'" onmouseout="this.style.borderColor='#30363d'">
                </a>
            </div>
        """, unsafe_allow_html=True)

def show_footer_ad():
    pass