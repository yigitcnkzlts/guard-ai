class AppError(Exception):
    def __init__(self, message: str, status_code: int, code: str = "APPLICATION_ERROR", details: dict | None = None) -> None:
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, 404, "RESOURCE_NOT_FOUND")


class BadRequestError(AppError):
    def __init__(self, message: str = "Bad request") -> None:
        super().__init__(message, 400, "BAD_REQUEST")


class UpstreamError(AppError):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message, status_code, "UPSTREAM_ERROR")
