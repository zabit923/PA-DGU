from app.core.integrations.mail.base import BaseEmailDataManager
from app.core.integrations.messaging import EmailProducer


class AuthEmailDataManager(BaseEmailDataManager):
    def __init__(self):
        super().__init__()
        self.producer = EmailProducer()

    async def send_verification_email(self, to_email: str, verification_token: str):
        self.logger.info(
            "Подготовка письма верификации",
            extra={"to_email": to_email},
        )

        try:
            return await self.producer.send_verification_email(
                to_email=to_email,
                verification_token=verification_token,
            )
        except Exception as e:
            self.logger.error(
                "Ошибка при подготовке письма верификации: %s",
                e,
                extra={"to_email": to_email},
            )
            raise

    async def send_password_reset_email(
        self, to_email: str, user_name: str, reset_token: str
    ):
        self.logger.info(
            "Подготовка письма для сброса пароля",
            extra={"to_email": to_email, "user_name": user_name},
        )

        try:
            return await self.producer.send_password_reset_email(
                to_email=to_email, user_name=user_name, reset_token=reset_token
            )
        except Exception as e:
            self.logger.error(
                "Ошибка при подготовке письма для сброса пароля: %s",
                e,
                extra={"to_email": to_email, "user_name": user_name},
            )
            raise

    async def send_registration_success_email(self, to_email: str, user_name: str):
        self.logger.info(
            "Подготовка письма об успешной регистрации",
            extra={"to_email": to_email, "user_name": user_name},
        )

        try:
            return await self.producer.send_registration_success_email(
                to_email=to_email, user_name=user_name
            )
        except Exception as e:
            self.logger.error(
                "Ошибка при подготовке письма об успешной регистрации: %s",
                e,
                extra={"to_email": to_email, "user_name": user_name},
            )
            raise
