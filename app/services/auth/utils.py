from app.models.user import UserAccount
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from typing import Annotated
from fastapi import Depends
from .token import validate_token
from app.utils.exception import TowTruckException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/oauth2")


async def get_current_user(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
):
    token_data = await validate_token(security_scopes, token)
    user = await UserAccount.get_or_none(pk=token_data.sub)
    return user
