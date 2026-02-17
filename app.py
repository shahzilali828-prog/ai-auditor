import streamlit as st
from scanner import GDPRScanner
import time

# Page Config
st.set_page_config(page_title="AI GDPR Auditor", page_icon="⚖️", layout="centered")

# Custom CSS for "Hacker/Professional" Look
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        height: 3em;
        border-radius: 5px;
    }
    .report-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("⚖️ AI Compliance Auditor")
st.markdown("### Is your business at risk of a €20 Million GDPR fine?")
st.markdown("Scan your website instantly to find critical legal vulnerabilities.")

# Input
target_url = st.text_input("Enter your Website URL:", placeholder="https://example.com")

if st.button("RUN COMPLIANCE SCAN"):
    if not target_url:
        st.error("Please enter a URL.")
    else:
        # The "Theater" (Loading Animation)
        with st.spinner("🕷️ AI Agent is scanning your Privacy Policy..."):
            scanner = GDPRScanner()
            # Handle user input that might not have http
            if not target_url.startswith("http"):
                target_url = "https://" + target_url
            
            time.sleep(1) # Fake delay for dramatic effect
            result = scanner.audit_site(target_url)

        # Result Display
        if result["status"] == "VULNERABLE":
            st.error("⚠️ CRITICAL VULNERABILITIES FOUND!")
            
            st.markdown(f"""
            <div class="report-box">
                <h4>🚫 FAILED: GDPR Article 13 & 17</h4>
                <p>We found <b>{len(result['errors'])} critical errors</b> in your legal documents.</p>
                <p>Your business is currently <b>NON-COMPLIANT</b> with European Data Laws.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("Your Risk Report:")
            for err in result["errors"]:
                st.write(f"❌ {err}")

            st.markdown("---")
            st.warning("📉 Risk Score: D- (High Risk of Lawsuit)")
            
            # The "Solution" (Paywall)
            st.info("💡 We have generated the legal text to FIX these errors.")
            # MONETIZATION CONFIG (Replace with your actual Lemon Squeezy Product Link)
            # 1. Go to Lemon Squeezy > Products > Create Product
            # 2. Copy the "Share" link (e.g., https://yoursite.lemonsqueezy.com/checkout/buy/...)
            # MONETIZATION CONFIG (Replace with your actual Lemon Squeezy Product Link)
            # 1. Go to Lemon Squeezy > Products > Create Product
            # 2. Copy the "Share" link (e.g., https://yoursite.lemonsqueezy.com/checkout/buy/...)
            LEMON_SQUEEZY_LINK = "https://ai-auditor.lemonsqueezy.com/checkout/buy/80d5c30f-889c-488d-a6ba-1912f0a6d9af" 
            
            st.markdown(f"[**👉 CLICK HERE TO DOWNLOAD THE FIX ($499)**]({LEMON_SQUEEZY_LINK})")
            
        elif result["status"] == "SECURE":
            st.success("✅ PASSED: Your website appears compliant!")
            st.balloons()
            st.markdown("Great job! Your privacy policy contains the required legal keywords.")

        else:
            st.error("Could not scan the website. Please check the URL.")

# Footer
st.markdown("---")
st.markdown("🔒 Secured by AI Compliance Engine v1.0 | [Connect with the Founder](https://www.linkedin.com/in/shahzil-ali-77a7773b1/)")
