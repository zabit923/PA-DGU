from starlette.authentication import BaseUser


class CustomUser(BaseUser):
    def __init__(self, id: int):
        self.id = id

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return str(self.id)
