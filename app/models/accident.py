from .audit import AuditableModel
from .user import UserAccount
from tortoise import fields, models
from enum import Enum


class Station(AuditableModel):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200)
    location = fields.CharField(max_length=200)

    class Meta:
        table = "station"


class AccidentStatus(str, Enum):
    REPORTED = "REPORTED"
    ON_THE_WAY = "ON_THE_WAY"
    PICKED_UP = "PICKED_UP"
    COMPLETED = "COMPLETED"


class Accident(AuditableModel):
    id = fields.IntField(pk=True)
    reported_by = fields.ForeignKeyField("models.UserAccount", related_name="accidents")
    assigned_to = fields.ForeignKeyField(
        "models.UserAccount", related_name="assigned_accidents", null=True
    )
    description = fields.TextField()
    location = fields.CharField(max_length=200)
    date_reported = fields.DatetimeField(auto_now_add=True)
    date_assigned = fields.DatetimeField(null=True)
    status = fields.CharEnumField(AccidentStatus, default=AccidentStatus.REPORTED)

    class Meta:
        table = "accident"


class AccidentChat(AuditableModel):
    id = fields.IntField(pk=True)
    accident = fields.ForeignKeyField("models.Accident", related_name="chats")
    user = fields.ForeignKeyField("models.UserAccount", related_name="chats")
    message = fields.TextField()
    date_sent = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "accident_chat"
