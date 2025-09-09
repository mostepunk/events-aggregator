from fastapi import APIRouter, Depends

from app.adapters.schemas.admin import ProfilerStartSchema, ProfilerStatusSchema
from app.dependencies.containers import Container
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post(
    "/profiler/start/",
    summary="Start profiler",
    response_model=ProfilerStatusSchema,
)
async def profiler_on(
    data: ProfilerStartSchema,
    service: AdminService = Depends(Container.admin_service),
):
    return await service.profiler("on", data.dict(exclude_unset=True))


@router.post(
    "/profiler/stop/",
    summary="Stop profiler",
    response_model=ProfilerStatusSchema,
)
async def profiler_off(
    service: AdminService = Depends(Container.admin_service),
):
    return await service.profiler("off")


@router.get(
    "/profiler/status/",
    summary="Get profiler status",
    response_model=ProfilerStatusSchema,
)
async def profiler_status(
    service: AdminService = Depends(Container.admin_service),
):
    return await service.profiler("status")


@router.post(
    "/profiler/raw-data/",
    summary="Get profiler raw data",
    # response_model=ProfilerStatusSchema,
)
async def profiler_raw_data(
    service: AdminService = Depends(Container.admin_service),
):
    return await service.get_raw_profiler_data()
