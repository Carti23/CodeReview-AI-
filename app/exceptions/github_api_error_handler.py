import logging
from fastapi import HTTPException

logger = logging.getLogger("GitHubAPIErrorHandler")


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""

    pass


class FileFetchError(Exception):
    """Custom exception for file fetching errors."""

    pass


class GitHubErrorHandler:
    """
    Handles errors and exceptions for interactions with the GitHub API.
    """

    @staticmethod
    def handle_http_error(status_code: int, url: str, message: str = ""):
        """
        Handles HTTP errors when interacting with the GitHub API.

        Args:
            status_code (int): The HTTP status code.
            url (str): The URL that caused the error.
            message (str): Additional context or error message.

        Raises:
            HTTPException: FastAPI HTTPException with appropriate details.
        """
        error_detail = (
            f"GitHub API request to {url} failed with status code {status_code}."
        )
        if message:
            error_detail += f" Message: {message}"

        logger.error(error_detail)

        if status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Repository not found at {url}. Please check the URL and try again.",
            )
        elif status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized access to GitHub API. Check your authentication token.",
            )
        elif status_code == 403:
            raise HTTPException(
                status_code=403,
                detail="Access forbidden by GitHub API. Ensure you have sufficient permissions.",
            )
        elif status_code >= 500:
            raise HTTPException(
                status_code=503,
                detail="GitHub API service is currently unavailable. Please try again later.",
            )
        else:
            raise HTTPException(
                status_code=status_code,
                detail=f"An unexpected error occurred with the GitHub API: {error_detail}",
            )

    @staticmethod
    def handle_file_fetch_error(file_url: str):
        """
        Handles errors when fetching file contents from GitHub.

        Args:
            file_url (str): The URL of the file that failed to fetch.

        Raises:
            FileFetchError: Custom exception for file fetching issues.
        """
        error_message = f"Failed to fetch file contents from {file_url}."
        logger.error(error_message)
        raise FileFetchError(error_message)
