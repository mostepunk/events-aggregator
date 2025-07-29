from fastapi import APIRouter, Depends

from app.dependencies.containers import Container
from app.services.health_service import HealthService

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def check_health(
    service: HealthService = Depends(Container.health_service),
):
    return await service.get_health()
