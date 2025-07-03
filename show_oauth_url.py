#!/usr/bin/env python3
"""
Show Google Fit OAuth URL with your credentials
"""

import urllib.parse

def show_google_fit_oauth_url():
    """Show what the Google Fit OAuth URL looks like with your credentials"""
    
    print("🔵 GOOGLE FIT OAUTH URL PREVIEW")
    print("=" * 40)
    
    # Your credentials
    client_id = "297328435894-v366kp0ac0obpobqdsn0l508htmacasm.apps.googleusercontent.com"
    redirect_uri = "http://127.0.0.1:8080/wearable/oauth/google_fit/callback"
    
    # OAuth parameters
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'https://www.googleapis.com/auth/fitness.activity.read https://www.googleapis.com/auth/fitness.body.read https://www.googleapis.com/auth/fitness.location.read',
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent',
        'state': 'example_state_123'
    }
    
    # Build URL
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    oauth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    print(f"📋 OAuth Parameters:")
    print(f"   Client ID: {client_id}")
    print(f"   Redirect URI: {redirect_uri}")
    print(f"   Scopes: fitness.activity.read, fitness.body.read, fitness.location.read")
    
    print(f"\n🔗 Complete OAuth URL:")
    print(oauth_url)
    
    print(f"\n✅ This URL will be generated when you click 'Connect Google Fit'")
    print(f"⚠️  Make sure the redirect URI is added to your Google Cloud Console!")

if __name__ == "__main__":
    show_google_fit_oauth_url()
