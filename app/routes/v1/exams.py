from typing import List

from core.exceptions import ExamNotFoundError
from fastapi import Depends
from models import User
from routes.base import BaseRouter
from schemas import (
    ExamCreateSchema,
    ExamResponseSchema,
    ExamResultResponseSchema,
    ExamResultUpdateSchema,
    ExamShortResponseSchema,
    ExamStudentResponseSchema,
    ExamUpdateSchema,
    PassingExamDataCreateSchema,
)
from services.v1.notifications.service import NotificationService
from services.v1.results.service import ExamResultService
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.dependencies import get_db_session
from app.core.security.auth import get_current_user
from app.services.v1.exams.service import ExamService


class ExamRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="exams", tags=["Exams"])

    def configure(self):
        @self.router.post(
            "", status_code=status.HTTP_201_CREATED, response_model=ExamResponseSchema
        )
        async def create_exam(
            exam_data: ExamCreateSchema,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            exam = await ExamService(session).create_exam(exam_data, user)
            await NotificationService(session).create_new_exam_notification(exam)
            return exam

        @self.router.get(
            "/get-by-teacher-id/{teacher_id}",
            status_code=status.HTTP_200_OK,
            response_model=List[ExamShortResponseSchema],
        )
        async def get_exams_by_teacher(
            teacher_id: int,
            _: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            exams = await ExamService(session).get_teacher_exams(teacher_id)
            return exams

        @self.router.get(
            "/get-by-group-id/{group_id}",
            status_code=status.HTTP_200_OK,
            response_model=List[ExamShortResponseSchema],
        )
        async def get_exams_by_group(
            group_id: int,
            _: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            exams = await ExamService(session).get_group_exams(group_id)
            return exams

        @self.router.patch(
            "/{exam_id}",
            status_code=status.HTTP_200_OK,
            response_model=ExamResponseSchema,
        )
        async def update_exam(
            exam_id: int,
            exam_data: ExamUpdateSchema,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            updated_exam = await ExamService(session).update_exam(
                user, exam_id, exam_data
            )
            return updated_exam

        @self.router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_exam(
            exam_id: int,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            exam = await ExamService(session).get_exam_by_id(exam_id)
            await ExamService(session).delete_exam(user, exam)
            return

        @self.router.delete(
            "/delete-question/{question_id}", status_code=status.HTTP_204_NO_CONTENT
        )
        async def delete_question(
            question_id: int,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            await ExamService(session).delete_question(user, question_id)
            return

        @self.router.delete(
            "/delete-text-question/{text_question_id}",
            status_code=status.HTTP_204_NO_CONTENT,
        )
        async def delete_text_question(
            text_question_id: int,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            await ExamService(session).delete_text_question(user, text_question_id)
            return

        @self.router.get("/{exam_id}", status_code=status.HTTP_200_OK)
        async def get_exam(
            exam_id: int,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ) -> ExamStudentResponseSchema | ExamResponseSchema:
            exam = await ExamService(session).get_exam_by_id(exam_id)
            if not exam:
                raise ExamNotFoundError()
            exam_data = exam.__dict__
            exam = await ExamService(session).get_full_exam(user, exam, exam_data)
            return exam

        @self.router.delete(
            "/delete-answer/{answer_id}", status_code=status.HTTP_204_NO_CONTENT
        )
        async def delete_answer(
            answer_id: int,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            await ExamService(session).delete_answer(user, answer_id)
            return

        @self.router.post(
            "/pass-exam/{exam_id}",
            status_code=status.HTTP_201_CREATED,
            response_model=ExamResultResponseSchema,
        )
        async def pass_exam(
            exam_id: int,
            answers_data: PassingExamDataCreateSchema,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            exam = await ExamService(session).get_exam_by_id(exam_id)
            result = await ExamService(session).pass_exam(user, exam, answers_data)
            return result

        @self.router.patch(
            "/update-result/{result_id}",
            status_code=status.HTTP_200_OK,
            response_model=ExamResultResponseSchema,
        )
        async def update_result(
            result_id: int,
            result_data: ExamResultUpdateSchema,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            result = await ExamResultService(session).update_result(
                result_id, result_data, user
            )
            await NotificationService(session).update_result_notification(result)
            return result

        @self.router.get(
            "/get-result/{result_id}",
            status_code=status.HTTP_200_OK,
            response_model=ExamResultResponseSchema,
        )
        async def get_result(
            result_id: int,
            _: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            result = await ExamResultService(session).get_result_by_id(result_id)
            return result

        @self.router.get(
            "/get-results-by-exam/{exam_id}",
            status_code=status.HTTP_200_OK,
            response_model=List[ExamResultResponseSchema],
        )
        async def get_results_by_exam(
            exam_id: int,
            _: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            result = await ExamResultService(session).get_results_by_exam(exam_id)
            return result

        @self.router.get(
            "/get-results-by-user/{user_id}",
            status_code=status.HTTP_200_OK,
            response_model=List[ExamResultResponseSchema],
        )
        async def get_results_by_user(
            user_id: int,
            _: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            result = await ExamResultService(session).get_results_by_user(user_id)
            return result

        @self.router.get(
            "/get-passed-answers-by-user/{user_id}/{exam_id}",
            status_code=status.HTTP_200_OK,
        )
        async def get_passed_answers_by_user(
            user_id: int,
            exam_id: int,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            exam = await ExamService(session).get_exam_by_id(exam_id)
            answers = await ExamService(session).passed_answers(user, user_id, exam)
            return {
                "passed_choice_answers": answers[0],
                "passed_text_answers": answers[1],
            }
