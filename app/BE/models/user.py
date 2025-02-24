from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List

class User(BaseModel):
    name: str
    password: str
    friend: List[ObjectId] = Field(default_factory=list)
    book: List[ObjectId] = Field(default_factory=list)
    survey_completed: bool = False

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: lambda v: str(v)
        }