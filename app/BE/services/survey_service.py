from fastapi import HTTPException, Request, status
from pymongo.database import Database
from bson import ObjectId
import numpy as np
from typing import List, Dict, Optional
from sklearn.metrics.pairwise import cosine_similarity

from ..models.user import User, UserEmbedding
from ..models.user_similarity import UserSimilarity
from ..database.mongodb import get_user_db
from .book_service import get_book_info
from ..schemas.survey import Rating

async def get_survey_books(db: Database):
    documents = await db["survey"].find({}).to_list(length=None)
    result = []
    for doc in documents:
        book_id = doc.get("book_id")
        if book_id is not None:
            book_info = await get_book_info(db, book_id)
            result.append(book_info)
    
    return result

async def get_survey_status(username: str, db: Database):
    user = await db["users"].find_one(
        {"name": username},
        {"survey_completed": 1}
    )
    return user["survey_completed"]

async def update_survey_status(username: str, db: Database):
    result = await db["users"].update_one(
        {"name": username},
        {"$set": {"survey_completed": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용자 상태 업데이트에 실패하였습니다."
        )
    return result

async def calculate_user_embedding(user_id: str, ratings: List[Rating]) -> Optional[np.ndarray]:
    """
    사용자의 설문 응답을 기반으로 임베딩을 계산
    
    Args:
        user_id (str): 사용자 ID
        ratings (List[Rating]): 설문 응답 (책 평가) 리스트
        
    Returns:
        Optional[np.ndarray]: 계산된 임베딩 벡터
    """
    user_embedding = UserEmbedding()
    embedding = await user_embedding.calculate_embedding(ratings)
    
    if embedding is not None:
        # 임베딩을 DB에 저장
        success = await user_embedding.save_embedding(user_id, embedding)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="임베딩 저장에 실패했습니다."
            )
    
    return embedding

async def calculate_and_save_similarities(user_id: str, user_embedding: np.ndarray):
    """
    한 사용자와 다른 모든 사용자 간의 유사도를 계산하고 저장
    
    Args:
        user_id (str): 사용자 ID
        user_embedding (np.ndarray): 사용자 임베딩 벡터
    """
    db = await get_user_db()
    
    # 임베딩이 있는 모든 사용자 조회
    users = await db.users.find(
        {"embedding": {"$exists": True}},
        {"_id": 1, "embedding": 1}
    ).to_list(length=None)
    
    # 자신을 제외한 다른 사용자들과의 유사도 계산
    similarities = {}
    for user in users:
        other_id = str(user["_id"])
        if other_id != user_id:  # 자기 자신은 제외
            other_embedding = np.array(user["embedding"])
            # 코사인 유사도 계산
            similarity = cosine_similarity(
                user_embedding.reshape(1, -1),
                other_embedding.reshape(1, -1)
            )[0][0]
            similarities[other_id] = float(similarity)
    
    # UserSimilarity 문서 생성/업데이트
    similarity_doc = UserSimilarity(
        user_id=user_id,
        similarities=similarities
    )
    
    # MongoDB에 저장
    await db.user_similarities.update_one(
        {"user_id": user_id},
        {"$set": similarity_doc.model_dump()},
        upsert=True
    )

async def process_survey_completion(user_id: str, ratings: List[Rating]):
    """
    설문 완료 처리: 임베딩 계산 및 유사도 저장
    
    Args:
        user_id (str): 사용자 ID
        ratings (List[Rating]): 설문 응답 리스트
    """
    # 1. 임베딩 계산
    embedding = await calculate_user_embedding(user_id, ratings)
    if embedding is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="임베딩 계산에 실패했습니다."
        )
    
    # 2. 유사도 계산 및 저장
    await calculate_and_save_similarities(user_id, embedding)
    
    # 3. 설문 완료 상태 업데이트
    db = await get_user_db()
    await update_survey_status(user_id, db)