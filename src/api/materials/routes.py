from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from api.groups.service import GroupService
from api.users.dependencies import get_current_user
from core.database.db import get_async_session
from core.database.models import User

from .schemas import LectureCreate, LectureRead, LectureUpdate
from .service import LectureService

router = APIRouter(prefix="/materials")
lecture_service = LectureService()
group_service = GroupService()


@router.post(
    "/lecture-create", status_code=status.HTTP_201_CREATED, response_model=LectureRead
)
async def create_lecture(
    title: str = Form(...),
    groups: List[int] = Form(...),
    file: UploadFile = File(...),
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


@router.get(
    "/{group_id}/get-lectures/{author_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[LectureRead],
)
async def get_lectures(
    group_id: int,
    author_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    if not await group_service.contrained_user_in_group(user, group_id, session):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not member of this group.",
        )
    lectures = await lecture_service.get_by_author_id(author_id, group_id, session)
    return lectures


@router.get(
    "/get-my-lectures",
    status_code=status.HTTP_200_OK,
    response_model=List[LectureRead],
)
async def get_my_lectures(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    lectures = await lecture_service.get_my_lectures(user, session)
    return lectures


@router.get(
    "/get-lecture/{lecture_id}",
    status_code=status.HTTP_200_OK,
    response_model=LectureRead,
)
async def get_lecture(
    lecture_id: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    if not request.user.is_authenticated:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    lecture = await lecture_service.get_by_id(lecture_id, session)
    return lecture


@router.patch(
    "/update-lecture/{lecture_id}",
    status_code=status.HTTP_200_OK,
    response_model=LectureRead,
)
async def update_lecture(
    lecture_id: int,
    title: str = Form(None),
    groups: List[int] = Form(None),
    file: UploadFile = File(None),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    lecture = await lecture_service.get_by_id(lecture_id, session)
    if not user.is_teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
        )
    if user != lecture.author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not author."
        )
    lecture_data = LectureUpdate(title=title, groups=groups)
    updated_lecture = await lecture_service.update_lecture(
        lecture, lecture_data, file, session
    )
    return updated_lecture
