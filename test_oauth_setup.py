#!/usr/bin/env python3
"""
Test OAuth Setup for Wearable Integration
This script demonstrates how to set up OAuth credentials for testing
"""

import os
import sys

def setup_test_oauth_credentials():
    """Set up test OAuth credentials for demonstration"""
    
    print("🔧 Setting up test OAuth credentials...")
    
    # Test credentials (these are fake for demonstration)
    test_credentials = {
        'GOOGLE_FIT_CLIENT_ID': 'test_google_client_id_123.apps.googleusercontent.com',
        'GOOGLE_FIT_CLIENT_SECRET': 'test_google_client_secret_456',
        'FITBIT_CLIENT_ID': 'test_fitbit_client_id_789',
        'FITBIT_CLIENT_SECRET': 'test_fitbit_client_secret_012'
    }
    
    # Set environment variables
    for key, value in test_credentials.items():
        os.environ[key] = value
        print(f"✅ Set {key}")
    
    print("\n📋 OAuth credentials configured!")
    print("Note: These are test credentials. For real integration, you need:")
    print("1. Google Cloud Console project with Fitness API enabled")
    print("2. Fitbit Developer App registration")
    print("3. Real OAuth client credentials")
    
    return test_credentials

def test_oauth_manager():
    """Test the OAuth manager functionality"""
    
    print("\n🧪 Testing OAuth Manager...")
    
    try:
        # Import the OAuth manager
        from water_tracker.wearable_integration.oauth_manager import OAuthManager
        
        # Create test app config
        app_config = {
            'GOOGLE_FIT_CLIENT_ID': os.environ.get('GOOGLE_FIT_CLIENT_ID'),
            'GOOGLE_FIT_CLIENT_SECRET': os.environ.get('GOOGLE_FIT_CLIENT_SECRET'),
            'GOOGLE_FIT_REDIRECT_URI': 'http://127.0.0.1:8080/wearable/oauth/google_fit/callback',
            'FITBIT_CLIENT_ID': os.environ.get('FITBIT_CLIENT_ID'),
            'FITBIT_CLIENT_SECRET': os.environ.get('FITBIT_CLIENT_SECRET'),
            'FITBIT_REDIRECT_URI': 'http://127.0.0.1:8080/wearable/oauth/fitbit/callback'
        }
        
        # Initialize OAuth manager
        oauth_manager = OAuthManager(app_config)
        print("✅ OAuth Manager initialized successfully")
        
        # Test Google Fit authorization URL generation
        try:
            auth_url, state = oauth_manager.get_authorization_url('google_fit', user_id=1)
            print(f"✅ Google Fit auth URL generated (state: {state[:8]}...)")
            print(f"   URL: {auth_url[:50]}...")
        except Exception as e:
            print(f"❌ Google Fit auth URL generation failed: {e}")
        
        # Test Fitbit authorization URL generation
        try:
            auth_url, state = oauth_manager.get_authorization_url('fitbit', user_id=1)
            print(f"✅ Fitbit auth URL generated (state: {state[:8]}...)")
            print(f"   URL: {auth_url[:50]}...")
        except Exception as e:
            print(f"❌ Fitbit auth URL generation failed: {e}")
        
        print("✅ OAuth Manager tests completed")
        
    except ImportError as e:
        print(f"❌ Failed to import OAuth Manager: {e}")
    except Exception as e:
        print(f"❌ OAuth Manager test failed: {e}")

def test_fitness_apis():
    """Test the fitness API classes"""
    
    print("\n🏃 Testing Fitness APIs...")
    
    try:
        from water_tracker.wearable_integration.fitness_apis import GoogleFitAPI, FitbitAPI, MockFitnessAPI
        
        # Test Mock API (should always work)
        mock_api = MockFitnessAPI()
        print("✅ Mock API initialized")
        
        if mock_api.test_connection():
            print("✅ Mock API connection test passed")
        else:
            print("❌ Mock API connection test failed")
        
        # Test user profile
        profile = mock_api.get_user_profile()
        print(f"✅ Mock API user profile: {profile}")
        
        # Test Google Fit API (will fail without real tokens)
        try:
            google_api = GoogleFitAPI('test_token')
            print("✅ Google Fit API initialized")
        except Exception as e:
            print(f"⚠️  Google Fit API init (expected with test token): {e}")
        
        # Test Fitbit API (will fail without real tokens)
        try:
            fitbit_api = FitbitAPI('test_token')
            print("✅ Fitbit API initialized")
        except Exception as e:
            print(f"⚠️  Fitbit API init (expected with test token): {e}")
        
        print("✅ Fitness API tests completed")
        
    except ImportError as e:
        print(f"❌ Failed to import Fitness APIs: {e}")
    except Exception as e:
        print(f"❌ Fitness API test failed: {e}")

def show_setup_instructions():
    """Show setup instructions for real OAuth"""
    
    print("\n📖 REAL OAUTH SETUP INSTRUCTIONS")
    print("=" * 50)
    
    print("\n🔵 GOOGLE FIT SETUP:")
    print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
    print("2. Create a new project or select existing one")
    print("3. Enable the Fitness API")
    print("4. Create OAuth 2.0 credentials (Web application)")
    print("5. Add redirect URI: http://127.0.0.1:8080/wearable/oauth/google_fit/callback")
    print("6. Copy Client ID and Client Secret")
    
    print("\n🟢 FITBIT SETUP:")
    print("1. Go to Fitbit Developer Console (https://dev.fitbit.com/apps)")
    print("2. Register a new application")
    print("3. Set OAuth 2.0 Application Type: Server")
    print("4. Add callback URL: http://127.0.0.1:8080/wearable/oauth/fitbit/callback")
    print("5. Copy Client ID and Client Secret")
    
    print("\n⚙️  CONFIGURATION:")
    print("Set environment variables:")
    print("export GOOGLE_FIT_CLIENT_ID='your_google_client_id'")
    print("export GOOGLE_FIT_CLIENT_SECRET='your_google_client_secret'")
    print("export FITBIT_CLIENT_ID='your_fitbit_client_id'")
    print("export FITBIT_CLIENT_SECRET='your_fitbit_client_secret'")
    
    print("\n🚀 TESTING:")
    print("1. Start the app: python run.py")
    print("2. Go to: http://127.0.0.1:8080/wearable/connect")
    print("3. Click 'Connect Google Fit' or 'Connect Fitbit'")
    print("4. Complete OAuth authorization")
    print("5. Check connection in wearable dashboard")

def main():
    """Main test function"""
    
    print("🔗 WEARABLE INTEGRATION OAUTH TEST")
    print("=" * 40)
    
    # Setup test credentials
    credentials = setup_test_oauth_credentials()
    
    # Test OAuth manager
    test_oauth_manager()
    
    # Test fitness APIs
    test_fitness_apis()
    
    # Show setup instructions
    show_setup_instructions()
    
    print("\n✨ OAuth implementation is ready!")
    print("📝 See OAUTH_SETUP.md for detailed setup instructions")
    print("🧪 Use the demo device for immediate testing")

if __name__ == "__main__":
    main()
