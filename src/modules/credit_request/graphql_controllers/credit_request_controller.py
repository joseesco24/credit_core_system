from pathlib import Path
from typing import Any
from typing import Union

from ariadne import QueryType
from ariadne import load_schema_from_path
from ariadne import make_executable_schema
from ariadne.asgi import GraphQL
from ariadne.validation import cost_validator
from graphql import GraphQLSchema
from starlette.routing import Route

from src.modules.credit_request.rest_controllers_dtos.credit_request_dtos import CreditRequestDataResponseDto
from src.modules.credit_request.services.credit_request_service import CreditRequestService
from src.sidecard.system.artifacts.env_provider import EnvProvider
from src.sidecard.system.artifacts.path_provider import PathProvider
from src.sidecard.system.graphql.custom_scalars_serializer import float_scalar
from src.sidecard.system.graphql.custom_scalars_serializer import integer_scalar
from src.sidecard.system.graphql.error_formatter import error_formatter

__all__: list[str] = ["credit_request_gpl_controller"]

# ** info: building router core
_credit_request_service: CreditRequestService = CreditRequestService()

# ** info: building sidecards
_path_provider: PathProvider = PathProvider()
_env_provider: EnvProvider = EnvProvider()  # type: ignore

# ---------------------------------------------------------------------------------------------------------------------
# ** info: assembling schema literal
# ---------------------------------------------------------------------------------------------------------------------

current_file_path: Path = Path(__file__).parent.resolve()
schema_path: Path = Path(current_file_path, "..", "graphql_controllers_dtos", "credit_request_dtos.graphql")
schema_literal: str = load_schema_from_path(path=str(schema_path))

# ---------------------------------------------------------------------------------------------------------------------
# ** info: assembling querie facades with resolvers
# ---------------------------------------------------------------------------------------------------------------------

query: QueryType = QueryType()


@query.field("getCreditRequestByFilters")
async def get_user_by_filters(
    *_: Any,
    requestId: Union[int, None] = None,
    accountId: Union[int, None] = None,
    userId: Union[int, None] = None,
    score: Union[int, None] = None,
    requestStatus: Union[int, None] = None,
) -> list[CreditRequestDataResponseDto]:
    credit_request_full_data_reponse: list[CreditRequestDataResponseDto] = await _credit_request_service.get_credit_request_by_filters_orchestator(
        id=requestId, account_id=accountId, user_id=userId, score=score, status=requestStatus
    )
    return credit_request_full_data_reponse


# ---------------------------------------------------------------------------------------------------------------------
# ** info: assembling schema literal with schema executable
# ---------------------------------------------------------------------------------------------------------------------

schema_executable: GraphQLSchema = make_executable_schema(schema_literal, query, integer_scalar, float_scalar)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: assembling schema executable with graphql endpoint
# ---------------------------------------------------------------------------------------------------------------------

graphql_endpoint_definition: GraphQL = GraphQL(
    debug=False if _env_provider.app_environment_mode == "production" else True,
    validation_rules=[cost_validator(maximum_cost=5)],
    error_formatter=error_formatter.formatter,
    schema=schema_executable,
    introspection=True,
)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: assembling graphql endpoint with the main router
# ---------------------------------------------------------------------------------------------------------------------

credit_request_gpl_controller: Route = Route(path=_path_provider.build_posix_path("credit-request"), endpoint=graphql_endpoint_definition)
