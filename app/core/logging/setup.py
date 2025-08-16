import logging
import os
from pathlib import Path

from app.core.settings import settings

from .formatters import CustomJsonFormatter, PrettyFormatter


def setup_logging():
    root = logging.getLogger()

    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)

    log_config = settings.logging.to_dict()

    console_formatter = (
        CustomJsonFormatter()
        if settings.logging.LOG_FORMAT == "json"
        else PrettyFormatter()
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    root.addHandler(console_handler)

    primary_log_path = log_config.get("filename")
    fallback_log_path = "./logs/app.log"

    if primary_log_path:
        try:
            log_path = Path(primary_log_path)
            if not log_path.parent.exists():
                os.makedirs(str(log_path.parent), exist_ok=True)

            with open(log_path, "a", encoding="utf-8") as _:
                pass

            file_handler = logging.FileHandler(
                filename=log_path,
                mode=log_config.get("filemode", "a"),
                encoding=log_config.get("encoding", "utf-8"),
            )
            file_handler.setFormatter(CustomJsonFormatter())
            root.addHandler(file_handler)
            print(f"✅ Логи будут писаться в: {log_path}")
        except (PermissionError, OSError) as e:
            print(
                f"⚠️ Не удалось использовать основной файл логов {primary_log_path}: {e}",
            )
            primary_log_path = None

    if not primary_log_path:
        try:
            fallback_path = Path(fallback_log_path)
            if not fallback_path.parent.exists():
                os.makedirs(str(fallback_path.parent), exist_ok=True)

            file_handler = logging.FileHandler(
                filename=str(fallback_path),
                mode=log_config.get("filemode", "a"),
                encoding=log_config.get("encoding", "utf-8"),
            )
            file_handler.setFormatter(CustomJsonFormatter())
            root.addHandler(file_handler)
            print(f"✅ Используем резервный путь для логов: {fallback_path}")
        except (PermissionError, OSError) as e:
            print(f"❌ Не удалось создать файл логов: {e}")

    root.setLevel(log_config.get("level", logging.INFO))

    for logger_name in [
        "python_multipart",
        "sqlalchemy.engine",
        "passlib",
        "aio_pika",
        "aiormq",
    ]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
