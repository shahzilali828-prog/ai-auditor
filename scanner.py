import requests
from bs4 import BeautifulSoup
import re
def colored(text, color=None, on_color=None, attrs=None):
    return text
from urllib.parse import urljoin
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class GDPRScanner:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            print(colored(f"[*] AI Auditor Initialized (New SDK: {self.api_key[:5]}...{self.api_key[-4:]})", "green"))
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = 'gemini-1.5-flash'
        else:
            print(colored("[!] WARNING: No Gemini API Key found.", "yellow"))
        
        # Original checks kept for fallback or specific logic hints
        self.compliance_checks = {
            "gdpr_compliance": "Does the privacy policy explicitly mention GDPR compliance and data subject rights (Art. 13/14)?",
            "erasure": "Does the policy explain the 'Right to Erasure' or 'Right to be Forgotten' (Art. 17)?",
            "ccpa": "Does the policy address CCPA/CPRA rights, specifically the right to opt-out of sales?",
            "ai_governance": "Does the site mention how AI/automated decision-making is handled (EU AI Act requirement)?"
        }

    def fetch_privacy_policy(self, url):
        """
        Tries to find the privacy policy from the homepage URL.
        """
        try:
            print(f"[*] Scanning Homepage: {url}...")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 1. Try to find a link that says "Privacy" or has "privacy" in the URL
            privacy_link = None
            for a in soup.find_all('a', href=True):
                if 'privacy' in a.text.lower() or 'privacy' in a['href'].lower():
                    privacy_link = a['href']
                    break
            
            if not privacy_link:
                print(colored("[-] Could not find 'Privacy Policy' link on homepage. Checking homepage text instead...", "yellow"))
                return soup.get_text().lower()

            # 2. Follow the link
            full_privacy_url = urljoin(url, privacy_link)
            print(f"[*] Found Policy Link: {full_privacy_url}")
            
            policy_response = requests.get(full_privacy_url, headers=headers, timeout=10)
            return policy_response.text.lower()

        except Exception as e:
            print(colored(f"[!] Connection Error: {e}", "red"))
            return None

    def audit_site(self, url):
        """
        Main function to audit a site using AI reasoning.
        """
        print(f"\n--- STARTING INTELLIGENT AUDIT FOR: {url} ---")
        text = self.fetch_privacy_policy(url)
        
        if not text:
            return {"status": "ERROR", "errors": ["Failed to fetch privacy policy text."]}

        if not self.api_key:
            print(colored("[!] AI Key missing. Falling back to keyword scan...", "yellow"))
            # Simple fallback check for keyword detection
            failed = []
            if "gdpr" not in text: failed.append("Likely missing GDPR mentions")
            if "delete" not in text and "erasure" not in text: failed.append("Likely missing deletion rights")
            return {"status": "VULNERABLE" if failed else "SECURE", "errors": failed}

        # AI REASONING BLOCK
        print(colored("[*] Sending content to AI Auditor (LLM)...", "cyan"))
        prompt = f"""
        Act as a Senior Data Privacy Auditor. Analyze the following Privacy Policy text from {url}.
        Check for compliance with GDPR (Art. 13, 17), CCPA, and general AI Governance.
        
        TEXT:
        {text[:15000]} # Limit text for token efficiency
        
        Return exactly in this JSON format:
        {{
            "status": "SECURE" or "VULNERABLE",
            "findings": ["List of specific missing clauses or legal gaps"],
            "reasoning": "Brief legal explanation of why it passed or failed"
        }}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            # Use regex to find JSON in case the model adds chatter
            import json
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                result = json.loads(match.group())
                return {
                    "status": result.get("status", "ERROR"),
                    "errors": result.get("findings", []),
                    "reasoning": result.get("reasoning", "")
                }
            print(colored(f"[!] AI Format Error. Raw Response: {response.text[:100]}", "red"))
            return {"status": "ERROR", "errors": ["AI response format error"]}
        except Exception as e:
            print(colored(f"[!] AI Audit Exception: {str(e)}", "red"))
            return {"status": "ERROR", "errors": [f"AI Audit Failed: {str(e)}"]}

if __name__ == "__main__":
    scanner = GDPRScanner()
    
    # Test with a known target (You can change this)
    target = input("Enter website URL to scan (e.g., https://example.com): ")
    scanner.audit_site(target)
