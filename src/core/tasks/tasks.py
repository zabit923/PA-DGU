from email.mime.text import MIMEText
from smtplib import SMTP
from typing import Dict, List, Optional

from celery import shared_task

from config import settings

smtp_server = "smtp.gmail.com"
smtp_port = 587
email_host_user = settings.email.email_host_user
email_host_password = settings.email.email_host_password


@shared_task
def send_new_lecture_notification(
    lecture_id: int, user_list: List[Dict[str, str]]
) -> None:
    for user in user_list:
        subject = "Новая лекция!"
        body = f"""
        Привет {user["username"]}
        Преподаватель выпустил новую лекцию:
        http://{settings.run.host}:{settings.run.port}/api/v1/materials/get-lecture/{lecture_id}
        """
        message = MIMEText(body, "plain")
        message["Subject"] = subject
        message["From"] = email_host_user
        message["To"] = user["email"]

        with SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_host_user, email_host_password)
            server.sendmail(email_host_user, user["email"], message.as_string())


@shared_task
def send_activation_email(email: str, username: str, activation_link: str) -> None:
    subject = "Активация аккаунта."
    body = f"""
    Привет {username},

    Спасибо за регистрацию. Пожалуйста перейдите по ссылке чтоб активировать профиль:
    {activation_link}
    """

    message = MIMEText(body, "plain")
    message["Subject"] = subject
    message["From"] = email_host_user
    message["To"] = email

    with SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_host_user, email_host_password)
        server.sendmail(email_host_user, email, message.as_string())


@shared_task
def send_new_group_message_email(
    group_id: int,
    user_list: List[Dict[str, str]],
    message_text: str,
    sender_username: str,
) -> None:
    for user in user_list:
        subject = "Новое сообщение!"
        body = f"""
        Привет {user["username"]},

        В группе новое сообщение от {sender_username}:

        {message_text[:50]}...

        http://{settings.run.host}:{settings.run.port}/api/v1/chats/groups/get-messages/{group_id}
        """

        message = MIMEText(body, "plain")
        message["Subject"] = subject
        message["From"] = email_host_user
        message["To"] = user["email"]

        with SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_host_user, email_host_password)
            server.sendmail(email_host_user, user["email"], message.as_string())


@shared_task
def send_new_private_message_email(
    room_id: int,
    user_list: List[Dict[str, str]],
    message_text: str,
    sender_username: str,
) -> None:
    for user in user_list:
        subject = "Новое сообщение!"
        body = f"""
        Привет {user["username"]},

        {sender_username} отправил(а) вам новое сообщение:

        {message_text[:50]}...

        http://{settings.run.host}:{settings.run.port}/api/v1/chats/private-chats/{room_id}
        """

        message = MIMEText(body, "plain")
        message["Subject"] = subject
        message["From"] = email_host_user
        message["To"] = user["email"]

        with SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_host_user, email_host_password)
            server.sendmail(email_host_user, user["email"], message.as_string())


@shared_task
def send_new_exam_email(
    exam_id: int,
    teacher_first_name: str,
    teacher_last_name: str,
    user_list: List[Dict[str, str]],
) -> None:
    for user in user_list:
        subject = "Новое сообщение!"
        body = f"""
        Привет {user["username"]},

        {teacher_first_name} {teacher_last_name} создал(а) новый тест:

        http://{settings.run.host}:{settings.run.port}/api/v1/exams/{exam_id}
        """

        message = MIMEText(body, "plain")
        message["Subject"] = subject
        message["From"] = email_host_user
        message["To"] = user["email"]

        with SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_host_user, email_host_password)
            server.sendmail(email_host_user, user["email"], message.as_string())


@shared_task
def send_new_result_to_teacher(
    author: dict,
    student: dict,
    exam_title: str,
    result_id: int,
    result_score: Optional[int] = None,
) -> None:
    subject = "Новое сообщение!"
    if result_score:
        body = f"""
        Здравствуйте {author["first_name"]} {author["last_name"]}!,

        Студент {student["first_name"]} {student["last_name"]} прошел тест "{exam_title}."
        Результат: {result_score}.

        http://{settings.run.host}:{settings.run.port}/api/v1/exams/get-result/{result_id}
        """
    else:
        body = f"""
        Здравствуйте {author["first_name"]} {author["last_name"]}!,

        Студент {student["first_name"]} {student["last_name"]} прошел тест "{exam_title}."
        выставьте оценку.

        http://{settings.run.host}:{settings.run.port}/api/v1/exams/get-result/{result_id}
        """

    message = MIMEText(body, "plain")
    message["Subject"] = subject
    message["From"] = email_host_user
    message["To"] = author["email"]

    with SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_host_user, email_host_password)
        server.sendmail(email_host_user, author["email"], message.as_string())


@shared_task
def send_update_result(
    result_id: int, exam_title: str, user: Dict[str, str], result_score: int
) -> None:
    subject = "Тебе выставили оценку!"
    body = f"""
    Экзамен: "{exam_title}"
    Оценкка: {result_score}
    http://{settings.run.host}:{settings.run.port}/api/v1/exams/get-result/{result_id}
    """

    message = MIMEText(body, "plain")
    message["Subject"] = subject
    message["From"] = email_host_user
    message["To"] = user["email"]

    with SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_host_user, email_host_password)
        server.sendmail(email_host_user, user["email"], message.as_string())


async def send_email_to_student(student, exam) -> None:
    subject = "Новое сообщение!"
    body = f"""
    Здравствуйте {student.username},
    Вы уже можете пройти экзамен "{exam.title}"!
    Успейте до {exam.end_time}.
    http://{settings.run.host}:{settings.run.port}/api/v1/exams/{exam.id}
    """
    message = MIMEText(body, "plain")
    message["Subject"] = subject
    message["From"] = email_host_user
    message["To"] = student.email

    with SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_host_user, email_host_password)
        server.sendmail(email_host_user, student.email, message.as_string())


async def send_email_to_teahcer(teacher, exam) -> None:
    subject = "Новое сообщение!"
    body = f"""
    Здравствуйте {teacher.username},
    Экзамен "{exam.title}" завершен!
    http://{settings.run.host}:{settings.run.port}/api/v1/exams/{exam.id}
    """
    message = MIMEText(body, "plain")
    message["Subject"] = subject
    message["From"] = email_host_user
    message["To"] = teacher.email

    with SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_host_user, email_host_password)
        server.sendmail(email_host_user, teacher.email, message.as_string())
