class AppException(Exception):
    """Base class for all custom application exceptions."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class PermissionDeniedError(AppException):
    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(message, status_code=403)


class ValidationError(AppException):
    def __init__(self, message: str = "Invalid input"):
        super().__init__(message, status_code=422)


class ConflictError(AppException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409)


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class AuthorizationError(AppException):
    def __init__(self, message: str = "Authorization failed"):
        super().__init__(message, status_code=403)

class InvalidOTPError(AppException):
    def __init__(self, message: str = "Invalid or expired OTP"):
        super().__init__(message, status_code=400)