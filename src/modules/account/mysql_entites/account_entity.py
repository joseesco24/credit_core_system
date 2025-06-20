from datetime import datetime

from sqlmodel import Field
from sqlmodel import SQLModel


class AccountEntitie(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    __tablename__ = "account"  # type: ignore

    id: int = Field(nullable=False, primary_key=True)
    user_id: int = Field(nullable=False)
    amount: float = Field(nullable=False)
    created_at: datetime = Field(nullable=False, default_factory=datetime.now)
    updated_at: datetime = Field(nullable=False, default_factory=datetime.now)
