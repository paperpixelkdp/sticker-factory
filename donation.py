import streamlit as st

def show_donation():
    st.markdown("""
    <div style="text-align: center; padding: 40px; background-color: #161b22; border-radius: 15px; border: 1px solid #30363d;">
        <h2 style="color: #ffffff;">☕ Support Paper Pixel Studio</h2>
        <p style="font-size: 1.1em; color: #8b949e;">We provide these AI automation tools for free to help the POD community grow.</p>
        <p style="font-size: 1.1em; color: #8b949e;">Your support keeps our servers running and our neural engines dreaming!</p>
        <br>
        <a href="#" style="background-color: #ffffff; color: #000000; padding: 15px 30px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 1.2em;">Buy Us a Coffee</a>
    </div>
    """, unsafe_allow_html=True)