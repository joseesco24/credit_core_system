# !/usr/bin/python3
# type: ignore

from modules.user.mysql_entites.user_entity import UserEntitie
from modules.user.rest_controllers_dtos.user_dtos import UserDataResponseDto


class UserMappers:
    @staticmethod
    def user_entitie_2_user_data_response_dto(user_entite: UserEntitie) -> UserDataResponseDto:
        return UserDataResponseDto(
            id=user_entite.id,
            document=user_entite.document,
            email=user_entite.email,
            name=user_entite.name,
            last_name=user_entite.last_name,
            is_validated=user_entite.is_validated,
            created_at=user_entite.created_at.isoformat(),
            updated_at=user_entite.updated_at.isoformat(),
        )
