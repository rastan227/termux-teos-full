from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.security_service import SecurityService
from app.core.redis_client import redis_client
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        path = request.url.path
        
        # Skip rate limit for health check
        if path == "/health":
            return await call_next(request)
        
        key = f"rate_limit:ip:{client_ip}:{path}"
        current = await redis_client.get(key)
        if current and int(current) > 100:  # 100 requests per minute
            raise HTTPException(status_code=429, detail="Too many requests")
        await redis_client.incr(key)
        await redis_client.expire(key, 60)
        
        response = await call_next(request)
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
