from datetime import datetime
from typing import List

import pytz
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.exams.schemas import ExamCreate, ExamUpdate
from api.groups.service import GroupService
from api.users.service import UserService
from core.database.models import Answer, Exam, Group, Question, User

user_service = UserService()
group_service = GroupService()


class ExamService:
    async def create_exam(
        self, exam_data: ExamCreate, user: User, session: AsyncSession
    ) -> Exam:
        if (
            exam_data.start_time >= exam_data.end_time
            or exam_data.start_time < datetime.now(pytz.timezone("UTC"))
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start time must be earlier than end time and start time must be later than now.",
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
                order=question_data.order,
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
        new_exam.quantity_questions = len(exam_data.questions)
        await session.commit()
        await session.refresh(new_exam)
        return new_exam

    async def update_exam(
        self, exam_id: int, exam_data: ExamUpdate, session: AsyncSession
    ) -> Exam:
        exam = await self.get_exam_by_id(exam_id, session)
        if not exam:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        exam_data_dict = exam_data.model_dump(exclude_unset=True)

        if "groups" in exam_data_dict:
            group_ids = exam_data_dict.pop("groups")
            groups_query = await session.execute(
                select(Group).filter(Group.id.in_(group_ids))
            )
            groups = groups_query.scalars().all()
            if len(groups) != len(group_ids):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Some groups were not found.",
                )
            exam.groups = groups

        if "questions" in exam_data_dict:
            questions_data = exam_data_dict.pop("questions")
            await self.update_question(questions_data, exam, session)

        for key, value in exam_data_dict.items():
            if value is None:
                continue
            setattr(exam, key, value)

        exam.quantity_questions = len(exam.questions)
        await session.commit()
        await session.refresh(exam)
        return exam

    async def update_question(
        self, questions_data: dict, exam: Exam, session: AsyncSession
    ):
        existing_questions = {q.id: q for q in exam.questions}
        for question_data in questions_data:
            if "id" in question_data:
                question = existing_questions.get(question_data["id"])
                if question:
                    question.text = question_data.get("text", question.text)
                    question.order = question_data.get("order", question.order)
                    if question.answers:
                        existing_answers = {a.id: a for a in question.answers}
                        new_answers_data = question_data.get("answers", [])
                        await self.update_answer(
                            existing_answers, new_answers_data, question, session
                        )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Question with id {question_data['id']} not found.",
                    )
            else:
                new_question = Question(
                    text=question_data["text"],
                    order=question_data["order"],
                    exam_id=exam.id,
                )
                session.add(new_question)
                await session.flush()
                for answer_data in question_data.get("answers", []):
                    new_answer = Answer(
                        text=answer_data["text"],
                        is_correct=answer_data["is_correct"],
                        question_id=new_question.id,
                    )
                    session.add(new_answer)
        await session.commit()

    async def update_answer(
        self,
        existing_answers: dict,
        new_answers_data: dict,
        question: Question,
        session: AsyncSession,
    ):
        updated_answer_ids = set()
        for answer_data in new_answers_data:
            if "id" in answer_data:
                answer = existing_answers.get(answer_data["id"])
                if answer:
                    answer.text = answer_data.get("text", answer.text)
                    answer.is_correct = answer_data.get("is_correct", answer.is_correct)
                    updated_answer_ids.add(answer.id)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Answer with id {answer_data['id']} not found.",
                    )
            else:
                new_answer = Answer(
                    text=answer_data["text"],
                    is_correct=answer_data["is_correct"],
                    question_id=question.id,
                )
                session.add(new_answer)
        await session.commit()

    async def get_teacher_exams(
        self, teacher_id: int, session: AsyncSession
    ) -> List[Exam]:
        teacher = await user_service.get_user_by_id(teacher_id, session)
        if not teacher:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        statement = select(Exam).where(Exam.author_id == teacher_id)
        result = await session.execute(statement)
        exams = result.unique().scalars().all()
        return exams

    async def get_group_exams(self, group_id: int, session: AsyncSession) -> List[Exam]:
        group = await group_service.get_group(group_id, session)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        statement = select(Exam).join(Exam.groups).where(Group.id == group_id)
        result = await session.execute(statement)
        exams = result.unique().scalars().all()
        return exams

    async def get_exam_by_id(self, exam_id: int, session: AsyncSession) -> Exam:
        statement = select(Exam).where(Exam.id == exam_id)
        result = await session.execute(statement)
        exam = result.scalars().first()
        return exam

    async def get_question_by_id(
        self, question_id: int, session: AsyncSession
    ) -> Question:
        statement = select(Question).where(Question.id == question_id)
        result = await session.execute(statement)
        question = result.scalars().first()
        return question

    async def get_answer_by_id(self, answer_id: int, session: AsyncSession) -> Answer:
        statement = select(Answer).where(Answer.id == answer_id)
        result = await session.execute(statement)
        exam = result.scalars().first()
        return exam

    async def get_group_users_by_exam(
        self,
        exam: Exam,
        session: AsyncSession,
    ) -> List[User]:
        statement = (
            select(User)
            .join(User.member_groups)
            .join(Group.exams)
            .where(Exam.id == exam.id)
            .distinct()
        )
        result = await session.execute(statement)
        users = result.scalars().all()
        return users

    async def delete_exam(self, exam_id: int, session: AsyncSession):
        exam = await self.get_exam_by_id(exam_id, session)
        if not exam:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await session.delete(exam)
        await session.commit()

    async def delete_question(self, question_id: int, session: AsyncSession):
        question = await self.get_question_by_id(question_id, session)
        if not question:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await session.delete(question)
        await session.commit()

    async def delete_answer(self, answer_id: int, session: AsyncSession):
        answer = await self.get_answer_by_id(answer_id, session)
        if not answer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await session.delete(answer)
        await session.commit()
