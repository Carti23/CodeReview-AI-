import re
import traceback
import logging
from fastapi import HTTPException
from services.github.github_access import fetch_repository_contents
from services.openai.openai_service import analyze_code
from models.request_models import ReviewRequest, ReviewResponse
from utils.logging_config.logging_config import logging_config

logging.config.dictConfig(logging_config)
logger = logging.getLogger("CodeReviewAI")


async def generate_review(request: ReviewRequest, repo_contents=None):
    """
    Generates a review for a given GitHub repository and assignment.

    Args:
        request (ReviewRequest): The review request object containing assignment details.
        repo_contents (optional): Pre-fetched repository contents. Defaults to None.

    Returns:
        ReviewResponse: Parsed review data.
    """
    try:
        # Step 1: Fetch repository contents if not provided
        github = repo_contents or await fetch_repository_contents(
            str(request.github_repo_url)
        )
        if not github.file_contents:
            raise HTTPException(
                status_code=400, detail="Repository contents are empty."
            )

        logger.info(f"Files in repository: {github.file_contents}")

        # Step 2: Validate and summarize repository contents
        github.file_contents = validate_and_transform_contents(github.file_contents)
        repo_files_summary = summarize_repo_contents(github.file_contents)
        logger.info(f"Repository contents summary: {repo_files_summary}")

        # Step 3: Analyze the code
        review = await analyze_code(
            assignment=request.assignment_description,
            level=request.candidate_level,
            contents=github.code_contents,
        )
        logger.debug(f"Raw response from analyze_code: {review}")

        # Step 4: Extract fields from the review
        review_data = parse_review(review, repo_files_summary)
        logger.info(f"Generated review data: {review_data}")

        return review_data

    except Exception as e:
        logger.error(f"Error in generate_review: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to generate review.")


def validate_and_transform_contents(file_contents):
    """
    Validates and transforms repository file contents into a consistent format.

    Args:
        file_contents (list): List of repository file data.

    Returns:
        list: Transformed list of dictionaries containing file paths and types.
    """
    if not isinstance(file_contents, list):
        raise HTTPException(
            status_code=400, detail="Repository contents must be a list."
        )

    # Transform plain paths into dictionaries
    if isinstance(file_contents[0], str):
        file_contents = [{"path": file, "type": "Unknown"} for file in file_contents]
        logger.warning(f"Transformed file paths into dictionaries: {file_contents}")

    if not all(isinstance(file, dict) for file in file_contents):
        raise HTTPException(
            status_code=400, detail="Repository contents structure is invalid."
        )

    return file_contents


def summarize_repo_contents(repo_contents):
    """
    Summarizes repository contents into a human-readable string for analysis.

    Args:
        repo_contents (list): List of repository files and directories.

    Returns:
        str: A summary of the repository contents.
    """
    if not isinstance(repo_contents, list):
        raise ValueError("Repository contents must be a list of files and directories.")

    summary_lines = [
        f"- {file.get('path', 'Unknown path')} ({file.get('type', 'Unknown type')})"
        for file in repo_contents
    ]
    return "\n".join(summary_lines)


def parse_review(review, repo_files_summary):
    """
    Parses the review response and extracts necessary fields.

    Args:
        review (str or dict): The response from analyze_code.
        repo_files_summary (str): Summary of repository files.

    Returns:
        ReviewResponse: Parsed review data.
    """
    MAX_LENGTH = 500  # Max character length for downsides and conclusion
    downsides, rating, conclusion = "", "", ""

    logger.info(f"Review data: {review}")

    if isinstance(review, str):  # Parse string-based review
        # Extract downsides
        if "### Downsides" in review:
            downsides_start = review.find("### Downsides")
            downsides_end = review.find("### Rating", downsides_start)
            downsides = (
                review[downsides_start + len("### Downsides") : downsides_end].strip()
                if downsides_end != -1
                else ""
            )

        # Extract rating
        if "### Rating" in review:
            rating_start = review.find("### Rating")
            rating_end = review.find("### Comments:", rating_start)
            rating_section = (
                review[rating_start + len("### Rating") : rating_end].strip()
                if rating_end != -1
                else ""
            )
            rating_match = re.search(r"\d+\/\d+", rating_section)
            if rating_match:
                raw_rating = rating_match.group(0).split("/")[0]
                # Clamp to [1, 5]
                rating = str(min(max(int(raw_rating), 1), 5))
            else:
                rating = "No rating provided"

        # Extract conclusion
        conclusion_start = review.find("### Comments:")
        conclusion = (
            review[conclusion_start + len("### Comments:") :].strip()
            if conclusion_start != -1
            else review.strip()
        )

    elif isinstance(review, dict):  # Parse dictionary-based review
        downsides = review.get("downsides", "")
        # Clamp rating
        rating = str(min(max(int(review.get("rating", 1)), 1), 5))
        conclusion = review.get("conclusion", "")

    else:
        logger.error("analyze_code did not return a valid string or dictionary.")
        raise ValueError("Invalid response format from analyze_code.")

    # Ensure downsides and conclusion do not exceed the max length
    downsides = downsides[:MAX_LENGTH]
    conclusion = conclusion[:MAX_LENGTH]

    return ReviewResponse(
        conclusion=conclusion,
        found_files=repo_files_summary.split("\n"),
        downsides=downsides,
        rating=rating,
    )
