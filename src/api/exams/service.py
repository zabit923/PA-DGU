from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.exams.schemas import ExamCreate, ExamUpdate
from core.database.models import Answer, Exam, Group, Question, User


class ExamService:
    async def create_exam(
        self, exam_data: ExamCreate, user: User, session: AsyncSession
    ) -> Exam:
        if exam_data.start_time >= exam_data.end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start time must be earlier than end time.",
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

        await session.refresh(exam)
        exam.quantity_questions = len(exam.questions)
        await session.commit()
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

    async def delete_answer(self, answer_id: int, session: AsyncSession):
        answer = await self.get_answer_by_id(answer_id, session)
        if not answer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await session.delete(answer)
        await session.commit()

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
