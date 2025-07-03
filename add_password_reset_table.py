#!/usr/bin/env python3
"""
Add Password Reset Token Table to Database
Run this script to add the password reset functionality to your existing database.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    # Import the app and database
    from water_tracker.app import app, db, PasswordResetToken
    
    def add_password_reset_table():
        """Add the password reset token table to the database"""
        
        with app.app_context():
            print("Adding password reset token table...")
            
            try:
                # Create the password reset token table
                db.create_all()
                print("✅ Password reset token table created successfully!")
                
                # Verify the table was created
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                
                if 'password_reset_tokens' in tables:
                    print("✅ Table 'password_reset_tokens' confirmed in database")
                    
                    # Show table structure
                    columns = inspector.get_columns('password_reset_tokens')
                    print("\n📋 Table structure:")
                    for column in columns:
                        print(f"   - {column['name']}: {column['type']}")
                else:
                    print("❌ Table 'password_reset_tokens' not found in database")
                    return False
                
                return True
                
            except Exception as e:
                print(f"❌ Error creating password reset table: {e}")
                return False
    
    if __name__ == '__main__':
        print("🔐 Password Reset Table Setup")
        print("=" * 40)
        
        success = add_password_reset_table()
        
        if success:
            print("\n🎉 Password reset functionality is now ready!")
            print("\nNext steps:")
            print("1. Configure email settings in your environment variables:")
            print("   - MAIL_SERVER (default: smtp.gmail.com)")
            print("   - MAIL_PORT (default: 587)")
            print("   - MAIL_USERNAME (your email)")
            print("   - MAIL_PASSWORD (your email password or app password)")
            print("   - MAIL_DEFAULT_SENDER (sender email)")
            print("\n2. For Gmail, you may need to:")
            print("   - Enable 2-factor authentication")
            print("   - Generate an app-specific password")
            print("   - Use the app password instead of your regular password")
            print("\n3. Test the password reset functionality:")
            print("   - Go to /forgot-password")
            print("   - Enter a valid email address")
            print("   - Check your email for the reset link")
        else:
            print("\n❌ Setup failed. Please check the error messages above.")
            sys.exit(1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
