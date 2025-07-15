import logging

from app.schemas import (
    EmailMessageSchema,
    PasswordResetEmailSchema,
    RegistrationSuccessEmailSchema,
    VerificationEmailSchema,
)

from .broker import broker

logger = logging.getLogger("app.messaging.producers")


class MessageProducer:
    async def publish(self, message: dict, queue: str) -> bool:
        try:
            await broker.publish(message, queue)
            logger.info("Сообщение отправлено в очередь: %s", queue)
            return True
        except Exception as e:
            logger.error(
                "Ошибка при отправке сообщения в очередь %s: %s", queue, str(e)
            )
            raise


class EmailProducer(MessageProducer):
    async def send_email_task(self, to_email: str, subject: str, body: str) -> bool:
        message = EmailMessageSchema(to_email=to_email, subject=subject, body=body)

        return await self.publish(message.model_dump(), "email_queue")

    async def send_verification_email(
        self, to_email: str, verification_token: str
    ) -> bool:
        message = VerificationEmailSchema(
            to_email=to_email,
            subject="Подтверждение email адреса",
            body="",
            verification_token=verification_token,
        )

        return await self.publish(message.model_dump(), "verification_email_queue")

    async def send_password_reset_email(
        self, to_email: str, user_name: str, reset_token: str
    ) -> bool:
        message = PasswordResetEmailSchema(
            to_email=to_email,
            subject="Восстановление пароля",
            body="",
            user_name=user_name,
            reset_token=reset_token,
        )

        return await self.publish(message.model_dump(), "password_reset_email_queue")

    async def send_registration_success_email(
        self, to_email: str, user_name: str
    ) -> bool:
        message = RegistrationSuccessEmailSchema(
            to_email=to_email,
            subject="Регистрация успешно завершена",
            body="",
            user_name=user_name,
        )

        return await self.publish(
            message.model_dump(), "registration_success_email_queue"
        )
