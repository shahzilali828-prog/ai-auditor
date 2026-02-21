import requests
from bs4 import BeautifulSoup
import re
def colored(text, color=None, on_color=None, attrs=None):
    return text
from urllib.parse import urljoin

class GDPRScanner:
    def __init__(self):
        # The "Kill List" of keywords. If these are missing, the site is ILLEGAL.
        self.compliance_checks = {
            "gdpr_contact": {
                "keywords": ["dpo@", "privacy@", "data protection officer", "contact us", "data protection lead", "privacy team"],
                "score": 1,
                "error_msg": "CRITICAL: No Data Protection Contact found (GDPR Art. 13)"
            },
            "erasure": {
                "keywords": ["right to erasure", "delete your data", "request deletion", "remove your information", "right to be forgotten", "deletion of personal data", "delete account"],
                "score": 1,
                "error_msg": "CRITICAL: No 'Right to Erasure' clause found (GDPR Art. 17)"
            },
            "ccpa_sells": {
                "keywords": ["do not sell my", "opt-out", "selling your personal information", "notice of right to opt-out", "don't sell", "personal information sales"],
                "score": 1,
                "error_msg": "CRITICAL: Missing 'Do Not Sell' link (CCPA Requirement)"
            }
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
        Main function to audit a site.
        """
        print(f"\n--- STARTING AUDIT FOR: {url} ---")
        text = self.fetch_privacy_policy(url)
        
        if not text:
            return {"status": "ERROR", "email_needed": False}

        failed_checks = []
        
        for check_name, rules in self.compliance_checks.items():
            found = False
            for keyword in rules['keywords']:
                if keyword in text:
                    found = True
                    break
            
            if not found:
                print(colored(f"[-] FAILED: {rules['error_msg']}", "red"))
                failed_checks.append(rules['error_msg'])
            else:
                print(colored(f"[+] PASSED: Found keyword for {check_name}", "green"))

        if len(failed_checks) > 0:
            print(colored(f"\n[!!!] VULNERABLE: {len(failed_checks)} Critical Errors Found.", "red", attrs=['bold']))
            return {"status": "VULNERABLE", "errors": failed_checks}
        else:
            print(colored("\n[OK] SECURE: No Machine-Detectable Errors.", "green", attrs=['bold']))
            return {"status": "SECURE", "errors": []}

if __name__ == "__main__":
    scanner = GDPRScanner()
    
    # Test with a known target (You can change this)
    target = input("Enter website URL to scan (e.g., https://example.com): ")
    scanner.audit_site(target)
