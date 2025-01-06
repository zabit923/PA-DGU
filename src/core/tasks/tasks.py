import asyncio
from datetime import datetime
from email.mime.text import MIMEText
from smtplib import SMTP
from typing import Dict, List

import pytz
from celery import shared_task
from sqlalchemy import select

from api.materials.service import LectureService
from config import settings
from core.database.db import async_session_maker
from core.database.models import Exam, User

service = LectureService()
smtp_server = "smtp.gmail.com"
smtp_port = 587
email_host_user = settings.email.email_host_user
email_host_password = settings.email.email_host_password


@shared_task
def send_new_lecture_notification(lecture_id: int, user_list: List[Dict[str, str]]):
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
def send_activation_email(email: str, username: str, activation_link: str):
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
):
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
):
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
):
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
def check_exams_for_starting():
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(check_exams_for_starting_async())


async def check_exams_for_starting_async():
    async with async_session_maker() as session:
        statement = select(Exam).filter(
            Exam.start_time <= datetime.now(pytz.timezone("UTC")),
            Exam.is_ended == False,
            Exam.is_started == False,
        )
        result = await session.execute(statement)
        exams = result.unique().scalars().all()

        for exam in exams:
            exam.is_started = True
            await session.commit()

            for group in exam.groups:
                student_statement = (
                    select(User)
                    .join(User.member_groups)
                    .filter(
                        User.member_groups.contains(group), User.is_teacher == False
                    )
                )
                student_result = await session.execute(student_statement)
                students = student_result.scalars().all()

                for student in set(students):
                    await send_email_to_student(student, exam)


async def send_email_to_student(student, exam):
    subject = "Новое сообщение!"
    body = f"""
    Здравствуйте {student.username},

    Вы можете начать экзамен "{exam.title}"!


    Ссылка для начала: http://{settings.run.host}:{settings.run.port}/api/v1/exams/{exam.id}
    """
    message = MIMEText(body, "plain")
    message["Subject"] = subject
    message["From"] = email_host_user
    message["To"] = student.email

    with SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_host_user, email_host_password)
        server.sendmail(email_host_user, student.email, message.as_string())


@shared_task
def check_exams_for_ending():
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(check_exams_for_ending_async())


async def check_exams_for_ending_async():
    async with async_session_maker() as session:
        statement = select(Exam).filter(
            Exam.end_time <= datetime.now(pytz.timezone("UTC")), Exam.is_ended == False
        )
        result = await session.execute(statement)
        exams = result.unique().scalars().all()

        for exam in exams:
            exam.is_ended = True
            exam.is_started = False
            await session.commit()
            await send_email_to_teahcer(exam.author, exam)


async def send_email_to_teahcer(teacher, exam):
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
