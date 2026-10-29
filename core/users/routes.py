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
from gettext import NullTranslations
from i18n.dependencies import get_language

router = APIRouter(prefix="/auth", tags=["Authentication"])

ACCESS_TOKEN_EXPIRE = 60 * 5


@router.post("/login")
def user_login(
    request: UserLoginSchema,
    response: Response,
    db: Session = Depends(get_db),
    translator: NullTranslations = Depends(get_language),
):
    user_obj = db.query(UserModel).filter_by(username=request.username.lower()).first()

    # Use a generic message for invalid credentials.
    if not user_obj or not user_obj.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=translator.gettext("Invalid username or password"),
        )

    set_auth_cookies(
        response,
        user_obj.id,
        token_version=user_obj.token_version,
    )

    return {"detail": translator.gettext("User logged in successfully")}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def user_register(
    request: UserRegisterSchema,
    db: Session = Depends(get_db),
    translator: NullTranslations = Depends(get_language),
):
    username = request.username.lower()

    if db.query(UserModel).filter_by(username=username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=translator.gettext("Username already exists"),
        )

    user_obj = UserModel(username=username)
    user_obj.set_password(request.password)

    db.add(user_obj)
    db.commit()

    return {"detail": translator.gettext("User registered successfully")}


@router.post("/refresh-token")
def user_refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    translator: NullTranslations = Depends(get_language),
):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=translator.gettext("Refresh token is missing"),
        )

    user_id, token_version = decode_refresh_token(refresh_token)

    user_obj = db.query(UserModel).filter_by(id=user_id).first()

    if user_obj is None or user_obj.token_version != token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=translator.gettext("Refresh token has been revoked"),
        )

    new_access_token = generate_access_token(
        user_obj.id,
        expires_in=ACCESS_TOKEN_EXPIRE,
        token_version=user_obj.token_version,
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

    return {"detail": translator.gettext("Access token refreshed successfully")}


@router.post("/logout")
def user_logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    translator: NullTranslations = Depends(get_language),
):
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        try:
            user_id, token_version = decode_refresh_token(refresh_token)

            user_obj = db.query(UserModel).filter_by(id=user_id).first()

            if user_obj and user_obj.token_version == token_version:
                user_obj.token_version += 1
                db.commit()

        except HTTPException:
            db.rollback()

    clear_auth_cookies(response)

    return {"detail": translator.gettext("Logged out successfully")}
