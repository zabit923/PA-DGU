from typing import Dict, Generic, List, Type, TypeVar

from pydantic import BaseModel

from app.schemas.v1.base import CommonBaseSchema

T = TypeVar("T", bound=CommonBaseSchema)


class SortOption(BaseModel):
    field: str
    description: str


class BaseSortFields:
    CREATED_AT = SortOption(
        field="created_at", description="Сортировка по дате создания"
    )
    UPDATED_AT = SortOption(
        field="updated_at", description="Сортировка по дате обновления"
    )

    @classmethod
    def get_default(cls) -> SortOption:
        return cls.UPDATED_AT

    @classmethod
    def get_all_fields(cls) -> Dict[str, SortOption]:
        fields = {}
        for base_cls in cls.__mro__:
            if hasattr(base_cls, "__dict__"):
                for name, value in base_cls.__dict__.items():
                    if isinstance(value, SortOption) and not name.startswith("_"):
                        fields[name] = value
        return fields

    @classmethod
    def get_field_values(cls) -> List[str]:
        return [option.field for option in cls.get_all_fields().values()]

    @classmethod
    def is_valid_field(cls, field: str) -> bool:
        return field in cls.get_field_values()

    @classmethod
    def get_field_or_default(cls, field: str) -> str:
        if cls.is_valid_field(field):
            return field
        return cls.get_default().field


class SortFields(BaseSortFields):
    """
    Стандартные поля сортировки, доступные для всех сущностей.

    Наследует базовые поля сортировки (created_at, updated_at) без добавления новых.
    Используется как класс по умолчанию, когда специфичный класс не найден.

    """


class UserSortFields(BaseSortFields):
    USERNAME = SortOption(
        field="username", description="Сортировка по имени пользователя"
    )


class SortFieldRegistry:
    _registry: Dict[str, Type[BaseSortFields]] = {
        "User": UserSortFields,
        "default": SortFields,
    }

    @classmethod
    def get_sort_field_class(cls, entity_name: str) -> Type[BaseSortFields]:
        return cls._registry.get(entity_name, cls._registry["default"])


class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int


class PaginationParams:
    def __init__(
        self,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "updated_at",
        sort_desc: bool = True,
        entity_name: str = "default",
    ):
        self.skip = skip
        self.limit = limit

        sort_field_class = SortFieldRegistry.get_sort_field_class(entity_name)

        self.sort_by = sort_field_class.get_field_or_default(sort_by)
        self.sort_desc = sort_desc

    @property
    def page(self) -> int:
        return self.skip // self.limit + 1
