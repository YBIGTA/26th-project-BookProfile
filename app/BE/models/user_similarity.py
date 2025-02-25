"""
User Similarity Model
-------------------
사용자 간 유사도를 저장하고 관리하는 모델
"""

from typing import Dict, List, Optional
from bson import ObjectId
from pydantic import BaseModel, Field

class UserSimilarity(BaseModel):
    """사용자 간 유사도를 저장하는 모델"""
    user_id: str
    similarities: Dict[str, float] = Field(default_factory=dict)  # {user_id: similarity_score}
    
    class Config:
        json_encoders = {
            ObjectId: lambda v: str(v)
        }

class Book(BaseModel):
    """책 정보를 위한 모델"""
    _id: str
    title: str
    author: str
    cover_image: Optional[str] = None
    description: Optional[str] = None
    
    class Config:
        json_encoders = {
            ObjectId: lambda v: str(v)
        }

class SimilarUser(BaseModel):
    """유사 사용자 정보를 반환하기 위한 모델"""
    user_id: str
    similarity_score: float
    name: str
    
    class Config:
        json_encoders = {
            ObjectId: lambda v: str(v)
        }
