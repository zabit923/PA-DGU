import json
from typing import List

from api.groups.service import GroupService, group_service_factory
from api.notifications.service import NotificationService, notification_service_factory
from api.users.dependencies import get_current_user
from core.database.models import User
from fastapi import APIRouter, Depends, File, Form, UploadFile
from starlette import status

from .schemas import LectureCreate, LectureRead, LectureUpdate
from .service import LectureService, lecture_service_factory

router = APIRouter(prefix="/materials")


@router.post("", status_code=status.HTTP_201_CREATED, response_model=LectureRead)
async def create_lecture(
    title: str = Form(...),
    text: str = Form(None),
    groups: str = Form(...),
    file: UploadFile = File(None),
    user: User = Depends(get_current_user),
    lecture_service: LectureService = Depends(lecture_service_factory),
    notification_service: NotificationService = Depends(notification_service_factory),
):
    groups_list = json.loads(groups)
    lecture_data = LectureCreate(title=title, text=text, groups=groups_list)
    new_lecture = await lecture_service.create_lecture(
        lecture_data, file, user, notification_service
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
    lecture_service: LectureService = Depends(lecture_service_factory),
    group_service: GroupService = Depends(group_service_factory),
):
    lectures = await lecture_service.get_by_author_id(
        author_id, group_id, user, group_service
    )
    return lectures


@router.get(
    "/get-my-lectures",
    status_code=status.HTTP_200_OK,
    response_model=List[LectureRead],
)
async def get_my_lectures(
    user: User = Depends(get_current_user),
    lecture_service: LectureService = Depends(lecture_service_factory),
):
    lectures = await lecture_service.get_my_lectures(user)
    return lectures


@router.get(
    "/get-all-lectures/{group_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[LectureRead],
)
async def get_all_lectures(
    group_id: int,
    user: User = Depends(get_current_user),
    lecture_service: LectureService = Depends(lecture_service_factory),
    group_service: GroupService = Depends(group_service_factory),
):
    lectures = await lecture_service.get_by_group_id(group_id, user, group_service)
    return lectures


@router.get(
    "/{lecture_id}",
    status_code=status.HTTP_200_OK,
    response_model=LectureRead,
)
async def get_lecture(
    lecture_id: int,
    _: User = Depends(get_current_user),
    lecture_service: LectureService = Depends(lecture_service_factory),
):
    lecture = await lecture_service.get_by_id(lecture_id)
    return lecture


@router.patch(
    "/{lecture_id}",
    status_code=status.HTTP_200_OK,
    response_model=LectureRead,
)
async def update_lecture(
    lecture_id: int,
    title: str = Form(None),
    text: str = Form(None),
    groups: str = Form(None),
    file: UploadFile = File(None),
    user: User = Depends(get_current_user),
    lecture_service: LectureService = Depends(lecture_service_factory),
):
    lecture = await lecture_service.get_by_id(lecture_id)
    groups_list = [int(g.strip()) for g in groups.split(",")] if groups else None
    lecture_data = LectureUpdate(title=title, text=text, groups=groups_list)
    updated_lecture = await lecture_service.update_lecture(
        lecture, lecture_data, file, user
    )
    return updated_lecture


@router.delete(
    "/{lecture_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_lecture(
    lecture_id: int,
    user: User = Depends(get_current_user),
    lecture_service: LectureService = Depends(lecture_service_factory),
):
    await lecture_service.delete_lecture(user, lecture_id)
    return
