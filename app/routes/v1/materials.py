import json

from core.dependencies import get_db_session
from core.security.auth import get_current_user
from fastapi import Depends, File, Form, Query, UploadFile
from models import User
from routes.base import BaseRouter
from schemas import (
    LectureCreateSchema,
    LectureListResponseSchema,
    LectureResponseSchema,
    LectureUpdateSchema,
    Page,
    PaginationParams,
)
from services.v1.materials.service import LectureService
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


class LectureRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="materials", tags=["Lectures"])

    def configure(self):
        @self.router.post(
            "",
            status_code=status.HTTP_201_CREATED,
            response_model=LectureResponseSchema,
        )
        async def create_lecture(
            title: str = Form(...),
            text: str = Form(None),
            groups: str = Form(...),
            file: UploadFile = File(None),
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            groups_list = json.loads(groups)
            lecture_data = LectureCreateSchema(
                title=title, text=text, groups=groups_list
            )
            new_lecture = await LectureService(session).create_lecture(
                lecture_data, file, user
            )
            return new_lecture

        @self.router.get(
            "/{group_id}/get-lectures/{author_id}",
            status_code=status.HTTP_200_OK,
            response_model=LectureListResponseSchema,
        )
        async def get_lectures(
            group_id: int,
            author_id: int,
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            """
            ### Args:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            """
            pagination = PaginationParams(skip=skip, limit=limit)
            lectures, total = await LectureService(session).get_by_author_id(
                author_id, group_id, user
            )
            page = Page(
                items=lectures,
                total=total,
                page=pagination.page,
                size=pagination.limit,
            )
            return LectureListResponseSchema(data=page)

        @self.router.get(
            "/get-my-lectures",
            status_code=status.HTTP_200_OK,
            response_model=LectureListResponseSchema,
        )
        async def get_my_lectures(
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            """
            ### Args:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            """
            pagination = PaginationParams(skip=skip, limit=limit)
            lectures, total = await LectureService(session).get_my_lectures(
                user, pagination
            )
            page = Page(
                items=lectures,
                total=total,
                page=pagination.page,
                size=pagination.limit,
            )
            return LectureListResponseSchema(data=page)

        @self.router.get(
            "/get-all-lectures/{group_id}",
            status_code=status.HTTP_200_OK,
            response_model=LectureListResponseSchema,
        )
        async def get_all_lectures(
            group_id: int,
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            """
            ### Args:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            """
            pagination = PaginationParams(skip=skip, limit=limit)
            lectures, total = await LectureService(session).get_by_group_id(
                group_id, user, pagination
            )
            page = Page(
                items=lectures,
                total=total,
                page=pagination.page,
                size=pagination.limit,
            )
            return LectureListResponseSchema(data=page)

        @self.router.get(
            "/{lecture_id}",
            status_code=status.HTTP_200_OK,
            response_model=LectureResponseSchema,
        )
        async def get_lecture(
            lecture_id: int,
            _: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            lecture = await LectureService(session).get_by_id(lecture_id)
            return lecture

        @self.router.patch(
            "/{lecture_id}",
            status_code=status.HTTP_200_OK,
            response_model=LectureResponseSchema,
        )
        async def update_lecture(
            lecture_id: int,
            title: str = Form(None),
            text: str = Form(None),
            groups: str = Form(None),
            file: UploadFile = File(None),
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            groups_list = (
                [int(g.strip()) for g in groups.split(",")] if groups else None
            )
            lecture_data = LectureUpdateSchema(
                title=title, text=text, groups=groups_list
            )
            updated_lecture = await LectureService(session).update_lecture(
                lecture_id, lecture_data, user, file
            )
            return updated_lecture

        @self.router.delete(
            "/{lecture_id}",
            status_code=status.HTTP_204_NO_CONTENT,
        )
        async def delete_lecture(
            lecture_id: int,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            await LectureService(session).delete_lecture(user, lecture_id)
            return
