class AppBaseException(Exception):
    """
    Base exception class for all custom exceptions in the application.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class RateLimitError(AppBaseException):
    """
    Raised when the OpenAI API rate limit is exceeded.
    """

    def __init__(self, retry_after: int):
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds.")
        self.retry_after = retry_after


class OpenAIError(AppBaseException):
    """
    Raised for generic OpenAI API errors.
    """

    def __init__(self, message: str):
        super().__init__(f"OpenAI API error: {message}")


class InvalidRequestError(AppBaseException):
    """
    Raised when an invalid request is sent to the OpenAI API.
    """

    def __init__(self, message: str):
        super().__init__(f"Invalid request: {message}")
