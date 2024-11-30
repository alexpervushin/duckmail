"""
HTTP-related utilities for the DuckMail client.
"""
from typing import Dict, Any
import aiohttp
import logging
from ..exceptions import APIError, ConnectionError

async def make_request(
    session: aiohttp.ClientSession,
    method: str,
    url: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Make an HTTP request with error handling.
    
    Args:
        session: The aiohttp client session
        method: HTTP method to use
        url: The URL to request
        **kwargs: Additional arguments to pass to the request
        
    Returns:
        Dict containing the JSON response
        
    Raises:
        APIError: If the server returns an error response
        ConnectionError: If there are network connectivity issues
    """
    try:
        async with session.request(method, url, **kwargs) as response:
            logging.info(f"Response status: {response.status}")
            data = await response.json()
            logging.info(f"Response data: {data}")
            
            if response.status >= 500 or (response.status >= 400 and 'error' not in data):
                raise APIError(data.get('error', 'Unknown API error'))
            
            return data
    except aiohttp.ClientError as e:
        raise ConnectionError(f"Request failed: {str(e)}")
