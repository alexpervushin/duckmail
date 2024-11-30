"""
Tests for the DuckMail client implementation.
"""

import pytest
from aiohttp import FormData, ClientError
from src.duckmail import DuckMailClient
from src.duckmail.exceptions import (
    DuckMailError,
    APIError,
    ValidationError,
    ConnectionError,
)
from src.duckmail.models import SignupResponse, SignupError


@pytest.mark.asyncio
async def test_client_context_manager():
    """Test that client works properly as a context manager."""
    async with DuckMailClient() as client:
        assert client._session is not None
    assert client._session is None


@pytest.mark.asyncio
async def test_client_raises_error_when_not_initialized():
    """Test that using client without context manager raises error."""
    client = DuckMailClient()
    with pytest.raises(DuckMailError):
        await client.signup("test", "test@example.com")


@pytest.mark.asyncio
class TestSignup:
    """Test suite for signup functionality."""

    async def test_successful_signup(self, client, mock_response, mocker):
        """Test successful signup with valid parameters."""
        username = "agregu9hqbhqadqwdba"
        mock_data = {"status": "valid", "user": username}
        mock_resp = mock_response(mock_data)
        mocker.patch("aiohttp.ClientSession.request", return_value=mock_resp)

        response = await client.signup(username, "goodemail@gmail.com")
        assert isinstance(response, SignupResponse)
        assert response.status == "valid"
        assert response.user == username

    async def test_signup_unavailable_username(self, client, mock_response, mocker):
        """Test signup with an unavailable username."""
        mock_data = {"error": "unavailable_username"}
        mock_resp = mock_response(mock_data, status=400)
        mocker.patch("aiohttp.ClientSession.request", return_value=mock_resp)

        response = await client.signup("durov", "goodemail@gmail.com")
        assert isinstance(response, SignupError)
        assert response.error == "unavailable_username"

    async def test_signup_invalid_email(self, client, mock_response, mocker):
        """Test signup with an email that fails MX check."""
        mock_data = {"error": "failed_mx_check"}
        mock_resp = mock_response(mock_data, status=400)
        mocker.patch("aiohttp.ClientSession.request", return_value=mock_resp)

        response = await client.signup("agregu9hqbhqadqwdba", "test@invalid-domain.com")
        assert isinstance(response, SignupError)
        assert response.error == "failed_mx_check"

    async def test_signup_duck_email_not_allowed(self, client, mock_response, mocker):
        """Test signup with a @duck.com email address."""
        mock_data = {"error": "duck_address_not_allowed"}
        mock_resp = mock_response(mock_data, status=400)
        mocker.patch("aiohttp.ClientSession.request", return_value=mock_resp)

        response = await client.signup("agregu9hqbhqadqwdba", "test@duck.com")
        assert isinstance(response, SignupError)
        assert response.error == "duck_address_not_allowed"

    async def test_signup_with_options(self, client, mock_response, mocker):
        """Test signup with optional parameters."""
        username = "agregu9hqbhqadqwdba"
        mock_data = {"status": "valid", "user": username}
        mock_resp = mock_response(mock_data)
        mock_request = mocker.patch(
            "aiohttp.ClientSession.request", return_value=mock_resp
        )

        await client.signup(
            username, "goodemail@gmail.com", disable_secure_reply=True, dry_run=True
        )

        called_args = mock_request.call_args
        assert called_args is not None, "Mock request was not called"
        assert "data" in called_args.kwargs, "Form data not found in request"
        form_data = called_args.kwargs["data"]
        assert isinstance(form_data, FormData)

        fields = list(form_data._fields)
        print("\nForm data fields:")
        for field in fields:
            print(f"Field: {field}")

        found_fields = {
            "user": False,
            "email": False,
            "disable_secure_reply": False,
            "dry_run": False,
        }

        for field in fields:
            multidict = field[0]
            value = str(field[2])
            name = multidict.get("name")
            print(f"Processing field - name: {name}, value: {value}")

            if name == "user" and value == username:
                found_fields["user"] = True
            elif name == "email" and value == "goodemail@gmail.com":
                found_fields["email"] = True
            elif name == "disable_secure_reply" and value == "1":
                found_fields["disable_secure_reply"] = True
            elif name == "dry_run" and value == "1":
                found_fields["dry_run"] = True

        assert all(
            found_fields.values()
        ), f"Missing or incorrect fields: {[k for k, v in found_fields.items() if not v]}"

    async def test_signup_network_error(self, client, mocker):
        """Test signup with network connectivity issues."""
        mocker.patch("aiohttp.ClientSession.request", side_effect=ClientError())

        with pytest.raises(ConnectionError):
            await client.signup("agregu9hqbhqadqwdba", "goodemail@gmail.com")

    async def test_signup_api_error(self, client, mock_response, mocker):
        """Test signup with API error response."""
        mock_resp = mock_response({"error": "internal_error"}, status=500)
        mocker.patch("aiohttp.ClientSession.request", return_value=mock_resp)

        with pytest.raises(APIError):
            await client.signup("testuser", "test@example.com")

    @pytest.mark.parametrize(
        "user,email",
        [
            ("", "test@example.com"),
            ("test", ""),
            ("test", "invalid-email"),
        ],
    )
    async def test_signup_validation_errors(self, client, user, email):
        """Test signup with invalid input parameters."""
        with pytest.raises(ValidationError):
            await client.signup(user, email)

    async def test_signup_without_context(self):
        """Test signup without using context manager."""
        client = DuckMailClient()
        with pytest.raises(DuckMailError):
            await client.signup("agregu9hqbhqadqwdba", "goodemail@gmail.com")
