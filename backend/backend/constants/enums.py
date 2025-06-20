from enum import Enum


class UserStatus(Enum):
    ACTIVE = "active"
    DELETED = "deleted"


class ReportStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
