from typing import List, Tuple

from core.exceptions import ForbiddenError, GroupNotFoundError
from core.settings import settings
from models import Group, User
from schemas import (
    GroupCreateSchema,
    GroupResponseSchema,
    GroupShortResponseSchema,
    PaginationParams,
    UserKickListSchema,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.base import BaseService
from app.services.v1.groups.data_manager import GroupDataManager


class GroupService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session)
        self.data_manager = GroupDataManager(session)

    async def get_group(self, group_id: int) -> Group:
        group = await self.data_manager.get_item_by_field("id", group_id)
        if not group:
            raise GroupNotFoundError(detail="Группа не найдена")
        return group

    async def get_my_groups(self, user: User) -> List[GroupResponseSchema]:
        groups = await self.data_manager.get_my_groups(user)
        return [GroupResponseSchema.model_validate(group) for group in groups]

    async def get_my_created_groups(self, user: User) -> List[GroupResponseSchema]:
        if not user.is_teacher:
            raise ForbiddenError(
                detail="Недостаточно прав для просмотра созданных групп"
            )
        groups = await self.data_manager.get_items_by_field("methodist", user)
        return [GroupResponseSchema.model_validate(group) for group in groups]

    async def get_all_groups(
        self,
        pagination: PaginationParams,
    ) -> Tuple[List[GroupShortResponseSchema], int]:
        groups, total = await self.data_manager.get_all_groups(pagination)
        return [
            GroupShortResponseSchema.model_validate(group) for group in groups
        ], total

    async def create_group(self, user: User, data: GroupCreateSchema) -> Group:
        if not user.is_teacher:
            raise ForbiddenError(detail="Недостаточно прав для создания группы")
        return await self.data_manager.create_group(data, user)

    async def update_group(
        self, group_id: int, user: User, data: GroupCreateSchema
    ) -> GroupResponseSchema:
        group = await self.data_manager.get_group_by_id(group_id)
        if not group:
            raise GroupNotFoundError(detail="Группа не найдена")
        if user.id != group.methodist.id:
            raise ForbiddenError(detail="Вы не являетесь методистом этой группы")
        updated_group = await self.data_manager.update_group(group, data)
        return GroupResponseSchema.model_validate(updated_group)

    async def delete_group(self, group_id: int, user: User) -> None:
        group = await self.data_manager.get_item_by_field("id", group_id)
        if not group:
            raise GroupNotFoundError(detail="Группа не найдена")
        if user.id != group.methodist.id:
            raise ForbiddenError(detail="Вы не являетесь методистом этой группы")
        await self.data_manager.delete_item(group.id)

    async def generate_invite_link(self, group_id: int, user: User) -> str:
        group = await self.data_manager.get_group_by_id(group_id)
        if not group:
            raise GroupNotFoundError(detail="Группа не найдена")
        if user.id != group.methodist.id:
            raise ForbiddenError(detail="Вы не являетесь методистом этой группы")
        await self.data_manager.generate_invite_link(group)
        return f"{settings.JOIN_GROUP_URL}{group.invite_token}"

    async def join_group_by_invite(
        self, invite_token: str, user: User
    ) -> GroupResponseSchema:
        user = await self.session.merge(user)
        group = await self.data_manager.get_by_invite_token(invite_token)
        if not group:
            raise GroupNotFoundError(detail="Неверная ссылка приглашения")
        member_ids = [member.id for member in group.members]
        if user.id in member_ids:
            raise ForbiddenError(detail="Пользователь уже является участником группы")
        await self.data_manager.join_group(user, group)
        return GroupResponseSchema.model_validate(group)

    async def leave_group(self, group_id: int, user: User) -> None:
        group = await self.data_manager.get_group_by_id(group_id)
        if not group:
            raise GroupNotFoundError(detail="Группа не найдена")
        if group.methodist == user:
            raise ForbiddenError(detail="Методист не может покинуть группу")
        member_ids = [member.id for member in group.members]
        if user.id not in member_ids:
            raise ForbiddenError(detail="Пользователь не является участником группы")
        await self.data_manager.delete_from_group(group, user)

    async def kick_users_from_group(
        self, group_id: int, data: UserKickListSchema, user: User
    ) -> None:
        group = await self.data_manager.get_group_by_id(group_id)
        if not group:
            raise GroupNotFoundError(detail="Группа не найдена")
        if user.id != group.methodist.id:
            raise ForbiddenError(
                detail="Только методист может исключать пользователей из группы"
            )
        for user_id in data.user_ids:
            member = next((m for m in group.members if m.id == user_id), None)
            if member:
                await self.data_manager.delete_from_group(group, member)

    async def contrained_user_in_group(self, user: User, group_id: int) -> bool:
        group = await self.data_manager.get_group_by_id(group_id)
        if not group:
            raise GroupNotFoundError(detail="Группа не найдена")
        return any(member.id == user.id for member in group.members)
