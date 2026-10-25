from fastapi import Response

from auth.jwt_cookie_auth import (
    generate_access_token,
    generate_refresh_token,
)
from core.config import settings

ACCESS_TOKEN_EXPIRE = 60 * 5
REFRESH_TOKEN_EXPIRE = 60 * 60 * 24

# Use False only for local HTTP development.
COOKIE_SECURE = settings.COOKIE_SECURE


def set_auth_cookies(response: Response, user_id: int) -> None:
    access_token = generate_access_token(
        user_id,
        expires_in=ACCESS_TOKEN_EXPIRE,
    )

    refresh_token = generate_refresh_token(
        user_id,
        expires_in=REFRESH_TOKEN_EXPIRE,
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=REFRESH_TOKEN_EXPIRE,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=COOKIE_SECURE,
        httponly=True,
        samesite="lax",
    )

    response.delete_cookie(
        key="refresh_token",
        path="/",
        secure=COOKIE_SECURE,
        httponly=True,
        samesite="lax",
    )
