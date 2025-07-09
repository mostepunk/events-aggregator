from app.adapters.db.cruds.base import BaseCRUD


class BaseService:
    def __init__(self, repository: BaseCRUD):
        self.repo = repository
