import os
from fastapi import Header, HTTPException, status
"""
 API key authentication dependency to protect endpoints
 Expected usage:
 - Client sends header:  X-API-Key: <secret>
 - The secret is compared against the value stored in environment variables
"""
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = os.getenv("DROPZONE_API_KEY")
    if not expected:
        # If no API key is configured on the server, authentication is disabled (open access)
        return  
    
    # If the API key is missing or does not match the expected value,
    # reject the request with HTTP 401 Unauthorized
    if x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
