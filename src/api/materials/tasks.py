# @celery.task(name="api.materials.tasks.send_email")
# def send_new_lecture_notification(email: str, lecture: Lecture):
#     smtp_server = "smtp.gmail.com"
#     smtp_port = 587
#     email_host_user = settings.email.email_host_user
#     email_host_password = settings.email.email_host_password
#
#     recipients =
#
#     subject = "Новая лекция."
#     body = f"""
#     Привет {username},
#
#     Спасибо за регистрацию. Пожалуйста перейдите по ссылке чтоб активировать профиль:
#     {activation_link}
#     """
#
#     message = MIMEText(body, "plain")
#     message["Subject"] = subject
#     message["From"] = email_host_user
#     message["To"] = email
#
#     try:
#         with SMTP(smtp_server, smtp_port) as server:
#             server.starttls()
#             server.login(email_host_user, email_host_password)
#             server.sendmail(email_host_user, email, message.as_string())
#     except Exception as e:
#         raise RuntimeError(f"Failed to send email: {e}")
