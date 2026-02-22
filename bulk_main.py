import time
import csv
import os
from termcolor import colored
from scanner import GDPRScanner
from lead_finder import LeadFinder
from auto_emailer import AutoEmailer
from niche_finder import NicheFinder

# Configuration
HISTORY_FILE = "outreach_history.csv"
EMAIL_DELAY = 60 # Seconds between emails to avoid spam filters

def log_to_history(domain, status, emails_found, email_sent):
    file_exists = os.path.isfile(HISTORY_FILE)
    with open(HISTORY_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Domain", "Status", "Emails Found", "Email Sent"])
        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), domain, status, emails_found, email_sent])

def is_already_contacted(domain):
    if not os.path.isfile(HISTORY_FILE):
        return False
    with open(HISTORY_FILE, mode='r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[1] == domain:
                return True
    return False

def main():
    print(colored("\n=================================================", "cyan", attrs=['bold']))
    print(colored("   AI AUDITOR - BULK AUTOMATION ENGINE v1.0", "cyan", attrs=['bold']))
    print(colored("=================================================\n", "cyan", attrs=['bold']))

    # 1. Setup
    print(colored("[1] Target Selection", "yellow"))
    print("1. Discovery Mode (Search a Niche)")
    print("2. Import Mode (Load from domains.txt)")
    choice = input("Select mode (1/2): ").strip()
    
    domains = []
    if choice == '1':
        niche = input("Enter target niche (e.g. 'lawyers in london'): ").strip()
        limit = int(input("How many businesses to target? (e.g. 10): ") or 10)
        finder = NicheFinder()
        domains = finder.find_domains(niche, num_results=limit)
    else:
        file_path = "domains.txt"
        if not os.path.isfile(file_path):
            print(colored(f"[-] {file_path} not found. Create it with one domain per line.", "red"))
            return
        with open(file_path, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
        print(colored(f"[+] Loaded {len(domains)} domains from {file_path}", "green"))

    if not domains:
        print(colored("[-] No domains found to process.", "red"))
        return

    run_email_mode = input("\nDo you want to send REAL emails? (y/n): ").lower()
    
    # 3. Initialize Components
    scanner = GDPRScanner()
    lead_finder = LeadFinder() # Using Free Scraper by default
    emailer = None
    
    if run_email_mode == 'y':
        sender_email = input("Enter your sender email (Gmail recommended): ").strip()
        sender_pass = input("Enter your App Password (NOT your login password): ").strip()
        emailer = AutoEmailer("smtp.gmail.com", 587, sender_email, sender_pass)

    print(colored(f"\n[*] Starting Bulk Run on {len(domains)} targets...", "yellow"))
    
    for i, domain in enumerate(domains):
        print(colored(f"\n[{i+1}/{len(domains)}] Processing: {domain}", "blue", attrs=['bold']))
        
        if is_already_contacted(domain):
            print(colored(f"[-] Already contacted {domain}. Skipping.", "yellow"))
            continue

        # Step A: Scan
        scan_result = scanner.audit_site(f"https://{domain}")
        if scan_result["status"] == "SECURE":
            log_to_history(domain, "SECURE", 0, False)
            continue
        
        if scan_result["status"] == "ERROR":
            print(colored(f"[!] Could not scan {domain}.", "red"))
            continue

        # Step B: Find Leads
        leads = lead_finder.find_emails(domain)
        if not leads:
            log_to_history(domain, "VULNERABLE (No Leads)", 0, False)
            continue
        
        # Step C: Email
        email_sent = False
        if run_email_mode == 'y' and emailer:
            target = leads[0] # Pitch the first valid lead
            print(f"[*] Pitching: {target['email']}")
            email_sent = emailer.send_pitch(target['email'], target['name'] or "Business Owner", domain)
            
            if email_sent:
                print(colored(f"[+] Pitch successful!", "green"))
                # Delay to prevent spam flags
                if i < len(domains) - 1:
                    print(f"[*] Sleeping for {EMAIL_DELAY}s...")
                    time.sleep(EMAIL_DELAY)
        else:
            print(colored(f"[DEMO] Would have emailed: {leads[0]['email']}", "white"))

        # Step D: Log
        log_to_history(domain, "VULNERABLE", len(leads), email_sent)

    print(colored("\n=================================================", "cyan"))
    print(colored("   BULK RUN COMPLETE. CHECK THE LOGS.", "cyan"))
    print(colored("=================================================", "cyan"))

if __name__ == "__main__":
    main()
