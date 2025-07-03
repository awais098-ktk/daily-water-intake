#!/usr/bin/env python3
"""
Debug OAuth Flow - Test the Google Fit connection step by step
"""

import requests
import json

def test_connect_page():
    """Test the connect page to see if OAuth is configured"""
    
    print("🔍 Testing Connect Page...")
    
    try:
        # Test the connect page
        response = requests.get('http://127.0.0.1:8080/wearable/connect')
        
        if response.status_code == 200:
            print("✅ Connect page loads successfully")
            
            # Check if Google Fit shows as available
            if 'Available' in response.text:
                print("✅ Google Fit shows as 'Available'")
            else:
                print("❌ Google Fit does not show as 'Available'")
                
            # Check for JavaScript errors
            if 'oauth_configured' in response.text:
                print("✅ OAuth configuration is being passed to template")
            else:
                print("❌ OAuth configuration missing in template")
                
        else:
            print(f"❌ Connect page failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing connect page: {e}")

def test_google_fit_connect():
    """Test the Google Fit connect endpoint directly"""
    
    print("\n🔍 Testing Google Fit Connect Endpoint...")
    
    try:
        # Test the Google Fit connect endpoint
        response = requests.get('http://127.0.0.1:8080/wearable/connect/google_fit', allow_redirects=False)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            # Should redirect to Google OAuth
            location = response.headers.get('Location', '')
            print(f"✅ Redirecting to: {location}")
            
            if 'accounts.google.com' in location:
                print("✅ Correctly redirecting to Google OAuth")
                print(f"🔗 OAuth URL: {location}")
            else:
                print(f"❌ Not redirecting to Google OAuth: {location}")
                
        elif response.status_code == 200:
            print("❌ Should redirect but returned 200")
            print(f"Response: {response.text[:500]}...")
            
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            
    except Exception as e:
        print(f"❌ Error testing Google Fit connect: {e}")

def test_oauth_manager():
    """Test OAuth manager directly"""
    
    print("\n🔍 Testing OAuth Manager...")
    
    try:
        # Import and test OAuth manager
        import sys
        import os
        sys.path.append(os.getcwd())
        
        from water_tracker.wearable_integration.oauth_manager import OAuthManager
        
        # Test configuration
        config = {
            'GOOGLE_FIT_CLIENT_ID': 'YOUR_GOOGLE_CLIENT_ID_HERE',
            'GOOGLE_FIT_CLIENT_SECRET': 'YOUR_GOOGLE_CLIENT_SECRET_HERE',
            'GOOGLE_FIT_REDIRECT_URI': 'http://127.0.0.1:8080/wearable/oauth/google_fit/callback'
        }
        
        oauth_manager = OAuthManager(config)
        print("✅ OAuth Manager created successfully")
        
        # Test URL generation
        auth_url, state = oauth_manager.get_authorization_url('google_fit', user_id=1)
        print(f"✅ Authorization URL generated")
        print(f"State: {state}")
        print(f"URL: {auth_url[:100]}...")
        
        if 'accounts.google.com' in auth_url:
            print("✅ URL points to Google OAuth")
        else:
            print("❌ URL does not point to Google OAuth")
            
    except Exception as e:
        print(f"❌ Error testing OAuth manager: {e}")
        import traceback
        traceback.print_exc()

def show_debugging_steps():
    """Show debugging steps for the user"""
    
    print("\n" + "=" * 50)
    print("🔧 DEBUGGING STEPS")
    print("=" * 50)
    
    print("\n1. 🌐 Open Browser Developer Tools:")
    print("   - Press F12 in your browser")
    print("   - Go to Console tab")
    print("   - Look for JavaScript errors")
    
    print("\n2. 🔍 Check Network Tab:")
    print("   - Go to Network tab in Developer Tools")
    print("   - Click 'Connect Google Fit' button")
    print("   - See if any requests are made")
    print("   - Check for failed requests")
    
    print("\n3. 📋 Manual Test:")
    print("   - Try this URL directly in browser:")
    print("   - http://127.0.0.1:8080/wearable/connect/google_fit")
    print("   - Should redirect to Google OAuth page")
    
    print("\n4. 🔄 Clear Browser Cache:")
    print("   - Clear browser cache and cookies")
    print("   - Try again")
    
    print("\n5. 📱 Check Console Output:")
    print("   - Look at the Flask app console")
    print("   - Check for any error messages")

def main():
    """Main debugging function"""
    
    print("🔵 GOOGLE FIT OAUTH DEBUGGING")
    print("=" * 40)
    
    # Test connect page
    test_connect_page()
    
    # Test Google Fit connect endpoint
    test_google_fit_connect()
    
    # Test OAuth manager
    test_oauth_manager()
    
    # Show debugging steps
    show_debugging_steps()
    
    print("\n✨ SUMMARY:")
    print("If all tests pass but clicking the button doesn't work,")
    print("the issue is likely in the JavaScript or browser.")
    print("Check the browser developer tools for errors!")

if __name__ == "__main__":
    main()
