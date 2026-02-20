import requests
from termcolor import colored

import requests
from termcolor import colored
import re
from bs4 import BeautifulSoup

class LeadFinder:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.hunter_url = "https://api.hunter.io/v2/domain-search"

    def find_emails(self, domain):
        """
        Try Hunter.io first. If no key, fail over to Free Scraping.
        """
        if self.api_key:
            return self.find_with_hunter(domain)
        else:
            print(colored("[*] No API Key provided. Switching to FREE SCRAPER Mode...", "yellow"))
            return self.find_with_scraper(domain)

    def find_with_hunter(self, domain):
        print(f"[*] Hunting emails for: {domain} using Hunter.io...")
        params = {
            "domain": domain,
            "api_key": self.api_key,
            "type": "personal",
            "limit": 5
        }
        try:
            response = requests.get(self.hunter_url, params=params)
            if response.status_code == 200:
                data = response.json()
                emails = data.get("data", {}).get("emails", [])
                results = []
                for email in emails:
                    results.append({
                        "name": f"{email.get('first_name', '')} {email.get('last_name', '')}",
                        "email": email.get('value'),
                        "role": email.get('position', 'Unknown')
                    })
                return results
            else:
                print(colored(f"[!] Hunter Error: {response.status_code}. Switching to Scraper...", "red"))
                return self.find_with_scraper(domain)
        except Exception as e:
            return self.find_with_scraper(domain)

    def find_with_scraper(self, domain):
        """
        FREE METHOD: Scans the homepage AND common contact pages for emails.
        """
        paths = ["", "/contact", "/contact-us", "/about", "/legal"]
        found_emails = set()
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        for path in paths:
            url = f"https://{domain}{path}"
            print(f"[*] Scraping {url}...")
            
            try:
                response = requests.get(url, headers=headers, timeout=8)
                if response.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')

                # 1. Search for 'mailto:' links
                for a in soup.find_all('a', href=True):
                    if 'mailto:' in a['href']:
                        email = a['href'].replace('mailto:', '').split('?')[0].strip()
                        if "@" in email:
                            found_emails.add(email)

                # 2. Regex Search in text (More robust regex)
                text = soup.get_text()
                regex_emails = re.findall(r'[a-zA-Z0-9.\-_+]+@[a-zA-Z0-9.\-_]+\.[a-zA-Z]{2,}', text)
                
                for email in regex_emails:
                    # Filter out junk common in scrapers
                    email = email.lower().strip()
                    junk_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']
                    if any(email.endswith(ext) for ext in junk_extensions):
                        continue
                    
                    # Only keep emails that likely belong to the domain or are common contact aliases
                    if domain.split('.')[0] in email or any(x in email for x in ['info@', 'contact@', 'hello@', 'support@', 'admin@']):
                        found_emails.add(email)

            except Exception:
                continue

        if found_emails:
            print(colored(f"[+] Found {len(found_emails)} emails for {domain}!", "green"))
            results = []
            for email in found_emails:
                results.append({"name": "Decision Maker", "email": email, "role": "Stakeholder"})
            return list(results)
        else:
            print(colored(f"[-] No leads found for {domain}.", "red"))
            return []

if __name__ == "__main__":
    print("\n--- LEAD FINDER (Hybrid Mode) ---")
    print("Tip: Press ENTER without a key to use the Free Scraper.")
    
    key = input("Enter Hunter.io Key (or press Enter for Free Mode): ").strip()
    target = input("Enter domain (e.g. stripe.com): ").strip()
    
    finder = LeadFinder(key if key else None)
    results = finder.find_emails(target)
    print(f"\n[Final Results] {results}")
