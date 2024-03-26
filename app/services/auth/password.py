from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
import bcrypt

from app.config import password_settings


async def hmac_hash_password(password: str) -> bytes:
    hmac_key = hmac.HMAC(
        password_settings.password_hash_secret, hashes.SHA256(), backend=default_backend()
    )
    hmac_key.update(password.encode("utf-8"))
    return hmac_key.finalize()

async def hash_password(password: str) -> str:
    hmac_hash = await hmac_hash_password(password)
    hashed = bcrypt.hashpw(hmac_hash, bcrypt.gensalt())
    return hashed.decode("utf-8")

async def check_password(hashed_password: str, password: str) -> bool:
    hmac_hash = await hmac_hash_password(password)
    return bcrypt.checkpw(hmac_hash, hashed_password.encode("utf-8"))



