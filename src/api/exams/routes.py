from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.exams.schemas import ExamCreate
from api.exams.service import ExamService
from api.users.dependencies import get_current_user
from core.database import get_async_session
from core.database.models import User

router = APIRouter(prefix="/exams")
exam_service = ExamService()


@router.post("")
async def create_exam(
    exam_data: ExamCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    exam = await exam_service.create_exam(
        exam_data,
        user,
        session,
    )
    return exam
