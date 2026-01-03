import streamlit as st

# --- REKLAM AYARLARI ---
# Redbubble Mağazan: https://www.redbubble.com/people/paperpixelkdp/shop?asc=u
RB_LINK = "https://www.redbubble.com/people/paperpixelkdp/shop?asc=u"

ADS_CONFIG = {
    "left_sidebar": [
        # Buraya istediğin kadar görsel ekleyebilirsin, alt alta sıralanır.
        {"image_url": "https://placehold.co/300x600/161b22/ffffff?text=My+Redbubble+Art+1", "link": RB_LINK},
        # {"image_url": "İKİNCİ_RESİM_LİNKİ", "link": RB_LINK}, 
    ],
    "right_sidebar": [
        {"image_url": "https://placehold.co/300x600/161b22/ffffff?text=My+Redbubble+Art+2", "link": RB_LINK},
    ]
}

def show_left_ad():
    """Sol reklam alanında görselleri dikey (alt alta) gösterir."""
    for ad in ADS_CONFIG["left_sidebar"]:
        st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <a href="{ad['link']}" target="_blank">
                    <img src="{ad['image_url']}" style="width:100%; border-radius:10px; border:1px solid #30363d; transition:0.3s;" onmouseover="this.style.borderColor='#ffffff'" onmouseout="this.style.borderColor='#30363d'">
                </a>
            </div>
        """, unsafe_allow_html=True)

def show_right_ad():
    """Sağ reklam alanında görselleri dikey (alt alta) gösterir."""
    for ad in ADS_CONFIG["right_sidebar"]:
        st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <a href="{ad['link']}" target="_blank">
                    <img src="{ad['image_url']}" style="width:100%; border-radius:10px; border:1px solid #30363d; transition:0.3s;" onmouseover="this.style.borderColor='#ffffff'" onmouseout="this.style.borderColor='#30363d'">
                </a>
            </div>
        """, unsafe_allow_html=True)

def show_footer_ad():
    """Kullanıcı istemediği için boş bırakıldı."""
    pass