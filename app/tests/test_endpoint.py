import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from api.main import app
from models.request_models import ReviewResponse


# Fixture to create an async client for testing
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# Fixture to create a synchronous test client
@pytest.fixture
def test_client():
    return TestClient(app)


# Test the root endpoint to ensure it redirects to API documentation
@pytest.mark.asyncio
async def test_redirect_to_docs(async_client):
    async for client in async_client:
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {
            "message": "Navigate to /swagger for API documentation."
        }


# Test successful code review scenario
@pytest.mark.asyncio
async def test_review_code_success(async_client):
    async for client in async_client:
        # Mock the expected review response
        mock_review_response = ReviewResponse(
            found_files=["file1.py", "file2.py"],
            downsides="Some downsides",
            rating="4",
            conclusion="Good overall",
        )

        # Mock the necessary dependencies
        with patch(
            "app.services.github.github_access.fetch_repository_contents",
            new_callable=AsyncMock,
        ) as mock_fetch:
            with patch(
                "app.services.review.review_service.generate_review",
                new_callable=AsyncMock,
            ) as mock_generate:
                with patch(
                    "app.utils.redis_cache.redis_utils.get_redis_client",
                    new_callable=AsyncMock,
                ) as mock_redis:
                    # Set up mock return values
                    mock_fetch.return_value = "mock_repo_contents"
                    mock_generate.return_value = mock_review_response
                    mock_redis.return_value.get.return_value = None

                    # Send a POST request to the review endpoint
                    response = await client.post(
                        "/api/review",
                        json={
                            "assignment_description": "Test assignment",
                            "github_repo_url": "https://github.com/test/repo",
                            "candidate_level": "junior",
                        },
                    )

        # Assert the response is as expected
        assert response.status_code == 200
        assert response.json() == mock_review_response.model_dump()


# Test invalid input handling
@pytest.mark.asyncio
async def test_review_code_invalid_input(async_client):
    async for client in async_client:
        # Send a POST request with invalid input
        response = await client.post(
            "/api/review",
            json={
                "assignment_description": "Short",
                "github_repo_url": "https://github.com/test/repo",
                "candidate_level": "invalid_level",
            },
        )

        # Assert that the response indicates a validation error
        assert response.status_code == 422


# Test error handling when GitHub API fails
@pytest.mark.asyncio
async def test_review_code_github_error(async_client):
    async for client in async_client:
        # Mock the GitHub API to raise an exception
        with patch(
            "app.api.endpoints.fetch_repository_contents", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.side_effect = Exception("GitHub API error")

            # Send a POST request to the review endpoint
            response = await client.post(
                "/api/review",
                json={
                    "assignment_description": "Test assignment",
                    "github_repo_url": "https://github.com/test/repo",
                    "candidate_level": "senior",
                },
            )

        # Assert that the response indicates a server error
        assert response.status_code == 500
        assert "An unexpected error occurred" in response.json()["detail"]


# Test error handling when review generation fails
@pytest.mark.asyncio
async def test_review_code_generation_error(async_client):
    async for client in async_client:
        # Mock the dependencies
        with patch(
            "app.api.endpoints.fetch_repository_contents", new_callable=AsyncMock
        ) as mock_fetch:
            with patch(
                "app.api.endpoints.generate_review", new_callable=AsyncMock
            ) as mock_generate:
                # Set up mock return values and side effects
                mock_fetch.return_value = "mock_repo_contents"
                mock_generate.side_effect = Exception("Review generation error")

                # Send a POST request to the review endpoint
                response = await client.post(
                    "/api/review",
                    json={
                        "assignment_description": "Test assignment",
                        "github_repo_url": "https://github.com/test/repo",
                        "candidate_level": "junior",
                    },
                )

        # Assert that the response indicates a server error
        assert response.status_code == 500
        assert "An unexpected error occurred" in response.json()["detail"]
