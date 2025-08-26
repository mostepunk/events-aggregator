from fastapi import APIRouter
from that_depends.integrations.fastapi import create_fastapi_route_class

from . import admin, catalogues, events, health

my_route_class = create_fastapi_route_class()
main_router = APIRouter(route_class=my_route_class)

main_router.include_router(events.router)
main_router.include_router(health.router)
main_router.include_router(catalogues.router)
main_router.include_router(admin.router)
