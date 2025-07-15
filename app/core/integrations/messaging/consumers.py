import logging

from faststream.rabbit.fastapi import Logger

from app.core.integrations.mail.base import BaseEmailDataManager
from app.schemas import (
    EmailMessageSchema,
    PasswordResetEmailSchema,
    RegistrationSuccessEmailSchema,
    VerificationEmailSchema,
)

from .broker import rabbit_router

logger = logging.getLogger("app.email.tasks")
logger.info("✨ Модуль consumers.py загружен")
email_manager = BaseEmailDataManager()


@rabbit_router.subscriber("email_queue")
async def process_email(message: EmailMessageSchema, logger: Logger):
    logger.info("📨 Обработка email для: %s", message.to_email)

    try:
        await email_manager.send_email(
            to_email=message.to_email, subject=message.subject, body=message.body
        )
        logger.info("✅ Email успешно отправлен: %s", message.to_email)
        return {"status": "success", "to_email": message.to_email}
    except Exception as e:
        logger.error("❌ Ошибка при отправке email: %s", str(e))
        return {"status": "error", "error": str(e), "to_email": message.to_email}


@rabbit_router.subscriber("verification_email_queue")
async def process_verification_email(message: VerificationEmailSchema, logger: Logger):
    from jinja2 import Environment, FileSystemLoader

    from app.core.settings import settings

    logger.info("📨 Подготовка письма верификации для: %s", message.to_email)

    try:
        template_dir = settings.paths.EMAIL_TEMPLATES_DIR
        env = Environment(loader=FileSystemLoader(str(template_dir)))

        template = env.get_template("verification.html")
        verification_url = f"{settings.VERIFICATION_URL}{message.verification_token}"

        html_content = template.render(
            user_name=message.user_name, verification_url=verification_url
        )

        await email_manager.send_email(
            to_email=message.to_email, subject=message.subject, body=html_content
        )

        logger.info("✅ Письмо верификации отправлено: %s", message.to_email)
        return {"status": "success", "to_email": message.to_email}
    except Exception as e:
        logger.error("❌ Ошибка при отправке письма верификации: %s", str(e))
        return {"status": "error", "error": str(e), "to_email": message.to_email}


@rabbit_router.subscriber("password_reset_email_queue")
async def process_password_reset_email(
    message: PasswordResetEmailSchema, logger: Logger
):
    from jinja2 import Environment, FileSystemLoader

    from app.core.settings import settings

    logger.info("📨 Подготовка письма сброса пароля для: %s", message.to_email)

    try:
        template_dir = settings.paths.EMAIL_TEMPLATES_DIR
        env = Environment(loader=FileSystemLoader(str(template_dir)))

        template = env.get_template("password_reset.html")
        reset_url = f"{settings.PASSWORD_RESET_URL}{message.reset_token}"

        html_content = template.render(user_name=message.user_name, reset_url=reset_url)

        await email_manager.send_email(
            to_email=message.to_email, subject=message.subject, body=html_content
        )

        logger.info("✅ Письмо сброса пароля отправлено: %s", message.to_email)
        return {"status": "success", "to_email": message.to_email}
    except Exception as e:
        logger.error("❌ Ошибка при отправке письма сброса пароля: %s", str(e))
        return {"status": "error", "error": str(e), "to_email": message.to_email}


@rabbit_router.subscriber("registration_success_email_queue")
async def process_registration_success_email(
    message: RegistrationSuccessEmailSchema, logger: Logger
):
    from jinja2 import Environment, FileSystemLoader

    from app.core.settings import settings

    logger.info("📨 Подготовка письма об успешной регистрации для: %s", message.to_email)

    try:
        template_dir = settings.paths.EMAIL_TEMPLATES_DIR
        env = Environment(loader=FileSystemLoader(str(template_dir)))

        template = env.get_template("registration_success.html")
        login_url = settings.LOGIN_URL

        html_content = template.render(user_name=message.user_name, login_url=login_url)

        await email_manager.send_email(
            to_email=message.to_email, subject=message.subject, body=html_content
        )

        logger.info("✅ Письмо об успешной регистрации отправлено: %s", message.to_email)
        return {"status": "success", "to_email": message.to_email}
    except Exception as e:
        logger.error("❌ Ошибка при отправке письма об успешной регистрации: %s", str(e))
        return {"status": "error", "error": str(e), "to_email": message.to_email}
