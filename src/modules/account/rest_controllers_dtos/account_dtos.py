from datetime import datetime
from pydantic import Field
from pydantic import BaseModel

__all__: list[str] = ["AccountCreationRequestDto", "AccountByIdRequestDto", "AccountByUserIdRequestDto", "AccountDataResponseDto"]


class AccountCreationRequestDto(BaseModel):
    user_id: int = Field(..., alias="userId")


class AccountByIdRequestDto(BaseModel):
    id: int = Field(..., alias="accountId")


class AccountByUserIdRequestDto(BaseModel):
    user_id: int = Field(..., alias="userId")


class AccountDataResponseDto(BaseModel):
    id: int = Field(..., alias="accountId")
    user_id: int = Field(..., alias="userId")
    amount: float = Field(..., alias="availableAmount")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        populate_by_name = True
