"""
OAuth Manager for Wearable Integration
Handles OAuth 2.0 flows for Google Fit and Fitbit APIs
"""

import secrets
import requests
import urllib.parse
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class OAuthManager:
    """Manages OAuth 2.0 flows for fitness platforms"""
    
    # OAuth endpoints and scopes for different platforms
    PLATFORM_CONFIG = {
        'google_fit': {
            'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
            'token_url': 'https://oauth2.googleapis.com/token',
            'scopes': [
                'https://www.googleapis.com/auth/fitness.activity.read',
                'https://www.googleapis.com/auth/fitness.body.read',
                'https://www.googleapis.com/auth/fitness.location.read'
            ],
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent'
        },
        'fitbit': {
            'auth_url': 'https://www.fitbit.com/oauth2/authorize',
            'token_url': 'https://api.fitbit.com/oauth2/token',
            'scopes': [
                'activity',
                'heartrate',
                'location',
                'profile'
            ],
            'response_type': 'code'
        }
    }
    
    def __init__(self, app_config: Dict):
        """Initialize OAuth manager with app configuration"""
        self.config = app_config
        self.states = {}  # Store OAuth states temporarily
    
    def get_authorization_url(self, platform: str, user_id: int) -> Tuple[str, str]:
        """
        Generate OAuth authorization URL for a platform
        
        Args:
            platform: Platform name ('google_fit' or 'fitbit')
            user_id: User ID for state tracking
            
        Returns:
            Tuple of (authorization_url, state)
        """
        if platform not in self.PLATFORM_CONFIG:
            raise ValueError(f"Unsupported platform: {platform}")
        
        platform_config = self.PLATFORM_CONFIG[platform]
        
        # Generate secure state parameter
        state = secrets.token_urlsafe(32)
        self.states[state] = {
            'platform': platform,
            'user_id': user_id,
            'created_at': datetime.now(timezone.utc)
        }
        
        # Build authorization parameters
        auth_params = {
            'client_id': self._get_client_id(platform),
            'redirect_uri': self._get_redirect_uri(platform),
            'scope': ' '.join(platform_config['scopes']),
            'response_type': platform_config['response_type'],
            'state': state
        }
        
        # Add platform-specific parameters
        if platform == 'google_fit':
            auth_params.update({
                'access_type': platform_config['access_type'],
                'prompt': platform_config['prompt']
            })
        
        # Build authorization URL
        auth_url = f"{platform_config['auth_url']}?{urllib.parse.urlencode(auth_params)}"
        
        logger.info(f"Generated OAuth URL for {platform} (user {user_id})")
        return auth_url, state
    
    def exchange_code_for_tokens(self, platform: str, code: str, state: str) -> Dict:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            platform: Platform name
            code: Authorization code from callback
            state: State parameter for validation
            
        Returns:
            Dictionary containing token information
        """
        # Validate state
        if state not in self.states:
            raise ValueError("Invalid or expired state parameter")
        
        state_info = self.states[state]
        if state_info['platform'] != platform:
            raise ValueError("Platform mismatch in state")
        
        # Check state expiration (30 minutes)
        if datetime.now(timezone.utc) - state_info['created_at'] > timedelta(minutes=30):
            del self.states[state]
            raise ValueError("State parameter expired")
        
        platform_config = self.PLATFORM_CONFIG[platform]
        
        # Prepare token exchange request
        token_data = {
            'client_id': self._get_client_id(platform),
            'client_secret': self._get_client_secret(platform),
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self._get_redirect_uri(platform)
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        try:
            # Make token exchange request
            response = requests.post(
                platform_config['token_url'],
                data=token_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed for {platform}: {response.text}")
                raise Exception(f"Token exchange failed: {response.status_code}")
            
            token_info = response.json()
            
            # Clean up state
            user_id = state_info['user_id']
            del self.states[state]
            
            # Add platform and user info
            token_info['platform'] = platform
            token_info['user_id'] = user_id
            token_info['obtained_at'] = datetime.now(timezone.utc)
            
            # Calculate expiration time
            if 'expires_in' in token_info:
                expires_in = int(token_info['expires_in'])
                token_info['expires_at'] = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            
            logger.info(f"Successfully exchanged code for tokens ({platform}, user {user_id})")
            return token_info
            
        except requests.RequestException as e:
            logger.error(f"Network error during token exchange for {platform}: {e}")
            raise Exception(f"Network error during token exchange: {e}")
    
    def refresh_access_token(self, platform: str, refresh_token: str) -> Dict:
        """
        Refresh access token using refresh token
        
        Args:
            platform: Platform name
            refresh_token: Refresh token
            
        Returns:
            Dictionary containing new token information
        """
        if platform not in self.PLATFORM_CONFIG:
            raise ValueError(f"Unsupported platform: {platform}")
        
        platform_config = self.PLATFORM_CONFIG[platform]
        
        # Prepare refresh request
        refresh_data = {
            'client_id': self._get_client_id(platform),
            'client_secret': self._get_client_secret(platform),
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.post(
                platform_config['token_url'],
                data=refresh_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Token refresh failed for {platform}: {response.text}")
                raise Exception(f"Token refresh failed: {response.status_code}")
            
            token_info = response.json()
            token_info['platform'] = platform
            token_info['refreshed_at'] = datetime.now(timezone.utc)
            
            # Calculate expiration time
            if 'expires_in' in token_info:
                expires_in = int(token_info['expires_in'])
                token_info['expires_at'] = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            
            logger.info(f"Successfully refreshed access token for {platform}")
            return token_info
            
        except requests.RequestException as e:
            logger.error(f"Network error during token refresh for {platform}: {e}")
            raise Exception(f"Network error during token refresh: {e}")
    
    def _get_client_id(self, platform: str) -> str:
        """Get client ID for platform"""
        key = f"{platform.upper()}_CLIENT_ID"
        client_id = self.config.get(key, '')
        if not client_id:
            raise ValueError(f"Missing {key} in configuration")
        return client_id
    
    def _get_client_secret(self, platform: str) -> str:
        """Get client secret for platform"""
        key = f"{platform.upper()}_CLIENT_SECRET"
        client_secret = self.config.get(key, '')
        if not client_secret:
            raise ValueError(f"Missing {key} in configuration")
        return client_secret
    
    def _get_redirect_uri(self, platform: str) -> str:
        """Get redirect URI for platform"""
        key = f"{platform.upper()}_REDIRECT_URI"
        redirect_uri = self.config.get(key, '')
        if not redirect_uri:
            # Provide default redirect URIs
            if platform == 'google_fit':
                redirect_uri = 'http://127.0.0.1:8080/wearable/oauth/google_fit/callback'
            elif platform == 'fitbit':
                redirect_uri = 'http://127.0.0.1:8080/wearable/oauth/fitbit/callback'
            else:
                raise ValueError(f"Missing {key} in configuration")
        return redirect_uri
    
    def cleanup_expired_states(self):
        """Clean up expired OAuth states"""
        now = datetime.now(timezone.utc)
        expired_states = [
            state for state, info in self.states.items()
            if now - info['created_at'] > timedelta(minutes=30)
        ]
        
        for state in expired_states:
            del self.states[state]
        
        if expired_states:
            logger.info(f"Cleaned up {len(expired_states)} expired OAuth states")
