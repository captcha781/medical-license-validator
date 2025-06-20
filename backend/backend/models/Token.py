from datetime import datetime
from pydantic import Field
from uuid import UUID
from beanie import Document, PydanticObjectId


class Token(Document):
    user_id: PydanticObjectId
    session_id: UUID
    access_token: str
    refresh_token: str
    expiration_time: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "tokens"
