from datetime import datetime
from io import BytesIO
from typing import List

import pytz
from openpyxl import Workbook
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Exam, Group, Question, User
from app.schemas import ExamDataSchema
from app.services.v1.answers.data_manager import AnswerDataManager
from app.services.v1.base import BaseEntityManager
from app.services.v1.questions.data_manager import (
    QuestionDataManager,
    TextQuestionDataManager,
)


class ExamDataManager(BaseEntityManager[ExamDataSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=ExamDataSchema, model=Exam)

    async def get_exam_by_id(self, exam_id: int) -> Exam:
        statement = (
            select(Exam)
            .where(Exam.id == exam_id)
            .options(
                selectinload(Exam.author),
                selectinload(Exam.groups),
                selectinload(Exam.questions).selectinload(Question.answers),
                selectinload(Exam.text_questions),
            )
        )
        return await self.get_one(statement)

    async def create_exam(
        self,
        data: ExamDataSchema,
        user: User,
        groups: List[Group],
    ) -> Exam:
        new_exam = Exam(
            title=data.title,
            time=data.time,
            start_time=data.start_time,
            end_time=data.end_time,
            author_id=user.id,
            groups=groups,
        )
        self.session.add(new_exam)
        await self.session.flush()

        questions = await QuestionDataManager(self.session).create_question(
            data, new_exam.id
        )
        answers = await AnswerDataManager(self.session).create_answer(data, questions)
        text_questions = await TextQuestionDataManager(
            self.session
        ).create_text_questions(data, new_exam.id)

        new_exam.is_advanced_exam = bool(text_questions)
        new_exam.quantity_questions = len(questions) + len(text_questions)

        self.session.add_all(questions)
        self.session.add_all(answers)
        self.session.add_all(text_questions)
        await self.session.commit()
        await self.session.refresh(new_exam)
        return new_exam

    async def update_exam(self, exam: Exam) -> Exam:
        await self.session.commit()
        await self.session.refresh(exam)
        return exam

    async def delete(self, exam: Exam) -> None:
        await self.session.delete(exam)
        await self.session.commit()

    async def get_by_author(self, teacher_id: int) -> List[Exam]:
        statement = select(Exam).where(Exam.author_id == teacher_id)
        return await self.get_all(statement)

    async def get_by_group(self, group_id: int) -> List[Exam]:
        statement = select(Exam).join(Exam.groups).where(Group.id == group_id)
        return await self.get_all(statement)

    async def get_exams_ready_to_start(self) -> List[Exam]:
        statement = select(Exam).filter(
            Exam.start_time <= datetime.now(pytz.UTC),
            Exam.is_ended.is_(False),
            Exam.is_started.is_(False),
        )
        return await self.get_all(statement)

    async def get_exams_ready_to_end(self) -> List[Exam]:
        statement = select(Exam).filter(
            Exam.end_time <= datetime.now(pytz.timezone("UTC")),
            Exam.is_ended.is_(False),
        )
        return await self.get_all(statement)

    async def mark_exam_as_started(self, exam: Exam) -> None:
        exam.is_started = True
        await self.session.commit()

    async def mark_exam_as_ended(self, exam: Exam) -> None:
        exam.is_started = False
        exam.is_ended = True
        await self.session.commit()

    @staticmethod
    async def create_results_report(exam: Exam) -> BytesIO:
        wb = Workbook()
        ws = wb.active
        ws.title = f'Результаты экзамена "{exam.title}"'
        ws.append(["Имя", "Фамилия", "Курс", "Направление", "Группа", "Оценка"])

        for result in exam.results:
            ws.append(
                [
                    result.student.first_name,
                    result.student.last_name,
                    result.student.member_groups[0].course,
                    result.student.member_groups[0].facult,
                    result.student.member_groups[0].subgroup,
                    result.score,
                ]
            )

        stream = BytesIO()
        wb.save(stream)
        stream.seek(0)
        return stream
