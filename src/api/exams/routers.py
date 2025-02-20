from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

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
from api.exams.service import ExamService
from api.exams.utils import calculate_exam_score
from api.notifications.service import NotificationService
from api.users.dependencies import get_current_user
from core.database import get_async_session
from core.database.models import Answer, PassedChoiceAnswer, PassedTextAnswer, User

router = APIRouter(prefix="/exams")

exam_service = ExamService()

notification_service = NotificationService()


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
    await notification_service.create_new_exam_notification(exam, session)
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


@router.delete(
    "/delete-text-question/{text_question_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_text_question(
    text_question_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    text_question = await exam_service.get_text_question_by_id(
        text_question_id, session
    )
    if user != text_question.exam.author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not author of this exam.",
        )
    await exam_service.delete_text_question(text_question_id, session)
    return {"message": "Question successfully deleted."}


@router.get("/{exam_id}", status_code=status.HTTP_200_OK)
async def get_exam(
    exam_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> ExamStudentRead | ExamRead:
    exam = await exam_service.get_exam_by_id(exam_id, session)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    exam_data = exam.__dict__
    exam = await exam_service.get_full_exam(user, exam, exam_data)
    return exam


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


@router.post(
    "/pass-exam/{exam_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=ResultRead,
)
async def pass_exam(
    exam_id: int,
    answers_data: PassingExamData,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    exam = await exam_service.get_exam_by_id(exam_id, session)
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
    if user not in await exam_service.get_group_users_by_exam(exam, session):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not in this exam's group.",
        )
    if any(result.exam.id == exam_id for result in user.results):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have already passed this exam.",
        )

    if exam.is_advanced_exam:
        for answer in answers_data.text_questions:
            question = await exam_service.get_text_question_by_id(
                answer.question_id, session
            )
            if not question:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            session.add(
                PassedTextAnswer(
                    user_id=user.id,
                    exam_id=exam.id,
                    question_id=answer.question_id,
                    text=answer.text,
                )
            )

    if answers_data.choise_questions:
        for answer in answers_data.choise_questions:
            question = await exam_service.get_question_by_id(
                answer.question_id, session
            )
            if not question:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            correct_answer = await session.execute(
                select(Answer).where(
                    Answer.question_id == answer.question_id, Answer.is_correct == True
                )
            )
            correct_answer = correct_answer.scalar()
            session.add(
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

    quantity = exam.quantity_questions
    if not exam.is_advanced_exam:
        score = await calculate_exam_score(
            answers_data.choise_questions, quantity, session
        )
        result = await exam_service.create_result(exam.id, user.id, session, score)
    else:
        result = await exam_service.create_result(exam.id, user.id, session)
    await notification_service.create_result_notification(result, session)
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
    session: AsyncSession = Depends(get_async_session),
):
    if not user.is_teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
        )
    result = await exam_service.get_result_by_id(result_id, session)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Result not found"
        )
    result.score = result_data.score
    session.add(result)
    await session.commit()
    await session.refresh(result)
    await notification_service.update_result_notification(result, session)
    return result


@router.get(
    "/get-result/{result_id}", status_code=status.HTTP_200_OK, response_model=ResultRead
)
async def get_result(
    request: Request,
    result_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    if not request.user.is_authenticated:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    result = await exam_service.get_result_by_id(result_id, session)
    return result


@router.get(
    "/get-results-by-exam/{exam_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[ResultRead],
)
async def get_results_by_exam(
    request: Request,
    exam_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    if not request.user.is_authenticated:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    result = await exam_service.get_results_by_exam(exam_id, session)
    return result


@router.get(
    "/get-results-by-user/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[ResultRead],
)
async def get_results_by_user(
    request: Request,
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    if not request.user.is_authenticated:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    result = await exam_service.get_results_by_user(user_id, session)
    return result


@router.get(
    "/get-passed-answers-by-user/{user_id}/{exam_id}", status_code=status.HTTP_200_OK
)
async def get_passed_answers_by_user(
    request: Request,
    user_id: int,
    exam_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    if not request.user.is_authenticated:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    exam = await exam_service.get_exam_by_id(exam_id, session)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )
    answers = await exam_service.passed_answers(user_id, exam, session)
    return {
        "passed_choice_answers": answers[0],
        "passed_text_answers": answers[1],
    }
