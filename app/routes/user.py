from fastapi import APIRouter, HTTPException, Security
from app.models.user import UserAccount
from app.schemas.user import UserAccountCreateRequest, UserAccountResponse
from typing import Annotated
from app.services.auth.utils import get_current_user

from app.utils.response import responses
from app.utils.exception import TowTruckException
from app.services.auth import hash_password

router = APIRouter(
    tags=["User Account"],
)


# create create, update, delete, get, list
@router.post("/", response_model=UserAccountResponse, responses=responses)
async def create_user_account(data: UserAccountCreateRequest):
    # remove password from data
    hashed_password = await hash_password(data.password)
    data = data.dict()
    data.pop("password")
    user_account = await UserAccount.create(**data, hashed_password=hashed_password)
    return user_account


"""
# get all
@router.get("/", response_model=list[UserAccountResponse], responses=responses)
async def get_user_accounts(current_user: UserAccount = Security(get_current_user)):
    user_accounts = await UserAccount.all()
    return user_accounts
"""


@router.get("/me", response_model=UserAccountResponse, responses=responses)
async def get_me(current_user: UserAccount = Security(get_current_user)):
    return current_user


"""
@router.get("/{uuid}", response_model=UserAccountResponse, responses=responses)
async def get_user_account(
    uuid: str, current_user: UserAccount = Security(get_current_user)
):
    user_account = UserAccount.all().filter(uuid=uuid).first()
    return user_account


@router.put("/{uuid}", response_model=UserAccountResponse, responses=responses)
async def update_user_account(
    uuid: str,
    data: UserAccountCreateRequest,
    current_user: UserAccount = Security(get_current_user),
):
    user_account = UserAccount.all().filter(uuid=uuid).first()

    if not user_account:
        raise TowTruckException("E1023", 404)

    user_account.update(**data.dict())

    return user_account
"""
