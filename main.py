import time
from termcolor import colored
from scanner import GDPRScanner
from lead_finder import LeadFinder
from auto_emailer import AutoEmailer

def main():
    print(colored("\n=================================================", "cyan", attrs=['bold']))
    print(colored("   AI COMPLIANCE AUDITOR - BUSINESS ENGINE v1.0", "cyan", attrs=['bold']))
    print(colored("=================================================\n", "cyan", attrs=['bold']))

    # 1. Setup
    target_domain = input("Enter target domain (e.g. stripe.com): ").strip()
    if not target_domain:
        print("Invalid domain.")
        return

    # User Credentials (In a real app, load these from a config file)
    print(colored("\n[1] SETUP CONFIGURATION", "yellow"))
    hunter_key = input("Enter Hunter.io Key (Press Enter for Free Mode): ").strip()
    
    sender_email = ""
    sender_pass = ""
    run_email_mode = input("Do you want to send REAL emails? (y/n): ").lower()
    if run_email_mode == 'y':
        sender_email = input("Enter YOUR Gmail: ").strip()
        sender_pass = input("Enter YOUR App Password: ").strip()

    # 2. The Scan
    print(colored("\n[2] RUNNING VULNERABILITY SCAN...", "yellow"))
    scanner = GDPRScanner()
    scan_result = scanner.audit_site(f"https://{target_domain}")

    if scan_result["status"] == "SECURE":
        print(colored(f"\n[!] Target {target_domain} is ALREADY COMPLIANT. Skipping.", "green"))
        return

    # 3. value Creation (The Audit Report)
    print(colored(f"\n[3] GENERATING AUDIT REPORT FOR {target_domain}...", "yellow"))
    report_filename = f"{target_domain}_gdpr_audit.txt"
    with open(report_filename, "w") as f:
        f.write(f"GDPR COMPLIANCE AUDIT REPORT: {target_domain}\n")
        f.write("=================================================\n\n")
        f.write("STATUS: FAILED (High Risk of Fines)\n\n")
        f.write("CRITICAL ISSUES FOUND:\n")
        for error in scan_result["errors"]:
            f.write(f"[X] {error}\n")
        f.write("\nRECOMMENDED ACTION:\n")
        f.write("Immediate implementation of Article 13 & 17 clauses required.\n")
    
    print(colored(f"[+] Report generated: {report_filename}", "green"))
    print("(This report is the 'Value' you give them. It proves you are not a scam.)")

    # 4. Find the Lead
    print(colored("\n[4] FINDING CEO / CONTACT...", "yellow"))
    finder = LeadFinder(hunter_key)
    leads = finder.find_emails(target_domain)

    if not leads:
        print(colored("[-] No emails found. Saving report for manual outreach.", "red"))
        return

    print(colored(f"[+] Found {len(leads)} potential contacts.", "green"))
    
    # 5. Send the Pitch
    if run_email_mode == 'y':
        print(colored("\n[5] SENDING SALES PITCH...", "yellow"))
        emailer = AutoEmailer("smtp.gmail.com", 587, sender_email, sender_pass)
        
        # Pick the best lead (first one)
        target_lead = leads[0]
        print(f"Targeting: {target_lead['name']} ({target_lead['email']})")
        
        confirm = input("Confirm send? (y/n): ").lower()
        if confirm == 'y':
            emailer.send_pitch(target_lead['email'], target_lead['name'], target_domain)
        else:
            print("Email skipped.")
    else:
        print(colored("\n[INFO] Email sending skipped (Demo Mode).", "blue"))
        print(f"You would have emailed: {leads[0]['email']}")

    print(colored("\n=================================================", "cyan"))
    print(colored("   PROCESS COMPLETE. MONEY WAITING.", "cyan"))
    print(colored("=================================================", "cyan"))

if __name__ == "__main__":
    main()
