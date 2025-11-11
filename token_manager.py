"""
Token Manager - Handles OAuth token persistence and validation.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from config import TOKEN_FILE


class TokenManager:
    """Manages OAuth token storage and validation."""

    def __init__(self, token_file: str = TOKEN_FILE):
        """
        Initialize TokenManager.

        Args:
            token_file: Path to the token cache file.
        """
        self.token_file = token_file

    def save_token(self, token_data: Dict[str, Any]) -> None:
        """
        Save OAuth token to file with timestamp.

        Args:
            token_data: Dictionary containing the OAuth token and related data.
        """
        token_data["timestamp"] = datetime.now().isoformat()
        with open(self.token_file, "w") as f:
            json.dump(token_data, f, indent=2)
        print(f"Token saved to {self.token_file}")

    def load_token(self) -> Optional[Dict[str, Any]]:
        """
        Load OAuth token from file.

        Returns:
            Dictionary containing the token data, or None if file doesn't exist.
        """
        if not os.path.exists(self.token_file):
            return None

        with open(self.token_file, "r") as f:
            return json.load(f)

    def is_token_valid(self, token_data: Optional[Dict[str, Any]]) -> bool:
        """
        Check if the stored token is still valid.

        Args:
            token_data: Dictionary containing the token data.

        Returns:
            True if token is valid (not expired), False otherwise.
        """
        if token_data is None:
            return False

        if "expires_in" not in token_data or "timestamp" not in token_data:
            return False

        try:
            timestamp = datetime.fromisoformat(token_data["timestamp"])
            expires_in = int(token_data["expires_in"])
            expiration_time = timestamp + timedelta(seconds=expires_in)
            return datetime.now() < expiration_time
        except (ValueError, KeyError):
            return False

    def get_valid_token(self) -> Optional[Dict[str, Any]]:
        """
        Get a valid token from cache, or None if expired/missing.

        Returns:
            Valid token data or None.
        """
        token_data = self.load_token()
        if self.is_token_valid(token_data):
            print("Using cached OAuth token")
            return token_data
        return None
