import pytest
from pydantic import ValidationError
from models.request_models import ReviewResponse

# Test case for valid ReviewResponse creation


def test_review_response_valid():
    # Create a ReviewResponse with valid data
    response = ReviewResponse(
        found_files=["file1.py", "file2.py"],
        downsides="Some minor issues.",
        rating="4",
        conclusion="Overall good.",
    )

    # Assert that the created object has the correct values
    assert response.found_files == ["file1.py", "file2.py"]
    assert response.downsides == "Some minor issues."
    assert response.rating == "4"
    assert response.conclusion == "Overall good."


# Test case for invalid rating in ReviewResponse


def test_review_response_invalid_rating():
    # Attempt to create a ReviewResponse with an invalid rating
    with pytest.raises(ValidationError) as exc_info:
        ReviewResponse(
            found_files=["file1.py"],
            downsides="Some issues.",
            rating="6",  # Invalid rating (should be between 1 and 5)
            conclusion="Conclusion here.",
        )

    # Assert that the correct error message is raised
    assert "Rating must be a string representing a number between 1 and 5." in str(
        exc_info.value
    )


# Test case for invalid optional string lengths in ReviewResponse


def test_review_response_invalid_optional_strings():
    # Attempt to create a ReviewResponse with an overly long downsides field
    with pytest.raises(ValidationError) as exc_info:
        ReviewResponse(
            found_files=["file1.py"],
            downsides="x" * 501,  # Exceeding maximum length of 500 characters
            rating="4",
            conclusion="Conclusion here.",
        )

    # Assert that the correct error message is raised
    assert "Downsides and conclusion must not exceed 500 characters." in str(
        exc_info.value
    )


# Test case for default values in ReviewResponse


def test_review_response_default_values():
    # Create a ReviewResponse without providing any values
    response = ReviewResponse()

    # Assert that default values are set correctly
    assert response.found_files == []
    assert response.downsides == ""
    assert response.rating == ""
    assert response.conclusion == ""
