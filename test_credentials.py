import smtplib
from termcolor import colored

def test_login():
    print(colored("\n--- SMTP LOGIN TEST ---", "cyan"))
    email = input("Enter your Gmail: ").strip()
    password_input = input("Enter your 16-character App Password (don't worry about spaces): ").strip()
    password = password_input.replace(" ", "")

    print(f"[*] Checking password length... {len(password)} characters found.")
    if len(password) != 16:
        print(colored(f"[!] Warning: App Passwords are usually exactly 16 characters. Yours is {len(password)}.", "yellow"))

    try:
        print(colored(f"[*] Connecting to Google SMTP (smtp.gmail.com:587)...", "yellow"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.set_debuglevel(1) # This will show us the RAW communication with Google
        server.starttls()
        
        print(colored(f"[*] Attempting login for {email}...", "yellow"))
        server.login(email, password)
        print(colored("\n[SUCCESS] Your credentials are correct! Google accepted the login.", "green", attrs=['bold']))
        server.quit()
    except smtplib.SMTPAuthenticationError as e:
        print(colored(f"\n[FAILED] Google rejected the login.", "red", attrs=['bold']))
        print(f"Server Response: {e}")
        print("\nTOP FIXES:")
        print("1. Are you sure 2-Step Verification is ENABLED on your account?")
        print("2. Did you generate an 'APP PASSWORD' specifically? (Not your normal login password)")
        print("3. Check for typos in your email address.")
    except Exception as e:
        print(colored(f"\n[FAILED] An unexpected error occurred.", "red", attrs=['bold']))
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
