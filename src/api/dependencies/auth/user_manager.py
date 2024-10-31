from fastapi import Depends

from core.auth.user_manager import UserManager

from .users import get_users_db


async def get_users_manager(user_db=Depends(get_users_db)):
    yield UserManager(user_db)
