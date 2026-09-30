"""User lookups against an external subscriptions API."""

import os
from typing import Dict, Optional

import requests

API_BASE_URL = "https://api.example.com"


def get_user_data(user_id: int) -> Optional[Dict]:
    """Fetch user data from an external API."""
    response = requests.get(f"{API_BASE_URL}/users/{user_id}")
    if response.status_code == 200:
        return response.json()
    return None


def get_api_key() -> str:
    """Get the API key from the environment, falling back to a default."""
    return os.getenv("API_KEY", "default_key")


def is_premium_user(user_id: int) -> bool:
    """
    Check if a user has premium status.

    Premium users are those who:
    - Have a valid subscription
    - Have a premium plan
    - Have not expired
    """
    user_data = get_user_data(user_id)
    if not user_data:
        return False

    has_subscription = user_data.get("has_subscription", False)
    # `get(key, default)` only falls back when the key is ABSENT, so a present
    # `None` (which real APIs do return) needs the `or ""` guard.
    plan_type = (user_data.get("plan") or "").lower()
    is_expired = user_data.get("is_expired", True)

    return has_subscription and plan_type == "premium" and not is_expired
