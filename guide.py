import streamlit as st

def show_guide():
    # Sayfa başlığı
    st.title("📄 System Architecture & Workflow")
    st.caption("How your professional assets are created by Paper Pixel Studio.")
    
    st.divider()

    # PHASE 1
    st.header("🚀 Phase 1: Hybrid Neural Generation")
    st.markdown("""
    Our engine uses a **Stubborn Hybrid System** that mimics human behavior to guarantee results:
    *   **Hugging Face Pool:** We query 15+ high-end models including **FLUX.1** and **SDXL**.
    *   **Pollinations.ai Fail-safe:** Automatic backup nodes ensure 100% uptime even during peak hours.
    *   **Human-Resilient Logic:** Multiple generation attempts with 20s cooldowns to bypass server congestion.
    """)

    # PHASE 2
    st.header("✂️ Phase 2: Professional Pre-Processing")
    st.markdown("""
    Once the raw image is captured, our processor takes over:
    *   **Automated Background Removal:** Using the **Rembg (U2-Net)** neural network for surgical precision.
    *   **Alpha Channel Cleaning:** We eliminate 'ghost pixels' and semi-transparent messy edges that cause printing errors.
    """)

    # PHASE 3
    st.header("💎 Phase 3: The 'Jilet' Enhancement")
    st.markdown("""
    This is where your design becomes a retail-ready product:
    *   **4X Ultra-Upscaling:** Every sticker is scaled up to 4000px+ using **Lanczos Resampling** for 300 DPI clarity.
    *   **Die-Cut Outline:** A mathematically calculated smooth white border is added specifically for POD standards.
    *   **Anti-Aliasing:** We apply **Gaussian Blur & Thresholding** to ensure corners are perfectly rounded, not pixelated.
    """)

    # PHASE 4
    st.header("📦 Phase 4: Smart Packaging & Export")
    st.markdown("""
    Final organization for Print-on-Demand efficiency:
    *   **Grid Optimization:** Automatic packing into custom sheets (e.g., 4500x5400 px) based on your layout choice.
    *   **Zero-Waste Logic:** Leftover stickers are automatically moved to additional master sheets.
    """)

    # PRO TIP
    st.success("💡 **PRO TIP:** For best results, always include **'white background'** and **'sticker design'** in your prompts. Our engine works best with clear, isolated subjects!")

    st.divider()
    st.markdown("© 2025 Paper Pixel Studio | All rights reserved.")