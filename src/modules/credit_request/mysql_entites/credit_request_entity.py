from datetime import datetime
from typing import Optional

from sqlmodel import Field
from sqlmodel import SQLModel


class CreditRequestEntitie(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    __tablename__ = "credit_request"  # type: ignore

    id: int = Field(nullable=False, primary_key=True)
    account_id: int = Field(nullable=False)
    user_id: int = Field(nullable=False)
    score: Optional[int] = Field(nullable=True)
    status: int = Field(nullable=False)
    amount: float = Field(nullable=True)
    created_at: datetime = Field(nullable=False, default_factory=datetime.now)
    updated_at: datetime = Field(nullable=False, default_factory=datetime.now)
