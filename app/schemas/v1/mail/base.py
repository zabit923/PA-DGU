from pydantic import EmailStr

from app.schemas.v1.base import CommonBaseSchema


class EmailMessageSchema(CommonBaseSchema):
    to_email: EmailStr
    subject: str
    body: str


class VerificationEmailSchema(EmailMessageSchema):
    verification_token: str


class PasswordResetEmailSchema(EmailMessageSchema):
    user_name: str
    reset_token: str


class RegistrationSuccessEmailSchema(EmailMessageSchema):
    user_name: str
