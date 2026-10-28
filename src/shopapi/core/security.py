from datetime import timedelta, datetime, timezone
import jwt
from pwdlib import PasswordHash
from shopapi.core.config import settings


password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(
        data: dict,
        expires_delta: timedelta | None = None,
) -> str:
    to_encode = data.copy() # копируем входящий словарь
    expire = datetime.now(timezone.utc) + (
            expires_delta if expires_delta else timedelta(minutes=settings.access_token_expire_minutes)
    ) # время жизни токена
    to_encode.update({"exp": expire}) # обязательное значение для JWT
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

