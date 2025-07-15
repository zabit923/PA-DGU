import logging
from typing import Any, Callable, Generic, List, Optional, Tuple, Type, TypeVar

from sqlalchemy import and_, asc, delete, desc, func, or_, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.sql.expression import Executable

from app.models.v1.base import BaseModel
from app.schemas.v1.base import BaseSchema
from app.schemas.v1.pagination import PaginationParams

M = TypeVar("M", bound=BaseModel)
T = TypeVar("T", bound=BaseSchema)


class SessionMixin:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


class BaseService(SessionMixin):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.logger = logging.getLogger(self.__class__.__name__)


class BaseDataManager(SessionMixin, Generic[T]):
    def __init__(self, session: AsyncSession, schema: Type[T], model: Type[M]):
        super().__init__(session)
        self.schema = schema
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)

    async def add_one(self, model: M) -> M:
        try:
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
            return model
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Ошибка при добавлении: %s", e)
            raise

    async def get_one(self, select_statement: Executable) -> M | None:
        try:
            self.logger.info("Получение записи из базы данных")
            self.logger.debug("SQL-запрос: %s", select_statement)
            result = await self.session.execute(select_statement)
            return result.scalar()
        except SQLAlchemyError as e:
            self.logger.error("Ошибка при получении записи: %s", e)
            raise

    async def get_all(self, select_statement: Executable) -> List[M]:
        try:
            result = await self.session.execute(select_statement)
            return list(result.unique().scalars().all())
        except SQLAlchemyError as e:
            self.logger.error("Ошибка при получении записей: %s", e)
            return []

    async def update_one(self, model_to_update: M, updated_model: Any = None) -> M:
        try:
            if not model_to_update:
                raise ValueError("Модель для обновления не предоставлена")

            if updated_model:
                for key, value in updated_model.items():
                    if key != "id":
                        setattr(model_to_update, key, value)

            await self.session.commit()
            await self.session.refresh(model_to_update)
            return model_to_update
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Ошибка при обновлении: %s", e)
            raise

    async def update_some(self, model: M, fields: dict) -> M:
        try:
            for field, value in fields.items():
                setattr(model, field, value)

            await self.session.commit()
            await self.session.refresh(model)
            return model
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Ошибка при обновлении полей: %s", e)
            raise

    async def delete_one(self, delete_statement: Executable) -> bool:
        try:
            self.logger.debug("SQL запрос на удаление: %s", delete_statement)
            await self.session.execute(delete_statement)
            await self.session.flush()
            await self.session.commit()
            self.logger.info("Запись успешно удалена")
            return True
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Ошибка при удалении: %s", e)
            return False

    async def exists(self, select_statement: Executable) -> bool:
        try:
            result = await self.session.execute(select_statement)
            return result.scalar() is not None
        except SQLAlchemyError as e:
            self.logger.error("Ошибка при проверке существования: %s", e)
            return False

    async def count(self, select_statement: Optional[Select] = None) -> int:
        try:
            if select_statement is None:
                select_statement = select(self.model)

            count_query = select(func.count()).select_from(select_statement.subquery())
            result = await self.session.execute(count_query)
            return result.scalar() or 0
        except SQLAlchemyError as e:
            self.logger.error("Ошибка при подсчете записей: %s", e)
            return 0

    async def bulk_create(self, models: List[M]) -> List[M]:
        try:
            self.session.add_all(models)
            await self.session.commit()

            for model in models:
                await self.session.refresh(model)

            return models
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Ошибка при массовом добавлении: %s", e)
            raise

    async def bulk_update(self, models: List[M]) -> List[M]:
        try:
            await self.session.commit()

            for model in models:
                await self.session.refresh(model)

            return models
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Ошибка при массовом обновлении: %s", e)
            raise

    async def get_or_create(
        self, filters: dict, defaults: Optional[dict] = None
    ) -> Tuple[M, bool]:
        try:
            conditions = []
            for field, value in filters.items():
                conditions.append(getattr(self.model, field) == value)

            statement = select(self.model).where(and_(*conditions))
            instance = await self.get_one(statement)

            if instance:
                return instance, False

            create_data = {**filters}
            if defaults:
                create_data.update(defaults)

            new_instance = self.model(**create_data)
            self.session.add(new_instance)
            await self.session.commit()
            await self.session.refresh(new_instance)

            return new_instance, True
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Ошибка при получении или создании записи: %s", e)
            raise

    async def update_or_create(self, filters: dict, defaults: dict) -> Tuple[M, bool]:
        try:
            conditions = []
            for field, value in filters.items():
                conditions.append(getattr(self.model, field) == value)

            statement = select(self.model).where(and_(*conditions))
            instance = await self.get_one(statement)

            if instance:
                for field, value in defaults.items():
                    setattr(instance, field, value)

                await self.session.commit()
                await self.session.refresh(instance)
                return instance, False

            create_data = {**filters, **defaults}
            new_instance = self.model(**create_data)
            self.session.add(new_instance)
            await self.session.commit()
            await self.session.refresh(new_instance)

            return new_instance, True
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Ошибка при обновлении или создании записи: %s", e)
            raise

    async def filter_by(self, **kwargs) -> List[M]:
        try:
            conditions = []

            for key, value in kwargs.items():
                if "__" in key:
                    field, operator = key.split("__", 1)
                    column = getattr(self.model, field)

                    if operator == "eq":
                        conditions.append(column == value)
                    elif operator == "ne":
                        conditions.append(column != value)
                    elif operator == "gt":
                        conditions.append(column > value)
                    elif operator == "lt":
                        conditions.append(column < value)
                    elif operator == "gte":
                        conditions.append(column >= value)
                    elif operator == "lte":
                        conditions.append(column <= value)
                    elif operator == "in":
                        conditions.append(column.in_(value))
                    elif operator == "not_in":
                        conditions.append(~column.in_(value))
                    elif operator == "like":
                        conditions.append(column.like(value))
                    elif operator == "ilike":
                        conditions.append(column.ilike(value))
                    elif operator == "is_null":
                        if value:
                            conditions.append(column.is_(None))
                        else:
                            conditions.append(column.is_not(None))
                else:
                    conditions.append(getattr(self.model, key) == value)

            statement = select(self.model).where(and_(*conditions))
            return await self.get_all(statement)
        except (SQLAlchemyError, AttributeError) as e:
            self.logger.error("Ошибка при фильтрации записей: %s", e)
            return []

    async def execute_raw_query(self, query: str, params: Optional[dict] = None) -> Any:
        try:
            result = await self.session.execute(text(query), params or {})
            return result
        except SQLAlchemyError as e:
            self.logger.error("Ошибка при выполнении произвольного запроса: %s", e)
            raise


class BaseEntityManager(BaseDataManager[T]):
    def __init__(self, session, schema: Type[T], model: Type[M]):
        super().__init__(session, schema, model)

    async def add_item(self, model: M) -> T:
        model_instance = await self.add_one(model)
        return self.schema.model_validate(model_instance)

    async def get_item(self, item_id: int) -> T | None:
        statement = select(self.model).where(self.model.id == item_id)
        model_instance = await self.get_one(statement)
        if model_instance is None:
            return None
        return self.schema.model_validate(model_instance)

    async def get_item_by_field(self, field: str, value: Any) -> Optional[T]:
        statement = select(self.model).where(getattr(self.model, field) == value)
        model_instance = await self.get_one(statement)

        if model_instance is None:
            return None

        return self.schema.model_validate(model_instance)

    async def get_model_by_field(self, field: str, value: Any) -> Optional[M]:
        statement = select(self.model).where(getattr(self.model, field) == value)
        return await self.get_one(statement)

    async def get_items(
        self,
        statement: Optional[Executable] = None,
        schema: Optional[Type[T]] = None,
        transform_func: Optional[Callable[[M], Any]] = None,
    ) -> List[T]:
        if statement is None:
            statement = select(self.model)

        models = await self.get_all(statement)
        schema_to_use = schema or self.schema

        if transform_func:
            models = [transform_func(model) for model in models]

        return [schema_to_use.model_validate(model) for model in models]

    async def get_items_by_field(self, field: str, value: any) -> list[T]:
        statement = select(self.model).where(getattr(self.model, field) == value)
        return await self.get_items(statement)

    async def get_paginated_items(
        self,
        select_statement: Select,
        pagination: PaginationParams,
        schema: Optional[Type[T]] = None,
        transform_func: Optional[Callable[[M], Any]] = None,
    ) -> tuple[List[T], int]:
        items = []
        total = 0

        try:
            total = (
                await self.session.scalar(
                    select(func.count()).select_from(select_statement.subquery())
                )
                or 0
            )

            sort_column = getattr(self.model, pagination.sort_by)
            select_statement = select_statement.order_by(
                desc(sort_column) if pagination.sort_desc else asc(sort_column)
            )

            select_statement = select_statement.offset(pagination.skip).limit(
                pagination.limit
            )

            models: List[M] = await self.get_all(select_statement)

            schema_to_use = schema or self.schema

            for model in models:
                if transform_func:
                    model = transform_func(model)
                items.append(schema_to_use.model_validate(model))

        except SQLAlchemyError as e:
            self.logger.error("Ошибка при получении пагинированных записей: %s", e)

        return items, total

    async def update_item(self, item_id: int, updated_item: T) -> T:
        statement = select(self.model).where(self.model.id == item_id)
        model_instance = await self.get_one(statement)

        if not model_instance:
            raise ValueError(f"Элемент с ID {item_id} не найден")

        updated_model = await self.update_one(model_instance, updated_item)

        return self.schema.model_validate(updated_model)

    async def update_items(self, item_id: int, fields: dict) -> T:
        statement = select(self.model).where(self.model.id == item_id)
        model = await self.get_one(statement)

        if not model:
            raise ValueError(f"Элемент с ID {item_id} не найден")

        updated_model = await self.update_some(model, fields)

        return self.schema.model_validate(updated_model)

    async def delete_item(self, item_id: int) -> bool:
        statement = delete(self.model).where(self.model.id == item_id)
        return await self.delete_one(statement)

    async def delete_items(self) -> bool:
        statement = delete(self.model)
        return await self.delete_one(statement)

    async def search_items(self, q: str, fields: Optional[List[str]] = None) -> List[T]:
        if fields is None:
            if hasattr(self.model, "title"):
                fields = ["title"]
            elif hasattr(self.model, "name"):
                fields = ["name"]
            else:
                raise AttributeError(
                    "Модель не имеет атрибута 'title' или 'name'. Укажите поля для поиска явно."
                )

        invalid_fields = [field for field in fields if not hasattr(self.model, field)]
        if invalid_fields:
            raise AttributeError(
                f"Модель не имеет следующих атрибутов: {', '.join(invalid_fields)}"
            )

        conditions = []
        for field in fields:
            conditions.append(getattr(self.model, field).ilike(f"%{q}%"))

        if not conditions:
            return []

        statement = select(self.model).where(or_(*conditions))

        return await self.get_items(statement)

    async def item_exists(self, item_id: int) -> bool:
        statement = select(self.model).where(self.model.id == item_id)
        return await self.exists(statement)

    async def bulk_create_items(self, models: List[M]) -> List[T]:
        model_instances = await self.bulk_create(models)
        return [self.schema.model_validate(model) for model in model_instances]
