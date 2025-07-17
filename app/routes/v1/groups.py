from typing import List

from core.dependencies import get_db_session
from core.exceptions import ForbiddenError, GroupNotFoundError
from core.security.auth import get_current_user
from fastapi import Depends, Query
from models import User
from routes.base import BaseRouter
from schemas import GroupListResponseSchema, GroupResponseSchema, Page, PaginationParams
from services.v1.groups.service import GroupService
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


class GroupsRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="groups", tags=["Groups"])

    def configure(self):
        @self.router.post(
            "",
            status_code=status.HTTP_201_CREATED,
            response_model=GroupResponseSchema,
        )
        async def create_group(
            group_data: GroupResponseSchema,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            new_group = await GroupService(session).create_group(user, group_data)
            return new_group

        @self.router.get(
            "/get-my-groups",
            status_code=status.HTTP_200_OK,
            response_model=List[GroupResponseSchema],
        )
        async def get_my_groups(
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            groups = await GroupService(session).get_my_groups(user)
            return groups

        @self.router.get(
            "/get-my-created-groups",
            status_code=status.HTTP_200_OK,
            response_model=List[GroupResponseSchema],
        )
        async def get_my_created_groups(
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            groups = await GroupService(session).get_my_created_groups(user)
            return groups

        @self.router.get(
            "/{group_id}",
            status_code=status.HTTP_200_OK,
            response_model=GroupResponseSchema,
        )
        async def get_group(
            group_id: int,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            group = await GroupService(session).get_group(group_id)
            if not group:
                raise GroupNotFoundError(detail="Группа не найдена")
            if user not in group.members:
                raise ForbiddenError(detail="Вы не являетесь участником этой группы")
            return group

        @self.router.patch(
            "/{group_id}",
            status_code=status.HTTP_200_OK,
            response_model=GroupResponseSchema,
        )
        async def update_group(
            group_id: int,
            group_data: GroupResponseSchema,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            updated_group = await GroupService(session).update_group(
                group_id, user, group_data
            )
            return updated_group

        @self.router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_group(
            group_id: int,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            await GroupService(session).delete_group(group_id, user)
            return

        @self.router.get(
            "",
            status_code=status.HTTP_200_OK,
            response_model=GroupListResponseSchema,
        )
        async def get_groups(
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            _: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            """
            ### Args:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            """
            pagination = PaginationParams(skip=skip, limit=limit)
            groups, total = await GroupService(session).get_all_groups(
                pagination=pagination
            )
            page = Page(
                items=groups,
                total=total,
                page=pagination.page,
                size=pagination.limit,
            )
            return GroupListResponseSchema(data=page)

        @self.router.get(
            "/invite/{group_id}",
            status_code=status.HTTP_200_OK,
        )
        async def invite_to_group(
            group_id: int,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            invite_url = await GroupService(session).generate_invite_link(
                group_id, user
            )
            return {"invite_url": invite_url}

        @self.router.get(
            "/join/{invite_token}",
            status_code=status.HTTP_200_OK,
            response_model=GroupResponseSchema,
        )
        async def join_group(
            invite_token: str,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            group = await GroupService(session).join_group_by_invite(invite_token, user)
            return group

        @self.router.get(
            "leave/{group_id}",
            status_code=status.HTTP_200_OK,
        )
        async def leave_group(
            group_id: int,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            await GroupService(session).leave_group(group_id, user)
            return {"message": "Вы успешно покинули группу."}

        @self.router.post(
            "/kick-user/{group_id}",
            status_code=status.HTTP_200_OK,
        )
        async def kick_user(
            group_id: int,
            user_ids: List[int],
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            await GroupService(session).kick_users_from_group(group_id, user_ids, user)
            return {"message": "Пользователи успешно удалены из группы."}
