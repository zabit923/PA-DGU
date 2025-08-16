from typing import Any, Dict, Optional

from starlette import status

from app.core.exceptions import BaseAPIException


class InvalidFileTypeError(BaseAPIException):
    def __init__(
        self,
        detail: str = "Неверный тип файла. Поддерживаются только JPEG и PNG",
        extra: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=detail,
            error_type="invalid_file_type",
            extra=extra,
        )


class StorageError(BaseAPIException):
    def __init__(
        self,
        detail: str = "Ошибка при загрузке файла в хранилище",
        extra: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=500, detail=detail, error_type="storage_error", extra=extra
        )
