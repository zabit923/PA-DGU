from typing import List

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import aliased
from starlette import status

from api.materials.schemas import LectureCreate
from core.database.models import Group, Lecture, User, group_lectures
from core.utils import save_file


class LectureService:
    async def create_lecture(
        self,
        lecture_data: LectureCreate,
        file: UploadFile,
        user: User,
        session: AsyncSession,
    ) -> Lecture:
        file_name = await save_file(file)

        lecture = Lecture(
            title=lecture_data.title,
            author_id=user.id,
            file=file_name,
        )
        session.add(lecture)
        await session.flush()

        groups_query = await session.execute(
            select(Group).where(Group.id.in_(lecture_data.groups))
        )
        groups = groups_query.scalars().all()
        if len(groups) != len(lecture_data.groups):
            raise HTTPException(status_code=400, detail="Some groups not found.")
        await session.execute(
            group_lectures.insert().values(
                [{"group_id": group.id, "lecture_id": lecture.id} for group in groups]
            )
        )
        await session.commit()
        await session.refresh(lecture)
        return lecture

    async def get_by_id(
        self,
        lecture_id: int,
        user: User,
        session: AsyncSession,
    ) -> Lecture:
        statement = select(Lecture).where(Lecture.id == lecture_id)
        result = await session.execute(statement)
        lecture = result.scalars().first()

        if not lecture:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        if not any(
            group.id in [g.id for g in lecture.groups] for group in user.member_groups
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this group.",
            )
        return lecture

    async def get_my_lectures(
        self,
        user: User,
        session: AsyncSession,
    ) -> List[Lecture]:
        if not user.is_teacher:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        statement = (
            select(Lecture)
            .where(Lecture.author == user)
            .order_by(Lecture.created_at.desc())
        )
        result = await session.execute(statement)
        lectures = result.scalars().all()
        return lectures

    async def get_by_author_id(
        self,
        author_id: int,
        group_id: int,
        session: AsyncSession,
    ) -> List[Lecture]:
        lecture_alias = aliased(Lecture)
        statement = (
            select(lecture_alias)
            .join(group_lectures, lecture_alias.id == group_lectures.c.lecture_id)
            .where(
                author_id == lecture_alias.author_id,
                group_id == group_lectures.c.group_id,
            )
            .order_by(lecture_alias.created_at.desc())
        )
        result = await session.execute(statement)
        lectures = result.scalars().all()
        return lectures
