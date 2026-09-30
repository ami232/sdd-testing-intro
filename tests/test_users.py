"""
Testing warm-up: solutions.

The first four tests are the worked examples from the `main` branch,
unchanged. The three below the divider are the exercises, solved.
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


# ================ Solutions ================


def test_custom_api_key(monkeypatch):
    """
    Exercise 1: a custom API key read from the environment.

    monkeypatch is the right tool because it restores the environment when the
    test ends. Assigning to os.environ directly would leak the value into
    every test that runs afterwards, and `test_env_default_key` above would
    start passing or failing depending on the order tests happen to run in.
    """
    expected_key = "my_custom_api_key_2026"
    monkeypatch.setenv("API_KEY", expected_key)

    assert get_api_key() == expected_key


@pytest.mark.parametrize(
    "user_data,expected",
    [
        (
            {"has_subscription": True, "plan": "premium", "is_expired": False},
            True,  # Active premium subscription
        ),
        (
            {"has_subscription": True, "plan": "premium", "is_expired": True},
            False,  # Expired premium subscription
        ),
        (
            {"has_subscription": True, "plan": "basic", "is_expired": False},
            False,  # Active basic plan
        ),
        (
            {"has_subscription": False, "plan": None, "is_expired": False},
            False,  # No subscription, and a null plan from the API
        ),
        (
            {"has_subscription": True, "plan": "PREMIUM", "is_expired": False},
            True,  # The comparison is case-insensitive
        ),
    ],
)
def test_subscription_status(mocker, user_data, expected):
    """
    Exercise 2: the subscription rules across several scenarios.

    The fourth case is the trap. `plan` is present and null, so
    `user_data.get("plan", "")` returns None rather than the default, and
    `.lower()` on it raises AttributeError. Note that the `has_subscription`
    check does not save us: `plan_type` is computed before the `and` chain
    runs, so there is nothing to short-circuit.
    """
    mocker.patch("premium_check.users.get_user_data", return_value=user_data)

    assert is_premium_user(123) is expected


def test_api_connection_error(mocker):
    """
    Exercise 3: the premium check when the upstream API is unavailable.

    get_user_data already turns a non-200 response into None, so returning
    None is how the outage reaches is_premium_user.
    """
    mocker.patch("premium_check.users.get_user_data", return_value=None)

    assert is_premium_user(123) is False


def test_api_raising_is_not_handled(mocker):
    """
    A connection error that raises is NOT handled, and this test documents it.

    A test can pin down a limitation as well as a feature. If someone later
    decides is_premium_user should swallow this, this test tells them they are
    changing behaviour on purpose.
    """
    import requests

    mocker.patch(
        "premium_check.users.get_user_data",
        side_effect=requests.exceptions.ConnectionError("API unreachable"),
    )

    with pytest.raises(requests.exceptions.ConnectionError):
        is_premium_user(123)
