from typing import Any
from typing import List
from typing import Union
from ariadne import QueryType
from ariadne import load_schema_from_path
from ariadne import make_executable_schema
from graphql import GraphQLSchema
from pathlib import Path
from ariadne.asgi import GraphQL
from starlette.routing import Route
from ariadne.validation import cost_validator
from modules.account.services.account_service import AccountService
from src.sidecard.system.artifacts.env_provider import EnvProvider
from src.sidecard.system.artifacts.path_provider import PathProvider
from src.sidecard.system.graphql.error_formatter import error_formatter
from modules.user.rest_controllers_dtos.user_dtos import UserDataResponseDto
from src.sidecard.system.graphql.custom_scalars_serializer import float_scalar
from src.sidecard.system.graphql.custom_scalars_serializer import integer_scalar

__all__: list[str] = ["account_gpl_controller"]

# ** info: building router core
_account_service: AccountService = AccountService()

# ** info: building sidecards
_path_provider: PathProvider = PathProvider()
_env_provider: EnvProvider = EnvProvider()  # type: ignore

# ---------------------------------------------------------------------------------------------------------------------
# ** info: assembling schema literal
# ---------------------------------------------------------------------------------------------------------------------

current_file_path: Path = Path(__file__).parent.resolve()
schema_path: Path = Path(current_file_path, "..", "graphql_controllers_dtos", "account_dtos.graphql")
schema_literal: str = load_schema_from_path(path=str(schema_path))

# ---------------------------------------------------------------------------------------------------------------------
# ** info: assembling querie facades with resolvers
# ---------------------------------------------------------------------------------------------------------------------

query: QueryType = QueryType()


@query.field("getAccountByFilters")
async def get_user_by_filters(*_: Any, accountId: Union[int, None] = None, userId: Union[int, None] = None) -> List[UserDataResponseDto]:
    account_full_data_reponse: List[UserDataResponseDto] = await _account_service.get_account_by_filters_orchestator(id=accountId, user_id=userId)
    return account_full_data_reponse


# ---------------------------------------------------------------------------------------------------------------------
# ** info: assembling schema literal with schema executable
# ---------------------------------------------------------------------------------------------------------------------

schema_executable: GraphQLSchema = make_executable_schema(schema_literal, query, integer_scalar, float_scalar)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: assembling schema executable with graphql endpoint
# ---------------------------------------------------------------------------------------------------------------------

graphql_endpoint_definition: GraphQL = GraphQL(
    introspection=False if _env_provider.app_environment_mode == "production" else True,
    debug=False if _env_provider.app_environment_mode == "production" else True,
    validation_rules=[cost_validator(maximum_cost=5)],
    error_formatter=error_formatter.formatter,
    schema=schema_executable,
)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: assembling graphql endpoint with the main router
# ---------------------------------------------------------------------------------------------------------------------

account_gpl_controller: Route = Route(path=_path_provider.build_posix_path("account"), endpoint=graphql_endpoint_definition)
