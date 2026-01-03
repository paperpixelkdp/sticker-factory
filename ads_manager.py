import streamlit as st

def show_left_ad():
    """Sol reklam alanı"""
    st.markdown('<div class="ad-sidebar">SOL REKLAM ALANI<br>(728x90 veya SkyScraper)</div>', unsafe_allow_html=True)

def show_right_ad():
    """Sağ reklam alanı"""
    st.markdown('<div class="ad-sidebar">SAĞ REKLAM ALANI<br>(728x90 veya SkyScraper)</div>', unsafe_allow_html=True)

def show_footer_ad():
    """Alt reklam alanı (Footer)"""
    st.markdown('<div class="ad-footer">ALT REKLAM ALANI (Banner)</div>', unsafe_allow_html=True)