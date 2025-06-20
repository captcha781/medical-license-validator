from beanie import Document, PydanticObjectId
from pydantic import Field, EmailStr
from typing import Optional
from datetime import datetime
from backend.constants.enums import UserStatus


class User(Document):
    name: str = Field(default="")
    email: EmailStr = Field(unique=True)
    password: str = Field(default="")
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(default=None)

    class Settings:
        collection = "users"
