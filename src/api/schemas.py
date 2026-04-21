from fastapi import HTTPException
from bcrypt import hashpw, checkpw, gensalt
from pydantic import BaseModel, Field, field_validator
import re
from hashlib import sha256

def hash_password(password: str):
    password_hash = sha256(password.encode()).digest()
    return hashpw(password_hash, gensalt()).decode()

def verify_password(plain_password, hashed_password):
    password_hash = sha256(plain_password.encode()).digest()
    return checkpw(password_hash, hashed_password.encode())

class UserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    email: str = Field(min_length=6, max_length=50)
    # Добавь валидатор для проверки пароля

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str):
        pattern = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?\s]+$"
        if not re.match(pattern, password):
            raise HTTPException(status_code=400, detail="Incorrect password")
        return password


