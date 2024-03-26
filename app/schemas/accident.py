from typing import Optional
from datetime import datetime
from pydantic import UUID4, BaseModel, EmailStr, validator, Field
from .general import Response
from .user import UserAccount
from app.models import AccidentStatus


class ReportAccident(BaseModel):
    location: str
    description: Optional[str] = None


class Accident(Response):
    id: int
    reported_by: UserAccount
    assigned_to: Optional[UserAccount] = None
    description: str
    location: str
    date_reported: datetime
    date_assigned: Optional[datetime] = None
    status: AccidentStatus


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
