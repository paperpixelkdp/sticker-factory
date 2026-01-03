import streamlit as st

def show_donation():
    st.title("☕ Support Paper Pixel Studio")
    st.markdown("""
    Paper Pixel Studio is committed to providing high-end AI automation tools for the Print-on-Demand community **100% free of charge**. 
    
    Maintaining high-performance AI engines and high-res processing requires significant computing costs. If this tool saved you time or helped your business, consider supporting our journey!
    """)

    st.divider()

    # BAĞIŞ KARTLARI
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💳 Global Support")
        st.info("The fastest way to support us via Credit Card or Digital Wallets.")
        # Senin Buy Me a Coffee Linkin
        st.link_button("🚀 Buy Me a Coffee", "https://buymeacoffee.com/paperpixelstudio", use_container_width=True)
        st.caption("Supports: Credit Card, Apple Pay, Google Pay, PayPal.")

    with col2:
        st.subheader("₿ Crypto Donation")
        st.warning("Secure and decentralized support via major networks.")
        
        # Kripto Adreslerin (Tıklayınca Kopyalanabilir)
        with st.expander("View Wallet Addresses"):
            st.write("**ERC20 (Ethereum/USDT):**")
            st.code("0xd11f07848e9db839f41fc8138d8c85972f378452", language="text")
            
            st.write("**BEP20 (BNB Smart Chain):**")
            st.code("0xd11f07848e9db839f41fc8138d8c85972f378452", language="text")
            
            st.write("**TRC20 (Tron Network):**")
            st.code("TYKPsfFHGrdMwL7FAUzNcf7nj217MaZcwd", language="text")
            
            st.write("**SOL (Solana Network):**")
            st.code("2yKXD4HJJYZ2PMQvD8pTMi1tNnnHpYKtjwS93LXCYJWZ", language="text")
            
            st.caption("⚠️ Please ensure you are using the correct network before sending funds.")

    st.divider()

    # İLETİŞİM VE GERİ BİLDİRİM
    st.subheader("📧 Requests & Feedback")
    st.markdown("""
    Do you have a feature request, a bug report, or a business inquiry? 
    We value every piece of feedback from our creative community!
    """)
    
    # Senin Proton Mailin
    contact_mail = "paperpixelstudio@proton.me"
    subject = "Paper Pixel Factory - Feedback"
    mail_link = f"mailto:{contact_mail}?subject={subject}"
    
    st.link_button("📬 Send us an Email", mail_link, use_container_width=True)
    st.markdown(f"<div style='text-align: center; color: #8b949e; margin-top: 10px;'>Direct contact: <b>{contact_mail}</b></div>", unsafe_allow_html=True)

    st.divider()
    st.success("Thank you for supporting independent AI development! 🚀")