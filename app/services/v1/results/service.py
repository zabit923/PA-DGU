from typing import List, Optional

from core.exceptions import UserNotFoundError
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.exceptions import ForbiddenError
from app.models import ExamResult, User
from app.schemas import ExamResultUpdateSchema
from app.services.v1.base import BaseService
from app.services.v1.results.data_manager import ExamResultDataManager
from app.services.v1.users.data_manager import UserDataManager


class ExamResultService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session)
        self.result_data_manager = ExamResultDataManager(session)
        self.user_data_manager = UserDataManager(session)

    async def get_result_by_id(self, result_id: int) -> ExamResult:
        exam_result = await self.result_data_manager.get_result_by_id(result_id)
        if not exam_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return exam_result

    async def create_result(
        self, exam_id: int, user_id: int, score: Optional[int] = None
    ) -> ExamResult:
        new_result = await self.result_data_manager.create(exam_id, user_id, score)
        return new_result

    async def update_result(
        self,
        result_id: int,
        result_data: ExamResultUpdateSchema,
        user: User,
    ) -> ExamResult:
        result = await self.result_data_manager.get_result_by_id(result_id)
        if not user.is_teacher:
            raise ForbiddenError(detail="У вас нет прав для обновления результата.")
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Результат не найден."
            )
        result.score = result_data.score
        await self.result_data_manager.update(result)
        return result

    async def get_results_by_exam(self, exam_id: int) -> List[ExamResult]:
        exam_results = await self.result_data_manager.get_by_exam(exam_id)
        return exam_results

    async def get_results_by_user(self, user_id: int) -> List[ExamResult]:
        user = await self.user_data_manager.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(detail="Пользователь не найден.")
        exam_results = await self.result_data_manager.get_by_user(user)
        return exam_results
