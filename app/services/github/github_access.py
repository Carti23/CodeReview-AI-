import logging
import aiohttp
import base64
from typing import List
from services.configs.config import settings
from models.repository_models import Result
from exceptions.github_api_error_handler import (
    GitHubAPIError,
    FileFetchError,
    GitHubErrorHandler,
)
from utils.logging_config.logging_config import logging_config

logging.config.dictConfig(logging_config)
logger = logging.getLogger("CodeReviewAI")

# GitHub API headers
GITHUB_HEADERS = {"Authorization": f"token {settings.GITHUB_TOKEN}"}


async def fetch_repository_contents(repo_url: str) -> Result:
    try:
        repo_url_str = str(repo_url)
        owner_repo = repo_url_str.rstrip("/").split("/")[-2:]
        repo_api_url = (
            f"https://api.github.com/repos/{owner_repo[0]}/{owner_repo[1]}/contents"
        )

        logger.info(f"Fetching repository contents from: {repo_api_url}")

        headers = {
            "Authorization": f"token {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }

        async with aiohttp.ClientSession() as session:
            all_files = []
            await fetch_files_recursively(session, repo_api_url, headers, all_files)

        file_contents = [file_info["path"] for file_info in all_files]
        code_contents = await fetch_file_contents(all_files)

        return Result(code_contents=code_contents, file_contents=file_contents)
    except Exception as e:
        logger.error(f"An error occurred while fetching repository contents: {str(e)}")
        raise GitHubAPIError(
            "Error occurred while fetching repository contents."
        ) from e


async def fetch_files_recursively(
    session, url: str, headers: dict, all_files: List[dict]
):
    try:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                GitHubErrorHandler.handle_http_error(
                    status_code=response.status,
                    url=url,
                    message="Failed to fetch repository contents.",
                )
            contents = await response.json()

        for item in contents:
            if item["type"] == "file":
                all_files.append(item)
            elif item["type"] == "dir":
                await fetch_files_recursively(session, item["url"], headers, all_files)
    except Exception as e:
        logger.error(f"Error while fetching files recursively: {str(e)}")
        raise GitHubAPIError("Error occurred while fetching files recursively.") from e


async def fetch_file_contents(all_files: List[dict]) -> str:
    code_contents = ""
    async with aiohttp.ClientSession() as session:
        for file_info in all_files:
            # Use API URL instead of raw content URL
            file_url = file_info["url"]
            try:
                async with session.get(file_url, headers=GITHUB_HEADERS) as response:
                    if response.status != 200:
                        GitHubErrorHandler.handle_file_fetch_error(file_url)
                    file_data = await response.json()

                    # Check if the file is too large
                    if file_data.get("size", 0) > 1000000:  # Skip files larger than 1MB
                        logger.warning(f"Skipping large file: {file_info['path']}")
                        continue

                    content = file_data.get("content", "")
                    if content:
                        try:
                            decoded_content = base64.b64decode(content).decode(
                                "utf-8", errors="replace"
                            )
                            code_contents += f"\n\n# File: {file_info['path']}\n"
                            code_contents += decoded_content
                        except Exception as e:
                            logger.error(f"Error decoding file content: {str(e)}")
                    else:
                        logger.warning(
                            f"No content found for file: {file_info['path']}"
                        )
            except FileFetchError as e:
                logger.error(f"Error fetching file: {str(e)}")
                continue
            except Exception as e:
                logger.error(
                    f"Unexpected error processing file {file_info['path']}: {str(e)}"
                )
                continue
    return code_contents
