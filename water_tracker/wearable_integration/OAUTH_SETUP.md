# OAuth Setup Guide for Wearable Integration

This guide explains how to set up OAuth credentials for Google Fit and Fitbit integration in the Water Intake Tracker app.

## Overview

The wearable integration feature supports OAuth 2.0 authentication for:
- **Google Fit API** - Access activity data from Android devices and compatible fitness trackers
- **Fitbit API** - Sync comprehensive activity and health data from Fitbit devices

## Google Fit API Setup

### Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Fitness API** for your project:
   - Go to "APIs & Services" > "Library"
   - Search for "Fitness API"
   - Click "Enable"

### Step 2: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Configure the OAuth consent screen if prompted
4. Select "Web application" as the application type
5. Add authorized redirect URIs:
   - `http://127.0.0.1:8080/wearable/oauth/google_fit/callback` (for local development)
   - `https://yourdomain.com/wearable/oauth/google_fit/callback` (for production)
6. Save and note down the **Client ID** and **Client Secret**

### Step 3: Configure Scopes

The app requests these Google Fit scopes:
- `https://www.googleapis.com/auth/fitness.activity.read`
- `https://www.googleapis.com/auth/fitness.body.read`
- `https://www.googleapis.com/auth/fitness.location.read`

## Fitbit API Setup

### Step 1: Register Your Application

1. Go to [Fitbit Developer Console](https://dev.fitbit.com/apps)
2. Click "Register an App"
3. Fill in the application details:
   - **Application Name**: Water Intake Tracker
   - **Description**: Hydration tracking with activity-based recommendations
   - **Application Website**: Your app's URL
   - **Organization**: Your organization name
   - **OAuth 2.0 Application Type**: Server
   - **Callback URL**: 
     - `http://127.0.0.1:8080/wearable/oauth/fitbit/callback` (for local development)
     - `https://yourdomain.com/wearable/oauth/fitbit/callback` (for production)

### Step 2: Get API Credentials

1. After registration, note down the **Client ID** and **Client Secret**
2. The app requests these Fitbit scopes:
   - `activity` - Access activity and exercise data
   - `heartrate` - Access heart rate data
   - `location` - Access location data
   - `profile` - Access profile information

## Environment Configuration

### Method 1: Environment Variables

Set the following environment variables:

```bash
# Google Fit
export GOOGLE_FIT_CLIENT_ID="your_google_client_id"
export GOOGLE_FIT_CLIENT_SECRET="your_google_client_secret"
export GOOGLE_FIT_REDIRECT_URI="http://127.0.0.1:8080/wearable/oauth/google_fit/callback"

# Fitbit
export FITBIT_CLIENT_ID="your_fitbit_client_id"
export FITBIT_CLIENT_SECRET="your_fitbit_client_secret"
export FITBIT_REDIRECT_URI="http://127.0.0.1:8080/wearable/oauth/fitbit/callback"
```

### Method 2: Update run_app.py

Add the credentials to your `run_app.py` file:

```python
import os

# Set OAuth credentials
os.environ['GOOGLE_FIT_CLIENT_ID'] = 'your_google_client_id'
os.environ['GOOGLE_FIT_CLIENT_SECRET'] = 'your_google_client_secret'
os.environ['FITBIT_CLIENT_ID'] = 'your_fitbit_client_id'
os.environ['FITBIT_CLIENT_SECRET'] = 'your_fitbit_client_secret'

# Import and run the app
from water_tracker.app import app
```

### Method 3: Direct Configuration

Modify `water_tracker/app.py` to set the credentials directly:

```python
# OAuth Configuration for Wearable Integration
app.config['GOOGLE_FIT_CLIENT_ID'] = 'your_google_client_id'
app.config['GOOGLE_FIT_CLIENT_SECRET'] = 'your_google_client_secret'
app.config['FITBIT_CLIENT_ID'] = 'your_fitbit_client_id'
app.config['FITBIT_CLIENT_SECRET'] = 'your_fitbit_client_secret'
```

## Testing the Setup

1. Start the application
2. Go to `/wearable/connect`
3. You should see "Available" badges on Google Fit and Fitbit cards
4. Click "Connect Google Fit" or "Connect Fitbit"
5. You should be redirected to the respective OAuth authorization page

## Troubleshooting

### Common Issues

1. **"Setup Required" message**: OAuth credentials are not configured
2. **"Invalid redirect URI"**: The redirect URI in your OAuth app doesn't match the configured URI
3. **"Unauthorized client"**: The client ID is incorrect or the API is not enabled
4. **"Access denied"**: User denied permission or scopes are not properly configured

### Debug Steps

1. Check that all environment variables are set correctly
2. Verify redirect URIs match exactly (including protocol and port)
3. Ensure APIs are enabled in Google Cloud Console
4. Check that the OAuth consent screen is properly configured
5. Verify that the client ID and secret are correct

## Security Notes

- Never commit OAuth credentials to version control
- Use environment variables or secure configuration management
- Regularly rotate client secrets
- Monitor API usage and quotas
- Implement proper error handling for OAuth flows

## Production Deployment

For production deployment:

1. Update redirect URIs to use HTTPS and your production domain
2. Use secure environment variable management
3. Enable proper logging for OAuth flows
4. Implement rate limiting and abuse protection
5. Monitor API quotas and usage

## Support

If you encounter issues:

1. Check the application logs for detailed error messages
2. Verify your OAuth app configuration
3. Test with the demo device first to ensure the integration works
4. Consult the Google Fit and Fitbit API documentation for specific issues
