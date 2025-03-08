from typing import TYPE_CHECKING, Sequence

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.users.schemas import UserShort
from config import settings
from core.database import get_async_session
from core.database.models import Exam, ExamResult, Notification, User
from core.database.repositories import (
    ExamRepository,
    NotificationRepository,
    UserRepository,
)
from core.tasks import send_new_exam_email, send_new_result_to_teacher
from core.tasks.tasks import send_email_to_student, send_email_to_teahcer

if TYPE_CHECKING:
    from api.exams.service import ExamService


class NotificationService:
    def __init__(
        self,
        notification_repository: NotificationRepository,
        exam_repository: ExamRepository,
        user_repository: UserRepository,
    ):
        self.notification_repository = notification_repository
        self.exam_repository = exam_repository
        self.user_repository = user_repository

    async def get_all_notifications(self, user: User) -> Sequence[Notification]:
        return await self.notification_repository.get_all(user)

    async def get_unread_notifications(self, user: User) -> Sequence[Notification]:
        return await self.notification_repository.get_unreads(user)

    async def create_result_notification(self, result: ExamResult) -> None:
        user = result.exam.author
        if result.score:
            title = "Кто-то прошел ваш экзамен!"
            body = (
                f"Студент {result.student.first_name} {result.student.last_name} "
                f"прошел ваш экзамен '{result.exam.title}'.\n"
                f"Результат: {result.score}.\n"
                f"exam_id: {result.exam.id}"
            )
            user = user
        else:
            title = "Кто-то прошел ваш экзамен!"
            body = (
                f"Студент {result.student.first_name} {result.student.last_name} "
                f"прошел ваш экзамен '{result.exam.title}'.\n"
                f"Выставьте оценку.\n"
                f"exam_id: {result.exam.id}"
            )
            user = user
        await self.notification_repository.create_notification(title, body, user)
        author_data = UserShort.model_validate(result.exam.author).model_dump()
        user_data = UserShort.model_validate(result.student).model_dump()
        send_new_result_to_teacher.delay(
            author_data,
            user_data,
            result.exam.title,
            result.id,
            result.score,
        )

    async def update_result_notification(self, result: ExamResult) -> None:
        user = result.exam.author
        if result.score:
            title = "Тебе выставили оценку!"
            body = (
                f"Экзамен '{result.exam.title}'."
                f"прошел ваш экзамен '{result.exam.title}'."
                f"Результат: {result.score}."
                f"exam_id: {result.exam.id}"
            )
            user = user
        else:
            title = "Кто-то прошел ваш экзамен!"
            body = (
                f"Студент {result.student.first_name} {result.student.last_name} "
                f"прошел ваш экзамен '{result.exam.title}'.\n"
                f"Выставьте оценку.\n"
                f"exam_id: {result.exam.id}"
            )
            user = user
        await self.notification_repository.create_notification(title, body, user)
        author_data = UserShort.model_validate(result.exam.author).model_dump()
        user_data = UserShort.model_validate(result.student).model_dump()
        send_new_result_to_teacher.delay(
            author_data,
            user_data,
            result.exam.title,
            result.id,
            result.score,
        )

    async def create_new_exam_notification(
        self,
        exam: Exam,
        exam_service: "ExamService",
    ) -> None:
        users = await exam_service.get_group_users_by_exam(exam)
        for user in users:
            if not user.is_teacher:
                title = "У вас новый экзамен!"
                body = (
                    f"Преподаватель {exam.author} создал новый экзамен."
                    f"\n exam_id: {exam.id}"
                )
                user = user
                await self.notification_repository.create_notification(
                    title, body, user
                )
        filtered_user_list = [
            u
            for u in users
            if u != exam.author or not u.is_teacher or not u.ignore_messages
        ]
        simplified_user_list = [
            {"email": user.email, "username": user.username}
            for user in filtered_user_list
        ]
        send_new_exam_email.delay(
            exam.id,
            exam.author.first_name,
            exam.author.first_name,
            simplified_user_list,
        )

    async def start_scheduled_exams(self) -> None:
        exams = await self.exam_repository.get_exams_ready_to_start()
        for exam in exams:
            users = await self.user_repository.get_by_exam(exam)
            for user in users:
                if not user.is_teacher:
                    await self.notification_repository.create_notification(
                        title=f"Экзамен '{exam.title}' уже можно пройти!",
                        body=(
                            f"Вы уже можете пройти экзамен '{exam.title}'! "
                            f"Успейте до {exam.end_time}."
                            f"\n http://{settings.run.host}:{settings.run.port}/api/v1/exams/{exam.id}"
                        ),
                        user=user,
                    )
            await self.exam_repository.mark_exam_as_started(exam)
            for group in exam.groups:
                students = await self.user_repository.get_by_group(group)
                for student in set(students):
                    await send_email_to_student(student, exam)

    async def end_scheduled_exams(self) -> None:
        exams = self.exam_repository.get_exams_ready_to_end()
        for exam in exams:
            user = exam.author
            await self.notification_repository.create_notification(
                title=f"Экзамен '{exam.title}' завершен.",
                body=(
                    f"Экзамен '{exam.title}' завершен."
                    f"\n http://{settings.run.host}:{settings.run.port}/api/v1/exams/{exam.id}"
                ),
                user=user,
            )
            await self.exam_repository.mark_exam_as_ended(exam)
            await send_email_to_teahcer(exam.author, exam)


def notification_service_factory(session: AsyncSession = Depends(get_async_session)):
    return NotificationService(
        NotificationRepository(session),
        UserRepository(session),
        ExamRepository(session),
    )
