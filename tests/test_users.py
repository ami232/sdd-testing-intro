"""
Testing warm-up: pytest-mock's `mocker`, `monkeypatch`, and `parametrize`.

The first four tests are worked examples. Read them, run them, then fill in
the three exercises at the bottom.
"""

import pytest

from premium_check.users import get_api_key, get_user_data, is_premium_user


@pytest.fixture
def mock_api_response(mocker):
    """A mock response object, so each test only sets what it cares about."""
    response = mocker.Mock()
    response.status_code = 200
    return response


@pytest.fixture
def api_url():
    """The base API URL, kept in one place."""
    return "https://api.example.com"


# ================ Worked examples ================


def test_env_default_key(monkeypatch):
    """monkeypatch: remove the env var and check the fallback."""
    monkeypatch.delenv("API_KEY", raising=False)
    assert get_api_key() == "default_key"


def test_get_user_profile(mocker, mock_api_response, api_url):
    """mocker.patch: replace requests.get and assert on the call it received."""
    mock_api_response.json.return_value = {
        "profile": {"name": "John Doe", "email": "john@example.com"}
    }
    mock_get = mocker.patch("requests.get", return_value=mock_api_response)

    result = get_user_data(1)

    assert result["profile"]["name"] == "John Doe"
    mock_get.assert_called_once_with(f"{api_url}/users/1")


@pytest.mark.parametrize("status_code", [500, 503, 429])
def test_api_errors(mocker, mock_api_response, status_code):
    """parametrize: one test body, three error responses."""
    mock_api_response.status_code = status_code
    mock_get = mocker.patch("requests.get", return_value=mock_api_response)

    assert get_user_data(1) is None
    assert mock_get.call_count == 1


def test_premium_trial_user(mocker):
    """
    Patch the function, not the transport.

    Note the target: `premium_check.users.get_user_data`, the name as
    `is_premium_user` looks it up. Patching where a name is *defined* rather
    than where it is *used* is the classic mistake here.
    """
    trial_data = {
        "has_subscription": True,
        "plan": "premium",
        "is_expired": False,
        # Extra keys the function should simply ignore.
        "trial_days_left": 7,
        "trial_features": ["advanced_search", "premium_support"],
    }
    mocker.patch("premium_check.users.get_user_data", return_value=trial_data)

    assert is_premium_user(1) is True


# ================ Exercises ================


# TODO Exercise 1: monkeypatch
# Write a test for get_api_key that sets a custom API key in the environment
# and verifies that it is the value returned.
def test_custom_api_key(monkeypatch):
    """Test a custom API key read from the environment."""
    # monkeypatch.setenv(...)
    pass  # Implement your solution here


# TODO Exercise 2: parametrized testing
# Fill in the case table for is_premium_user. Cover: active premium, expired
# premium, an active basic plan, and no subscription at all.
@pytest.mark.parametrize(
    "user_data,expected",
    [
        # Add your cases here, following this shape:
        # ({"has_subscription": bool, "plan": str, "is_expired": bool}, expected),
    ],
)
def test_subscription_status(mocker, user_data, expected):
    """Test the subscription rules across several scenarios."""
    pass  # Implement your solution here


# TODO Exercise 3: patching a failure
# Test that is_premium_user degrades gracefully when the API gives us nothing
# back. Patch get_user_data to simulate it.
def test_api_connection_error(mocker):
    """Test the premium check when the upstream API is unavailable."""
    pass  # Implement your solution here
