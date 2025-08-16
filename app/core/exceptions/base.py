import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import pytz
from fastapi import HTTPException

logger = logging.getLogger(__name__)
moscow_tz = pytz.timezone("Europe/Moscow")


class BaseAPIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_type: str,
        extra: Optional[Dict[Any, Any]] = None,
    ) -> None:

        self.error_type = error_type
        self.extra = extra or {}

        context = {
            "timestamp": datetime.now(moscow_tz).isoformat(),
            "request_id": str(uuid.uuid4()),
            "status_code": status_code,
            "error_type": error_type,
            **(extra or {}),
        }

        logger.error(detail, extra=context)
        super().__init__(status_code=status_code, detail=detail)
