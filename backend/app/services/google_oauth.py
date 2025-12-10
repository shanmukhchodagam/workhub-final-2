"""
Google OAuth Service for WorkHub Manager Authentication
"""
import os
import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token
import logging

logger = logging.getLogger(__name__)

class GoogleOAuthService:
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
        
        if not self.client_id or not self.client_secret:
            logger.warning("⚠️ Google OAuth credentials not configured!")
            logger.info("📋 To enable Google OAuth:")
            logger.info("   1. Go to https://console.cloud.google.com/")
            logger.info("   2. Create OAuth 2.0 credentials")
            logger.info("   3. Add environment variables to docker-compose.yml")
        else:
            logger.info("✅ Google OAuth service configured")
            logger.info(f"   Client ID: {self.client_id[:20]}...")
            logger.info(f"   Redirect URI: {self.redirect_uri}")

    def get_google_auth_url(self) -> str:
        """Generate Google OAuth authorization URL"""
        if not self.client_id:
            raise HTTPException(
                status_code=500, 
                detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
            )
        
        # Google OAuth 2.0 authorization endpoint
        auth_url = (
            "https://accounts.google.com/o/oauth2/auth"
            f"?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            "&scope=openid email profile"
            "&response_type=code"
            "&access_type=offline"
            "&prompt=consent"
            "&state=manager_signin"  # We can use this to identify manager signin
        )
        
        return auth_url

    async def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token and user info"""
        if not self.client_id or not self.client_secret:
            raise HTTPException(
                status_code=500,
                detail="Google OAuth not configured"
            )

        token_url = "https://oauth2.googleapis.com/token"
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }

        async with httpx.AsyncClient() as client:
            try:
                # Exchange code for tokens
                token_response = await client.post(token_url, data=data)
                token_response.raise_for_status()
                token_data = token_response.json()

                # Get user info from Google
                access_token = token_data.get("access_token")
                if not access_token:
                    raise HTTPException(status_code=400, detail="Failed to get access token")

                user_info_response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                user_info_response.raise_for_status()
                user_info = user_info_response.json()

                return {
                    "access_token": access_token,
                    "user_info": user_info,
                    "token_data": token_data
                }

            except httpx.HTTPError as e:
                logger.error(f"Google OAuth error: {e}")
                raise HTTPException(
                    status_code=400,
                    detail="Failed to authenticate with Google"
                )

    async def verify_google_token(self, id_token_str: str) -> Optional[Dict[str, Any]]:
        """Verify Google ID token and return user info"""
        try:
            if not self.client_id:
                raise ValueError("Google Client ID not configured")

            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                requests.Request(), 
                self.client_id
            )

            # Check if token is for our app
            if idinfo['aud'] != self.client_id:
                raise ValueError('Invalid audience')

            # Token is valid, return user info
            return {
                "google_id": idinfo['sub'],
                "email": idinfo['email'],
                "name": idinfo.get('name', ''),
                "picture": idinfo.get('picture', ''),
                "email_verified": idinfo.get('email_verified', False)
            }

        except ValueError as e:
            logger.error(f"Invalid Google token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying Google token: {e}")
            return None

    def is_configured(self) -> bool:
        """Check if Google OAuth is properly configured"""
        return bool(self.client_id and self.client_secret)

# Global Google OAuth service instance
google_oauth_service = GoogleOAuthService()