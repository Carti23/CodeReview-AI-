import pytest
from pydantic import ValidationError
from models.request_models import (
    ReviewRequest,
)


# Test case for valid ReviewRequest creation
def test_review_request_valid():
    # Create a ReviewRequest with valid data
    request = ReviewRequest(
        assignment_description="This is a valid description.",
        github_repo_url="https://github.com/example/repo",
        candidate_level="middle",  # Using "middle" as a valid candidate level
    )

    # Assert that the created object has the correct values
    assert request.assignment_description == "This is a valid description."
    assert str(request.github_repo_url) == "https://github.com/example/repo"
    assert request.candidate_level == "middle"


# Test case for invalid assignment description (too short)
def test_review_request_invalid_description():
    # Attempt to create a ReviewRequest with an invalid (short) description
    with pytest.raises(ValidationError) as exc_info:
        ReviewRequest(
            assignment_description="Short",  # This is too short
            github_repo_url="https://github.com/example/repo",
            candidate_level="mid",
        )

    # Assert that the correct error message is raised
    assert "Assignment description must be at least 10 characters long." in str(
        exc_info.value
    )


# Test case for invalid candidate level
def test_review_request_invalid_candidate_level():
    # Attempt to create a ReviewRequest with an invalid candidate level
    with pytest.raises(ValidationError) as exc_info:
        ReviewRequest(
            assignment_description="This is a valid description.",
            github_repo_url="https://github.com/example/repo",
            candidate_level="invalid_level",  # This is not a valid level
        )

    # Assert that the error message contains the expected text
    assert "Candidate level must be one of:" in str(
        exc_info.value
    )  # Check for part of the message
