from .index_manager import IndexManager
from app import getLogger
from app.adapters.db import get_database

logging = getLogger(__name__)


async def init_indexes() -> None:
    """Инициализация индексов MongoDB при старте приложения"""
    logging.info("Initializing MongoDB indexes...")

    try:
        async with get_database() as db:
            index_manager = IndexManager(db)
            await index_manager.initialize_all_indexes()

    except Exception as e:
        logging.error(f"Failed to initialize MongoDB indexes: {e}")
        # Не падаем - приложение может работать и без индексов (медленнее)
        logging.warning("Application will continue without optimized indexes")

    logging.info("MongoDB indexes initialization completed successfully")
