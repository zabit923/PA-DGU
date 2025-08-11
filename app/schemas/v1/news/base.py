from pydantic import Field
from schemas import BaseSchema

from app.schemas.v1.categories.response import CategoryResponseSchema


class NewsDataSchema(BaseSchema):
    title: str = Field(
        description="Название новости",
        example="Новая версия приложения выпущена",
    )
    text: str = Field(
        description="Текст новости",
        example="Мы рады сообщить о выпуске новой версии нашего приложения.",
    )
    time_to_read: int = Field(
        description="Время на чтение новости в минутах",
        example=5,
    )
    image: str = Field(
        description="Ссылка на изображение новости",
        example="https://example.com/image.jpg",
        default=None,
    )
    category: "CategoryResponseSchema"
