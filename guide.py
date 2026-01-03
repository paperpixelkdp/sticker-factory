import streamlit as st

def show_guide():
    # Sayfa tasarımıyla uyumlu bir kutu içinde sunuyoruz
    st.markdown("""
    <div style="background-color: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #30363d; line-height: 1.6;">
        <h1 style="color: #ffffff; text-align: center; border-bottom: 2px solid #30363d; padding-bottom: 10px;">📄 SYSTEM ARCHITECTURE & WORKFLOW</h1>
        
        <p style="text-align: center; color: #8b949e; font-style: italic;">Welcome to the most advanced AI Sticker Factory. Here is exactly how your assets are created.</p>
        
        <h3 style="color: #ffffff; border-left: 5px solid #ffffff; padding-left: 15px;">🚀 Phase 1: Hybrid Neural Generation</h3>
        <p>Our engine doesn't just rely on one AI. We use a <b>"Stubborn Hybrid Engine"</b> that mimics human behavior to guarantee results:</p>
        <ul>
            <li><b>Hugging Face Integration:</b> We query a pool of 15+ high-end models including <b>FLUX.1, SDXL, and DreamShaper</b>.</li>
            <li><b>Pollinations.ai Fail-safe:</b> If our primary nodes are busy, the system automatically switches to the Pollinations global cluster as a backup.</li>
            <li><b>Human-Resilient Logic:</b> Each prompt is attempted multiple times with 20-second "cooldown" periods to bypass server congestion.</li>
        </ul>

        <h3 style="color: #ffffff; border-left: 5px solid #ffffff; padding-left: 15px;">✂️ Phase 2: Professional Pre-Processing</h3>
        <p>Once the raw image is captured, the <b>Sticker Factory Processor</b> takes over:</p>
        <ul>
            <li><b>Automated Background Removal:</b> Using the <b>Rembg (U2-Net)</b> library, we isolate the subject from reality with surgical precision.</li>
            <li><b>Alpha Channel Cleaning:</b> We eliminate "ghost pixels" and semi-transparent edges that cause printing errors.</li>
        </ul>

        <h3 style="color: #ffffff; border-left: 5px solid #ffffff; padding-left: 15px;">💎 Phase 3: The "Jilet" (Razor) Enhancement</h3>
        <p>This is where your design becomes a professional product:</p>
        <ul>
            <li><b>4X Ultra-Upscaling:</b> We use <b>Lanczos Resampling</b> to scale images up to 4000px+ without losing the sharp aesthetic needed for 300 DPI prints.</li>
            <li><b>Die-Cut Outline:</b> A mathematically calculated smooth white border is added. We use <b>Gaussian Blur & Thresholding</b> techniques to ensure corners are perfectly rounded, not pixelated.</li>
        </ul>

        <h3 style="color: #ffffff; border-left: 5px solid #ffffff; padding-left: 15px;">📦 Phase 4: Smart Packaging & Export</h3>
        <p>The final step organizes your production for immediate use:</p>
        <ul>
            <li><b>Grid Optimization:</b> Your stickers are automatically packed into your custom-sized sheets (Default: 4500x5400 px) using our <b>Leftover Logic</b> (no sticker is left behind).</li>
            <li><b>The Production Pack (ZIP):</b> You receive two folders:
                <ul>
                    <li><i>Individual_Stickers:</i> Transparent PNGs for single uploads.</li>
                    <li><i>Print_Ready_Sheets:</i> Master sheets for Redbubble/Amazon "Sticker Pack" options.</li>
                </ul>
            </li>
        </ul>

        <div style="margin-top: 30px; padding: 15px; background-color: #0d1117; border-left: 5px solid #00ff00; border-radius: 5px;">
            <b style="color: #00ff00;">💡 PRO TIP:</b> For best results, always include <b>"white background"</b> and <b>"sticker design"</b> in your prompts. Our engine works best with clear subjects!
        </div>
    </div>
    """, unsafe_allow_html=True)