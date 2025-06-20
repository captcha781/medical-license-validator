from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from backend.constants import enums

class ReportHistory(Document):
    user_id: PydanticObjectId
    report_id: str
    
    credential_type: str
    credential_path: str
    
    validator_type: str
    validator_path: str
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: enums.ReportStatus = Field(default=enums.ReportStatus.PENDING)
    