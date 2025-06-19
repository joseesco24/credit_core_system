from modules.account.mysql_entites.account_entity import AccountEntitie
from modules.account.rest_controllers_dtos.account_dtos import AccountDataResponseDto


class AccountMappers:
    @staticmethod
    def account_entitie_2_account_data_response_dto(account_entite: AccountEntitie) -> AccountDataResponseDto:
        return AccountDataResponseDto(
            id=account_entite.id,  # type: ignore
            user_id=account_entite.user_id,  # type: ignore
            amount=account_entite.amount,  # type: ignore
            created_at=account_entite.created_at,  # type: ignore
            updated_at=account_entite.updated_at,  # type: ignore
        )
