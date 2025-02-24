from pydantic import BaseModel, Field
from typing import List

class Rating(BaseModel):
    book_id: str
    rating: int = Field(..., ge=1, le=5, description="1~5 사이의 점수")

class SurveyResponse(BaseModel):
    """설문 응답 데이터"""
    user_id: str
    ratings: List[Rating]