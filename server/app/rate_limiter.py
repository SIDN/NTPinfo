from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
"""
Create a rate limiter instance using the client's IP address as the unique identifier.

This Limiter is used with FastAPI to enforce rate limiting on specific endpoints.
It uses `get_remote_address` to extract the client's IP from the request, ensuring
that limits are applied by ip address

Attributes:
    limiter (Limiter): The configured SlowAPI rate limiter instance.
"""
