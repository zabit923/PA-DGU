from .auth import (
    AuthenticationError,
    InvalidCredentialsError,
    InvalidCurrentPasswordError,
    InvalidEmailFormatError,
    InvalidPasswordError,
    TokenError,
    TokenExpiredError,
    TokenInvalidError,
    TokenMissingError,
    WeakPasswordError,
)
from .base import BaseAPIException
from .categories import CategoryNotFoundError
from .common import InvalidFileTypeError, StorageError
from .groups import GroupNotFoundError
from .materials import LectureNotFoundError
from .rate_limit import RateLimitExceededError
from .users import ForbiddenError, UserCreationError, UserExistsError, UserNotFoundError

__all__ = [
    "BaseAPIException",
    "AuthenticationError",
    "InvalidCredentialsError",
    "InvalidEmailFormatError",
    "InvalidPasswordError",
    "InvalidCurrentPasswordError",
    "WeakPasswordError",
    "TokenError",
    "TokenMissingError",
    "TokenExpiredError",
    "TokenInvalidError",
    "ForbiddenError",
    "UserNotFoundError",
    "UserCreationError",
    "UserExistsError",
    "InvalidFileTypeError",
    "StorageError",
    "RateLimitExceededError",
    "GroupNotFoundError",
    "LectureNotFoundError",
    "CategoryNotFoundError",
]
