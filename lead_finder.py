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
        FREE METHOD: Scans the homepage for mailto: links and regex matches.
        """
        url = f"https://{domain}"
        print(f"[*] Scraping {url} for emails (Free Mode)...")
        found_emails = set()
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 1. Search for 'mailto:' links
            for a in soup.find_all('a', href=True):
                if 'mailto:' in a['href']:
                    email = a['href'].replace('mailto:', '').split('?')[0]
                    found_emails.add(email)

            # 2. Regex Search in text
            text = soup.get_text()
            # Simple email regex
            regex_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
            for email in regex_emails:
                # Filter out junk (like image@2x.png)
                if domain in email: # Only keep emails from the target domain
                    found_emails.add(email)

            if found_emails:
                print(colored(f"[+] Found {len(found_emails)} emails on the page!", "green"))
                results = []
                for email in found_emails:
                    print(f"    - {email}")
                    results.append({"name": "Contact", "email": email, "role": "Website Contact"})
                return list(results)
            else:
                print(colored("[-] No emails found on homepage.", "red"))
                return []

        except Exception as e:
            print(colored(f"[!] Scrape Error: {e}", "red"))
            return []

if __name__ == "__main__":
    print("\n--- LEAD FINDER (Hybrid Mode) ---")
    print("Tip: Press ENTER without a key to use the Free Scraper.")
    
    key = input("Enter Hunter.io Key (or press Enter for Free Mode): ").strip()
    target = input("Enter domain (e.g. stripe.com): ").strip()
    
    finder = LeadFinder(key if key else None)
    results = finder.find_emails(target)
    print(f"\n[Final Results] {results}")
