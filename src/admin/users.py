from sqladmin import ModelView

from core.database.models import User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.first_name, User.last_name, User.username]
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"
