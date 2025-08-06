from pymongo.asynchronous.database import AsyncDatabase


class IndexManager:
    def __init__(self, db: AsyncDatabase):
        self.db = db

    async def initialize_all_indexes(self):
        pass
