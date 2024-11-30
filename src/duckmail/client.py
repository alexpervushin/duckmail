"""
Async API client implementation for DuckMail.
"""

from typing import Optional, Union
import aiohttp
import logging
from .models import ClientConfig, SignupRequest, SignupResponse, SignupError
from .exceptions import DuckMailError, APIError, ValidationError, ConnectionError
from .utils.http import make_request


class DuckMailClient:
    def __init__(self, **config):
        self.config = ClientConfig(**config)
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = await self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close_session()

    async def _create_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession()

    async def _close_session(self):
        if self._session:
            await self._session.close()
            self._session = None

    async def signup(
        self,
        user: str,
        email: str,
        *,
        disable_secure_reply: bool = False,
        dry_run: bool = False,
    ) -> Union[SignupResponse, SignupError]:
        """
        Register a new user account with DuckDuckGo Email Protection.

        Args:
            user: Desired username for signup
            email: Email address for registration
            disable_secure_reply: Flag to disable secure reply feature
            dry_run: Flag to perform a dry run without actual registration

        Returns:
            SignupResponse on success, or SignupError if the request fails

        Raises:
            APIError: If the API returns an error response
            ValidationError: If the request parameters are invalid
            ConnectionError: If there are network connectivity issues
        """
        if not self._session:
            raise DuckMailError("Client session not initialized")

        logging.info(f"Attempting signup for user: {user}")
        logging.info(
            f"Request parameters: user={user}, email={email}, disable_secure_reply={disable_secure_reply}, dry_run={dry_run}"
        )

        if not user or not isinstance(user, str):
            raise ValidationError("Username is required and must be a string")
        if not email or not isinstance(email, str):
            raise ValidationError("Email is required and must be a string")
        if "@" not in email or "." not in email:
            raise ValidationError("Invalid email format")

        request = SignupRequest(
            user=user,
            email=email,
            disable_secure_reply=disable_secure_reply,
            dry_run=dry_run,
        )

        form_data = aiohttp.FormData()
        form_data.add_field("user", request.user)
        form_data.add_field("email", request.email)
        if request.disable_secure_reply:
            form_data.add_field("disable_secure_reply", "1")
        if request.dry_run:
            form_data.add_field("dry_run", "1")

        try:
            data = await make_request(
                self._session,
                "POST",
                f"{self.config.base_url}/auth/signup",
                data=form_data,
            )

            logging.info(f"Received response data: {data}")

            if "error" in data:
                logging.warning(f"Signup failed for user: {user} - {data['error']}")
                return SignupError(**data)
            else:
                logging.info(f"Signup successful for user: {user}")
                return SignupResponse(**data)

        except (APIError, ConnectionError) as e:
            logging.error(f"Request error during signup: {str(e)}")
            raise
        except ValidationError as e:
            logging.error(f"Validation error during signup: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error during signup: {str(e)}")
            raise DuckMailError(f"Signup failed: {str(e)}")
