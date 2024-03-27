from fastapi import APIRouter, HTTPException, Security
from app.models.user import UserAccount
from app.schemas.user import (
    UserAccountCreateRequest,
    UserAccountResponse,
    AddUserToStation,
)
from app.models import Station
from typing import Annotated
from app.services.auth.utils import get_current_user

from app.utils.response import responses
from app.utils.exception import TowTruckException
from app.services.auth import hash_password
from app.queue import check_if_assign_is_possible


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

    user_account = await UserAccount.all().filter(uuid=user_account.uuid).first().prefetch_related("station")

    return user_account


# get all
@router.get("/", response_model=list[UserAccountResponse], responses=responses)
async def get_user_accounts(current_user: UserAccount = Security(get_current_user)):
    user_accounts = await UserAccount.all().prefetch_related("station")
    return user_accounts


@router.get("/me", response_model=UserAccountResponse, responses=responses)
async def get_me(current_user: UserAccount = Security(get_current_user)):

    current_user = await UserAccount.all().filter(uuid=current_user.uuid).first().prefetch_related("station")

    return current_user


# add user to station
@router.post("/add/station", response_model=UserAccountResponse, responses=responses)
async def add_user_to_station(data: AddUserToStation):
    user_account = await UserAccount.all().filter(uuid=data.user).first()
    if not user_account:
        raise TowTruckException("E1023", 404)

    station = await Station.all().filter(id=data.station).first()
    if not station:
        raise TowTruckException("E1024", 404)

    user_account.station = station
    await user_account.save()

    user_account = await UserAccount.all().filter(uuid=user_account.uuid).first().prefetch_related("station")

    await check_if_assign_is_possible(station.id)

    return user_account


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
