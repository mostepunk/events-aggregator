from app.adapters.db.cruds.health_crud import HealthCRUD
from app.services.base import BaseService
from app.settings import config

logging = config.logging.get_logger("HealthService")


class HealthService(BaseService):
    def __init__(self, repository: HealthCRUD):
        super().__init__(repository)

    async def get_health(self):
        logging.debug(
            f"Check connection to MongoDB: {config.mongo.host}, {config.mongo.port}"
        )
        try:
            res = await self.repo.ping()
            logging.debug(f"Health check result: {res}")
        except Exception as e:
            logging.warning(f"Health check failed: {e}")
            return False

        return True
