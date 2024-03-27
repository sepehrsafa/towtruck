from typing import Optional
from datetime import datetime
from pydantic import UUID4, BaseModel, EmailStr, validator, Field
from .general import Response
from .user import UserAccount, UserAccountResponse
from app.models import AccidentStatus


class CreateStation(BaseModel):
    name: str
    location: str


class Station(CreateStation):
    id: int
    users: Optional[list[UserAccount]] = None


class StationRegular(CreateStation):
    id: int

class StationResponse(Response, Station):
    pass


class StationsResponse(Response):
    stations: list[Station]


class StatusUpdate(BaseModel):
    status: AccidentStatus


class ReportAccident(BaseModel):
    location: str
    description: Optional[str] = None
    assigned_station: int


class Accident(Response):
    id: int
    reported_by: UserAccount
    assigned_to: Optional[UserAccount] = None
    description: str
    location: str
    date_reported: datetime
    date_assigned: Optional[datetime] = None
    status: AccidentStatus
    assigned_station: StationRegular


class Accidents(Response):
    accidents: list[Accident]


class AddChat(BaseModel):
    message: str
    accident: int


class AccidentChat(BaseModel):
    id: int
    user: UserAccount
    message: str
    date_sent: datetime


class AccidentChats(Response):
    chats: list[AccidentChat]
