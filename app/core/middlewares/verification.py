from fastapi import HTTPException, Request

from app.core.security.token import TokenManager


class VerificationMiddleware:
    ALLOWED_UNVERIFIED_PATHS = {
        "/api/v1/verification/verify-email",
        "/api/v1/verification/resend",
        "/api/v1/verification/status",
        "/api/v1/auth/logout",
        "/api/v1/users/profile",
    }

    VERIFICATION_REQUIRED_PATHS = {
        "/api/v1/users/update",
    }

    async def __call__(self, request: Request, call_next):
        path = request.url.path

        if not self._requires_auth(path):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return await call_next(request)

        try:
            token = TokenManager.get_token_from_header(auth_header)
            payload = TokenManager.decode_token(token)

            if self._requires_verification(path):
                is_limited = payload.get("limited", False)
                is_verified = not is_limited

                if not is_verified:
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "message": "Требуется подтверждение email",
                            "error_type": "email_verification_required",
                            "verification_url": "/api/v1/verification/resend",
                        },
                    )

        except Exception:
            pass

        return await call_next(request)

    def _requires_auth(self, path: str) -> bool:
        public_paths = {
            "/docs",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/register",
        }
        return not any(path.startswith(p) for p in public_paths)

    def _requires_verification(self, path: str) -> bool:
        if any(path.startswith(p) for p in self.ALLOWED_UNVERIFIED_PATHS):
            return False

        if any(path.startswith(p) for p in self.VERIFICATION_REQUIRED_PATHS):
            return True

        return True
