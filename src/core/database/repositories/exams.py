from datetime import datetime
from typing import List, Sequence

import pytz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.exams.schemas import ExamCreate, TextQuestionUpdate
from core.database.models import Answer, Exam, Group, Question, TextQuestion, User


class ExamRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, exam_id: int) -> Exam | None:
        return await self.session.get(Exam, exam_id)

    async def create(
        self, exam_data: ExamCreate, user: User, groups: List[Group]
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

        questions = []
        answers = []
        text_questions = []

        if exam_data.questions:
            for question_data in exam_data.questions:
                question = Question(
                    text=question_data.text,
                    order=question_data.order,
                    exam_id=new_exam.id,
                )
                questions.append(question)

                for answer_data in question_data.answers:
                    answers.append(
                        Answer(
                            text=answer_data.text,
                            is_correct=answer_data.is_correct,
                            question=question,
                        )
                    )

        if exam_data.text_questions:
            new_exam.is_advanced_exam = True
            for question_data in exam_data.text_questions:
                text_questions.append(
                    TextQuestion(
                        text=question_data.text,
                        order=question_data.order,
                        exam_id=new_exam.id,
                    )
                )

        self.session.add_all(questions)
        self.session.add_all(answers)
        self.session.add_all(text_questions)

        new_exam.quantity_questions = len(questions) + len(text_questions)

        await self.session.commit()
        await self.session.refresh(new_exam)
        return new_exam

    async def update(self, exam: Exam) -> Exam:
        await self.session.commit()
        await self.session.refresh(exam)
        return exam

    async def update_questions(self, exam: Exam, questions_data: List[dict]) -> None:
        existing_questions = {q.id: q for q in exam.questions}
        new_questions = []

        for question_data in questions_data:
            if "id" in question_data and question_data["id"] in existing_questions:
                question = existing_questions[question_data["id"]]
                question.text = question_data.get("text", question.text)
                question.order = question_data.get("order", question.order)
                await self.update_answers(question, question_data.get("answers", []))
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
        return result.scalars().all()

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
