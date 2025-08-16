from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.dependencies import get_db_session
from app.routes.base import BaseRouter
from app.schemas import CategoryListResponseSchema, CategoryResponseSchema, PaginationParams
from app.services.v1.categories.service import CategoryService


class CategoryRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="categories", tags=["Categories"])

    def configure(self):
        @self.router.get(
            "/",
            status_code=status.HTTP_200_OK,
            response_model=CategoryListResponseSchema,
        )
        async def get_all_categories(
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            session: AsyncSession = Depends(get_db_session),
        ):
            """
            ### Args:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            """
            pagination = PaginationParams(skip=skip, limit=limit)
            categories, total = await CategoryService(session).get_all_categories(
                pagination
            )
            page = {
                "items": categories,
                "total": total,
                "page": pagination.page,
                "size": pagination.limit,
            }
            return CategoryListResponseSchema(data=page)

        @self.router.get(
            "/{category_id}",
            status_code=status.HTTP_200_OK,
            response_model=CategoryResponseSchema,
        )
        async def get_category(
            category_id: int,
            session: AsyncSession = Depends(get_db_session),
        ):
            category = await CategoryService(session).get_category_by_id(category_id)
            return category
