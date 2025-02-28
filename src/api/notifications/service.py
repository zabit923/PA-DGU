# from typing import Sequence
#
# from api.exams.service import ExamService
# from api.users.schemas import UserShort
# from core.database.models import Notification, User, ExamResult, Exam
# from core.database.repositories import NotificationRepository
# from core.tasks import (
#     send_new_result_to_teacher,
# )
#
#
# exam_service = ExamService()
#
#
# class NotificationService:
#     def __init__(self, repository: NotificationRepository):
#         self.repository = repository
#
#     async def get_all_notifications(self, user: User) -> Sequence[Notification]:
#         return await self.repository.get_all(user)
#
#     async def get_unread_notifications(self, user: User) -> Sequence[Notification]:
#         return await self.repository.get_unreads(user)
#
#     async def create_result_notification(self, result: ExamResult) -> None:
#         user = result.exam.author
#         if result.score:
#             title = "Кто-то прошел ваш экзамен!"
#             body = (
#                 f"Студент {result.student.first_name} {result.student.last_name} "
#                 f"прошел ваш экзамен '{result.exam.title}'.\n"
#                 f"Результат: {result.score}.\n"
#                 f"exam_id: {result.exam.id}"
#             )
#             user = user
#         else:
#             title = "Кто-то прошел ваш экзамен!"
#             body = (
#                 f"Студент {result.student.first_name} {result.student.last_name} "
#                 f"прошел ваш экзамен '{result.exam.title}'.\n"
#                 f"Выставьте оценку.\n"
#                 f"exam_id: {result.exam.id}"
#             )
#             user = user
#         await self.repository.create_notification(title, body, user)
#         author_data = UserShort.model_validate(result.exam.author).model_dump()
#         user_data = UserShort.model_validate(result.student).model_dump()
#         send_new_result_to_teacher.delay(
#             author_data,
#             user_data,
#             result.exam.title,
#             result.id,
#             result.score,
#         )
#
#     async def update_result_notification(self, result: ExamResult) -> None:
#         user = result.exam.author
#         if result.score:
#             title = "Тебе выставили оценку!"
#             body = (
#                 f"Экзамен '{result.exam.title}'."
#                 f"прошел ваш экзамен '{result.exam.title}'."
#                 f"Результат: {result.score}."
#                 f"exam_id: {result.exam.id}"
#             )
#             user = user
#         else:
#             title = "Кто-то прошел ваш экзамен!"
#             body = (
#                 f"Студент {result.student.first_name} {result.student.last_name} "
#                 f"прошел ваш экзамен '{result.exam.title}'.\n"
#                 f"Выставьте оценку.\n"
#                 f"exam_id: {result.exam.id}"
#             )
#             user = user
#         await self.repository.create_notification(title, body, user)
#         author_data = UserShort.model_validate(result.exam.author).model_dump()
#         user_data = UserShort.model_validate(result.student).model_dump()
#         send_new_result_to_teacher.delay(
#             author_data,
#             user_data,
#             result.exam.title,
#             result.id,
#             result.score,
#         )
#
#     async def create_new_exam_notification(self, exam: Exam) -> None:
#         users = await exam_service.get_group_users_by_exam(exam, session)
#         for user in users:
#             if not user.is_teacher:
#                 notification = Notification(
#                     title="У вас новый экзамен!",
#                     body=f"Преподаватель {exam.author} создал новый экзамен."
#                     f"\n exam_id: {exam.id}",
#                     user=user,
#                 )
#                 session.add(notification)
#         filtered_user_list = [
#             u
#             for u in users
#             if u != exam.author or not u.is_teacher or not u.ignore_messages
#         ]
#         simplified_user_list = [
#             {"email": user.email, "username": user.username}
#             for user in filtered_user_list
#         ]
#         send_new_exam_email.delay(
#             exam.id,
#             exam.author.first_name,
#             exam.author.first_name,
#             simplified_user_list,
#         )
#         await session.commit()
