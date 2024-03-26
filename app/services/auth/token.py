from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import JWTError, jwt
from pydantic import ValidationError

from app.config import auth_settings
from app.schemas.auth import RefreshTokenData, TokenData, TokenResponse
from app.utils.exception import TowTruckException


async def create_access_token(
    uuid, jti,username, email
):
    expire = datetime.utcnow() + timedelta(minutes=auth_settings.access_token_expire_minutes)
    refresh_expire = datetime.utcnow() + timedelta(
        days=auth_settings.refresh_token_expire_days
    )
    refresh_data = {
        "sub": str(uuid),
        "exp": refresh_expire,
        "token_type": "refresh",
        "jti": str(jti),
    }

    data = {
        "sub": str(uuid),
        "username": username,
        "email": email,
        "exp": expire,
        "token_type": "access",
    }
    token = jwt.encode(data, auth_settings.secret_key, algorithm=auth_settings.algorithm)
    refresh_token = jwt.encode(
        refresh_data, auth_settings.secret_key, algorithm=auth_settings.algorithm
    )
    return TokenResponse(
        access_token=token, refresh_token=refresh_token, token_type="bearer"
    )


async def validate_token(security_scopes, token):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, auth_settings.secret_key, algorithms=[auth_settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_type = payload.get("token_type")
        if token_type != "access":
            raise credentials_exception
    except (JWTError, ValidationError) as e:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return TokenData(**payload)


async def validate_refresh_token(token):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, auth_settings.secret_key, algorithms=[auth_settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_type = payload.get("type")
        if token_type != "refresh":
            raise credentials_exception
    except (JWTError, ValidationError) as e:
        raise credentials_exception

    return RefreshTokenData(**payload)
