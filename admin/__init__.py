from app.models import User

from .config import admin
from .views.users import UserAdmin

admin.add_view(UserAdmin(model=User, icon="fa-solid fa-user"))
