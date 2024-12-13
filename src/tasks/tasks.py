from email.mime.text import MIMEText
from smtplib import SMTP

from config import celery, settings


@celery.task
def send_activation_email(email: str, username: str, activation_link: str):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email_host_user = settings.email.email_host_user
    email_host_password = settings.email.email_host_password

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

    try:
        with SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_host_user, email_host_password)
            server.sendmail(email_host_user, email, message.as_string())
    except Exception as e:
        raise RuntimeError(f"Failed to send email: {e}")
