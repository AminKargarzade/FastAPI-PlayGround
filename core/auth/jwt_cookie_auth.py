from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from core.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import (
    DecodeError,
    InvalidSignatureError,
    ExpiredSignatureError,
    InvalidTokenError,
)
from core.config import settings
from users.models import UserModel

security = HTTPBearer()


# def get_authenticated_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db: Session = Depends(get_db),
# ):

#     token = credentials.credentials
#     try:
#         decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms="HS256")
#         user_id = decoded.get("user_id", None)
#         if not user_id:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Authentication Failed: user_id not in the payload",
#             )

#         if decoded.get("type") != "access":
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
#             )

#         if datetime.now() > datetime.fromtimestamp(decoded.get("exp")):  # type: ignore
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
#             )

#         user_obj = (
#             db.query(UserModel).filter_by(id=user_id).one()
#         )  # Check if user exists in the database
#         return user_obj

#     except InvalidSignatureError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature"
#         )
#     except DecodeError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Error decoding token"
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=f"Authentication Failed: {str(e)}",
#         )


def get_authenticated_user(
    request: Request,
    db: Session = Depends(get_db),
):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is missing",
        )

    try:
        decoded = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"],
        )

        if decoded.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        user_id = decoded.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user_id missing from token",
            )

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired",
        )

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    user_obj = db.query(UserModel).filter_by(id=user_id).first()

    if user_obj is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user_obj


def generate_access_token(user_id: int, expires_in: int = 60 * 5) -> str:
    now = datetime.utcnow()
    payload = {
        "type": "access",
        "user_id": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def generate_refresh_token(user_id: int, expires_in: int = 3600 * 24) -> str:
    now = datetime.utcnow()
    payload = {
        "type": "refresh",
        "user_id": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def decode_refresh_token(token: str) -> int:
    try:
        decoded = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"],
        )

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if decoded.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = decoded.get("user_id")

    if not isinstance(user_id, int) or isinstance(user_id, bool):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user_id in token",
        )

    return user_id
