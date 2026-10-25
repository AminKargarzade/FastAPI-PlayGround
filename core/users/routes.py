from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from users.schemas import UserLoginSchema, UserRegisterSchema
from users.models import UserModel
from core.database import get_db
from core.config import settings
from auth.cookies import set_auth_cookies, clear_auth_cookies
from auth.jwt_cookie_auth import (
    generate_access_token,
    decode_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

ACCESS_TOKEN_EXPIRE = 60 * 5


@router.post("/login")
def user_login(
    request: UserLoginSchema,
    response: Response,
    db: Session = Depends(get_db),
):
    user_obj = db.query(UserModel).filter_by(username=request.username.lower()).first()

    # Use a generic message for invalid credentials.
    if not user_obj or not user_obj.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    set_auth_cookies(response, user_obj.id)

    return {"detail": "User logged in successfully"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def user_register(
    request: UserRegisterSchema,
    db: Session = Depends(get_db),
):
    username = request.username.lower()

    if db.query(UserModel).filter_by(username=username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    user_obj = UserModel(username=username)
    user_obj.set_password(request.password)

    db.add(user_obj)
    db.commit()

    return {"detail": "User registered successfully"}


@router.post("/refresh-token")
def user_refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing",
        )

    user_id = decode_refresh_token(refresh_token)

    user_obj = db.query(UserModel).filter_by(id=user_id).first()

    if user_obj is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    new_access_token = generate_access_token(
        user_obj.id,
        expires_in=ACCESS_TOKEN_EXPIRE,
    )

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        max_age=ACCESS_TOKEN_EXPIRE,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        path="/",
    )

    return {"detail": "Access token refreshed successfully"}


@router.post("/logout")
def user_logout(response: Response):
    clear_auth_cookies(response)

    return {"detail": "Logged out successfully"}
