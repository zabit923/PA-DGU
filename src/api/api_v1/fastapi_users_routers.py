from fastapi_users import FastAPIUsers

from api.dependencies.auth import auth_backend, get_users_manager
from core.database.models import User

fastapi_users = FastAPIUsers[User, int](
    get_users_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
