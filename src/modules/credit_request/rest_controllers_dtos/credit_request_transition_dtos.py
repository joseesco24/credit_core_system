from pydantic import BaseModel
from pydantic import Field


class CreditRequestMakeTransitionRequestDto(BaseModel):
    transition: int = Field(..., alias="transitionId")
    id: int = Field(..., alias="requestId")
