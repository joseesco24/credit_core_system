from src.modules.credit_request.mysql_entites.credit_request_entity import CreditRequestEntitie
from src.modules.credit_request.rest_controllers_dtos.credit_request_dtos import CreditRequestDataResponseDto


class CreditRequestMappers:
    @staticmethod
    def credit_request_entitie_2_credit_request_response_dto(credit_request_entite: CreditRequestEntitie) -> CreditRequestDataResponseDto:
        response = CreditRequestDataResponseDto(
            id=credit_request_entite.id,  # type: ignore
            account_id=credit_request_entite.account_id,  # type: ignore
            user_id=credit_request_entite.user_id,  # type: ignore
            score=credit_request_entite.score,  # type: ignore
            status=credit_request_entite.status,  # type: ignore
            amount=credit_request_entite.amount,  # type: ignore
            created_at=credit_request_entite.created_at,  # type: ignore
            updated_at=credit_request_entite.updated_at,  # type: ignore
        )
        return response
