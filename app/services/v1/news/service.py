from typing import Optional

from core.integrations.storage import CommonS3DataManager
from services.v1.base import BaseService
from services.v1.news.data_manager import NewsDataManager
from sqlalchemy.ext.asyncio import AsyncSession


class NewsService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        s3_data_manager: Optional[CommonS3DataManager] = None,
    ):
        super().__init__(session)
        self.news_data_manager = NewsDataManager(session)
        self.s3_data_manager = s3_data_manager
