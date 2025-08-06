from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import (
    Answer,
    Exam,
    PassedChoiceAnswer,
    PassedTextAnswer,
    Question,
    User,
)
from app.schemas import (
    AnswerDataSchema,
    ExamCreateSchema,
    SelectAnswerDataCreateSchema,
    TextAnswerDataCreateSchema,
)
from app.services.v1.base import BaseEntityManager


class AnswerDataManager(BaseEntityManager[AnswerDataSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=AnswerDataSchema, model=Answer)

    async def get_answer_by_id(self, answer_id: int) -> Answer:
        statement = select(self.model).where(self.model.id == answer_id)
        return await self.get_one(statement)

    @staticmethod
    async def create_answer(
        data: ExamCreateSchema, questions: List[Question]
    ) -> List[Answer]:
        answers = []
        for question, question_data in zip(questions, data.questions or []):
            for answer_data in question_data.answers:
                answers.append(
                    Answer(
                        text=answer_data.text,
                        is_correct=answer_data.is_correct,
                        question=question,
                    )
                )
        return answers

    async def get_correct_answer(self, answer_id: int, question: Question) -> Answer:
        statement = select(Answer).where(
            Answer.id == answer_id,
            Answer.question == question,
            Answer.is_correct.is_(True),
        )
        return await self.get_one(statement)

    async def get_passed_choise_answers(
        self, user: User, exam: Exam
    ) -> List[PassedChoiceAnswer]:
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
        result = await self.session.execute(statement)
        return result.unique().scalars().all()

    async def get_passed_text_answers(
        self, user: User, exam: Exam
    ) -> List[PassedTextAnswer]:
        statement = (
            select(PassedTextAnswer)
            .options(joinedload(PassedTextAnswer.question))
            .where(
                PassedTextAnswer.user_id == user.id, PassedTextAnswer.exam_id == exam.id
            )
        )
        result = await self.session.execute(statement)
        return result.unique().scalars().all()

    async def create_passed_text_answers(
        self, user: User, exam: Exam, answer: TextAnswerDataCreateSchema
    ) -> None:
        self.session.add(
            PassedTextAnswer(
                user_id=user.id,
                exam_id=exam.id,
                question_id=answer.question_id,
                text=answer.text,
            )
        )

    async def create_passed_choise_answers(
        self, user: User, exam: Exam, answer: SelectAnswerDataCreateSchema
    ) -> None:
        correct_answer = await self.session.execute(
            select(Answer).where(
                Answer.question_id == answer.question_id, Answer.is_correct == True
            )
        )
        correct_answer = correct_answer.scalar()
        self.session.add(
            PassedChoiceAnswer(
                user_id=user.id,
                exam_id=exam.id,
                question_id=answer.question_id,
                selected_answer_id=answer.answer_id,
                is_correct=answer.answer_id == correct_answer.id
                if correct_answer
                else False,
            )
        )

    async def update_answers(
        self, question: Question, answers_data: List[dict]
    ) -> None:
        existing_answers = {a.id: a for a in question.answers}
        new_answers = []

        for answer_data in answers_data:
            if "id" in answer_data and answer_data["id"] in existing_answers:
                answer = existing_answers[answer_data["id"]]
                answer.text = answer_data.get("text", answer.text)
                answer.is_correct = answer_data.get("is_correct", answer.is_correct)
            else:
                new_answers.append(
                    Answer(
                        text=answer_data["text"],
                        is_correct=answer_data["is_correct"],
                        question_id=question.id,
                    )
                )

        self.session.add_all(new_answers)
        await self.session.flush()

    async def delete(self, answer: Answer) -> None:
        await self.session.delete(answer)
        await self.session.commit()
