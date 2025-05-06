from __future__ import annotations

import time
from typing import Callable, Dict, Optional, Any
from functools import wraps
from fastapi import Request, Depends
from .errors import AuthenticationError, AuthorizationError, RateLimitError
from nexon.OAuth2 import OAuth2Session

def require_auth(func: Callable) -> Callable:
    """Decorator to require authentication for routes"""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        token = await request.app.state.backend.verify_auth(request)
        if not token:
            raise AuthenticationError()
        return await func(request, *args, **kwargs)
    return wrapper

def require_permissions(*required_perms: str) -> Callable:
    """Decorator to require specific permissions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            token = await request.app.state.backend.verify_auth(request)
            if not token:
                raise AuthenticationError()
                
            # Get user permissions
            user = await request.app.state.backend.oauth.get_user(token)
            user_perms = user.get("permissions", [])
            
            # Check permissions
            if not all(perm in user_perms for perm in required_perms):
                raise AuthorizationError()
                
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

def rate_limit(
    max_requests: int,
    per_seconds: int = 60
) -> Callable:
    """Decorator for route-specific rate limiting"""
    def decorator(func: Callable) -> Callable:
        # Store rate limit state
        state: Dict[str, list[float]] = {}
        
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Implement per-route rate limiting here
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()
            
            # Clean old requests
            if client_ip in state:
                state[client_ip] = [
                    req_time for req_time in state[client_ip]
                    if now - req_time < per_seconds
                ]
            
            # Check rate limit
            if client_ip in state and len(state[client_ip]) >= max_requests:
                raise RateLimitError()
                
            # Add request
            if client_ip not in state:
                state[client_ip] = []
            state[client_ip].append(now)
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator