"""
API client for SenseChat-Character-Pro
Handles JWT authentication and API requests
"""
import time
import jwt
import requests
from typing import Dict, List, Optional
from backend.config import settings
from backend.models import CharacterSettings, RoleSetting, Message


class SenseChatClient:
    """Client for interacting with SenseChat-Character-Pro API"""

    def __init__(self):
        self.access_key_id = settings.SENSENOVA_ACCESS_KEY_ID
        self.secret_access_key = settings.SENSENOVA_SECRET_ACCESS_KEY
        self.model_name = settings.MODEL_NAME
        self.base_url = settings.API_BASE_URL
        self.endpoint = settings.CHARACTER_CHAT_ENDPOINT
        self._token = None
        self._token_expiry = 0

    def _generate_jwt_token(self) -> str:
        """
        Generate JWT token for API authentication
        Based on the resources documentation
        """
        headers = {
            "alg": "HS256",
            "typ": "JWT"
        }
        payload = {
            "iss": self.access_key_id,
            "exp": int(time.time()) + settings.TOKEN_EXPIRY_SECONDS,  # 30 minutes
            "nbf": int(time.time()) - 5  # Valid from 5 seconds ago
        }
        token = jwt.encode(payload, self.secret_access_key, headers=headers)
        return token

    def _get_valid_token(self) -> str:
        """
        Get a valid JWT token, generating a new one if expired
        Tokens are refreshed 5 minutes before expiry
        """
        current_time = int(time.time())
        # Refresh token 5 minutes (300 seconds) before expiry
        if not self._token or current_time >= (self._token_expiry - 300):
            self._token = self._generate_jwt_token()
            self._token_expiry = current_time + settings.TOKEN_EXPIRY_SECONDS
        return self._token

    def create_character_chat(
        self,
        character_settings: List[Dict],
        role_setting: Dict,
        messages: List[Dict],
        max_new_tokens: int = 1024,
        n: int = 1
    ) -> Dict:
        """
        Create a character chat completion

        Args:
            character_settings: List of character setting dictionaries
            role_setting: Role setting dictionary with user_name and primary_bot_name
            messages: List of message dictionaries with name and content
            max_new_tokens: Maximum tokens to generate (default 1024)
            n: Number of responses to generate (default 1)

        Returns:
            API response dictionary

        Raises:
            requests.RequestException: If API request fails
        """
        url = f"{self.base_url}{self.endpoint}"
        token = self._get_valid_token()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        payload = {
            "model": self.model_name,
            "character_settings": character_settings,
            "role_setting": role_setting,
            "messages": messages,
            "max_new_tokens": max_new_tokens,
            "n": n
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            raise

    def test_connection(self) -> bool:
        """
        Test the API connection with a simple request

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Simple test with minimal character settings
            # MUST include both user and AI character
            test_character = [
                {
                    "name": "用戶",
                    "gender": "男",
                    "detail_setting": "測試用戶"
                },
                {
                    "name": "測試角色",
                    "gender": "女",
                    "detail_setting": "溫柔體貼的性格"
                }
            ]

            test_role = {
                "user_name": "用戶",
                "primary_bot_name": "測試角色"
            }

            test_messages = [{
                "name": "用戶",
                "content": "你好"
            }]

            response = self.create_character_chat(
                character_settings=test_character,
                role_setting=test_role,
                messages=test_messages,
                max_new_tokens=100
            )

            return "data" in response and "reply" in response["data"]
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
