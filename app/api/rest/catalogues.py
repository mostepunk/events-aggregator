from fastapi import APIRouter

from app import getLogger
from app.utils.enums import PirorityLevelEnum

logging = getLogger("Catalogue.API")


router = APIRouter(prefix="/catalogue", tags=["Catalogue"])


@router.get("/priorties/")
async def get_priorities():
    return [{"key": k, "value": v} for k, v in PirorityLevelEnum.choices()]
