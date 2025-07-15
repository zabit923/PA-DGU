from functools import lru_cache

from .settings import Settings


class Config(Settings):
    def __init__(self, **kwargs):
        Settings.__init__(self, **kwargs)


@lru_cache
def get_config() -> Config:
    config_instance = Config()

    return config_instance


settings = get_config()

__all__ = ["settings"]
