from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field

__all__: list[str] = ["UserCreationRequestDto", "UserByEmailRequestDto", "UserByIdRequestDto", "UserByDocumentRequestDto", "UserDataResponseDto"]


class UserCreationRequestDto(BaseModel):
    email: EmailStr = Field(..., max_length=100, alias="emailAddress")
    name: str = Field(..., max_length=100, alias="firstName")
    last_name: str = Field(..., max_length=100, alias="lastName")
    document: int = Field(..., ge=0, alias="documentNumber")


class UserByEmailRequestDto(BaseModel):
    email: EmailStr = Field(..., max_length=100, alias="emailAddress")


class UserByIdRequestDto(BaseModel):
    id: int = Field(..., ge=0, alias="userId")


class UserByDocumentRequestDto(BaseModel):
    document: int = Field(..., ge=0, alias="documentNumber")


class UserDataResponseDto(BaseModel):
    id: int = Field(..., alias="userId")
    document: int = Field(..., alias="documentNumber")
    email: str = Field(..., alias="emailAddress")
    name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    is_validated: Optional[bool] = Field(..., alias="isValidated")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        populate_by_name = True
