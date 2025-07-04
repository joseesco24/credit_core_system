from fastapi import APIRouter
from fastapi import Response
from fastapi import status as HttpStatus

from src.sidecard.system.artifacts.path_provider import PathProvider

__all__: list[str] = ["heart_beat_controller"]
_path_provider: PathProvider = PathProvider()
heart_beat_controller: APIRouter = APIRouter(prefix=_path_provider.build_posix_path("heart-beat"), tags=["Heart Beat"])


@heart_beat_controller.post(
    description="allows to check if the service is or not healthy",
    summary="allows to check if the service is or not healthy",
    path=_path_provider.build_posix_path(""),
    status_code=HttpStatus.HTTP_200_OK,
)
async def api_heart_beat() -> Response:
    return Response(status_code=HttpStatus.HTTP_200_OK)
