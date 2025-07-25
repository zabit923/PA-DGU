from models import News
from schemas import NewsDataSchema
from services.v1.base import BaseEntityManager
from sqlalchemy.ext.asyncio import AsyncSession


class NewsDataManager(BaseEntityManager[NewsDataSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=NewsDataSchema, model=News)
