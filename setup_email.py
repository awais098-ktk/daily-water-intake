#!/usr/bin/env python3
"""
Email Configuration Setup for Water Intake Tracker
"""

import os

def setup_gmail_config():
    """Setup Gmail configuration"""
    print("🔧 Gmail Email Configuration Setup")
    print("=" * 50)
    
    print("\n📋 To use Gmail for password reset emails, you need:")
    print("1. A Gmail account")
    print("2. Enable 2-Factor Authentication on your Gmail account")
    print("3. Generate an App Password (not your regular Gmail password)")
    print("\n🔗 How to get Gmail App Password:")
    print("   1. Go to https://myaccount.google.com/security")
    print("   2. Enable 2-Step Verification if not already enabled")
    print("   3. Go to 'App passwords' section")
    print("   4. Generate a new app password for 'Mail'")
    print("   5. Use this 16-character password (not your regular password)")
    
    print("\n" + "=" * 50)
    email = input("Enter your Gmail address: ").strip()
    
    if not email or '@gmail.com' not in email:
        print("❌ Please enter a valid Gmail address")
        return False
    
    app_password = input("Enter your Gmail App Password (16 characters): ").strip()
    
    if not app_password or len(app_password) != 16:
        print("❌ Gmail App Password should be 16 characters long")
        print("   Make sure you're using the App Password, not your regular password")
        return False
    
    # Create environment variables file
    env_content = f"""# Email Configuration for Water Intake Tracker
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME={email}
MAIL_PASSWORD={app_password}
MAIL_DEFAULT_SENDER={email}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ Email configuration saved to .env file")
    print(f"   Email: {email}")
    print(f"   Server: smtp.gmail.com:587")
    
    return True

def setup_alternative_config():
    """Setup alternative email service"""
    print("🔧 Alternative Email Service Configuration")
    print("=" * 50)
    
    print("\nSupported email services:")
    print("1. Gmail (smtp.gmail.com:587)")
    print("2. Outlook/Hotmail (smtp-mail.outlook.com:587)")
    print("3. Yahoo (smtp.mail.yahoo.com:587)")
    print("4. Custom SMTP server")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == '1':
        return setup_gmail_config()
    elif choice == '2':
        server = 'smtp-mail.outlook.com'
        port = 587
    elif choice == '3':
        server = 'smtp.mail.yahoo.com'
        port = 587
    elif choice == '4':
        server = input("Enter SMTP server: ").strip()
        port = int(input("Enter SMTP port (usually 587): ").strip() or 587)
    else:
        print("❌ Invalid choice")
        return False
    
    email = input("Enter your email address: ").strip()
    password = input("Enter your email password: ").strip()
    
    if not email or not password:
        print("❌ Email and password are required")
        return False
    
    # Create environment variables file
    env_content = f"""# Email Configuration for Water Intake Tracker
MAIL_SERVER={server}
MAIL_PORT={port}
MAIL_USE_TLS=true
MAIL_USERNAME={email}
MAIL_PASSWORD={password}
MAIL_DEFAULT_SENDER={email}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ Email configuration saved to .env file")
    print(f"   Email: {email}")
    print(f"   Server: {server}:{port}")
    
    return True

def test_email_config():
    """Test email configuration"""
    print("\n🧪 Testing Email Configuration...")
    
    if not os.path.exists('.env'):
        print("❌ No .env file found. Please run setup first.")
        return False
    
    # Load environment variables from .env file
    with open('.env', 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
    
    try:
        from flask_mail import Mail, Message
        from flask import Flask
        
        # Create test Flask app
        app = Flask(__name__)
        app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
        app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
        app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
        
        mail = Mail(app)
        
        with app.app_context():
            # Create test message
            msg = Message(
                subject='Test Email - Water Intake Tracker',
                recipients=[os.environ.get('MAIL_USERNAME')],
                body='This is a test email to verify your email configuration is working correctly.'
            )
            
            mail.send(msg)
            print("✅ Test email sent successfully!")
            print(f"   Check your inbox: {os.environ.get('MAIL_USERNAME')}")
            return True
            
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        print("\n🔍 Common issues:")
        print("   - Wrong email/password combination")
        print("   - Need to use App Password for Gmail (not regular password)")
        print("   - 2-Factor Authentication not enabled for Gmail")
        print("   - SMTP server/port incorrect")
        return False

def main():
    """Main function"""
    print("📧 Water Intake Tracker - Email Setup")
    print("=" * 50)
    
    if os.path.exists('.env'):
        print("⚠️  Email configuration file (.env) already exists")
        choice = input("Do you want to (1) Reconfigure or (2) Test existing config? [1/2]: ").strip()
        
        if choice == '2':
            test_email_config()
            return
        elif choice != '1':
            print("❌ Invalid choice")
            return
    
    print("\nChoose email service:")
    print("1. Gmail (Recommended)")
    print("2. Other email service")
    
    choice = input("Select option [1/2]: ").strip()
    
    if choice == '1':
        success = setup_gmail_config()
    elif choice == '2':
        success = setup_alternative_config()
    else:
        print("❌ Invalid choice")
        return
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 Email configuration complete!")
        print("\n📋 Next steps:")
        print("1. Restart your Flask application")
        print("2. Test the password reset functionality")
        print("3. Go to /forgot-password and enter a valid email")
        
        test_choice = input("\nWould you like to test the email configuration now? [y/n]: ").strip().lower()
        if test_choice == 'y':
            test_email_config()

if __name__ == '__main__':
    main()
