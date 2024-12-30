from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.exams.schemas import ExamCreate
from core.database.models import Answer, Exam, Group, Question, User


class ExamService:
    async def create_exam(
        self, exam_data: ExamCreate, user: User, session: AsyncSession
    ) -> Exam:
        if not user.is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
            )
        groups_query = await session.execute(
            select(Group).filter(Group.id.in_(exam_data.groups))
        )
        groups = groups_query.scalars().all()
        if len(groups) != len(exam_data.groups):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Some groups were not found.",
            )
        new_exam = Exam(
            title=exam_data.title,
            quantity_questions=exam_data.quantity_questions,
            time=exam_data.time,
            start_time=exam_data.start_time,
            end_time=exam_data.end_time,
            author_id=user.id,
            groups=groups,
        )
        session.add(new_exam)
        await session.flush()

        for question_data in exam_data.questions:
            new_question = Question(
                text=question_data.text,
                exam_id=new_exam.id,
            )
            session.add(new_question)
            await session.flush()

            for answer_data in question_data.answers:
                new_answer = Answer(
                    text=answer_data.text,
                    is_correct=answer_data.is_correct,
                    question_id=new_question.id,
                )
                session.add(new_answer)
        await session.commit()
        await session.refresh(new_exam)
        return new_exam
