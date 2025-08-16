from pydantic import Field
from app.schemas import BaseSchema


class CategoryDataSchema(BaseSchema):
    title: str = Field(
        description="Название категории",
        example="Программирование",
    )
