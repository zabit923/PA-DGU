from datetime import datetime
from typing import List, Optional, Sequence

import pytz
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from api.exams.schemas import (
    AnswerRead,
    AnswerStudentRead,
    ExamCreate,
    ExamRead,
    ExamStudentRead,
    ExamUpdate,
    PassedChoiceAnswerRead,
    PassedTextAnswerRead,
    QuestionRead,
    QuestionStudentRead,
    ShortQuestionRead,
    TextQuestionRead,
    TextQuestionUpdate,
)
from api.groups.schemas import GroupShort
from api.groups.service import GroupService
from api.users.service import user_service
from core.database.models import (
    Answer,
    Exam,
    ExamResult,
    Group,
    PassedChoiceAnswer,
    PassedTextAnswer,
    Question,
    TextQuestion,
    User,
)

group_service = GroupService()


class ExamService:
    @staticmethod
    async def create_exam(
        exam_data: ExamCreate, user: User, session: AsyncSession
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

        if exam_data.questions:
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

        if exam_data.text_questions:
            new_exam.is_advanced_exam = True
            for question_data in exam_data.text_questions:
                new_text_question = TextQuestion(
                    text=question_data.text,
                    order=question_data.order,
                    exam_id=new_exam.id,
                )
                session.add(new_text_question)

        total_questions = (len(exam_data.questions) if exam_data.questions else 0) + (
            len(exam_data.text_questions) if exam_data.text_questions else 0
        )
        new_exam.quantity_questions = total_questions

        await session.commit()
        await session.refresh(new_exam)
        return new_exam

    async def update_exam(
        self, exam_id: int, exam_data: ExamUpdate, session: AsyncSession
    ) -> Exam:
        exam = await self.get_exam_by_id(exam_id, session)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
            )

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

        if "text_questions" in exam_data_dict:
            text_questions_data = exam_data_dict.pop("text_questions")
            await self.update_text_questions(text_questions_data, exam, session)

        for key, value in exam_data_dict.items():
            if value is not None:
                setattr(exam, key, value)

        await session.commit()
        await session.refresh(exam)
        exam.quantity_questions = len(exam.questions) + len(exam.text_questions)
        await session.commit()
        return exam

    async def update_question(
        self, questions_data: dict, exam: Exam, session: AsyncSession
    ) -> None:
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

    @staticmethod
    async def update_text_questions(
        text_questions_data: List[dict], exam: Exam, session: AsyncSession
    ) -> None:
        existing_text_questions = {q.id: q for q in exam.text_questions}

        for text_question_dict in text_questions_data:
            text_question_data = TextQuestionUpdate(**text_question_dict)

            if text_question_data.id:
                if text_question_data.id not in existing_text_questions:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Text question with id {text_question_data.id} not found",
                    )
                text_question = existing_text_questions[text_question_data.id]
                text_question.text = text_question_data.text or text_question.text
                text_question.order = text_question_data.order or text_question.order
            else:
                new_text_question = TextQuestion(
                    text=text_question_data.text,
                    order=text_question_data.order,
                    exam_id=exam.id,
                )
                session.add(new_text_question)
        await session.commit()

    @staticmethod
    async def update_answer(
        existing_answers: dict,
        new_answers_data: dict,
        question: Question,
        session: AsyncSession,
    ) -> None:
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

    @staticmethod
    async def get_teacher_exams(
        teacher_id: int, session: AsyncSession
    ) -> Sequence[Exam]:
        teacher = await user_service.get_user_by_id(teacher_id, session)
        if not teacher:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        statement = select(Exam).where(Exam.author_id == teacher_id)
        result = await session.execute(statement)
        exams = result.unique().scalars().all()
        return exams

    @staticmethod
    async def get_group_exams(group_id: int, session: AsyncSession) -> Sequence[Exam]:
        group = await group_service.get_group(group_id, session)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        statement = select(Exam).join(Exam.groups).where(Group.id == group_id)
        result = await session.execute(statement)
        exams = result.unique().scalars().all()
        return exams

    @staticmethod
    async def get_exam_by_id(exam_id: int, session: AsyncSession) -> Exam:
        statement = select(Exam).where(Exam.id == exam_id)
        result = await session.execute(statement)
        exam = result.scalars().first()
        return exam

    @staticmethod
    async def get_full_exam(
        user: User, exam: Exam, exam_data: dict
    ) -> ExamStudentRead | ExamRead:
        exam_data["groups"] = [
            GroupShort.model_validate(group.__dict__) for group in exam.groups
        ]
        exam_data["questions"] = [
            QuestionRead.model_validate(
                {
                    **question.__dict__,
                    "answers": [
                        AnswerRead.model_validate(answer.__dict__)
                        for answer in question.answers
                    ],
                }
            )
            if user.is_teacher
            else QuestionStudentRead.model_validate(
                {
                    **question.__dict__,
                    "answers": [
                        AnswerStudentRead.model_validate(
                            {"id": answer.id, "text": answer.text}
                        )
                        for answer in question.answers
                    ],
                }
            )
            for question in exam.questions
        ]
        exam_data["text_questions"] = (
            [
                TextQuestionRead.model_validate(text_question.__dict__)
                for text_question in exam.text_questions
            ]
            if exam.is_advanced_exam
            else []
        )

        return (
            ExamRead.model_validate(exam_data)
            if user.is_teacher
            else ExamStudentRead.model_validate(exam_data)
        )

    @staticmethod
    async def get_question_by_id(question_id: int, session: AsyncSession) -> Question:
        statement = select(Question).where(Question.id == question_id)
        result = await session.execute(statement)
        question = result.scalars().first()
        return question

    @staticmethod
    async def get_text_question_by_id(
        text_question_id: int, session: AsyncSession
    ) -> TextQuestion:
        statement = select(TextQuestion).where(TextQuestion.id == text_question_id)
        result = await session.execute(statement)
        question = result.scalars().first()
        return question

    @staticmethod
    async def get_answer_by_id(answer_id: int, session: AsyncSession) -> Answer:
        statement = select(Answer).where(Answer.id == answer_id)
        result = await session.execute(statement)
        exam = result.scalars().first()
        return exam

    @staticmethod
    async def get_group_users_by_exam(
        exam: Exam,
        session: AsyncSession,
    ) -> Sequence[User]:
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

    async def delete_exam(self, exam_id: int, session: AsyncSession) -> None:
        exam = await self.get_exam_by_id(exam_id, session)
        if not exam:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await session.delete(exam)
        await session.commit()

    async def delete_question(self, question_id: int, session: AsyncSession) -> None:
        question = await self.get_question_by_id(question_id, session)
        if not question:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await session.delete(question)
        await session.commit()

    async def delete_text_question(
        self, question_id: int, session: AsyncSession
    ) -> None:
        question = await self.get_text_question_by_id(question_id, session)
        if not question:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await session.delete(question)
        await session.commit()

    async def delete_answer(self, answer_id: int, session: AsyncSession) -> None:
        answer = await self.get_answer_by_id(answer_id, session)
        if not answer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await session.delete(answer)
        await session.commit()

    @staticmethod
    async def create_result(
        exam_id: int, user_id: int, session: AsyncSession, score: Optional[int] = None
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
        session.add(new_result)
        await session.commit()
        await session.refresh(new_result)
        return new_result

    @staticmethod
    async def get_result_by_id(result_id: int, session: AsyncSession) -> ExamResult:
        statement = select(ExamResult).where(ExamResult.id == result_id)
        result = await session.execute(statement)
        exam_result = result.scalars().first()
        return exam_result

    @staticmethod
    async def get_results_by_exam(
        exam_id: int, session: AsyncSession
    ) -> Sequence[ExamResult]:
        statement = select(ExamResult).where(ExamResult.exam_id == exam_id)
        result = await session.execute(statement)
        exam_results = result.scalars().all()
        return exam_results

    @staticmethod
    async def get_results_by_user(
        user_id: int, session: AsyncSession
    ) -> Sequence[ExamResult]:
        user = await user_service.get_user_by_id(user_id, session)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        statement = select(ExamResult).where(ExamResult.student == user)
        result = await session.execute(statement)
        exam_results = result.scalars().all()
        return exam_results

    async def get_passed_choice_answers(
        self, user_id: int, exam_id: int, session: AsyncSession
    ) -> Sequence[PassedChoiceAnswer]:
        user = await user_service.get_user_by_id(user_id, session)
        exam = await self.get_exam_by_id(exam_id, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
            )
        statement = (
            select(PassedChoiceAnswer)
            .options(
                joinedload(PassedChoiceAnswer.question),
                joinedload(PassedChoiceAnswer.selected_answer),
            )
            .where(
                PassedChoiceAnswer.user_id == user.id,
                PassedChoiceAnswer.exam_id == exam.id,
            )
        )
        result = await session.execute(statement)
        passed_answers = result.unique().scalars().all()
        return passed_answers

    async def get_passed_text_answers(
        self, user_id: int, exam_id: int, session: AsyncSession
    ) -> Sequence[PassedTextAnswer]:
        user = await user_service.get_user_by_id(user_id, session)
        exam = await self.get_exam_by_id(exam_id, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
            )
        statement = (
            select(PassedTextAnswer)
            .options(joinedload(PassedTextAnswer.question))
            .where(
                PassedTextAnswer.user_id == user.id, PassedTextAnswer.exam_id == exam.id
            )
        )
        result = await session.execute(statement)
        passed_answers = result.unique().scalars().all()
        return passed_answers

    async def passed_answers(
        self, user_id: int, exam: Exam, session: AsyncSession
    ) -> list:
        passed_text_answers, passed_choice_answers = [], []
        if exam.is_advanced_exam:
            passed_text_answers = (
                await self.get_passed_text_answers(user_id, exam.id, session) or []
            )
            if hasattr(exam, "passed_choice_answers"):
                passed_choice_answers = (
                    await self.get_passed_choice_answers(user_id, exam.id, session)
                    or []
                )
        else:
            passed_choice_answers = (
                await self.get_passed_choice_answers(user_id, exam.id, session) or []
            )

        choice_answers = [
            PassedChoiceAnswerRead(
                id=answer.id,
                question=ShortQuestionRead.model_validate(answer.question.__dict__),
                selected_answer=AnswerRead.model_validate(
                    answer.selected_answer.__dict__
                ),
                is_correct=answer.is_correct,
                created_at=answer.created_at,
            )
            for answer in passed_choice_answers
        ]
        text_answers = [
            PassedTextAnswerRead(
                id=answer.id,
                question=ShortQuestionRead.model_validate(answer.question.__dict__),
                text=answer.text,
                created_at=answer.created_at,
            )
            for answer in passed_text_answers
        ]
        return [choice_answers, text_answers]
