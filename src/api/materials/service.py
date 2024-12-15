from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.materials.schemas import LectureCreate
from core.database.models import Group, User
from core.database.models.materials import Lecture
from core.utils import save_file


class LectureService:
    async def create_lecture(
        self,
        lecture_data: LectureCreate,
        file: Optional[UploadFile],
        user: User,
        session: AsyncSession,
    ) -> Lecture:
        lecture = Lecture(title=lecture_data.title, author_id=user.id)
        session.add(lecture)
        await session.flush()

        groups_query = await session.execute(
            select(Group).where(Group.id.in_(lecture_data.groups))
        )
        groups = groups_query.scalars().all()
        if len(groups) != len(lecture_data.groups):
            raise HTTPException(status_code=400, detail="Некоторые группы не найдены")
        lecture.groups.extend(groups)

        if file:
            file_name = await save_file(file)
            lecture.file = file_name

        await session.commit()
        await session.refresh(lecture)
        return lecture
