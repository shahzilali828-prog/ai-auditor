import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from termcolor import colored
import time

class AutoEmailer:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        self.server = smtp_server
        self.port = smtp_port
        self.email = sender_email
        self.password = sender_password

    def send_pitch(self, recipient_email, recipient_name, company_name):
        """
        Sends the Cold Email Pitch to the CEO.
        """
        subject = f"Legal vulnerability on {company_name} (GDPR)"
        
        # The "Million Dollar Script"
        body = f"""
        Hi,

        I’m an automated compliance auditor. I just scanned your website {company_name}.

        CRITICAL ERROR: You are missing the 'Right to Erasure' and 'Do Not Sell' clauses (GDPR/CCPA).
        
        This exposes you to significant legal risk from international visitors.

        I have generated the correct legal text for you to fix this immediately:
        
        https://ai-auditor-jwjp8ql8ifdk7i92j52pdt.streamlit.app

        Best,
        AI Compliance Auditor
        """

        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            print(f"[*] Connecting to SMTP Server ({self.server})...")
            server = smtplib.SMTP(self.server, self.port)
            server.starttls()
            server.login(self.email, self.password)
            
            print(f"[*] Sending email to {recipient_email}...")
            server.sendmail(self.email, recipient_email, msg.as_string())
            server.quit()
            
            print(colored(f"[+] Email Sent to {recipient_name}!", "green"))
            return True

        except Exception as e:
            print(colored(f"[!] Email Failed: {e}", "red"))
            return False

if __name__ == "__main__":
    print("\n--- AUTO EMAILER (SMTP) ---")
    print("Warning: Use a 'Burner' Gmail or a Professional Domain (G-Suite) to avoid spam filters.")
    
    # User Inputs
    my_email = input("Enter YOUR Gmail Address: ").strip()
    my_pass = input("Enter YOUR Gmail App Password (Not login password): ").strip()
    
    if my_email and my_pass:
        # Gmail SMTP Settings
        emailer = AutoEmailer("smtp.gmail.com", 587, my_email, my_pass)
        
        # Test Target
        target_email = input("Enter TEST Recipient Email: ").strip()
        target_name = input("Enter Recipient Name: ").strip()
        
        emailer.send_pitch(target_email, target_name, "TestCompany.com")
    else:
        print("Credentials required to run.")
