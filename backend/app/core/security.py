from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from app.core.config import settings
import bcrypt



MAX_PASSWORD_LENGTH = 20

def hash_password(plainPassword):            
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(plainPassword.encode("utf-8"), salt)
    return hashed_bytes.decode("utf-8")

def check_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

