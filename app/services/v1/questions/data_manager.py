from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Exam, Question, TextQuestion
from app.schemas import (
    ExamCreateSchema,
    QuestionDataSchema,
    TextQuestionDataSchema,
    TextQuestionUpdateSchema,
)
from app.services.v1.answers.data_manager import AnswerDataManager
from app.services.v1.base import BaseEntityManager


class QuestionDataManager(BaseEntityManager[QuestionDataSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=QuestionDataSchema, model=Question)

    @staticmethod
    async def create_question(data: ExamCreateSchema, exam_id: int) -> List[Question]:
        if not data.questions:
            return []
        return [
            Question(text=q.text, order=q.order, exam_id=exam_id)
            for q in data.questions
        ]

    async def get_question_by_id(self, question_id: int) -> Question:
        statement = select(Question).where(Question.id == question_id)
        return await self.get_one(statement)

    async def update_questions(
        self,
        exam: Exam,
        questions_data: List[dict],
    ) -> None:
        existing_questions = {q.id: q for q in exam.questions}
        new_questions = []

        for question_data in questions_data:
            if "id" in question_data and question_data["id"] in existing_questions:
                question = existing_questions[question_data["id"]]
                question.text = question_data.get("text", question.text)
                question.order = question_data.get("order", question.order)
                await AnswerDataManager(self.session).update_answers(
                    question, question_data.get("answers", [])
                )
            else:
                new_questions.append(
                    Question(
                        text=question_data["text"],
                        order=question_data["order"],
                        exam_id=exam.id,
                    )
                )

        self.session.add_all(new_questions)
        await self.session.commit()
        await self.session.flush()

    async def delete_question(self, question: Question) -> None:
        await self.session.delete(question)
        await self.session.commit()


class TextQuestionDataManager(BaseEntityManager[TextQuestionDataSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session, schema=TextQuestionDataSchema, model=TextQuestion
        )

    @staticmethod
    async def create_text_questions(
        data: ExamCreateSchema, exam_id: int
    ) -> List[TextQuestion]:
        if not data.text_questions:
            return []
        return [
            TextQuestion(text=q.text, order=q.order, exam_id=exam_id)
            for q in data.text_questions
        ]

    async def get_text_question_by_id(self, question_id: int) -> TextQuestion:
        statement = select(TextQuestion).where(TextQuestion.id == question_id)
        return await self.get_one(statement)

    async def update_text_questions(
        self, exam: Exam, text_questions_data: List[dict]
    ) -> None:
        existing_text_questions = {q.id: q for q in exam.text_questions}
        new_text_questions = []

        for text_question_dict in text_questions_data:
            text_question_data = TextQuestionUpdateSchema(**text_question_dict)

            if (
                text_question_data.id
                and text_question_data.id in existing_text_questions
            ):
                text_question = existing_text_questions[text_question_data.id]
                text_question.text = text_question_data.text or text_question.text
                text_question.order = text_question_data.order or text_question.order
            else:
                new_text_questions.append(
                    TextQuestion(
                        text=text_question_data.text,
                        order=text_question_data.order,
                        exam_id=exam.id,
                    )
                )

        self.session.add_all(new_text_questions)
        await self.session.commit()
        await self.session.flush()

    async def delete_text_question(self, text_question: TextQuestion) -> None:
        await self.session.delete(text_question)
        await self.session.commit()
