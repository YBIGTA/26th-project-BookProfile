"""
Similar Users Router
------------------
유사 유저 조회 관련 엔드포인트
"""

from fastapi import APIRouter, HTTPException, status
from typing import List

from ..models.user_similarity import SimilarUser
from ..services.similarity_service import get_similar_users

router = APIRouter(
    prefix="/api",
    tags=["similar-users"]
)

@router.get("/similar-users/{user_id}", response_model=List[SimilarUser])
async def get_similar_users_endpoint(
    user_id: str,
    limit: int = 5
) -> List[SimilarUser]:
    """
    특정 유저와 가장 유사한 유저들을 조회
    
    Args:
        user_id (str): 기준 유저 ID
        limit (int): 반환할 유사 유저 수 (기본값: 5)
        
    Returns:
        List[SimilarUser]: 유사한 유저 정보 리스트
    """
    return await get_similar_users(user_id, limit)
