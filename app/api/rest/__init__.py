from fastapi import APIRouter
from that_depends.integrations.fastapi import create_fastapi_route_class

from . import events

my_route_class = create_fastapi_route_class()
main_router = APIRouter(route_class=my_route_class)

main_router.include_router(events.router)
