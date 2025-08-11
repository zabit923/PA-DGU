from app.schemas.v1.base import BaseResponseSchema

from .base import (
    RegistrationDataSchema,
    ResendVerificationDataSchema,
    VerificationDataSchema,
    VerificationStatusDataSchema,
)


class RegistrationResponseSchema(BaseResponseSchema):
    data: RegistrationDataSchema


class VerificationResponseSchema(BaseResponseSchema):
    data: VerificationDataSchema


class ResendVerificationResponseSchema(BaseResponseSchema):
    data: ResendVerificationDataSchema


class VerificationStatusResponseSchema(BaseResponseSchema):
    data: VerificationStatusDataSchema
