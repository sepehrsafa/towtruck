from tortoise import fields, models


class UserToken(models.Model):
    jti = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField("models.UserAccount", related_name="tokens")
    refresh_token = fields.CharField(max_length=2000)
    expire = fields.DatetimeField()

    class Meta:
        table = "user_tokens"
