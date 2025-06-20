import re
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
from backend.constants import regex


class SignupValidator(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)
    confirm_password: str = Field(min_length=8, max_length=32)

    @field_validator("email")
    def validate_email(cls, email: str) -> str:
        if not re.match(regex.EMAIL_REGEX, email):
            raise ValueError("Invalid email format")
        return email

    @field_validator("name")
    def validate_name(cls, name: str) -> str:
        if not re.match(regex.NAME_REGEX, name):
            raise ValueError(
                "Name must be 3-50 characters long and contain only letters and spaces"
            )
        return name


class SigninValidator(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)

    @field_validator("email")
    def validate_email(cls, email: str) -> str:
        if not re.match(regex.EMAIL_REGEX, email):
            raise ValueError("Invalid email format")
        return email
