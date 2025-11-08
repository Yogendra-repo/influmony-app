"""
Test Email Configuration
------------------------
This script helps you verify your SMTP email settings before using the app.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

def test_email_config():
    """Test SMTP email configuration"""
    
    print("🔧 Testing Email Configuration...")
    print(f"SMTP Server: {SMTP_SERVER}")
    print(f"SMTP Port: {SMTP_PORT}")
    print(f"Email: {SMTP_EMAIL}")
    print(f"Password: {'*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else '(not set)'}")
    print()
    
    # Check if credentials are set
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("❌ ERROR: SMTP_EMAIL or SMTP_PASSWORD not configured in .env file")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Add your email credentials")
        print("3. For Gmail, use App Password (see EMAIL_SETUP.md)")
        return False
    
    # Try to connect and send a test email
    try:
        print("📤 Attempting to send test email...")
        
        # Create message
        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_EMAIL
        msg["To"] = SMTP_EMAIL  # Send to yourself
        msg["Subject"] = "🧪 Influmony Email Test"
        
        # Email body
        text = """
        This is a test email from Influmony.
        
        If you received this, your email configuration is working correctly!
        
        You can now send outreach emails to influencers.
        """
        
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2563EB;">✅ Email Configuration Success!</h2>
            <p>This is a test email from <strong>Influmony</strong>.</p>
            <p>If you received this, your email configuration is working correctly!</p>
            <p>You can now send outreach emails to influencers.</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
              Sent from: {SMTP_EMAIL}<br>
              SMTP Server: {SMTP_SERVER}:{SMTP_PORT}
            </p>
          </body>
        </html>
        """
        
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)
        
        # Connect and send
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            print("🔌 Connecting to SMTP server...")
            server.starttls()
            
            print("🔐 Logging in...")
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            
            print("📧 Sending test email...")
            server.send_message(msg)
        
        print()
        print("=" * 60)
        print("✅ SUCCESS! Email sent successfully!")
        print("=" * 60)
        print(f"\n📬 Check your inbox at: {SMTP_EMAIL}")
        print("\n✨ Your email configuration is ready to use!")
        print("You can now send emails to influencers from the Influmony app.")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print()
        print("=" * 60)
        print("❌ AUTHENTICATION FAILED")
        print("=" * 60)
        print("\nPossible solutions:")
        print("1. For Gmail: Use App Password, not regular password")
        print("   - Enable 2FA: https://myaccount.google.com/security")
        print("   - Create App Password: https://myaccount.google.com/apppasswords")
        print("2. For other providers: Check if you need to enable 'Less secure apps'")
        print("3. Verify your email and password are correct in .env")
        return False
        
    except smtplib.SMTPConnectError:
        print()
        print("=" * 60)
        print("❌ CONNECTION FAILED")
        print("=" * 60)
        print("\nPossible solutions:")
        print("1. Check your internet connection")
        print("2. Verify SMTP_SERVER and SMTP_PORT in .env")
        print("3. Check firewall/antivirus settings")
        print(f"4. Try port 465 instead of {SMTP_PORT}")
        return False
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR")
        print("=" * 60)
        print(f"\nError: {str(e)}")
        print("\nPlease check:")
        print("1. Your .env file configuration")
        print("2. Your email provider's SMTP settings")
        print("3. The EMAIL_SETUP.md guide for detailed instructions")
        return False

if __name__ == "__main__":
    print()
    print("=" * 60)
    print("  INFLUMONY EMAIL CONFIGURATION TEST")
    print("=" * 60)
    print()
    
    success = test_email_config()
    
    print()
    if not success:
        print("💡 TIP: See EMAIL_SETUP.md for detailed setup instructions")
    print()
