from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class CreditRequestCreationRequestDto(BaseModel):
    user_id: int = Field(..., alias="userId")
    account_id: int = Field(..., alias="accountId")
    amount: float = Field(..., alias="amount")


class CreditRequestByIdRequestDto(BaseModel):
    id: int = Field(..., alias="requestId")


class CreditRequestByUserIdRequestDto(BaseModel):
    user_id: int = Field(..., alias="userId")


class CreditRequestByStatusRequestDto(BaseModel):
    status: int = Field(..., alias="requestStatus")


class CreditRequestByAccountIdRequestDto(BaseModel):
    account_id: int = Field(..., alias="accountId")


class CreditRequestDataResponseDto(BaseModel):
    id: int = Field(..., alias="requestId")
    account_id: int = Field(..., alias="accountId")
    user_id: int = Field(..., alias="userId")
    score: Optional[int] = Field(..., alias="score")
    status: int = Field(..., alias="requestStatus")
    amount: float = Field(..., alias="amount")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        populate_by_name = True
