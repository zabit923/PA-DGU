from typing import List

from api.exams.schemas import (
    ExamCreate,
    ExamRead,
    ExamShort,
    ExamStudentRead,
    ExamUpdate,
    PassingExamData,
    ResultRead,
    ResultUpdate,
)
from api.exams.service import ExamService, exam_service_factory
from api.notifications.service import NotificationService, notification_service_factory
from api.users.dependencies import get_current_user
from core.database.models import User
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.requests import Request

router = APIRouter(prefix="/exams")


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ExamRead)
async def create_exam(
    exam_data: ExamCreate,
    user: User = Depends(get_current_user),
    exam_service: ExamService = Depends(exam_service_factory),
    notification_service: NotificationService = Depends(notification_service_factory),
):
    exam = await exam_service.create_exam(exam_data, user)
    await notification_service.create_new_exam_notification(exam, exam_service)
    return exam


@router.get(
    "/get-by-teacher-id/{teacher_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[ExamShort],
)
async def get_exams_by_teacher(
    teacher_id: int,
    request: Request,
    exam_service: ExamService = Depends(exam_service_factory),
):
    user = request.user
    exams = await exam_service.get_teacher_exams(user, teacher_id)
    return exams


@router.get(
    "/get-by-group-id/{group_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[ExamShort],
)
async def get_exams_by_group(
    group_id: int,
    request: Request,
    exam_service: ExamService = Depends(exam_service_factory),
):
    user = request.user
    exams = await exam_service.get_group_exams(user, group_id)
    return exams


@router.patch("/{exam_id}", status_code=status.HTTP_200_OK, response_model=ExamRead)
async def update_exam(
    exam_id: int,
    exam_data: ExamUpdate,
    user: User = Depends(get_current_user),
    exam_service: ExamService = Depends(exam_service_factory),
):
    updated_exam = await exam_service.update_exam(user, exam_id, exam_data)
    return updated_exam


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(
    exam_id: int,
    user: User = Depends(get_current_user),
    exam_service: ExamService = Depends(exam_service_factory),
):
    exam = await exam_service.get_exam_by_id(exam_id)
    await exam_service.delete_exam(user, exam)
    return


@router.delete("/delete-question/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    user: User = Depends(get_current_user),
    exam_service: ExamService = Depends(exam_service_factory),
):
    await exam_service.delete_question(user, question_id)
    return


@router.delete(
    "/delete-text-question/{text_question_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_text_question(
    text_question_id: int,
    user: User = Depends(get_current_user),
    exam_service: ExamService = Depends(exam_service_factory),
):
    await exam_service.delete_text_question(user, text_question_id)
    return


@router.get("/{exam_id}", status_code=status.HTTP_200_OK)
async def get_exam(
    exam_id: int,
    user: User = Depends(get_current_user),
    exam_service: ExamService = Depends(exam_service_factory),
) -> ExamStudentRead | ExamRead:
    exam = await exam_service.get_exam_by_id(exam_id)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    exam_data = exam.__dict__
    exam = await exam_service.get_full_exam(user, exam, exam_data)
    return exam


@router.delete("/delete-answer/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(
    answer_id: int,
    user: User = Depends(get_current_user),
    exam_service: ExamService = Depends(exam_service_factory),
):
    await exam_service.delete_answer(user, answer_id)
    return


@router.post(
    "/pass-exam/{exam_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=ResultRead,
)
async def pass_exam(
    exam_id: int,
    answers_data: PassingExamData,
    user: User = Depends(get_current_user),
    exam_service: ExamService = Depends(exam_service_factory),
    notification_service: NotificationService = Depends(notification_service_factory),
):
    exam = await exam_service.get_exam_by_id(exam_id)
    result = await exam_service.pass_exam(
        user, exam, answers_data, notification_service
    )
    return result


@router.patch(
    "/update-result/{result_id}",
    status_code=status.HTTP_200_OK,
    response_model=ResultRead,
)
async def update_result(
    result_id: int,
    result_data: ResultUpdate,
    user: User = Depends(get_current_user),
    exam_service: ExamService = Depends(exam_service_factory),
    notification_service: NotificationService = Depends(notification_service_factory),
):
    result = await exam_service.update_result(result_id, result_data, user)
    await notification_service.update_result_notification(result)
    return result


@router.get(
    "/get-result/{result_id}", status_code=status.HTTP_200_OK, response_model=ResultRead
)
async def get_result(
    result_id: int,
    _: User = Depends(get_current_user),
    exam_service: ExamService = Depends(exam_service_factory),
):
    result = await exam_service.get_result_by_id(result_id)
    return result


@router.get(
    "/get-results-by-exam/{exam_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[ResultRead],
)
async def get_results_by_exam(
    exam_id: int,
    _: User = Depends(get_current_user),
    exam_service: ExamService = Depends(exam_service_factory),
):
    result = await exam_service.get_results_by_exam(exam_id)
    return result


@router.get(
    "/get-results-by-user/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[ResultRead],
)
async def get_results_by_user(
    user_id: int,
    _: User = Depends(get_current_user),
    exam_service: ExamService = Depends(exam_service_factory),
):
    result = await exam_service.get_results_by_user(user_id)
    return result


@router.get(
    "/get-passed-answers-by-user/{user_id}/{exam_id}", status_code=status.HTTP_200_OK
)
async def get_passed_answers_by_user(
    user_id: int,
    exam_id: int,
    _: User = Depends(get_current_user),
    exam_service: ExamService = Depends(exam_service_factory),
):
    exam = await exam_service.get_exam_by_id(exam_id)
    answers = await exam_service.passed_answers(user_id, exam)
    return {
        "passed_choice_answers": answers[0],
        "passed_text_answers": answers[1],
    }
