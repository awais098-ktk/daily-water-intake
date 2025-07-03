#!/usr/bin/env python3
"""
Quick Login Test - Test the login and OAuth flow
"""

import requests
from requests.sessions import Session

def test_login_and_oauth():
    """Test login and then OAuth flow"""
    
    print("🔵 TESTING LOGIN AND OAUTH FLOW")
    print("=" * 40)
    
    # Create a session to maintain cookies
    session = Session()
    
    # Step 1: Get login page
    print("\n1. 🔍 Getting login page...")
    login_page = session.get('http://127.0.0.1:8080/login')
    
    if login_page.status_code == 200:
        print("✅ Login page accessible")
    else:
        print(f"❌ Login page failed: {login_page.status_code}")
        return
    
    # Step 2: Extract CSRF token (if needed)
    # For now, let's try without CSRF
    
    # Step 3: Login with demo credentials
    print("\n2. 🔐 Logging in with demo credentials...")
    login_data = {
        'username': 'demo',
        'password': 'demo123'
    }
    
    login_response = session.post('http://127.0.0.1:8080/login', data=login_data, allow_redirects=False)
    
    if login_response.status_code == 302:
        print("✅ Login successful (redirected)")
        print(f"Redirect to: {login_response.headers.get('Location', 'Unknown')}")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text[:200]}...")
        return
    
    # Step 4: Test connect page
    print("\n3. 🔗 Testing connect page...")
    connect_response = session.get('http://127.0.0.1:8080/wearable/connect')
    
    if connect_response.status_code == 200:
        print("✅ Connect page accessible after login")
        
        # Check for OAuth configuration
        if 'oauth_configured' in connect_response.text:
            print("✅ OAuth configuration found in page")
        else:
            print("❌ OAuth configuration missing")
            
        # Check for Google Fit availability
        if 'Available' in connect_response.text:
            print("✅ Google Fit shows as Available")
        else:
            print("❌ Google Fit does not show as Available")
            
    else:
        print(f"❌ Connect page failed: {connect_response.status_code}")
        return
    
    # Step 5: Test Google Fit connect
    print("\n4. 🚀 Testing Google Fit connect...")
    google_fit_response = session.get('http://127.0.0.1:8080/wearable/connect/google_fit', allow_redirects=False)
    
    if google_fit_response.status_code == 302:
        location = google_fit_response.headers.get('Location', '')
        print(f"✅ Google Fit connect redirects to: {location}")
        
        if 'accounts.google.com' in location:
            print("✅ Successfully redirecting to Google OAuth!")
            print(f"🔗 OAuth URL: {location[:100]}...")
        else:
            print(f"❌ Not redirecting to Google OAuth: {location}")
    else:
        print(f"❌ Google Fit connect failed: {google_fit_response.status_code}")
        print(f"Response: {google_fit_response.text[:200]}...")

def show_manual_test_steps():
    """Show manual test steps"""
    
    print("\n" + "=" * 50)
    print("🧪 MANUAL TEST STEPS")
    print("=" * 50)
    
    print("\n1. 🔐 LOGIN:")
    print("   - Go to: http://127.0.0.1:8080/login")
    print("   - Username: demo")
    print("   - Password: demo123")
    print("   - Click Login")
    
    print("\n2. 🔗 CONNECT PAGE:")
    print("   - Go to: http://127.0.0.1:8080/wearable/connect")
    print("   - Open Developer Tools (F12)")
    print("   - Check Console for OAuth configuration")
    print("   - Google Fit should show 'Available' badge")
    
    print("\n3. 🚀 GOOGLE FIT:")
    print("   - Click 'Connect Google Fit' button")
    print("   - Should show confirmation dialog")
    print("   - Click 'OK'")
    print("   - Should redirect to Google OAuth")
    
    print("\n4. 🔍 TROUBLESHOOTING:")
    print("   - Check browser console for JavaScript errors")
    print("   - Check Network tab for failed requests")
    print("   - Check Flask console for server errors")

if __name__ == "__main__":
    test_login_and_oauth()
    show_manual_test_steps()
