from typing import List, Tuple

from core.settings import settings
from models import Exam, ExamResult, Lecture, User
from schemas import (
    GroupMessageResponseSchema,
    NotificationCreateSchema,
    NotificationResponseSchema,
    PaginationParams,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.base import BaseService
from app.services.v1.exams.data_manager import ExamDataManager
from app.services.v1.notifications.data_manager import NotificationDataManager
from app.services.v1.users.data_manager import UserDataManager


class NotificationService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session)
        self.notification_data_manager = NotificationDataManager(session)
        self.user_data_manager = UserDataManager(session)
        self.exam_data_manager = ExamDataManager(session)

    async def get_all_notifications(
        self,
        user: User,
        pagination: PaginationParams,
    ) -> Tuple[List[NotificationResponseSchema], int]:
        (
            notifications,
            total,
        ) = await self.notification_data_manager.get_all_notifications(user, pagination)
        return notifications, total

    async def get_unread_notifications(
        self,
        user: User,
        pagination: PaginationParams,
    ) -> Tuple[List[NotificationResponseSchema], int]:
        notifications, total = await self.notification_data_manager.get_unreads(
            user, pagination
        )
        return notifications, total

    async def create_lecture_notification(self, lecture: Lecture) -> None:
        user_list = await self.user_data_manager.get_by_lecture(lecture)
        for user in user_list:
            data = NotificationCreateSchema(
                title="Новая лекция!",
                body=(
                    f"Преподаватель {lecture.author.username} выпустил новую лекцию: "
                    f"{settings.BASE_URL}/materials/get-lecture/{lecture.id}"
                ),
            )
            await self.notification_data_manager.create_notification(data, user)
        # filtered_user_list = [
        #     u
        #     for u in user_list
        #     if u != lecture.author or not u.is_teacher or not u.ignore_messages
        # ]
        # simplified_user_list = [
        #     {"email": user.email, "username": user.username}
        #     for user in filtered_user_list
        # ]
        # send_new_lecture_notification.delay(lecture.id, simplified_user_list)

    # async def create_private_message_notification(
    #     self,
    #     private_message: PrivateMessage,
    #     chat_service: PrivateChatService
    # ) -> None:
    #     users = await chat_service.get_users_by_message(private_message)
    #     for user in users:
    #         if not private_message.sender == user:
    #             title = "У вас новое сообщение!"
    #             body = (
    #                 f"Пользователь {private_message.sender.username} написал новое сообщение."
    #                 f"\n http://{settings.run.host}:{settings.run.port}/api/v1/chats/chats/{private_message.room_id}"
    #             )
    #             await self.notification_data_manager.create_notification(
    #                 title, body, user
    #             )
    #     filtered_user_list = [
    #         u for u in users if u != private_message.sender or not u.ignore_messages
    #     ]
    #     simplified_user_list = [
    #         {"email": user.email, "username": user.username}
    #         for user in filtered_user_list
    #     ]
    #     send_new_private_message_email.delay(
    #         private_message.room_id,
    #         simplified_user_list,
    #         private_message.text,
    #         private_message.sender.username,
    #     )

    async def create_group_message_notification(
        self,
        group_message: GroupMessageResponseSchema,
    ) -> None:
        users = await self.user_data_manager.get_users_by_group_message(group_message)
        for user in users:
            if not user.is_teacher:
                data = NotificationCreateSchema(
                    title="Новое сообщение в группе!",
                    body=(
                        f"Пользователь {group_message.sender.username} написал новое сообщение."
                        f"\n {settings.BASE_URL}/api/v1/chats/groups/get-messages/{group_message.group_id}"
                    ),
                )
                await self.notification_data_manager.create_notification(data, user)

    #     filtered_user_list = [
    #         u
    #         for u in users
    #         if u != group_message.sender or not u.ignore_messages or not u.is_teacher
    #     ]
    #     simplified_user_list = [
    #         {"email": user.email, "username": user.username}
    #         for user in filtered_user_list
    #     ]
    #     send_new_group_message_email.delay(
    #         group_message.group_id,
    #         simplified_user_list,
    #         group_message.text,
    #         group_message.sender.username,
    #     )

    async def create_result_notification(self, result: ExamResult) -> None:
        user = result.exam.author
        data = NotificationCreateSchema(
            title="Кто-то прошел ваш экзамен!",
            body=(
                f"Студент {result.student.first_name} {result.student.last_name} "
                f"прошел ваш экзамен '{result.exam.title}'.\n"
                f"Выставьте оценку.\n"
                f"exam_id: {result.exam.id}"
            ),
        )
        user = user
        await self.notification_data_manager.create_notification(data, user)

    async def update_result_notification(self, result: ExamResult) -> None:
        user = result.exam.author
        data = NotificationCreateSchema(
            title="Результат экзамена обновлен!",
            body=(
                f"Студент {result.student.first_name} {result.student.last_name} "
                f"обновил результат экзамена '{result.exam.title}'.\n"
                f"Выставьте оценку.\n"
                f"exam_id: {result.exam.id}"
            ),
        )
        await self.notification_data_manager.create_notification(data, user)
        # user_data = UserShort.model_validate(result.student).model_dump()
        # send_update_result.delay(
        #     result.id,
        #     result.exam.title,
        #     user_data,
        #     result.score,
        # )

    async def create_new_exam_notification(
        self,
        exam: Exam,
    ) -> None:
        user_list = await self.user_data_manager.get_by_exam(exam)
        for user in user_list:
            if not user.is_teacher:
                data = NotificationCreateSchema(
                    title="У вас новый экзамен!",
                    body=(
                        f"Преподаватель {exam.author.username} создал новый экзамен."
                        f"\n exam_id: {exam.id}"
                    ),
                )
                await self.notification_data_manager.create_notification(data, user)
        # filtered_user_list = [
        #     u
        #     for u in user_list
        #     if u != exam.author or not u.is_teacher or not u.ignore_messages
        # ]
        # simplified_user_list = [
        #     {"email": user.email, "username": user.username}
        #     for user in filtered_user_list
        # ]
        # send_new_exam_email.delay(
        #     exam.id,
        #     exam.author.first_name,
        #     exam.author.first_name,
        #     simplified_user_list,
        # )

    async def start_scheduled_exams(self) -> None:
        exams = await self.exam_data_manager.get_exams_ready_to_start()
        for exam in exams:
            user_list = await self.user_data_manager.get_by_exam(exam)
            for user in user_list:
                if not user.is_teacher:
                    data = NotificationCreateSchema(
                        title=f"Экзамен '{exam.title}' уже можно пройти!",
                        body=(
                            f"Вы уже можете пройти экзамен '{exam.title}'!"
                            f"Успейте до {exam.end_time}."
                            f"\n {settings.BASE_URL}/api/v1/exams/{exam.id}"
                        ),
                    )
                    await self.notification_data_manager.create_notification(data, user)
            await self.exam_data_manager.mark_exam_as_started(exam)
            # for group in exam.groups:
            #     students = await self.user_repository.get_by_group(group)
            #     for student in set(students):
            #         await send_email_to_student(student, exam)

    # async def end_scheduled_exams(self) -> None:
    #     exams = await self.exam_data_manager.get_exams_ready_to_end()
    #     for exam in exams:
    #         user = exam.author
    #         report = await self.exam_data_manager.create_results_report(exam)
    #         await self.notification_data_manager.create_notification(
    #             title=f"Экзамен '{exam.title}' завершен.",
    #             body=(
    #                 f"Экзамен '{exam.title}' завершен."
    #                 f"Отчет отправлен на ваш email"
    #                 f"\n http://{settings.run.host}:{settings.run.port}/api/v1/exams/{exam.id}"
    #             ),
    #             user=user,
    #         )
    #         await self.exam_data_manager.mark_exam_as_ended(exam)
    #         await send_email_to_teahcer(exam.author, exam, report)
