from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.exams.schemas import ExamCreate, ExamRead
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
