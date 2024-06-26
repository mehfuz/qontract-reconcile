from typing import Any
from unittest.mock import call, create_autospec

import pytest
from oauthlib.oauth2 import TokenExpiredError
from pytest_mock import MockerFixture
from requests import Response
from requests.adapters import HTTPAdapter

from reconcile.utils.oauth2_backend_application_session import (
    OAuth2BackendApplicationSession,
)

CLIENT_ID = "client_id"
CLIENT_SECRET = "client_secret"
TOKEN_URL = "https://token_url"
SCOPE = ["some-scope"]

EXPECTED_FETCH_TOKEN_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Connection": "close",
}


@pytest.fixture
def mock_backend_application_client(mocker: MockerFixture) -> Any:
    return mocker.patch(
        "reconcile.utils.oauth2_backend_application_session.BackendApplicationClient",
        autospec=True,
    )


@pytest.fixture
def mock_oauth2_session(mocker: MockerFixture) -> Any:
    return mocker.patch(
        "reconcile.utils.oauth2_backend_application_session.OAuth2Session",
        autospec=True,
    )


def test_oauth2_auto_session_init(
    mock_backend_application_client: Any,
    mock_oauth2_session: Any,
) -> None:
    with OAuth2BackendApplicationSession(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_url=TOKEN_URL,
        scope=SCOPE,
    ):
        pass

    mock_backend_application_client.assert_called_once_with(client_id=CLIENT_ID)
    mock_oauth2_session.assert_called_once_with(
        client=mock_backend_application_client.return_value,
        scope=SCOPE,
    )
    mock_oauth2_session.return_value.close.assert_called_once_with()


def build_oauth2_backend_application_session() -> OAuth2BackendApplicationSession:
    return OAuth2BackendApplicationSession(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_url=TOKEN_URL,
        scope=SCOPE,
    )


def test_first_request_auto_fetch_token(
    mock_oauth2_session: Any,
) -> None:
    mocked_oauth2_session = mock_oauth2_session.return_value
    mocked_oauth2_session.authorized = False
    session = build_oauth2_backend_application_session()

    response = session.request(method="GET", url="http://some-url")

    assert response == mocked_oauth2_session.request.return_value
    mocked_oauth2_session.fetch_token.assert_called_once_with(
        token_url=TOKEN_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scope=SCOPE,
        headers=EXPECTED_FETCH_TOKEN_HEADERS,
    )
    mocked_oauth2_session.request.assert_called_once_with(
        method="GET",
        url="http://some-url",
        data=None,
        headers=None,
        withhold_token=False,
        client_id=None,
        client_secret=None,
    )


def test_request_when_token_is_fetched(
    mock_oauth2_session: Any,
) -> None:
    mocked_oauth2_session = mock_oauth2_session.return_value
    mocked_oauth2_session.authorized = True
    session = build_oauth2_backend_application_session()

    response = session.request(method="GET", url="http://some-url")

    assert response == mocked_oauth2_session.request.return_value
    mocked_oauth2_session.fetch_token.assert_not_called()
    mocked_oauth2_session.request.assert_called_once_with(
        method="GET",
        url="http://some-url",
        data=None,
        headers=None,
        withhold_token=False,
        client_id=None,
        client_secret=None,
    )


def test_request_when_token_is_expired(
    mock_oauth2_session: Any,
) -> None:
    mocked_oauth2_session = mock_oauth2_session.return_value
    mocked_oauth2_session.authorized = True
    expected_response = create_autospec(Response)
    mocked_oauth2_session.request.side_effect = [
        TokenExpiredError(),
        expected_response,
    ]
    session = build_oauth2_backend_application_session()

    response = session.request(method="GET", url="http://some-url")

    assert response == expected_response
    mocked_oauth2_session.fetch_token.assert_called_once_with(
        token_url=TOKEN_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scope=SCOPE,
        headers=EXPECTED_FETCH_TOKEN_HEADERS,
    )
    mocked_oauth2_session.request.assert_has_calls([
        call(
            method="GET",
            url="http://some-url",
            data=None,
            headers=None,
            withhold_token=False,
            client_id=None,
            client_secret=None,
        ),
        call(
            method="GET",
            url="http://some-url",
            data=None,
            headers=None,
            withhold_token=False,
            client_id=None,
            client_secret=None,
        ),
    ])


def test_fetch_token(
    mock_oauth2_session: Any,
) -> None:
    expected_token = {"access_token": "abc"}
    mock_oauth2_session.return_value.fetch_token.return_value = expected_token
    session = build_oauth2_backend_application_session()

    token = session.fetch_token()

    assert token == expected_token
    mock_oauth2_session.return_value.fetch_token.assert_called_once_with(
        token_url=TOKEN_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scope=SCOPE,
        headers=EXPECTED_FETCH_TOKEN_HEADERS,
    )


def test_mount(
    mock_oauth2_session: Any,
) -> None:
    session = build_oauth2_backend_application_session()
    adapter = HTTPAdapter()

    session.mount("http://", adapter)

    mock_oauth2_session.return_value.mount.assert_called_once_with("http://", adapter)


def test_headers(
    mock_oauth2_session: Any,
) -> None:
    mock_oauth2_session.return_value.headers = {}
    session = build_oauth2_backend_application_session()

    session.headers.update({"Content-Type": "application/json"})

    assert mock_oauth2_session.return_value.headers == {
        "Content-Type": "application/json"
    }


def test_get_auth(
    mock_oauth2_session: Any,
) -> None:
    mock_oauth2_session.return_value.auth = "auth"
    session = build_oauth2_backend_application_session()

    auth = session.auth

    assert auth == mock_oauth2_session.return_value.auth


def test_set_auth(
    mock_oauth2_session: Any,
) -> None:
    mock_oauth2_session.return_value.auth = "auth"
    session = build_oauth2_backend_application_session()

    session.auth = None

    assert mock_oauth2_session.return_value.auth is None


def test_get(
    mock_oauth2_session: Any,
) -> None:
    session = build_oauth2_backend_application_session()

    response = session.get("http://some-url")

    assert response == mock_oauth2_session.return_value.get.return_value
    mock_oauth2_session.return_value.get.assert_called_once_with("http://some-url")


def test_post(
    mock_oauth2_session: Any,
) -> None:
    session = build_oauth2_backend_application_session()

    response = session.post("http://some-url")

    assert response == mock_oauth2_session.return_value.post.return_value
    mock_oauth2_session.return_value.post.assert_called_once_with("http://some-url")


def test_put(
    mock_oauth2_session: Any,
) -> None:
    session = build_oauth2_backend_application_session()

    response = session.put("http://some-url")

    assert response == mock_oauth2_session.return_value.put.return_value
    mock_oauth2_session.return_value.put.assert_called_once_with("http://some-url")


def test_delete(
    mock_oauth2_session: Any,
) -> None:
    session = build_oauth2_backend_application_session()

    response = session.delete("http://some-url")

    assert response == mock_oauth2_session.return_value.delete.return_value
    mock_oauth2_session.return_value.delete.assert_called_once_with("http://some-url")
