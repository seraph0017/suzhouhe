"""
Authentication Middleware
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from jose import JWTError, jwt

from app.config import settings
from app.database import SessionLocal
from app.models.user import User


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT authentication"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip authentication for these paths
        skip_paths = [
            "/api/auth/login",
            "/api/auth/refresh",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/",
            "/health",
        ]

        # Check if path should skip authentication
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)

        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(
                content='{"detail": "Missing or invalid authorization header"}',
                status_code=401,
                media_type="application/json",
            )

        token = auth_header.split(" ")[1]

        # Validate token
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            token_type = payload.get("type")

            if token_type != "access":
                return Response(
                    content='{"detail": "Invalid token type"}',
                    status_code=401,
                    media_type="application/json",
                )

            # Get user from database
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if not user or not user.is_active:
                    return Response(
                        content='{"detail": "User not found or inactive"}',
                        status_code=401,
                        media_type="application/json",
                    )

                # Store user in request state
                request.state.current_user = user
                request.state.db = db
            finally:
                db.close()

        except JWTError:
            return Response(
                content='{"detail": "Invalid or expired token"}',
                status_code=401,
                media_type="application/json",
            )

        # Continue with request
        return await call_next(request)
