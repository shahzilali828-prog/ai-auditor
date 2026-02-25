def get_ceo_templates():
    return {
        "regulatory": {
            "subject": "Urgent: AI Compliance Audit for {domain} (Vulnerabilities Detected)",
            "body": """Hi {name},

I am writing to you directly because our automated compliance scanner flagged several high-risk AI vulnerabilities on {domain}.

With the recent enforcement updates to the EU AI Act and GDPR AI Privacy mandates, businesses in your sector are facing fines of up to €30M for unmasked data processing.

I have generated a preliminary risk report for your team. Usually, a manual audit of this scale costs $5,000+, but we can provide a Full Compliance Certification for a flat fee of $1,250.

Are you available for a 5-minute brief on how to shield {domain} from these regulatory risks?

Best regards,

{sender_name}
AI Compliance Auditor"""
        },
        "merger": {
            "subject": "Notice: AI Privacy Risks impacting {domain} Valuation",
            "body": """Hi {name},

As highly-valued platforms move toward acquisition or scaling, AI technical debt and privacy leaks are becoming the #1 deal-breaker in M&A due diligence.

Our scanner has identified potential 'Shadow AI' usage on {domain} that could jeopardize your compliance standing.

We specialize in rapid AI Safeguard Audits ($1,250) that certify your platform as 'Audit-Ready' for investors.

Would you like to see the preliminary findings for {domain}?

Best,

{sender_name}
CEO, AI Auditor"""
        }
    }
