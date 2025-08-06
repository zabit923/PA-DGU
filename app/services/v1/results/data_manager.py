from typing import List, Optional

from models import User
from schemas import ExamResultDataSchema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ExamResult
from app.services.v1.base import BaseEntityManager


class ExamResultDataManager(BaseEntityManager[ExamResultDataSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=ExamResultDataSchema, model=ExamResult)

    async def get_result_by_id(self, result_id: int) -> ExamResult:
        statement = select(self.model).where(self.model.id == result_id)
        return await self.get_one(statement)

    async def get_by_exam(self, exam_id: int) -> List[ExamResultDataSchema]:
        statement = select(ExamResult).where(ExamResult.exam_id == exam_id)
        return await self.get_all(statement)

    async def get_by_user(self, user: User) -> List[ExamResultDataSchema]:
        statement = select(ExamResult).where(ExamResult.student == user)
        return await self.get_all(statement)

    async def create(
        self, exam_id: int, user_id: int, score: Optional[int] = None
    ) -> ExamResult:
        if score:
            new_result = ExamResult(
                exam_id=exam_id,
                student_id=user_id,
                score=score,
            )
        else:
            new_result = ExamResult(
                exam_id=exam_id,
                student_id=user_id,
            )
        return await self.add_one(new_result)

    async def update(self, result: ExamResult) -> None:
        await self.session.commit()
        await self.session.refresh(result)
