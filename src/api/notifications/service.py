from sqlalchemy.ext.asyncio import AsyncSession

from api.chats.group_chats.service import GroupMessageService
from api.chats.private_chats.service import PersonalMessageService
from api.exams.service import ExamService
from api.materials.service import LectureService
from api.users.schemas import UserShort
from config import settings
from core.database.models import (
    Exam,
    ExamResult,
    GroupMessage,
    Lecture,
    Notification,
    PrivateMessage,
)
from core.tasks import (
    send_new_exam_email,
    send_new_group_message_email,
    send_new_lecture_notification,
    send_new_private_message_email,
    send_new_result_to_teacher,
)

lecture_service = LectureService()
group_message_service = GroupMessageService()
private_message_service = PersonalMessageService()
exam_service = ExamService()


class NotificationService:
    async def create_lecture_notification(
        self,
        lecture: Lecture,
        session: AsyncSession,
    ):
        users = await lecture_service.get_group_users_by_lecture(lecture, session)
        for user in users:
            if not user.is_teacher:
                notification = Notification(
                    title="Новая лекция!",
                    body=f"Преподаватель {lecture.author.first_name} {lecture.author.last_name} написал новую лекцию."
                    f"\n http://{settings.run.host}:{settings.run.port}/api/v1/materials/get-lecture/{lecture.id}",
                    user=user,
                )
                session.add(notification)
        filtered_user_list = [
            u
            for u in users
            if u != lecture.author or not u.is_teacher or not u.ignore_messages
        ]
        simplified_user_list = [
            {"email": user.email, "username": user.username}
            for user in filtered_user_list
        ]
        send_new_lecture_notification.delay(lecture.id, simplified_user_list)
        await session.commit()

    async def create_group_message_notification(
        self,
        group_message: GroupMessage,
        session: AsyncSession,
    ):
        users = await group_message_service.get_group_users_by_message(
            group_message, session
        )
        for user in users:
            if not user.is_teacher:
                notification = Notification(
                    title="Новое сообщение в группе!",
                    body=f"Пользователь {group_message.sender.username} написал новое сообщение."
                    f"\n http://{settings.run.host}:{settings.run.port}/api/v1/chats/groups/get-messages/{group_message.group_id}",
                    user=user,
                )
                session.add(notification)
        filtered_user_list = [
            u for u in users if u != group_message.sender or not u.ignore_messages
        ]
        simplified_user_list = [
            {"email": user.email, "username": user.username}
            for user in filtered_user_list
        ]
        send_new_group_message_email.delay(
            group_message.group_id,
            simplified_user_list,
            group_message.text,
            group_message.sender.username,
        )
        await session.commit()

    async def create_private_message_notification(
        self,
        private_message: PrivateMessage,
        session: AsyncSession,
    ):
        users = await private_message_service.get_user_by_message(
            private_message, session
        )
        for user in users:
            if not private_message.sender == user:
                notification = Notification(
                    title="У вас новое сообщение!",
                    body=f"Пользователь {private_message.sender.username} написал новое сообщение."
                    f"\n http://{settings.run.host}:{settings.run.port}/api/v1/chats/chats/{private_message.room_id}",
                    user=user,
                )
                session.add(notification)
        filtered_user_list = [
            u for u in users if u != private_message.sender or not u.ignore_messages
        ]
        simplified_user_list = [
            {"email": user.email, "username": user.username}
            for user in filtered_user_list
        ]
        send_new_private_message_email.delay(
            private_message.room_id,
            simplified_user_list,
            private_message.text,
            private_message.sender.username,
        )
        await session.commit()

    async def create_new_exam_notification(
        self,
        exam: Exam,
        session: AsyncSession,
    ):
        users = await exam_service.get_group_users_by_exam(exam, session)
        for user in users:
            if not user.is_teacher:
                notification = Notification(
                    title="У вас новый экзамен!",
                    body=f"Преподаватель {exam.author} создал новый экзамен."
                    f"\n http://{settings.run.host}:{settings.run.port}/api/v1/exams/{exam.id}",
                    user=user,
                )
                session.add(notification)
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
        await session.commit()

    async def create_result_notification(
        self,
        result: ExamResult,
        session: AsyncSession,
    ):
        user = result.exam.author
        notification = Notification(
            title="Кто-то прошел ваш экзамен!",
            body=f"Студент {result.student.first_name} {result.student.last_name} прошел ваш экзамен '{result.exam.title}'."
            f"\n Результат: {result.score}."
            f"\n http://{settings.run.host}:{settings.run.port}/api/v1/exams/{result.exam.id}",
            user=user,
        )
        session.add(notification)
        author_data = UserShort.model_validate(result.exam.author).model_dump()
        user_data = UserShort.model_validate(result.student).model_dump()
        send_new_result_to_teacher.delay(
            author_data,
            user_data,
            result.exam.title,
            result.score,
            result.id,
        )
        await session.commit()
