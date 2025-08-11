import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class PathSettings:
    @staticmethod
    def find_project_root() -> Path:
        current_dir = Path.cwd()

        markers = [".git", "pyproject.toml", "README.md"]

        for parent in [current_dir, *current_dir.parents]:
            if any((parent / marker).exists() for marker in markers):
                return parent

        logger.warning(
            "Не удалось определить корень проекта, используем текущую директорию"
        )
        return current_dir

    PROJECT_ROOT = find_project_root()

    APP_DIR = PROJECT_ROOT / "app"
    CORE_DIR = APP_DIR / "core"
    TEMPLATES_DIR = CORE_DIR / "templates"
    EMAIL_TEMPLATES_DIR = TEMPLATES_DIR / "mail"
    POLICIES_DIR = CORE_DIR / "security" / "policies"

    @staticmethod
    def get_env_file_and_type() -> tuple[Path, str]:
        ENV_FILE = Path(".env")
        DEV_ENV_FILE = Path(".env.dev")

        env_file_path = os.getenv("ENV_FILE")
        if env_file_path:
            env_path = Path(env_file_path)
            if ".env.test" in str(env_path):
                env_type = "test"
            else:
                env_type = "custom"
        elif DEV_ENV_FILE.exists():
            env_path = DEV_ENV_FILE
            env_type = "dev"
        else:
            env_path = ENV_FILE
            env_type = "prod"
        logger.info("Запуск в режиме: %s", env_type.upper())
        logger.info("Конфигурация: %s", env_path)

        return env_path, env_type
