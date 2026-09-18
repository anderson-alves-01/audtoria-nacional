class ProblemError(Exception):
    def __init__(self, status: int, title: str, code: str, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.title = title
        self.code = code
        self.detail = detail


class UnauthorizedError(ProblemError):
    def __init__(self, detail: str = "Authentication is required") -> None:
        super().__init__(401, "Unauthorized", "unauthorized", detail)


class ForbiddenError(ProblemError):
    def __init__(self, detail: str) -> None:
        super().__init__(403, "Forbidden", "forbidden", detail)


class NotVisibleError(ProblemError):
    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(404, "Not Found", "not-found", detail)


class ValidationFailedError(ProblemError):
    def __init__(self, detail: str) -> None:
        super().__init__(422, "Unprocessable Entity", "validation-failed", detail)
