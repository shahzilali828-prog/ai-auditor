try:
    import streamlit as st
    import time
    from scanner import GDPRScanner
except Exception as e:
    import streamlit as st
    st.error(f"Startup Error: {e}")
    import traceback
    st.code(traceback.format_exc())
    st.stop()

# Page Config
st.set_page_config(page_title="AI GDPR Auditor", page_icon="⚖️", layout="centered")

# Custom CSS for "Premium/Professional" Look
st.markdown("""
    <style>
    .stApp {
        background-color: #f8fafc;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #ff4b4b 0%, #ff7676 100%);
        color: white !important;
        height: 3.5em;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .report-box {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #ff4b4b;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .buy-button {
        display: block;
        width: 100%;
        text-align: center;
        background: #10b981;
        color: white !important;
        padding: 15px;
        border-radius: 8px;
        font-weight: bold;
        text-decoration: none;
        font-size: 1.2em;
        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
        margin-top: 20px;
    }
    .buy-button:hover {
        background: #059669;
        text-decoration: none;
    }
    .trust-footer {
        text-align: center;
        color: #64748b;
        font-size: 0.85em;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("⚖️ AI Compliance Auditor")
st.markdown("### Protect your business from €20M+ GDPR fines.")
st.markdown("Instantly scan your digital presence for hidden legal liabilities.")

# Input
target_url = st.text_input("Enter your Website URL:", placeholder="https://example.com")

if st.button("START COMPLIANCE AUDIT"):
    if not target_url:
        st.error("Please enter a URL.")
    else:
        # The "Theater" (Loading Animation)
        with st.spinner("🕵️ AI Engine is auditing legal clauses..."):
            scanner = GDPRScanner()
            if not target_url.startswith("http"):
                target_url = "https://" + target_url
            
            time.sleep(1.5) # Dramatic pause
            result = scanner.audit_site(target_url)

        # Result Display
        if result["status"] == "VULNERABLE":
            st.error("🚨 CRITICAL LEGAL RISKS DETECTED")
            
            st.markdown(f"""
            <div class="report-box">
                <h3 style="color:#1e293b; margin-top:0;">🚫 AUDIT FAILED: Non-Compliant</h3>
                <p style="color:#64748b;">Our AI matched your site against <b>GDPR Articles 13 & 17</b>.</p>
                <div style="background:#fff1f2; padding:10px; border-radius:6px; color:#be123c; font-weight:bold;">
                    Found {len(result['errors'])} High-Severity Vulnerabilities.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("Vulnerability Summary:")
            for err in result["errors"]:
                st.markdown(f"🚩 **{err}**")

            st.markdown("---")
            st.error("📉 Risk Profile: **HIGH (Class Action Lawsuit Potential)**")
            
            # The "Solution" (Paywall)
            st.markdown("### 💡 Immediate Mitigation Required")
            st.info("Our legal engine has generated the custom Article 13 & 17 clauses specifically for your domain to patch these gaps instantly.")
            
            LEMON_SQUEEZY_LINK = "https://ai-auditor.lemonsqueezy.com/checkout/buy/80d5c30f-889c-488d-a6ba-1912f0a6d9af" 
            
            st.markdown(f"""
                <a href="{LEMON_SQUEEZY_LINK}" class="buy-button">
                    🚀 DOWNLOAD THE FIX & SECURE BUSINESS ($297)
                </a>
                <p class="trust-footer">✅ 100% Satisfaction Guarantee | Attorney-Reviewed Templates</p>
            """, unsafe_allow_html=True)
            
        elif result["status"] == "SECURE":
            st.success("✅ AUDIT PASSED: No Machine-Detectable Gaps Found.")
            st.balloons()
            st.markdown("Your privacy policy currently meets the standard algorithmic compliance requirements.")

        else:
            st.error("Audit Interrupted. Please verify the URL and try again.")

# Footer
st.markdown("---")
st.markdown("""
<div class="trust-footer">
    🛡️ Powered by AI Compliance Engine v1.1<br>
    <a href="https://www.linkedin.com/in/shahzil-ali-77a7773b1/">Contact Chief Compliance Officer</a>
</div>
""", unsafe_allow_html=True)
