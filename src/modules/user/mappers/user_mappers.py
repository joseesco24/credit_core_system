from modules.user.mysql_entites.user_entity import UserEntitie
from modules.user.rest_controllers_dtos.user_dtos import UserDataResponseDto


class UserMappers:
    @staticmethod
    def user_entitie_2_user_data_response_dto(user_entite: UserEntitie) -> UserDataResponseDto:
        return UserDataResponseDto(
            id=user_entite.id,  # type: ignore
            document=user_entite.document,  # type: ignore
            email=user_entite.email,  # type: ignore
            name=user_entite.name,  # type: ignore
            last_name=user_entite.last_name,  # type: ignore
            is_validated=user_entite.is_validated,  # type: ignore
            created_at=user_entite.created_at.isoformat(),  # type: ignore
            updated_at=user_entite.updated_at.isoformat(),  # type: ignore
        )
