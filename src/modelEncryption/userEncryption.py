from typing import Tuple
from models.user import User
from services.crypto_utils import encrypt, decrypt
import bcrypt
from datetime import datetime

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def user_to_encrypted_row(user: User) -> Tuple:
    return (
        encrypt(user.username),
        user.password_hash,  # already hashed deos not need to be encrypted
        user.role,
        encrypt(user.first_name),
        encrypt(user.last_name),
        user.registration_date.isoformat()
    )

def row_to_user(row: tuple) -> User:
    return User(
        username=decrypt(row[0]),
        password_hash=row[1],
        role=row[2],
        first_name=decrypt(row[3]),
        last_name=decrypt(row[4]),
        registration_date=datetime.fromisoformat(row[5])
    )
