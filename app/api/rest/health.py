from fastapi import APIRouter, Depends

from app.adapters.schemas.health import HealthStatusSchema
from app.dependencies.containers import Container
from app.services.health_service import HealthService

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", response_model=HealthStatusSchema)
async def check_health(
    service: HealthService = Depends(Container.health_service),
):
    if await service.is_ok():
        return {"status": "ok"}
    return {"status": "error"}
