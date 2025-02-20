from pydantic import BaseModel
from typing import List

class SurveyInput(BaseModel):
    ratings: List[int]
