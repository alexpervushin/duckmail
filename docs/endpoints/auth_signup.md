# DuckDuckGo Auth Signup API

## Endpoint Details

- **URL**: `https://quack.duckduckgo.com/api/auth/signup`
- **Method**: POST
- **Content-Type**: multipart/form-data

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user | string | Yes | Desired username for signup |
| email | string | Yes | Email address for registration |
| disable_secure_reply | string | No | Flag to disable secure reply (value: "1") |
| dry_run | string | No | Flag to perform a dry run without actual registration (value: "1") |

## Response Structure

### Success Response (200)

```json
{
    "status": "valid",
    "user": "<username>"
}
```

### Error Responses (400)

The API returns a 400 status code with different error messages:

```json
{"error": "unavailable_username"}  // When username is already taken
{"error": "failed_mx_check"}      // When email MX record check fails
{"error": "duck_address_not_allowed"}  // When using a @duck.com email address
```

## Dependencies

- Python 3.x
- aiohttp library
- asyncio library

## Implementation Details

The endpoint is implemented using asynchronous HTTP requests with the following characteristics:

- Uses `aiohttp.ClientSession` for making HTTP requests
- Implements form data submission using `aiohttp.FormData`
- Handles both successful and error responses
- Performs synchronous execution using `asyncio.run()`

## Usage Example

```python
import aiohttp
import asyncio

async def signup():
    url = "https://quack.duckduckgo.com/api/auth/signup"
    form_data = aiohttp.FormData()
    form_data.add_field("user", "username")
    form_data.add_field("email", "user@example.com")
    form_data.add_field("disable_secure_reply", "1")
    form_data.add_field("dry_run", "1")

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=form_data) as response:
            return await response.text()

asyncio.run(signup())
```

## Known Limitations

1. Email Domain Restrictions:
   - @duck.com email addresses are not allowed
   - Email domain must have valid MX records

2. Username Limitations:
   - Usernames must be unique
   - Previously used usernames cannot be reused

## Notes

- The implementation includes a dry run mode for testing signup without actual registration
- The API performs email validation including MX record checks
- All responses are in JSON format
- The implementation uses form data for request submission rather than JSON
