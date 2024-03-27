from typing import Optional

from pydantic import UUID4, BaseModel, EmailStr, validator, Field


from .general import Response, Password
from app.models import UserAccountType
import datetime


class UserAccountCreateRequest(Password):
    username: str
    type: UserAccountType
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserAccount(BaseModel):
    uuid: UUID4
    username: str
    type: UserAccountType
    email: Optional[EmailStr] = None


class UserAccountResponse(Response):
    uuid: UUID4
    username: str
    type: UserAccountType
    is_user_on_duty: bool
    station_id: Optional[int] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_joined: datetime.datetime
    last_login: datetime.datetime


class AddUserToStation(BaseModel):
    user: UUID4
    station: int
