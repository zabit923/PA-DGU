from typing import Optional

from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import ExamResult, User


class ResultRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, result_id: int) -> ExamResult:
        statement = select(ExamResult).where(ExamResult.id == result_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_by_exam(self, exam_id: int) -> Sequence[ExamResult]:
        statement = select(ExamResult).where(ExamResult.exam_id == exam_id)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_user(self, user: User) -> Sequence[ExamResult]:
        statement = select(ExamResult).where(ExamResult.student == user)
        result = await self.session.execute(statement)
        return result.scalars().all()

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
        self.session.add(new_result)
        await self.session.commit()
        await self.session.refresh(new_result)
        return new_result

    async def update(self, result: ExamResult) -> None:
        await self.session.commit()
        await self.session.refresh(result)
