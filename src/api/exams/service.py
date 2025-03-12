from datetime import datetime
from typing import Optional, Sequence

import pytz
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.authentication import BaseUser

from api.exams.schemas import (
    AnswerRead,
    AnswerStudentRead,
    ExamCreate,
    ExamRead,
    ExamStudentRead,
    ExamUpdate,
    PassedChoiceAnswerRead,
    PassedTextAnswerRead,
    PassingExamData,
    QuestionRead,
    QuestionStudentRead,
    ResultUpdate,
    ShortQuestionRead,
    TextQuestionRead,
)
from api.exams.utils import calculate_exam_score
from api.groups.schemas import GroupShort
from api.notifications.service import NotificationService
from api.users.schemas import UserShort
from core.database import get_async_session
from core.database.models import (
    Answer,
    Exam,
    ExamResult,
    PassedChoiceAnswer,
    PassedTextAnswer,
    Question,
    TextQuestion,
    User,
)
from core.database.repositories import (
    AnswerRepository,
    ExamRepository,
    GroupRepository,
    QuestionRepository,
    ResultRepository,
    UserRepository,
)


class ExamService:
    def __init__(
        self,
        exam_repository: ExamRepository,
        group_repository: GroupRepository,
        user_repository: UserRepository,
        question_repository: QuestionRepository,
        answer_repository: AnswerRepository,
        result_repository: ResultRepository,
    ):
        self.exam_repository = exam_repository
        self.group_repository = group_repository
        self.user_repository = user_repository
        self.question_repository = question_repository
        self.answer_repository = answer_repository
        self.result_repository = result_repository

    async def create_exam(self, exam_data: ExamCreate, user: User) -> Exam:
        if not user.is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
            )
        if (
            exam_data.start_time >= exam_data.end_time
            or exam_data.start_time < datetime.now(pytz.timezone("UTC"))
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start time must be earlier than end time and start time must be later than now.",
            )
        groups = await self.group_repository.get_by_ids(exam_data.groups)
        if len(groups) != len(exam_data.groups):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Some groups were not found.",
            )
        new_exam = await self.exam_repository.create(
            exam_data, user, groups, self.question_repository, self.answer_repository
        )
        return new_exam

    async def update_exam(
        self, user: User, exam_id: int, exam_data: ExamUpdate
    ) -> Exam:
        if not user.is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
            )
        exam = await self.exam_repository.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        exam_data_dict = exam_data.model_dump(exclude_unset=True)

        if "groups" in exam_data_dict:
            groups = await self.group_repository.get_by_ids(
                exam_data_dict.pop("groups")
            )
            if len(groups) != len(exam_data.groups):
                raise HTTPException(
                    status_code=404, detail="Some groups were not found."
                )
            exam.groups = groups
        if "questions" in exam_data_dict:
            try:
                await self.question_repository.update_questions(
                    exam, exam_data_dict.pop("questions"), self.answer_repository
                )
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
        if "text_questions" in exam_data_dict:
            try:
                await self.question_repository.update_text_questions(
                    exam, exam_data_dict.pop("text_questions")
                )
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))

        for key, value in exam_data_dict.items():
            setattr(exam, key, value)

        return await self.exam_repository.update(exam)

    async def get_teacher_exams(
        self, user: BaseUser, teacher_id: int
    ) -> Sequence[Exam]:
        if not user.is_authenticated:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        teacher = await self.user_repository.get_by_id(teacher_id)
        if not teacher:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        exams = await self.exam_repository.get_by_author(teacher_id)
        return exams

    async def get_group_exams(self, user: BaseUser, group_id: int) -> Sequence[Exam]:
        if not user.is_authenticated:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        group = await self.group_repository.get_by_id(group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        exams = await self.exam_repository.get_by_group(group_id)
        return exams

    async def get_exam_by_id(self, exam_id: int) -> Exam:
        exam = await self.exam_repository.get_by_id(exam_id)
        return exam

    @staticmethod
    async def get_full_exam(
        user: User, exam: Exam, exam_data: dict
    ) -> ExamStudentRead | ExamRead:
        exam_data["author"] = UserShort.model_validate(exam.author.__dict__)
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

    async def get_question_by_id(self, question_id: int) -> Question:
        question = await self.question_repository.get_question_by_id(question_id)
        return question

    async def get_text_question_by_id(self, text_question_id: int) -> TextQuestion:
        question = await self.question_repository.get_text_question_by_id(
            text_question_id
        )
        return question

    async def get_answer_by_id(self, answer_id: int) -> Answer:
        answer = await self.answer_repository.get_by_id(answer_id)
        return answer

    async def get_group_users_by_exam(self, exam: Exam) -> Sequence[User]:
        users = await self.user_repository.get_by_exam(exam)
        return users

    async def delete_exam(self, user: User, exam: Exam) -> None:
        if user != exam.author:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not author of this exam.",
            )
        if not exam:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await self.exam_repository.delete(exam)

    async def delete_question(self, user: User, question_id: int) -> None:
        question = await self.question_repository.get_question_by_id(question_id)
        if user != question.exam.author:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not author of this exam.",
            )
        if not question:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await self.question_repository.delete_question(question)

    async def delete_text_question(self, user: User, question_id: int) -> None:
        question = await self.question_repository.get_text_question_by_id(question_id)
        if user != question.exam.author:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not author of this exam.",
            )
        if not question:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await self.question_repository.delete_text_question(question)

    async def delete_answer(self, user: User, answer_id: int) -> None:
        answer = await self.answer_repository.get_by_id(answer_id)
        if user != answer.question.exam.author:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not author of this exam.",
            )
        if not answer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await self.answer_repository.delete(answer)

    async def create_result(
        self, exam_id: int, user_id: int, score: Optional[int] = None
    ) -> ExamResult:
        new_result = await self.result_repository.create(exam_id, user_id, score)
        return new_result

    async def update_result(
        self,
        result_id: int,
        result_data: ResultUpdate,
        user: User,
    ) -> ExamResult:
        result = await self.result_repository.get_by_id(result_id)
        if not user.is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
            )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Result not found"
            )
        result.score = result_data.score
        await self.result_repository.update(result)
        return result

    async def get_result_by_id(self, result_id: int) -> ExamResult:
        exam_result = await self.result_repository.get_by_id(result_id)
        if not exam_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return exam_result

    async def get_results_by_exam(self, exam_id: int) -> Sequence[ExamResult]:
        exam_results = await self.result_repository.get_by_exam(exam_id)
        return exam_results

    async def get_results_by_user(self, user_id: int) -> Sequence[ExamResult]:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        exam_results = await self.result_repository.get_by_user(user)
        return exam_results

    async def passed_answers(self, user_id: int, exam: Exam) -> list:
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
            )
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

    async def __get_passed_choice_answers(
        self, user_id: int, exam_id: int
    ) -> Sequence[PassedChoiceAnswer]:
        user = await self.user_repository.get_by_id(user_id)
        exam = await self.exam_repository.get_by_id(exam_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
            )
        passed_answers = await self.answer_repository.get_passed_choise_answers(
            user, exam
        )
        return passed_answers

    async def __get_passed_text_answers(
        self, user_id: int, exam_id: int
    ) -> Sequence[PassedTextAnswer]:
        user = await self.user_repository.get_by_id(user_id)
        exam = await self.exam_repository.get_by_id(exam_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
            )
        passed_answers = await self.answer_repository.get_passed_text_answers(
            user, exam
        )
        return passed_answers

    async def get_correct_answer(self, answer_id: int, question: Question) -> Answer:
        answer = await self.answer_repository.get_correct_answer(answer_id, question)
        return answer

    async def pass_exam(
        self,
        user: User,
        exam: Exam,
        answers_data: PassingExamData,
        notification_service: NotificationService,
    ) -> ExamResult:
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found."
            )
        if exam.is_ended or not exam.is_started:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exam was ended." if exam.is_ended else "Exam is not started.",
            )
        if user.is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not a student."
            )
        if user not in await self.user_repository.get_by_exam(exam):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not in this exam's group.",
            )
        if any(result.exam.id == exam.id for result in user.results):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You have already passed this exam.",
            )

        if exam.is_advanced_exam:
            for answer in answers_data.text_questions:
                question = await self.question_repository.get_text_question_by_id(
                    answer.question_id
                )
                if not question:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
                await self.answer_repository.create_passed_text_answers(
                    user, exam, answer
                )

        if answers_data.choise_questions:
            for answer in answers_data.choise_questions:
                question = await self.question_repository.get_question_by_id(
                    answer.question_id
                )
                if not question:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
                await self.answer_repository.create_passed_choise_answers(
                    user, exam, answer
                )

        quantity = exam.quantity_questions
        if not exam.is_advanced_exam:
            score = await calculate_exam_score(
                self, answers_data.choise_questions, quantity
            )
            result = await self.create_result(exam.id, user.id, score)
            await notification_service.create_result_notification(result)
            return result
        else:
            result = await self.create_result(exam.id, user.id)
            await notification_service.create_result_notification(result)
            return result


def exam_service_factory(
    session: AsyncSession = Depends(get_async_session),
) -> ExamService:
    return ExamService(
        ExamRepository(session),
        GroupRepository(session),
        UserRepository(session),
        QuestionRepository(session),
        AnswerRepository(session),
        ResultRepository(session),
    )
