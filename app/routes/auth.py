from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.models import UserAccount, UserToken
from app.schemas.auth import (
    TokenData,
    TokenResponse,
    RefreshTokenData,
    UsernamePasswordLoginRequest,
    RefreshTokenRequest,
)
from app.schemas.general import Response
from app.utils.exception import TowTruckException
from app.utils.response import responses
from app.services.auth import validate_refresh_token

from app.services.auth import hash_password, check_password

router = APIRouter(tags=["Authentication"])


# Internal function to handle password login logic
async def _password_login(data) -> TokenResponse:
    user: UserAccount = await UserAccount.get_by_identifier(data.username)
    if await user.check_password(data.password):
        return await user.create_access_token()
    raise TowTruckException("E1002")


# Endpoint for OAuth2 login
@router.post(
    "/oauth2",
    response_model=TokenResponse,
    responses=responses,
    include_in_schema=False,
)
async def oauth2_login(data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Login endpoint. This endpoint is used to get an access token for a user. The access token is used to authenticate the user for all other endpoints.
    """
    return await _password_login(data)


# Endpoint for password-based login
@router.post("/password", response_model=TokenResponse, responses=responses)
async def password_login(data: UsernamePasswordLoginRequest):
    """
    This endpoint is used to get an access token for a user.

    The access token is used to authenticate the user for all other endpoints.

    Future requests should include the access token in the Authorization header.

    """
    hashed_pass = await hash_password("mypassword")
    result = await check_password(hashed_pass, "mypassword")
    print(result)  # Should print True
    return await _password_login(data)


# Endpoint to refresh an access token
@router.post("/refresh", response_model=TokenResponse, responses=responses)
async def refresh_token(refresh_token: RefreshTokenRequest):
    """
    Refresh an access token

    This endpoint is used to get a new access token using a refresh token.

    The old refresh token is invalidated and a new refresh token is returned.
    """
    refresh_token_data: RefreshTokenData = await validate_refresh_token(
        refresh_token.refresh_token
    )

    # get token from db
    user_token: UserToken = await UserToken.get_or_none(jti=refresh_token_data.jti)

    if not user_token:
        raise TowTruckException("E1017")

    user: UserAccount = await user_token.user

    new_access_token: TokenResponse = await user.create_access_token()
    # delete old token
    await refresh_token.delete()
    return new_access_token


# Endpoint to logout a user
@router.post("/logout", response_model=Response, responses=responses)
async def logout(refresh_token: RefreshTokenRequest):
    """
    Logout a user

    This endpoint is used to logout a user.

    The refresh token is invalidated and the user is logged out.
    """
    refresh_token_data: RefreshTokenData = await validate_refresh_token(
        refresh_token.refresh_token
    )
    # get token from db
    user_token: UserToken = await UserToken.get_or_none(pk=refresh_token_data.jti)

    if not refresh_token:
        return Response()
    # delete old token
    await user_token.delete()
    return Response()
