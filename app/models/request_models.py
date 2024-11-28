from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional, List


class ReviewRequest(BaseModel):
    assignment_description: str
    github_repo_url: HttpUrl
    candidate_level: str

    @field_validator("assignment_description")
    def validate_assignment_description(cls, value: str) -> str:
        if len(value) < 10:
            raise ValueError(
                "Assignment description must be at least 10 characters long."
            )
        return value

    @field_validator("candidate_level")
    def validate_candidate_level(cls, value: str) -> str:
        allowed_levels = {"junior", "middle", "senior"}
        if value not in allowed_levels:
            raise ValueError(
                f'Candidate level must be one of: {", ".join(allowed_levels)}.'
            )
        return value


class ReviewResponse(BaseModel):
    found_files: Optional[List[str]] = Field(default_factory=list)
    downsides: Optional[str] = ""
    rating: Optional[str] = ""
    conclusion: Optional[str] = ""

    @field_validator("rating")
    def validate_rating(cls, value: Optional[str]) -> Optional[str]:
        if value and value not in {"1", "2", "3", "4", "5"}:
            raise ValueError(
                "Rating must be a string representing a number between 1 and 5."
            )
        return value

    @field_validator("downsides", "conclusion")
    def validate_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and len(value) > 500:
            raise ValueError("Downsides and conclusion must not exceed 500 characters.")
        return value
