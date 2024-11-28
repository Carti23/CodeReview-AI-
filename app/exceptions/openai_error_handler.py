import asyncio
import logging
from fastapi import HTTPException
from exceptions.excpetions import InvalidRequestError, OpenAIError


class OpenAIErrorHandler:
    def __init__(self, max_retries=5, backoff_factor=2):
        """
        Initializes the error handler with configurable settings.

        Args:
            max_retries (int): Maximum number of retries for rate limit errors.
            backoff_factor (int): Exponential backoff factor for retries.
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.logger = logging.getLogger("OpenAIErrorHandler")

    async def handle_rate_limit_error(self, retries: int) -> bool:
        """
        Handles rate limit errors with exponential backoff.

        Args:
            retries (int): Current retry count.

        Returns:
            bool: True if retries are available, False if max retries are reached.
        """
        if retries < self.max_retries:
            wait_time = self.backoff_factor**retries
            self.logger.warning(
                f"Rate limit exceeded. Retrying in {wait_time} seconds... (Retry {retries}/{self.max_retries})"
            )
            await asyncio.sleep(wait_time)
            return True
        else:
            self.logger.error("Max retries exceeded for rate limit error.")
            raise HTTPException(
                status_code=503,
                detail="Rate limit exceeded. Please try again later.",
            )

    def handle_invalid_request_error(self, error: InvalidRequestError):
        """
        Handles invalid request errors from OpenAI.

        Args:
            error (InvalidRequestError): The exception instance.

        Raises:
            HTTPException: A 400 error with a descriptive message.
        """
        self.logger.error(f"Invalid request error: {str(error)}")
        raise HTTPException(
            status_code=400,
            detail="Invalid request to OpenAI API. Check input parameters and format.",
        )

    def handle_openai_error(self, error: OpenAIError):
        """
        Handles general OpenAI API errors.

        Args:
            error (OpenAIError): The exception instance.

        Raises:
            HTTPException: A 500 error with a descriptive message.
        """
        self.logger.error(f"OpenAI API error: {str(error)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred with OpenAI API: {str(error)}",
        )

    def handle_unexpected_error(self, error: Exception):
        """
        Handles unexpected errors.

        Args:
            error (Exception): The exception instance.

        Raises:
            HTTPException: A 500 error with a descriptive message.
        """
        self.logger.exception(
            "Unexpected error occurred during OpenAI API interaction."
        )
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later.",
        )
