from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from api.users.service import UserService
from api.users.utils import decode_token
from core.database import get_async_session

user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = decode_token(token)

        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
            )

        self.verify_token_data(token_data)
        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)
        return token_data is not None

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child classes.")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has provided an access token when a refresh token is needed",
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has provided an access token when a refresh token is needed",
            )


async def get_current_user(
    token: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_async_session),
):
    user_id = token["user_id"]
    user = await user_service.get_user_by_id(user_id, session)
    return user
