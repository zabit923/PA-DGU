from api.users.dependencies import get_current_user
from core.database.models import User
from core.utils.paginated_response import PaginatedResponse
from fastapi import APIRouter, Depends, Form, Query
from starlette import status

from .schemas import CategoryCreate, CategoryRead, CategoryUpdate
from .service import CategoryService, category_service_factory

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CategoryRead)
async def add_category(
    title: str = Form(...),
    category_service: CategoryService = Depends(category_service_factory),
    user: User = Depends(get_current_user),
):
    category_data = CategoryCreate(title=title)
    new_category = await category_service.create_category(user, category_data)
    return new_category


@router.patch(
    "/{category_id}", status_code=status.HTTP_200_OK, response_model=CategoryRead
)
async def update_category(
    category_id: int,
    title: str = Form(...),
    category_service: CategoryService = Depends(category_service_factory),
    user=Depends(get_current_user),
):
    category = await category_service.get_news_by_id(category_id)
    category_data = CategoryUpdate(title=title)
    return await category_service.update_news(user, category, category_data)


@router.get(
    "", status_code=status.HTTP_200_OK, response_model=PaginatedResponse[CategoryRead]
)
async def get_all_news(
    category_service: CategoryService = Depends(category_service_factory),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    total, category = await category_service.get_all_categories(offset, limit)
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": category,
    }


@router.get(
    "/{category_id}", status_code=status.HTTP_200_OK, response_model=CategoryRead
)
async def get_category(
    category_id: int,
    category_service: CategoryService = Depends(category_service_factory),
):
    return await category_service.get_news_by_id(category_id)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    category_id: int,
    user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(category_service_factory),
):
    await category_service.delete_category(user, category_id)
    return
