import logging
import smtplib
import ssl
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader

from app.core.settings import settings


class BaseEmailDataManager:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.sender_email = settings.SENDER_EMAIL
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD.get_secret_value()

        template_dir = settings.paths.EMAIL_TEMPLATES_DIR

        self.env = Environment(loader=FileSystemLoader(str(template_dir)))

    async def send_email(self, to_email: str, subject: str, body: str):
        self.logger.info(
            "Отправка email", extra={"to_email": to_email, "subject": subject}
        )
        try:
            msg = MIMEText(body, "html")
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = to_email

            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                self.logger.debug(
                    "Подключение к SMTP серверу %s:%s", self.smtp_server, self.smtp_port
                )
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                response = server.send_message(msg)

                if response:
                    failed_recipients = list(response.keys())
                    self.logger.error(
                        "Не удалось отправить email некоторым получателям: %s",
                        failed_recipients,
                        extra={"to_email": to_email, "subject": subject},
                    )
                    return False

            self.logger.info(
                "Email успешно отправлен",
                extra={"to_email": to_email, "subject": subject},
            )
            return True

        except smtplib.SMTPConnectError as e:
            self.logger.error(
                "Ошибка подключения к SMTP серверу: %s",
                str(e),
                extra={"to_email": to_email, "subject": subject},
            )
            raise
        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(
                "Ошибка аутентификации на SMTP сервере: %s",
                str(e),
                extra={"to_email": to_email, "subject": subject},
            )
            raise
        except smtplib.SMTPException as e:
            self.logger.error(
                "Ошибка SMTP при отправке email: %s",
                str(e),
                extra={"to_email": to_email, "subject": subject},
            )
            raise
        except TimeoutError as e:
            self.logger.error(
                "Таймаут при подключении к SMTP серверу: %s",
                str(e),
                extra={"to_email": to_email, "subject": subject},
            )
            raise
        except Exception as e:
            self.logger.error(
                "Неизвестная ошибка при отправке email: %s",
                str(e),
                extra={"to_email": to_email, "subject": subject},
            )
            raise
