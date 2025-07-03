#!/usr/bin/env python3
"""
Detailed OAuth Test - Check every step of the OAuth flow
"""

import requests
from requests.sessions import Session
import urllib.parse

def detailed_oauth_test():
    """Test OAuth flow in detail"""
    
    print("🔵 DETAILED OAUTH FLOW TEST")
    print("=" * 50)
    
    # Create session
    session = Session()
    
    # Step 1: Login
    print("\n1. 🔐 Logging in...")
    login_data = {'username': 'demo', 'password': 'demo123'}
    login_response = session.post('http://127.0.0.1:8080/login', data=login_data, allow_redirects=False)
    
    if login_response.status_code != 302:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    print("✅ Login successful")
    
    # Step 2: Test Google Fit connect endpoint
    print("\n2. 🚀 Testing Google Fit connect endpoint...")
    
    google_fit_response = session.get(
        'http://127.0.0.1:8080/wearable/connect/google_fit', 
        allow_redirects=False
    )
    
    print(f"Status Code: {google_fit_response.status_code}")
    print(f"Headers: {dict(google_fit_response.headers)}")
    
    if google_fit_response.status_code == 302:
        location = google_fit_response.headers.get('Location', '')
        print(f"✅ Redirecting to: {location}")
        
        # Parse the OAuth URL
        if 'accounts.google.com' in location:
            print("✅ Correctly redirecting to Google OAuth")
            
            # Parse URL parameters
            parsed_url = urllib.parse.urlparse(location)
            params = urllib.parse.parse_qs(parsed_url.query)
            
            print("\n📋 OAuth URL Parameters:")
            for key, value in params.items():
                print(f"   {key}: {value[0] if value else 'None'}")
            
            # Check redirect URI specifically
            redirect_uri = params.get('redirect_uri', [''])[0]
            if redirect_uri:
                decoded_redirect = urllib.parse.unquote(redirect_uri)
                print(f"\n🔗 Redirect URI: {decoded_redirect}")
                
                if decoded_redirect == 'http://127.0.0.1:8080/wearable/oauth/google_fit/callback':
                    print("✅ Redirect URI matches Google Cloud Console configuration")
                else:
                    print("❌ Redirect URI does NOT match Google Cloud Console configuration")
                    print("   Expected: http://127.0.0.1:8080/wearable/oauth/google_fit/callback")
                    print(f"   Got: {decoded_redirect}")
            
            # Test if we can access the OAuth URL
            print("\n3. 🌐 Testing OAuth URL accessibility...")
            try:
                oauth_response = requests.get(location, allow_redirects=False, timeout=10)
                print(f"OAuth URL Status: {oauth_response.status_code}")
                
                if oauth_response.status_code == 200:
                    print("✅ Google OAuth page is accessible")
                elif oauth_response.status_code == 302:
                    print("✅ Google OAuth redirects (normal behavior)")
                else:
                    print(f"⚠️ Unexpected OAuth response: {oauth_response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error accessing OAuth URL: {e}")
        
        else:
            print(f"❌ Not redirecting to Google OAuth: {location}")
    
    elif google_fit_response.status_code == 200:
        print("❌ Should redirect but returned 200")
        print("Response content:")
        print(google_fit_response.text[:500])
    
    else:
        print(f"❌ Unexpected status: {google_fit_response.status_code}")
        print("Response content:")
        print(google_fit_response.text[:500])

def show_troubleshooting_steps():
    """Show troubleshooting steps"""
    
    print("\n" + "=" * 50)
    print("🔧 TROUBLESHOOTING STEPS")
    print("=" * 50)
    
    print("\n1. ✅ GOOGLE CLOUD CONSOLE:")
    print("   - Make sure you clicked 'Save' after adding the redirect URI")
    print("   - Wait 5-10 minutes for changes to take effect")
    print("   - Redirect URI should be: http://127.0.0.1:8080/wearable/oauth/google_fit/callback")
    
    print("\n2. 🌐 BROWSER TEST:")
    print("   - Clear browser cache and cookies")
    print("   - Try in incognito/private mode")
    print("   - Check browser console for errors (F12)")
    
    print("\n3. 🔄 MANUAL STEPS:")
    print("   a. Login: http://127.0.0.1:8080/login (demo/demo123)")
    print("   b. Direct URL: http://127.0.0.1:8080/wearable/connect/google_fit")
    print("   c. Should redirect to Google OAuth page")
    
    print("\n4. 📱 COMMON ISSUES:")
    print("   - Google Cloud Console changes not saved")
    print("   - Browser blocking redirects")
    print("   - Popup blockers enabled")
    print("   - JavaScript disabled")
    
    print("\n5. 🆘 IF STILL NOT WORKING:")
    print("   - Try the OAuth URL directly in a new browser tab")
    print("   - Check if your Google account has 2FA enabled")
    print("   - Verify the Google Cloud project is active")

if __name__ == "__main__":
    detailed_oauth_test()
    show_troubleshooting_steps()
