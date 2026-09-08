class AppError(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ServiceUnavailableError(AppError):
    def __init__(self, message: str = "AI provider is not configured") -> None:
        super().__init__(message, 503)


class GuardUnavailableError(AppError):
    def __init__(self, message: str = "GUARD security gateway is unavailable") -> None:
        super().__init__(message, 503)


class AgentProcessingError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, 422)
