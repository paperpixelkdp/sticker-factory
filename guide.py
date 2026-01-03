import streamlit as st

def show_guide():
    # CSS ile hem taşmayı engelliyoruz hem de HTML'in düzgün görünmesini sağlıyoruz
    st.markdown("""
        <style>
        .guide-container {
            background-color: #161b22;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #30363d;
            color: #ffffff;
            line-height: 1.6;
            max-width: 100%;
            word-wrap: break-word;
        }
        .guide-container h1, .guide-container h3 {
            color: #ffffff;
            margin-top: 20px;
        }
        .guide-container ul {
            padding-left: 20px;
        }
        .guide-container li {
            margin-bottom: 10px;
            color: #c9d1d9;
        }
        .step-header {
            border-left: 4px solid #ffffff;
            padding-left: 15px;
            margin-bottom: 15px;
        }
        .pro-tip {
            margin-top: 30px;
            padding: 15px;
            background-color: #0d1117;
            border-left: 5px solid #00ff00;
            border-radius: 5px;
        }
        </style>
        
        <div class="guide-container">
            <h1 style="text-align: center; border-bottom: 2px solid #30363d; padding-bottom: 10px;">📄 SYSTEM ARCHITECTURE</h1>
            <p style="text-align: center; color: #8b949e; font-style: italic;">How your professional assets are created by Paper Pixel Studio.</p>
            
            <div class="step-header">
                <h3>🚀 Phase 1: Hybrid Neural Generation</h3>
            </div>
            <p>Our engine uses a <b>Stubborn Hybrid System</b> that mimics human behavior to guarantee results:</p>
            <ul>
                <li><b>Hugging Face Pool:</b> We query 15+ high-end models including FLUX.1 and SDXL.</li>
                <li><b>Pollinations.ai Fail-safe:</b> Automatic backup nodes for 100% uptime.</li>
                <li><b>Human-Resilient Logic:</b> Multiple attempts with 20s cooldowns to bypass congestion.</li>
            </ul>

            <div class="step-header">
                <h3>✂️ Phase 2: Professional Pre-Processing</h3>
            </div>
            <p>Once captured, the <b>Sticker Factory Processor</b> takes over:</p>
            <ul>
                <li><b>Automated Background Removal:</b> Using Rembg (U2-Net) for surgical precision.</li>
                <li><b>Alpha Channel Cleaning:</b> No ghost pixels or semi-transparent messy edges.</li>
            </ul>

            <div class="step-header">
                <h3>💎 Phase 3: The "Jilet" Enhancement</h3>
            </div>
            <p>This is where your design becomes a retail-ready product:</p>
            <ul>
                <li><b>4X Ultra-Upscaling:</b> Scaled up to 4000px+ using Lanczos Resampling.</li>
                <li><b>Die-Cut Outline:</b> Mathematically calculated smooth white borders for POD.</li>
                <li><b>Anti-Aliasing:</b> Gaussian Blur & Thresholding for perfectly rounded corners.</li>
            </ul>

            <div class="step-header">
                <h3>📦 Phase 4: Smart Packaging & Export</h3>
            </div>
            <p>Final organization for Print-on-Demand speed:</p>
            <ul>
                <li><b>Grid Optimization:</b> Automatic packing into custom sheets (e.g., 4500x5400 px).</li>
                <li><b>Zero-Waste Logic:</b> Leftover stickers are moved to additional master sheets.</li>
            </ul>

            <div class="pro-tip">
                <b style="color: #00ff00;">💡 PRO TIP:</b> For best results, include <b>"white background"</b> and <b>"sticker design"</b> in your prompts.
            </div>
        </div>
    """, unsafe_allow_html=True)