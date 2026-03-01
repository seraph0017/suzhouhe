"""
Token schemas for authentication
"""

from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """Token payload"""
    sub: Optional[int] = None
    exp: Optional[int] = None
    type: Optional[str] = None
