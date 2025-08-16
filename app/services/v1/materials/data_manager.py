from typing import List, Optional

from app.models import Group, Lecture, User, group_lectures
from app.schemas import (
    LectureCreateSchema,
    LectureDataSchema,
    LectureUpdateSchema,
    PaginationParams,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.services.v1.base import BaseEntityManager


class LectureDataManager(BaseEntityManager[LectureDataSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=LectureDataSchema, model=Lecture)

    async def get_lecture_by_id(self, lecture_id: int) -> Lecture:
        statement = select(self.model).where(self.model.id == lecture_id)
        return await self.get_one(statement)

    async def get_my_lectures(
        self,
        user: User,
        pagination: PaginationParams,
    ) -> tuple[List[Lecture], int]:
        statement = (
            select(self.model)
            .where(self.model.author == user)
            .order_by(self.model.created_at.desc())
        )
        return await self.get_paginated_items(statement, pagination)

    async def get_by_author(
        self,
        author_id: int,
        group_id: int,
        pagination: PaginationParams,
    ) -> tuple[List[Lecture], int]:
        statement = (
            select(self.model)
            .options(selectinload(self.model.author), selectinload(self.model.groups))
            .join(group_lectures, self.model.id == group_lectures.c.lecture_id)
            .where(
                self.model.author_id == author_id,
                group_lectures.c.group_id == group_id,
            )
            .order_by(self.model.created_at.desc())
        )
        return await self.get_paginated_items(statement, pagination)

    async def get_by_group(
        self,
        group_id: int,
        pagination: PaginationParams,
    ) -> tuple[List[Lecture], int]:
        statement = select(self.model).join(Lecture.groups).where(Group.id == group_id)
        return await self.get_paginated_items(statement, pagination)

    async def create(
        self,
        user: User,
        data: LectureCreateSchema,
        groups: List[Group],
        file_url: Optional[str] = None,
    ) -> Lecture:
        lecture_model = Lecture(
            title=data.title,
            text=data.text,
            author_id=user.id,
            file=file_url,
        )
        self.session.add(lecture_model)
        await self.session.flush()
        await self.session.execute(
            group_lectures.insert().values(
                [
                    {"group_id": group.id, "lecture_id": lecture_model.id}
                    for group in groups
                ]
            )
        )
        await self.session.commit()
        await self.session.refresh(lecture_model)
        return lecture_model

    async def update_lecture(
        self,
        lecture: Lecture,
        data: LectureUpdateSchema,
        groups: List[Group] = None,
        file_url: Optional[str] = None,
    ) -> Lecture:
        if groups:
            current_groups = {group.id for group in lecture.groups}
            groups_to_remove = current_groups - set(data.groups)
            groups_to_add = set(data.groups) - current_groups

            for group_id in groups_to_remove:
                group = next(group for group in lecture.groups if group.id == group_id)
                lecture.groups.remove(group)
            for group_id in groups_to_add:
                group = next(group for group in groups if group.id == group_id)
                lecture.groups.append(group)
        if data.title:
            lecture.title = data.title
        if data.text:
            lecture.text = data.text
        if file_url:
            lecture.file = file_url
        return await self.update_one(lecture)
