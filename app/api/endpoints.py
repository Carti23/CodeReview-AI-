import logging
import json
from fastapi import APIRouter, HTTPException, Depends
from redis.asyncio import Redis
from models.request_models import ReviewRequest, ReviewResponse
from services.github.github_access import fetch_repository_contents
from services.review.review_service import generate_review
from utils.redis_cache.redis_utils import get_redis_client
from utils.logging_config.logging_config import logging_config

logging.config.dictConfig(logging_config)
logger = logging.getLogger("CodeReviewAI")

# Router setup
review_router = APIRouter()


@review_router.post("/review", response_model=ReviewResponse)
async def review_code(request: ReviewRequest, redis: Redis = Depends(get_redis_client)):
    """
    Endpoint to review code from a GitHub repository.

    Steps:
    1. Fetch repository contents from GitHub.
    2. Check Redis cache for an existing review.
    3. Generate a new review if no cached response is found.
    4. Cache the generated review and return it.

    Args:
        request (ReviewRequest): The incoming request payload containing GitHub repo URL and candidate level.
        redis (Redis): Redis client dependency for caching.

    Returns:
        ReviewResponse: The review results.
    """
    try:
        # Step 1: Fetch repository contents and generate a unique cache key
        logger.info(f"Fetching repository contents for {request.github_repo_url}.")
        repo_contents = await fetch_repository_contents(request.github_repo_url)
        cache_key = f"review:{request.github_repo_url}:{request.candidate_level}"

        # Step 2: Check Redis cache for existing review
        logger.info(f"Checking cache for key: {cache_key}")
        cached_response = await redis.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit for key: {cache_key}")
            try:
                # Parse the cached response into a ReviewResponse object
                cached_review = ReviewResponse.parse_raw(cached_response)
                return cached_review
            except Exception as e:
                logger.error(f"Failed to parse cached response: {e}")
                # Remove corrupted cache if parsing fails
                await redis.delete(cache_key)

        # Step 3: Generate a new review if no cache exists
        logger.info("Cache miss. Generating a new review.")
        review = await generate_review(request, repo_contents)
        logger.info(f"Generated review: {review}")

        # Validate and format the generated review
        if isinstance(review, ReviewResponse):
            # Ensure all fields are populated with default values if missing
            review = ReviewResponse(
                found_files=review.found_files or [],
                downsides=review.downsides or "",
                rating=review.rating or "",
                conclusion=review.conclusion or "",
            )
            review_json = review.json()

        elif isinstance(review, str):
            # Validate the review string as JSON
            try:
                json.loads(review)  # Check if valid JSON
                review_json = review
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON string received from generate_review.")
        else:
            raise TypeError("Unsupported type for the review object.")

        # Step 4: Cache the generated review for 1 hour
        await redis.set(cache_key, review_json, ex=3600)
        logger.info(f"Cached review for key: {cache_key}")
        return ReviewResponse.parse_raw(review_json)

    except HTTPException as e:
        logger.error(f"HTTP exception occurred: {e.detail}")
        raise e

    except Exception as e:
        # Log unexpected errors and raise a 500 Internal Server Error
        logger.exception("Unexpected error occurred during review generation.")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )
