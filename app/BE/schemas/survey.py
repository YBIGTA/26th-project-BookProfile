from pydantic import BaseModel, Field
from typing import List

class Rating(BaseModel):
    book_id: str
    rating: int = Field(..., ge=1, le=5, description="1~5 사이의 점수")

class SurveyInput(BaseModel):
    ratings: List[Rating]