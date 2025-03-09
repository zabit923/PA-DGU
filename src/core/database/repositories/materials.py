from typing import List, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from core.database.models import Group, Lecture, User, group_lectures


class MaterialRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, lecture_id: int) -> Lecture:
        statement = select(Lecture).where(Lecture.id == lecture_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_my_lectures(self, user: User) -> Sequence[Lecture]:
        statement = (
            select(Lecture)
            .where(Lecture.author == user)
            .order_by(Lecture.created_at.desc())
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_author(self, author_id: int, group_id: int) -> Sequence[Lecture]:
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
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_group(self, group_id: int) -> Sequence[Lecture]:
        statement = select(Lecture).join(Lecture.groups).where(Group.id == group_id)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create(self, lecture: Lecture, groups: List[Group]) -> None:
        self.session.add(lecture)
        await self.session.flush()
        await self.session.execute(
            group_lectures.insert().values(
                [{"group_id": group.id, "lecture_id": lecture.id} for group in groups]
            )
        )
        await self.session.commit()
        await self.session.refresh(lecture)

    async def update(self, lecture: Lecture) -> None:
        await self.session.commit()
        await self.session.refresh(lecture)

    async def delete(self, lecture: Lecture) -> None:
        await self.session.delete(lecture)
        await self.session.commit()
