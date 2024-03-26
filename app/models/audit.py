import uuid
from enum import Enum

from tortoise import fields
from tortoise.models import Model
from app.utils.exception import TowTruckException


class TypeEnum(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class AuditLog(Model):
    uuid = fields.UUIDField(pk=True, default=uuid.uuid4)
    model_name = fields.CharField(max_length=255)
    model_pk = fields.CharField(max_length=255)
    type = fields.CharEnumField(TypeEnum)
    changes = fields.JSONField()
    timestamp = fields.DatetimeField(auto_now_add=True)
    changed_by = fields.ForeignKeyField(
        "models.UserAccount", related_name="audit_logs", null=True
    )


async def log_changes(instance, model_pk, type, changes, user=None):
    # check user type if string or object
    if user:
        if isinstance(user, str):
            user = user
        else:
            user = user.uuid

    await AuditLog.create(
        model_name=instance.__class__.__name__,
        model_pk=model_pk,
        type=type,
        changes=changes,
        changed_by_id=user,
    )


class AuditableModel(Model):
    class Meta:
        abstract = True

    async def save(self, *args, user=None, **kwargs):
        changes = {}
        new_instance = False

        original_instance = await type(self).get_or_none(pk=self.pk)
        if original_instance:
            for field in self._meta.fields_map.keys():
                original_value = getattr(original_instance, field)
                current_value = getattr(self, field)
                if original_value != current_value:
                    changes[field] = {
                        "old": str(original_value),
                        "new": str(current_value),
                    }
        else:
            new_instance = True
            for field in self._meta.fields_map.keys():
                current_value = getattr(self, field)
                changes[field] = {"old": None, "new": str(current_value)}

        await super().save(*args, **kwargs)
        if changes and new_instance:
            await log_changes(self, self.pk, TypeEnum.CREATE, changes, user=user)
        else:
            await log_changes(self, self.pk, TypeEnum.UPDATE, changes, user=user)

    async def get_or_exception(self, *args, **kwargs):
        data = await self.get_or_none(*args, **kwargs)
        if data is None:
            raise TowTruckException("E1023", 404)
