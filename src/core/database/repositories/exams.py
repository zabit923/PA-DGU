from datetime import datetime
from typing import List

import pytz
from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.exams.schemas import ExamCreate
from core.database.models import Exam, Group, Question, User

from .answers import AnswerRepository
from .questions import QuestionRepository


class ExamRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, exam_id: int) -> Exam | None:
        stmt = (
            select(Exam)
            .where(Exam.id == exam_id)
            .options(
                selectinload(Exam.author),
                selectinload(Exam.groups),
                selectinload(Exam.questions).selectinload(Question.answers),
                selectinload(Exam.text_questions),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        exam_data: ExamCreate,
        user: User,
        groups: List[Group],
        question_repository: QuestionRepository,
        answer_repository: AnswerRepository,
    ) -> Exam:
        new_exam = Exam(
            title=exam_data.title,
            time=exam_data.time,
            start_time=exam_data.start_time,
            end_time=exam_data.end_time,
            author_id=user.id,
            groups=groups,
        )
        self.session.add(new_exam)
        await self.session.flush()

        questions = await question_repository.create_questions(exam_data, new_exam.id)
        answers = await answer_repository.create_answers(exam_data, questions)
        text_questions = await question_repository.create_text_questions(
            exam_data, new_exam.id
        )

        new_exam.is_advanced_exam = bool(text_questions)
        new_exam.quantity_questions = len(questions) + len(text_questions)

        self.session.add_all(questions)
        self.session.add_all(answers)
        self.session.add_all(text_questions)
        await self.session.commit()
        await self.session.refresh(new_exam)
        return new_exam

    async def update(self, exam: Exam) -> Exam:
        await self.session.commit()
        await self.session.refresh(exam)
        return exam

    async def delete(self, exam: Exam) -> None:
        await self.session.delete(exam)
        await self.session.commit()

    async def get_by_author(self, teacher_id: int) -> Sequence[Exam]:
        statement = select(Exam).where(Exam.author_id == teacher_id)
        result = await self.session.execute(statement)
        return result.unique().scalars().all()

    async def get_by_group(self, group_id: int) -> Sequence[Exam]:
        statement = select(Exam).join(Exam.groups).where(Group.id == group_id)
        result = await self.session.execute(statement)
        return result.unique().scalars().all()

    async def get_exams_ready_to_start(self) -> Sequence[Exam]:
        statement = select(Exam).filter(
            Exam.start_time <= datetime.now(pytz.UTC),
            Exam.is_ended == False,
            Exam.is_started == False,
        )
        result = await self.session.execute(statement)
        return result.unique().scalars().all()

    async def get_exams_ready_to_end(self) -> Sequence[Exam]:
        statement = select(Exam).filter(
            Exam.end_time <= datetime.now(pytz.timezone("UTC")), Exam.is_ended == False
        )
        result = await self.session.execute(statement)
        return result.unique().scalars().all()

    async def mark_exam_as_started(self, exam: Exam) -> None:
        exam.is_started = True
        await self.session.commit()

    async def mark_exam_as_ended(self, exam: Exam) -> None:
        exam.is_started = False
        exam.is_ended = True
        await self.session.commit()
