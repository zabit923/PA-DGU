from typing import List

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

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

    async def get_by_author_id(
        self,
        author_id: int,
        group_id: int,
        session: AsyncSession,
    ) -> List[Lecture]:
        statement = (
            select(User)
            .join(group_lectures, Lecture.id == group_lectures.c.lecture_id)
            .where(Lecture.author_id == author_id)
            .where(group_id == group_lectures.c.group_id)
            .order_by(Lecture.created_at.desc())
        )
        result = await session.execute(statement)
        lectures = result.scalars().all()
        return lectures
