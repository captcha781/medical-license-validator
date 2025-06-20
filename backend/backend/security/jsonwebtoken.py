import logging
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from beanie import PydanticObjectId
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, field_serializer

from backend.models.User import User
from backend.models.Token import Token
from backend.config.main import (
    JWT_ACCESS_EXPIRY,
    JWT_REFRESH_EXPIRY,
    JWT_ACCESS_KEY,
    JWT_REFRESH_KEY,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):
    session_id: str
    _id: str
    mode: str = ""
    exp: str | datetime

    @field_serializer("exp", check_fields=True)
    @classmethod
    def validate_exp(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v)
        return v


def generate_jwt_token(payload: dict, token_type: str) -> str:
    enc_data = payload.copy()

    expiry = (
        (datetime.now(tz=timezone.utc) + JWT_ACCESS_EXPIRY)
        if token_type == "access"
        else (datetime.now(tz=timezone.utc) + JWT_REFRESH_EXPIRY)
    )
    enc_key = JWT_ACCESS_KEY if token_type == "access" else JWT_REFRESH_KEY

    enc_token = jwt.encode({**enc_data, "exp": expiry}, enc_key, algorithm="HS256")

    return enc_token


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def verify_jwt_token(token: str, token_type: str) -> dict:
    try:
        dec_key = JWT_ACCESS_KEY if token_type == "access" else JWT_REFRESH_KEY

        payload = jwt.decode(token, dec_key, algorithms=["HS256"])

        non_bearer = token.replace("Bearer ", "")

        id: str = payload.get("_id")
        if not id:
            raise credentials_exception

        user_info = await Token.aggregate(
            {
                "$match": {
                    "user_id": PydanticObjectId(id),
                    "$or": [
                        {"access_token": non_bearer},
                        {"refresh_token": non_bearer},
                    ],
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "_id",
                    "as": "user_info",
                }
            },
            {"$unwind": "$user_info"},
        ).to_list()

        if not user_info:
            raise credentials_exception

        return user_info[0].get("user_info")

    except JWTError as e:
        logging.error(e)
        raise credentials_exception
    except Exception as e:
        logging.error(f"Unexpected error during JWT verification: {e}")
        raise credentials_exception


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    return await verify_jwt_token(token)
