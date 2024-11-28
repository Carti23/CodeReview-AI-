# File: models/repository_models.py

from pydantic import BaseModel
from typing import List


class Result(BaseModel):
    """
    Data model to store the results of repository content fetching.

    Attributes:
        code_contents (str): Combined contents of all fetched code files.
        file_contents (List[str]): List of file paths for all fetched code files.
    """

    code_contents: str
    file_contents: List[str]

    def dict(self, *args, **kwargs):
        """
        Converts the Result object into a serializable dictionary for FastAPI responses.
        """
        return {
            "code_contents": self.code_contents,
            "file_contents": self.file_contents,
        }
