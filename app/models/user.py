import uuid
from datetime import datetime, timedelta

import pytz
from tortoise import fields, models

from app.config import auth_settings
from app.schemas.auth import TokenResponse
from app.services.auth import check_password, create_access_token, hash_password
from app.utils.exception import TowTruckException
from app.utils.validation import is_valid_email, is_valid_phone_number

from .audit import AuditableModel
from .token import UserToken
from enum import Enum


class UserAccountType(str, Enum):
    HQ_EMPLOYEE = "HQ_EMPLOYEE"
    DRIVER = "DRIVER"


class UserAccount(AuditableModel):
    uuid = fields.UUIDField(pk=True, default=uuid.uuid4)
    username = fields.CharField(max_length=30, unique=True)
    type = fields.CharEnumField(UserAccountType)
    email = fields.CharField(max_length=150, null=True, unique=True)

    first_name = fields.CharField(max_length=100, null=True)
    last_name = fields.CharField(max_length=110, null=True)

    date_joined = fields.DatetimeField(auto_now_add=True)
    last_login = fields.DatetimeField(auto_now=True)

    hashed_password = fields.CharField(max_length=300, null=True)

    class Meta:
        table = "user_account"

    def __str__(self):
        return f"{self.username}"

    async def set_password(self, password: str) -> None:
        self.hashed_password = await hash_password(password)
        await self.save()

    async def check_password(self, password) -> bool:
        return await check_password(self.hashed_password, password)

    async def create_access_token(self) -> TokenResponse:
        jti = uuid.uuid4()
        refresh_expire = datetime.utcnow() + timedelta(
            days=auth_settings.refresh_token_expire_days
        )

        token: TokenResponse = await create_access_token(
            self.uuid,
            jti,
            self.username,
            self.email,
        )
        await UserToken.create(
            jti=jti,
            user=self,
            refresh_token=token.refresh_token,
            expire=refresh_expire,
        )
        return token

    @classmethod
    async def get_by_identifier(cls, identifier: str) -> "UserAccount":
        if is_valid_email(identifier):
            user_field = "email"
        else:
            user_field = "username"

        query = {user_field: identifier.lower()}

        user = await cls.get_or_none(**query)

        if not user:
            raise TowTruckException("E1002")

        return user
