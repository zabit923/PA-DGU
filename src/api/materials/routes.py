from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.users.dependencies import get_current_user
from core.database.db import get_async_session
from core.database.models import User

from .schemas import LectureCreate, LectureRead
from .service import LectureService

router = APIRouter(prefix="/materials")
lecture_service = LectureService()


@router.post(
    "/lecture-create", status_code=status.HTTP_201_CREATED, response_model=LectureRead
)
async def create_lecture(
    title: str = Form(...),
    groups: List[int] = Form(...),
    file: Optional[UploadFile] = File(None),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    if not user.is_teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
        )
    lecture_data = LectureCreate(title=title, groups=groups)
    new_lecture = await lecture_service.create_lecture(
        lecture_data, file, user, session
    )
    return new_lecture
