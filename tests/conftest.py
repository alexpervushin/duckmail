"""
pytest fixtures and configuration.
"""
import pytest
import pytest_asyncio
from src.duckmail import DuckMailClient

@pytest_asyncio.fixture
async def client():
    """Fixture that provides a DuckMailClient instance."""
    async with DuckMailClient() as client:
        yield client

@pytest.fixture
def mock_response():
    """Fixture for creating mock aiohttp responses."""
    class MockResponse:
        def __init__(self, data, status=200):
            self._data = data
            self.status = status

        async def json(self):
            return self._data

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def __call__(self, *args, **kwargs):
            return self

    return lambda data, status=200: MockResponse(data, status)
