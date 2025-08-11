from datetime import datetime
from typing import List

import pytz
from core.exceptions import (
    AnswerNotFoundError,
    ExamNotFoundError,
    QuestionNotFoundError,
    UserNotFoundError,
)
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.exceptions import ForbiddenError, GroupNotFoundError
from app.models import (
    Answer,
    Exam,
    ExamResult,
    PassedChoiceAnswer,
    PassedTextAnswer,
    Question,
    TextQuestion,
    User,
)
from app.schemas import (
    AnswerResponseSchema,
    AnswerStudentResponseSchema,
    ExamCreateSchema,
    ExamResponseSchema,
    ExamStudentResponseSchema,
    ExamUpdateSchema,
    GroupShortResponseSchema,
    PassedChoiceAnswerResponseSchema,
    PassedTextAnswerResponseSchema,
    PassingExamDataCreateSchema,
    QuestionResponseSchema,
    QuestionShortResponseSchema,
    QuestionStudentResponseSchema,
    SelectAnswerDataCreateSchema,
    TextQuestionResponseSchema,
    UserShortSchema,
)
from app.services.v1.answers.data_manager import AnswerDataManager
from app.services.v1.base import BaseService
from app.services.v1.exams.data_manager import ExamDataManager
from app.services.v1.groups.data_manager import GroupDataManager
from app.services.v1.notifications.service import NotificationService
from app.services.v1.questions.data_manager import (
    QuestionDataManager,
    TextQuestionDataManager,
)
from app.services.v1.results.data_manager import ExamResultDataManager
from app.services.v1.results.service import ExamResultService
from app.services.v1.users.data_manager import UserDataManager


class ExamService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session)
        self.exam_data_manager = ExamDataManager(session)
        self.group_data_manager = GroupDataManager(session)
        self.question_data_manager = QuestionDataManager(session)
        self.text_question_data_manager = TextQuestionDataManager(session)
        self.answer_data_manager = AnswerDataManager(session)
        self.user_data_manager = UserDataManager(session)
        self.result_data_manager = ExamResultDataManager(session)

    async def get_exam_by_id(self, exam_id: int) -> Exam:
        exam = await self.exam_data_manager.get_exam_by_id(exam_id)
        return exam

    async def create_exam(self, exam_data: ExamCreateSchema, user: User) -> Exam:
        if not user.is_teacher:
            raise ForbiddenError(detail="У вас нет прав для создания экзамена.")
        if (
            exam_data.start_time >= exam_data.end_time
            or exam_data.start_time < datetime.now(pytz.timezone("UTC"))
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Время начала экзамена должно быть раньше времени окончания и позже текущего времени.",
            )
        groups = await self.group_data_manager.get_by_ids(exam_data.groups)
        if len(groups) != len(exam_data.groups):
            raise GroupNotFoundError(detail="Некоторые группы не найдены.")
        new_exam = await self.exam_data_manager.create_exam(exam_data, user, groups)
        return new_exam

    async def update_exam(
        self, user: User, exam_id: int, exam_data: ExamUpdateSchema
    ) -> Exam:
        if not user.is_teacher:
            raise ForbiddenError(detail="У вас нет прав для редактирования экзамена.")
        exam = await self.exam_data_manager.get_exam_by_id(exam_id)
        if not exam:
            raise ExamNotFoundError()
        exam_data_dict = exam_data.model_dump(exclude_unset=True)

        if "groups" in exam_data_dict:
            groups = await self.group_data_manager.get_by_ids(
                exam_data_dict.pop("groups")
            )
            if len(groups) != len(exam_data.groups):
                raise GroupNotFoundError(detail="Некоторые группы не найдены.")
            exam.groups = groups
        if "questions" in exam_data_dict:
            try:
                await self.question_data_manager.update_questions(
                    exam, exam_data_dict.pop("questions")
                )
            except ValueError:
                raise QuestionNotFoundError()
        if "text_questions" in exam_data_dict:
            try:
                await self.text_question_data_manager.update_text_questions(
                    exam, exam_data_dict.pop("text_questions")
                )
            except ValueError:
                raise QuestionNotFoundError()

        for key, value in exam_data_dict.items():
            setattr(exam, key, value)

        return await self.exam_data_manager.update_exam(exam)

    async def get_teacher_exams(self, teacher_id: int) -> List[Exam]:
        teacher = await self.user_data_manager.get_user_by_id(teacher_id)
        if not teacher:
            raise UserNotFoundError(detail="Пользователь не найден.")
        exams = await self.exam_data_manager.get_by_author(teacher_id)
        return exams

    async def get_group_exams(self, group_id: int) -> List[Exam]:
        group = await self.group_data_manager.get_group_by_id(group_id)
        if not group:
            raise GroupNotFoundError(detail="Группа не найдена.")
        exams = await self.exam_data_manager.get_by_group(group_id)
        return exams

    @staticmethod
    async def get_full_exam(
        user: User, exam: Exam, exam_data: dict
    ) -> ExamStudentResponseSchema | ExamResponseSchema:
        exam_data["author"] = UserShortSchema.model_validate(exam.author.__dict__)
        exam_data["groups"] = [
            GroupShortResponseSchema.model_validate(group.__dict__)
            for group in exam.groups
        ]
        exam_data["questions"] = [
            QuestionResponseSchema.model_validate(
                {
                    **question.__dict__,
                    "answers": [
                        AnswerResponseSchema.model_validate(answer.__dict__)
                        for answer in question.answers
                    ],
                }
            )
            if user.is_teacher
            else QuestionStudentResponseSchema.model_validate(
                {
                    **question.__dict__,
                    "answers": [
                        AnswerStudentResponseSchema.model_validate(
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
                TextQuestionResponseSchema.model_validate(text_question.__dict__)
                for text_question in exam.text_questions
            ]
            if exam.is_advanced_exam
            else []
        )

        return (
            ExamResponseSchema.model_validate(exam_data)
            if user.is_teacher
            else ExamStudentResponseSchema.model_validate(exam_data)
        )

    async def get_question_by_id(self, question_id: int) -> Question:
        question = await self.question_data_manager.get_question_by_id(question_id)
        return question

    async def get_text_question_by_id(self, text_question_id: int) -> TextQuestion:
        text_question = await self.text_question_data_manager.get_text_question_by_id(
            text_question_id
        )
        return text_question

    async def get_answer_by_id(self, answer_id: int) -> Answer:
        answer = await self.answer_data_manager.get_answer_by_id(answer_id)
        return answer

    async def get_group_users_by_exam(self, exam: Exam) -> List[User]:
        users = await self.user_data_manager.get_by_exam(exam)
        return users

    async def delete_exam(self, user: User, exam: Exam) -> None:
        if user != exam.author:
            raise ForbiddenError(detail="У вас нет прав для удаления этого экзамена.")
        if not exam:
            raise ExamNotFoundError()
        await self.exam_data_manager.delete(exam)

    async def delete_question(self, user: User, question_id: int) -> None:
        question = await self.question_data_manager.get_question_by_id(question_id)
        if not question:
            raise QuestionNotFoundError()
        if user != question.exam.author:
            raise ForbiddenError(detail="У вас нет прав для удаления этого вопроса.")
        await self.question_data_manager.delete_question(question)

    async def delete_text_question(self, user: User, question_id: int) -> None:
        question = await self.text_question_data_manager.get_text_question_by_id(
            question_id
        )
        if not question:
            raise QuestionNotFoundError()
        if user != question.exam.author:
            raise ForbiddenError(
                detail="У вас нет прав для удаления этого текстового вопроса."
            )
        await self.text_question_data_manager.delete_text_question(question)

    async def delete_answer(self, user: User, answer_id: int) -> None:
        answer = await self.answer_data_manager.get_answer_by_id(answer_id)
        if not answer:
            raise AnswerNotFoundError()
        if user != answer.question.exam.author:
            raise ForbiddenError(detail="У вас нет прав для удаления этого ответа.")
        await self.answer_data_manager.delete(answer)

    async def passed_answers(self, user: User, user_id: int, exam: Exam) -> List:
        if user != exam.author:
            raise ForbiddenError(
                detail="У вас нет прав для просмотра ответов на этот экзамен."
            )
        if not exam:
            raise ExamNotFoundError()
        passed_text_answers, passed_choice_answers = [], []
        if exam.is_advanced_exam:
            passed_text_answers = (
                await self.__get_passed_text_answers(user_id, exam.id) or []
            )
            if hasattr(exam, "passed_choice_answers"):
                passed_choice_answers = (
                    await self.__get_passed_choice_answers(user_id, exam.id) or []
                )
        else:
            passed_choice_answers = (
                await self.__get_passed_choice_answers(user_id, exam.id) or []
            )

        choice_answers = [
            PassedChoiceAnswerResponseSchema(
                id=answer.id,
                question=QuestionShortResponseSchema.model_validate(
                    answer.question.__dict__
                ),
                selected_answer=AnswerResponseSchema.model_validate(
                    answer.selected_answer.__dict__
                ),
                is_correct=answer.is_correct,
                created_at=answer.created_at,
            )
            for answer in passed_choice_answers
        ]
        text_answers = [
            PassedTextAnswerResponseSchema(
                id=answer.id,
                question=QuestionShortResponseSchema.model_validate(
                    answer.question.__dict__
                ),
                text=answer.text,
                created_at=answer.created_at,
            )
            for answer in passed_text_answers
        ]
        return [choice_answers, text_answers]

    async def __get_passed_choice_answers(
        self, user_id: int, exam_id: int
    ) -> List[PassedChoiceAnswer]:
        user = await self.user_data_manager.get_user_by_id(user_id)
        exam = await self.exam_data_manager.get_exam_by_id(exam_id)
        if not user:
            raise UserNotFoundError()
        if not exam:
            raise ExamNotFoundError()
        passed_answers = await self.answer_data_manager.get_passed_choise_answers(
            user, exam
        )
        return passed_answers

    async def __get_passed_text_answers(
        self, user_id: int, exam_id: int
    ) -> List[PassedTextAnswer]:
        user = await self.user_data_manager.get_user_by_id(user_id)
        exam = await self.exam_data_manager.get_exam_by_id(exam_id)
        if not user:
            raise UserNotFoundError()
        if not exam:
            raise ExamNotFoundError()
        passed_answers = await self.answer_data_manager.get_passed_text_answers(
            user, exam
        )
        return passed_answers

    async def get_correct_answer(self, answer_id: int, question: Question) -> Answer:
        answer = await self.answer_data_manager.get_correct_answer(answer_id, question)
        return answer

    async def pass_exam(
        self,
        user: User,
        exam: Exam,
        answers_data: PassingExamDataCreateSchema,
    ) -> ExamResult:
        if not exam:
            raise ExamNotFoundError()
        if exam.is_ended or not exam.is_started:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Экзамен закончился."
                if exam.is_ended
                else "Экзамен еще не начался.",
            )
        if user.is_teacher:
            raise ForbiddenError(detail="Учителя не могут проходить экзамены.")
        if user not in await self.user_data_manager.get_by_exam(exam):
            raise ForbiddenError(
                detail="Вы не состоите в группе, связанной с этим экзаменом."
            )
        if any(result.exam.id == exam.id for result in user.results):
            raise ForbiddenError(detail="Вы уже проходили этот экзамен.")

        if exam.is_advanced_exam:
            for answer in answers_data.text_questions:
                question = (
                    await self.text_question_data_manager.get_text_question_by_id(
                        answer.question_id
                    )
                )
                if not question:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
                await self.answer_data_manager.create_passed_text_answers(
                    user, exam, answer
                )

        if answers_data.choise_questions:
            for answer in answers_data.choise_questions:
                question = await self.question_data_manager.get_question_by_id(
                    answer.question_id
                )
                if not question:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
                await self.answer_data_manager.create_passed_choise_answers(
                    user, exam, answer
                )

        quantity = exam.quantity_questions
        if not exam.is_advanced_exam:
            score = await self.__calculate_exam_score(
                answers_data.choise_questions, quantity
            )
            result = await ExamResultService(self.session).create_result(
                exam.id, user.id, score
            )
            return result
        else:
            result = await ExamResultService(self.session).create_result(
                exam.id, user.id
            )
            await NotificationService(self.session).create_result_notification(result)
            return result

    async def __calculate_exam_score(
        self,
        answers_data: List[SelectAnswerDataCreateSchema],
        quantity: int,
    ):
        if quantity == 0:
            return None

        correct_answers = 0
        for answer_data in answers_data:
            question_id = answer_data.question_id
            answer_id = answer_data.answer_id

            question = await self.get_question_by_id(question_id)
            answer = await self.get_answer_by_id(answer_id)
            if not question:
                raise QuestionNotFoundError()
            if not answer:
                raise AnswerNotFoundError()
            correct_answer = await self.get_correct_answer(answer_id, question)
            if correct_answer:
                correct_answers += 1

        percentage_correct = (correct_answers / quantity) * 100
        if percentage_correct < 30:
            return 2
        elif 40 <= percentage_correct < 70:
            return 3
        elif 70 <= percentage_correct < 90:
            return 4
        elif 90 <= percentage_correct <= 100:
            return 5
        else:
            return None
