"""
Authentication manager for ETSPI MCP server

Handles loading and persisting Etsy API authentication tokens
from the ~/.etspi/auth.env file created by the etspi auth CLI command.
"""
from pathlib import Path
from dotenv import dotenv_values, set_key
from typing import Dict
import time


class AuthenticationError(Exception):
    """Raised when authentication configuration is invalid or missing"""
    pass


class EtspiAuthManager:
    """Manages authentication for ETSPI MCP server"""

    def __init__(self):
        """Initialize authentication manager"""
        self.auth_file = Path.home() / ".etspi" / "auth.env"
        self._ensure_auth_file_exists()

    def _ensure_auth_file_exists(self):
        """Ensure auth file and directory exist"""
        if not self.auth_file.parent.exists():
            raise AuthenticationError(
                "Auth directory not found at ~/.etspi/. "
                "Please run 'etspi auth -tF' first to set up authentication."
            )

        if not self.auth_file.exists():
            raise AuthenticationError(
                "Auth config not found at ~/.etspi/auth.env. "
                "Please run 'etspi auth -tF' to authenticate with Etsy."
            )

    def get_auth_config(self) -> Dict[str, str]:
        """
        Load authentication configuration from auth.env file

        Returns:
            Dictionary containing 'key', 'token', 'refresh_token', and 'expiry'

        Raises:
            AuthenticationError: If auth file is missing or incomplete
        """
        config = dotenv_values(self.auth_file)

        required_keys = ['key', 'token', 'refresh_token', 'expiry']
        missing_keys = [key for key in required_keys if key not in config or not config[key]]

        if missing_keys:
            raise AuthenticationError(
                f"Auth config is missing required keys: {', '.join(missing_keys)}. "
                f"Please run 'etspi auth -tF' to re-authenticate."
            )

        return {
            'key': config['key'],
            'token': config['token'],
            'refresh_token': config['refresh_token'],
            'expiry': int(config['expiry'])
        }

    def save_tokens(self, token: str, refresh_token: str, expiry: int):
        """
        Save refreshed tokens back to auth.env file

        This callback is used by EtsyAPI when tokens are automatically refreshed.

        Args:
            token: New access token
            refresh_token: New refresh token
            expiry: Token expiration timestamp
        """
        try:
            set_key(self.auth_file, 'token', token)
            set_key(self.auth_file, 'refresh_token', refresh_token)
            set_key(self.auth_file, 'expiry', str(expiry))
        except Exception as ex:
            # Log but don't fail - token refresh can continue in memory
            print(f"Warning: Failed to persist refreshed tokens: {ex}")

    def is_token_valid(self) -> bool:
        """
        Check if current token is still valid (not expired)

        Returns:
            True if token is valid, False otherwise
        """
        try:
            config = self.get_auth_config()
            # Add 60 second buffer to avoid edge cases
            return int(config['expiry']) > (int(time.time()) + 60)
        except (AuthenticationError, ValueError, KeyError):
            return False

    def get_status(self) -> Dict[str, any]:
        """
        Get authentication status information

        Returns:
            Dictionary with authentication status details
        """
        try:
            config = self.get_auth_config()
            expiry = int(config['expiry'])
            current_time = int(time.time())
            is_valid = expiry > current_time

            return {
                'authenticated': True,
                'token_valid': is_valid,
                'expires_in_seconds': max(0, expiry - current_time),
                'api_key_present': bool(config['key'])
            }
        except AuthenticationError as ex:
            return {
                'authenticated': False,
                'error': str(ex)
            }
