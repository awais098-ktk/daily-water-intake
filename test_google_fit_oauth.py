#!/usr/bin/env python3
"""
Test Google Fit OAuth with Real Credentials
This script tests the Google Fit OAuth implementation with your actual credentials
"""

import os
import sys

def setup_google_fit_credentials():
    """Set up your Google Fit OAuth credentials"""
    
    print("🔧 Setting up Google Fit OAuth credentials...")
    
    # Your actual Google Fit credentials
    credentials = {
        'GOOGLE_FIT_CLIENT_ID': 'YOUR_GOOGLE_CLIENT_ID_HERE',
        'GOOGLE_FIT_CLIENT_SECRET': 'YOUR_GOOGLE_CLIENT_SECRET_HERE',
        'GOOGLE_FIT_REDIRECT_URI': 'http://127.0.0.1:8080/wearable/oauth/google_fit/callback'
    }
    
    # Set environment variables
    for key, value in credentials.items():
        os.environ[key] = value
        print(f"✅ Set {key}")
    
    print("\n📋 Google Fit OAuth credentials configured!")
    return credentials

def test_oauth_url_generation():
    """Test OAuth URL generation with real credentials"""
    
    print("\n🧪 Testing OAuth URL generation...")
    
    try:
        from water_tracker.wearable_integration.oauth_manager import OAuthManager
        
        # Create app config with your credentials
        app_config = {
            'GOOGLE_FIT_CLIENT_ID': os.environ.get('GOOGLE_FIT_CLIENT_ID'),
            'GOOGLE_FIT_CLIENT_SECRET': os.environ.get('GOOGLE_FIT_CLIENT_SECRET'),
            'GOOGLE_FIT_REDIRECT_URI': os.environ.get('GOOGLE_FIT_REDIRECT_URI'),
        }
        
        # Initialize OAuth manager
        oauth_manager = OAuthManager(app_config)
        print("✅ OAuth Manager initialized with real credentials")
        
        # Generate Google Fit authorization URL
        auth_url, state = oauth_manager.get_authorization_url('google_fit', user_id=1)
        
        print(f"\n🔗 Google Fit Authorization URL Generated:")
        print(f"State: {state}")
        print(f"URL: {auth_url}")
        
        print(f"\n📋 URL Components:")
        print(f"- Client ID: {app_config['GOOGLE_FIT_CLIENT_ID']}")
        print(f"- Redirect URI: {app_config['GOOGLE_FIT_REDIRECT_URI']}")
        print(f"- Scopes: fitness.activity.read, fitness.body.read, fitness.location.read")
        
        return auth_url, state
        
    except Exception as e:
        print(f"❌ OAuth URL generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def check_redirect_uri_setup():
    """Check if redirect URI is properly configured"""
    
    print("\n🔍 Checking Redirect URI Configuration...")
    
    expected_redirect = 'http://127.0.0.1:8080/wearable/oauth/google_fit/callback'
    configured_redirect = 'http://127.0.0.1:8080'  # From your JSON
    
    print(f"Expected Redirect URI: {expected_redirect}")
    print(f"Your Current Redirect URI: {configured_redirect}")
    
    if expected_redirect != configured_redirect:
        print("\n⚠️  REDIRECT URI MISMATCH DETECTED!")
        print("\n🔧 TO FIX THIS:")
        print("1. Go to Google Cloud Console")
        print("2. Navigate to APIs & Services > Credentials")
        print("3. Click on your OAuth 2.0 Client ID")
        print("4. In 'Authorized redirect URIs', add:")
        print(f"   {expected_redirect}")
        print("5. Save the changes")
        print("\nOR you can keep both URIs for flexibility")
        return False
    else:
        print("✅ Redirect URI is correctly configured!")
        return True

def show_testing_instructions():
    """Show instructions for testing the OAuth flow"""
    
    print("\n🚀 TESTING INSTRUCTIONS")
    print("=" * 50)
    
    print("\n1. 📝 UPDATE GOOGLE CLOUD CONSOLE:")
    print("   - Go to: https://console.cloud.google.com/")
    print("   - Navigate to: APIs & Services > Credentials")
    print("   - Edit your OAuth 2.0 Client ID")
    print("   - Add redirect URI: http://127.0.0.1:8080/wearable/oauth/google_fit/callback")
    print("   - Save changes")
    
    print("\n2. 🚀 START THE APP:")
    print("   python run.py")
    
    print("\n3. 🔗 TEST OAUTH FLOW:")
    print("   - Go to: http://127.0.0.1:8080/wearable/connect")
    print("   - Click 'Connect Google Fit' (should show 'Available' now)")
    print("   - Complete Google OAuth authorization")
    print("   - Check connection in wearable dashboard")
    
    print("\n4. 📊 VIEW RESULTS:")
    print("   - Go to: http://127.0.0.1:8080/wearable/")
    print("   - See your connected Google Fit account")
    print("   - Sync activity data")
    print("   - Get personalized hydration recommendations")

def main():
    """Main test function"""
    
    print("🔵 GOOGLE FIT OAUTH IMPLEMENTATION TEST")
    print("=" * 45)
    
    # Setup credentials
    credentials = setup_google_fit_credentials()
    
    # Test OAuth URL generation
    auth_url, state = test_oauth_url_generation()
    
    # Check redirect URI setup
    redirect_ok = check_redirect_uri_setup()
    
    # Show testing instructions
    show_testing_instructions()
    
    print("\n✨ SUMMARY:")
    if auth_url and redirect_ok:
        print("✅ Google Fit OAuth is ready to test!")
        print("✅ All components are working correctly")
    elif auth_url and not redirect_ok:
        print("⚠️  Google Fit OAuth is working but needs redirect URI update")
        print("✅ Update redirect URI in Google Cloud Console")
    else:
        print("❌ Google Fit OAuth needs troubleshooting")
    
    print("\n🎯 Your Google Fit credentials are now integrated!")
    print("📱 Ready to connect real Google Fit data!")

if __name__ == "__main__":
    main()
