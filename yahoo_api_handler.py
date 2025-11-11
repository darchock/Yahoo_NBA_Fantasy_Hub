"""
Yahoo API Handler - Static handler class for all Yahoo Fantasy API interactions.
"""

import requests
from typing import Optional, Dict, Any
from urllib.parse import urlencode
import base64

from config import YAHOO_CLIENT_ID, YAHOO_CLIENT_SECRET, YAHOO_REDIRECT_URI
from token_manager import TokenManager


class YahooAPIHandler:
    """Static handler class for Yahoo Fantasy API operations."""

    # OAuth endpoints
    OAUTH_AUTHORIZE_URL = "https://api.login.yahoo.com/oauth2/request_auth"
    OAUTH_TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"
    OAUTH_REFRESH_URL = "https://api.login.yahoo.com/oauth2/get_token"

    # Yahoo Fantasy API endpoints
    FANTASY_API_BASE = "https://fantasysports.yahooapis.com/fantasy/v2"

    # Token manager instance
    _token_manager = TokenManager()

    @staticmethod
    def get_authorization_url(state: str = "12345") -> str:
        """
        Generate the authorization URL for OAuth flow.

        Args:
            state: Optional state parameter for security.

        Returns:
            Authorization URL.
        """
        params = {
            "client_id": YAHOO_CLIENT_ID,
            "redirect_uri": YAHOO_REDIRECT_URI,
            "response_type": "code",
            "scope": "fspt-r",
            "state": state,
        }
        return f"{YahooAPIHandler.OAUTH_AUTHORIZE_URL}?{urlencode(params)}"

    @staticmethod
    def fetch_token(authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.

        Args:
            authorization_code: The authorization code from OAuth callback.

        Returns:
            Dictionary containing access_token, refresh_token, and expires_in.

        Raises:
            Exception: If token exchange fails.
        """
        auth_string = base64.b64encode(
            f"{YAHOO_CLIENT_ID}:{YAHOO_CLIENT_SECRET}".encode()
        ).decode()

        headers = {"Authorization": f"Basic {auth_string}"}

        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": YAHOO_REDIRECT_URI,
        }

        response = requests.post(
            YahooAPIHandler.OAUTH_TOKEN_URL, headers=headers, data=data
        )
        response.raise_for_status()

        token_data = response.json()
        YahooAPIHandler._token_manager.save_token(token_data)
        return token_data

    @staticmethod
    def refresh_token() -> Optional[Dict[str, Any]]:
        """
        Refresh the access token using the refresh token.

        Returns:
            Dictionary containing new access_token and expires_in, or None if refresh fails.

        Raises:
            Exception: If token refresh fails.
        """
        token_data = YahooAPIHandler._token_manager.load_token()
        if token_data is None or "refresh_token" not in token_data:
            return None

        auth_string = base64.b64encode(
            f"{YAHOO_CLIENT_ID}:{YAHOO_CLIENT_SECRET}".encode()
        ).decode()

        headers = {"Authorization": f"Basic {auth_string}"}

        data = {
            "grant_type": "refresh_token",
            "refresh_token": token_data["refresh_token"],
        }

        response = requests.post(
            YahooAPIHandler.OAUTH_REFRESH_URL, headers=headers, data=data
        )
        response.raise_for_status()

        new_token_data = response.json()
        # Preserve the old refresh_token if not provided in response
        if "refresh_token" not in new_token_data:
            new_token_data["refresh_token"] = token_data["refresh_token"]

        YahooAPIHandler._token_manager.save_token(new_token_data)
        return new_token_data

    @staticmethod
    def get_valid_access_token() -> Optional[str]:
        """
        Get a valid access token, either from cache or by refreshing.

        Returns:
            Valid access token, or None if unable to obtain one.
        """
        # Check if cached token is still valid
        valid_token = YahooAPIHandler._token_manager.get_valid_token()
        if valid_token and "access_token" in valid_token:
            return valid_token["access_token"]

        # Try to refresh the token
        try:
            refreshed_token = YahooAPIHandler.refresh_token()
            if refreshed_token and "access_token" in refreshed_token:
                print("Refreshed OAuth token")
                return refreshed_token["access_token"]
        except Exception as e:
            print(f"Token refresh failed: {e}")

        return None

    @staticmethod
    def make_request(
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """
        Make an authenticated request to the Yahoo Fantasy API.

        Args:
            endpoint: The API endpoint (relative to base URL).
            method: HTTP method (GET, POST, etc.).
            params: Query parameters.
            data: Request body data.

        Returns:
            Response object.

        Raises:
            Exception: If unable to get a valid token or request fails.
        """
        access_token = YahooAPIHandler.get_valid_access_token()
        if access_token is None:
            raise Exception(
                "Unable to obtain valid access token. "
                "Please authenticate first using get_authorization_url()."
            )

        headers = {"Authorization": f"Bearer {access_token}"}

        url = f"{YahooAPIHandler.FANTASY_API_BASE}{endpoint}"

        response = requests.request(
            method, url, headers=headers, params=params, json=data
        )
        response.raise_for_status()

        return response

    @staticmethod
    def reset_token() -> None:
        """Clear the stored token cache."""
        import os

        if os.path.exists(YahooAPIHandler._token_manager.token_file):
            os.remove(YahooAPIHandler._token_manager.token_file)
            print("Token cache cleared")
