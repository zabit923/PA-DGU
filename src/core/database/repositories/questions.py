from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Question, TextQuestion


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

    async def delete_question(self, question: Question) -> None:
        await self.session.delete(question)
        await self.session.commit()

    async def delete_text_question(self, text_question: TextQuestion) -> None:
        await self.session.delete(text_question)
        await self.session.commit()
