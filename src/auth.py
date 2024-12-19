from passlib.context import CryptContext
from pydantic import EmailStr
from jose import jwt
from sqlalchemy import text
from typing import List

from datetime import (
    datetime,
    timedelta,
    timezone
)

from src.db.database import async_session
from src.config import get_jwt_params


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=2)
    to_encode.update({"exp": expire})

    jwt_params = get_jwt_params()
    encoded_jwt = jwt.encode(to_encode, jwt_params['secret_key'], algorithm=jwt_params['algorithm'])

    return encoded_jwt


async def authenticate_user(email: EmailStr, password: str):
    async with async_session() as session:
        async with session.begin():
            mail_check_query = text(
                '''
                SELECT user_id, role
                FROM users
                WHERE email = :email
                '''
            )
            result = await session.execute(mail_check_query, {'email': email})
            user = result.fetchone()

            password_check_query = text(
                '''
                SELECT password_hash
                FROM users
                WHERE user_id = :user_id
                '''
            )
            result = await session.execute(password_check_query, {'user_id': int(user.user_id)})
            password_hash = result.scalar()

            if user is None or verify_password(plain_password=password, hashed_password=password_hash) is False:
                return None

            return {"user_id": user.user_id, "role": user.role}