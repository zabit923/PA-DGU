from routes.v1.categories import CategoryRouter

from app.routes.base import BaseRouter
from app.routes.v1.auth import AuthRouter
from app.routes.v1.exams import ExamRouter
from app.routes.v1.groups import GroupRouter
from app.routes.v1.materials import LectureRouter
from app.routes.v1.news import NewsRouter
from app.routes.v1.notifications import NotificationRouter
from app.routes.v1.registration import RegisterRouter
from app.routes.v1.users import UserRouter


class APIv1(BaseRouter):
    def configure_routes(self):
        self.router.include_router(RegisterRouter().get_router())
        self.router.include_router(AuthRouter().get_router())
        self.router.include_router(UserRouter().get_router())
        self.router.include_router(GroupRouter().get_router())
        self.router.include_router(LectureRouter().get_router())
        self.router.include_router(NewsRouter().get_router())
        self.router.include_router(CategoryRouter().get_router())
        self.router.include_router(ExamRouter().get_router())
        self.router.include_router(NotificationRouter().get_router())
