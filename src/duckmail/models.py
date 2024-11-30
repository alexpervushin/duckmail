"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field

class ClientConfig(BaseModel):
    """Configuration settings for the DuckMail client."""
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    base_url: str = Field(
        default="https://quack.duckduckgo.com/api",
        description="Base URL for the DuckDuckGo Email Protection API"
    )

class SignupRequest(BaseModel):
    """Request model for signup endpoint."""
    user: str = Field(..., description="Desired username for signup")
    email: str = Field(..., description="Email address for registration")
    disable_secure_reply: bool = Field(False, description="Flag to disable secure reply")
    dry_run: bool = Field(False, description="Flag to perform a dry run without actual registration")

class SignupResponse(BaseModel):
    """Response model for successful signup."""
    status: str = Field(..., description="Response status (valid)")
    user: str = Field(..., description="Confirmed username")

class SignupError(BaseModel):
    """Response model for signup error."""
    error: str = Field(..., description="Error code from the API")
