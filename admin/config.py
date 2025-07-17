from starlette_admin.contrib.sqla import Admin

from app.core.connections.database import database_client

from .auth import CustomAuthProvider


def get_engine() -> None:
    engine = database_client.get_engine()
    return engine


admin = Admin(
    engine=get_engine(),
    logo_url="https://upload.wikimedia.org/wikipedia/ru/5/56/%D0%AD%D0%BC%D0%B1%D0%BB%D0%B5%D0%BC%D0%B0_%D0%94%D0%B0%D0%B3%D0%B5%D1%81%D1%82%D0%B0%D0%BD%D1%81%D0%BA%D0%BE%D0%B3%D0%BE_%D0%B3%D0%BE%D1%81%D1%83%D0%B4%D0%B0%D1%80%D1%81%D1%82%D0%B2%D0%B5%D0%BD%D0%BD%D0%BE%D0%B3%D0%BE_%D1%83%D0%BD%D0%B8%D0%B2%D0%B5%D1%80%D1%81%D0%B8%D1%82%D0%B5%D1%82%D0%B0.png",
    login_logo_url="https://upload.wikimedia.org/wikipedia/ru/5/56/%D0%AD%D0%BC%D0%B1%D0%BB%D0%B5%D0%BC%D0%B0_%D0%94%D0%B0%D0%B3%D0%B5%D1%81%D1%82%D0%B0%D0%BD%D1%81%D0%BA%D0%BE%D0%B3%D0%BE_%D0%B3%D0%BE%D1%81%D1%83%D0%B4%D0%B0%D1%80%D1%81%D1%82%D0%B2%D0%B5%D0%BD%D0%BD%D0%BE%D0%B3%D0%BE_%D1%83%D0%BD%D0%B8%D0%B2%D0%B5%D1%80%D1%81%D0%B8%D1%82%D0%B5%D1%82%D0%B0.png",
    favicon_url="https://upload.wikimedia.org/wikipedia/ru/5/56/%D0%AD%D0%BC%D0%B1%D0%BB%D0%B5%D0%BC%D0%B0_%D0%94%D0%B0%D0%B3%D0%B5%D1%81%D1%82%D0%B0%D0%BD%D1%81%D0%BA%D0%BE%D0%B3%D0%BE_%D0%B3%D0%BE%D1%81%D1%83%D0%B4%D0%B0%D1%80%D1%81%D1%82%D0%B2%D0%B5%D0%BD%D0%BD%D0%BE%D0%B3%D0%BE_%D1%83%D0%BD%D0%B8%D0%B2%D0%B5%D1%80%D1%81%D0%B8%D1%82%D0%B5%D1%82%D0%B0.png",
    auth_provider=CustomAuthProvider(),
)
