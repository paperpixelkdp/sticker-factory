import streamlit as st

def show_guide():
    st.markdown("""
    <div style="text-align: center; font-size: 1.2em; padding: 20px; background-color: #161b22; border-radius: 15px; border: 1px solid #30363d;">
        <h2 style="color: #ffffff;">📘 Professional Workflow Guide</h2>
        <p>1. Enter up to <b>12 unique prompts</b> in the factory area.</p>
        <p>2. Define your <b>Canvas Size</b> (e.g., 4500x5400 for Redbubble Master sheets).</p>
        <p>3. Select your <b>Layout Grid</b> for automatic packing.</p>
        <p>4. Execute <b>Run Factory</b> and wait for the neural engines to finish.</p>
        <p>5. Download your <b>Production Pack</b> containing all assets.</p>
    </div>
    """, unsafe_allow_html=True)