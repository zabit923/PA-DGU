from typing import List

from api.exams.schemas import ExamCreate, TextQuestionUpdate
from core.database.models import Exam, Question, TextQuestion
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .answers import AnswerRepository


class QuestionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_question_by_id(self, question_id: int) -> Question:
        statement = select(Question).where(Question.id == question_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_text_question_by_id(self, question_id: int) -> TextQuestion:
        statement = select(TextQuestion).where(TextQuestion.id == question_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    @staticmethod
    async def create_questions(exam_data: ExamCreate, exam_id: int) -> List[Question]:
        if not exam_data.questions:
            return []
        return [
            Question(text=q.text, order=q.order, exam_id=exam_id)
            for q in exam_data.questions
        ]

    @staticmethod
    async def create_text_questions(
        exam_data: ExamCreate, exam_id: int
    ) -> List[TextQuestion]:
        if not exam_data.text_questions:
            return []
        return [
            TextQuestion(text=q.text, order=q.order, exam_id=exam_id)
            for q in exam_data.text_questions
        ]

    async def update_questions(
        self,
        exam: Exam,
        questions_data: List[dict],
        answer_repository: AnswerRepository,
    ) -> None:
        existing_questions = {q.id: q for q in exam.questions}
        new_questions = []

        for question_data in questions_data:
            if "id" in question_data and question_data["id"] in existing_questions:
                question = existing_questions[question_data["id"]]
                question.text = question_data.get("text", question.text)
                question.order = question_data.get("order", question.order)
                await answer_repository.update_answers(
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
        await self.session.flush()

    async def update_text_questions(
        self, exam: Exam, text_questions_data: List[dict]
    ) -> None:
        existing_text_questions = {q.id: q for q in exam.text_questions}
        new_text_questions = []

        for text_question_dict in text_questions_data:
            text_question_data = TextQuestionUpdate(**text_question_dict)

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
        await self.session.flush()

    async def delete_question(self, question: Question) -> None:
        await self.session.delete(question)
        await self.session.commit()

    async def delete_text_question(self, text_question: TextQuestion) -> None:
        await self.session.delete(text_question)
        await self.session.commit()
