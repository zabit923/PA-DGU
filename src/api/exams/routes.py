from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from api.exams.schemas import ExamCreate, ExamRead, ExamShort, ExamUpdate
from api.exams.service import ExamService
from api.users.dependencies import get_current_user
from core.database import get_async_session
from core.database.models import User
from core.tasks import send_new_exam_email

router = APIRouter(prefix="/exams")
exam_service = ExamService()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ExamRead)
async def create_exam(
    exam_data: ExamCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    if not user.is_teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
        )
    exam = await exam_service.create_exam(exam_data, user, session)

    user_list = await exam_service.get_group_users_by_exam(exam, session)
    filtered_user_list = [u for u in user_list if u != user or not u.is_teacher]
    simplified_user_list = [
        {"email": user.email, "username": user.username} for user in filtered_user_list
    ]
    send_new_exam_email.delay(
        exam.id, user.first_name, user.last_name, simplified_user_list
    )

    return exam


@router.get(
    "/get-by-teacher-id/{teacher_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[ExamShort],
)
async def get_exams_by_teacher(
    teacher_id: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    user = request.user
    if not user.is_authenticated:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    exams = await exam_service.get_teacher_exams(teacher_id, session)
    return exams


@router.get(
    "/get-by-group-id/{group_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[ExamShort],
)
async def get_exams_by_group(
    group_id: int, request: Request, session: AsyncSession = Depends(get_async_session)
):
    user = request.user
    if not user.is_authenticated:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    exams = await exam_service.get_group_exams(group_id, session)
    return exams


@router.patch("/{exam_id}", status_code=status.HTTP_200_OK, response_model=ExamRead)
async def update_exam(
    exam_id: int,
    exam_data: ExamUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    if not user.is_teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
        )
    updated_exam = await exam_service.update_exam(exam_id, exam_data, session)
    return updated_exam


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(
    exam_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    exam = await exam_service.get_exam_by_id(exam_id, session)
    if user != exam.author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not author of this exam.",
        )
    await exam_service.delete_exam(exam_id, session)
    return {"message": "Exam successfully deleted."}


@router.delete("/delete-question/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    question = await exam_service.get_question_by_id(question_id, session)
    if user != question.exam.author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not author of this exam.",
        )
    await exam_service.delete_question(question_id, session)
    return {"message": "Question successfully deleted."}


@router.delete("/delete-answer/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(
    answer_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    answer = await exam_service.get_answer_by_id(answer_id, session)
    if user != answer.question.exam.author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not author of this exam.",
        )
    await exam_service.delete_answer(answer_id, session)
    return {"message": "Answer successfully deleted."}
