"""
Rate limiting singleton.

Exported as a module so that routers can import ``limiter`` without
creating a circular dependency through ``app.main``.
"""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings


def _rate_limit_key(request: Request) -> str:
    """Rate-limit key function.

    In production each request is keyed by the client IP.  In non-production
    environments a unique key is returned per request so that the limiter
    never actually triggers — this keeps the test suite clean without
    needing to reset limiter state between tests.
    """
    if settings.APP_ENV != "production":
        return f"dev-{id(request)}"
    return get_remote_address(request)


# Shared limiter instance imported by routers and registered on the app in main.py
limiter = Limiter(key_func=_rate_limit_key)
