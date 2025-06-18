from datetime import datetime
from sqlmodel import Field
from sqlmodel import SQLModel


class UserEntitie(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    __tablename__ = "user"  # type: ignore

    id: int = Field(nullable=False, primary_key=True)
    document: int = Field(nullable=False)
    email: str = Field(nullable=False, max_length=100, unique=True)
    name: str = Field(nullable=False, max_length=100)
    last_name: str = Field(nullable=False, max_length=100)
    is_validated: bool = Field(nullable=True)
    created_at: datetime = Field(nullable=False, default_factory=datetime.now)
    updated_at: datetime = Field(nullable=False, default_factory=datetime.now)
