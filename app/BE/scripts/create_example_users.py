"""
Example Users Generation Script
-----------------------------
리뷰어 데이터를 기반으로 예시 유저를 생성하는 스크립트
"""

import asyncio
from typing import List, Dict, Any
import numpy as np
import random
import string
import sys
from bson import ObjectId
from sentence_transformers import SentenceTransformer
from collections import defaultdict

from ..database.mongodb import get_crawling_db, get_user_db
from ..models.user import User

# UTF-8 출력 설정
sys.stdout.reconfigure(encoding='utf-8')

# 책 임베딩과 동일한 모델 사용
_MODEL_NAME = "all-MiniLM-L6-v2"
_EMBEDDING_DIM = 384
_encoder = SentenceTransformer(_MODEL_NAME)

async def get_active_reviewers(min_books: int = 10) -> List[Dict[str, Any]]:
    """
    최소 min_books개의 서로 다른 책에 리뷰를 작성한 리뷰어 추출
    
    Args:
        min_books (int): 최소 리뷰 작성 책 수
        
    Returns:
        List[Dict[str, Any]]: 리뷰어 정보 리스트. 각 딕셔너리는 reviewer와 book_ids를 포함
    """
    db = await get_crawling_db()
    
    # 리뷰어별 리뷰한 책 목록 집계
    pipeline = [
        {"$match": {"reviewer": {"$ne": None}}},  # reviewer가 None인 경우 제외
        {"$group": {
            "_id": "$reviewer",
            "unique_books": {"$addToSet": "$book_id"},
            "review_count": {"$sum": 1}
        }},
        {"$match": {
            "$expr": {"$gte": [{"$size": "$unique_books"}, min_books]}
        }},
        {"$project": {
            "reviewer": "$_id",
            "book_ids": "$unique_books",
            "review_count": 1,
            "_id": 0
        }}
    ]
    
    result = await db.reviews.aggregate(pipeline).to_list(length=None)
    return result

async def get_reviewer_reviews(reviewer: str) -> List[str]:
    """
    특정 리뷰어의 모든 리뷰 텍스트 조회
    
    Args:
        reviewer (str): 리뷰어 이름
        
    Returns:
        List[str]: 리뷰 텍스트 리스트
    """
    db = await get_crawling_db()
    reviews = await db.reviews.find(
        {"reviewer": reviewer},
        {"review": 1}
    ).to_list(length=None)
    
    return [r["review"] for r in reviews if "review" in r]

def generate_user_embedding(reviews: List[str]) -> np.ndarray:
    """
    리뷰 텍스트들을 기반으로 유저 임베딩 생성
    
    Args:
        reviews (List[str]): 리뷰 텍스트 리스트
        
    Returns:
        np.ndarray: 임베딩 벡터
    """
    if not reviews:
        return np.zeros(_EMBEDDING_DIM)
        
    # 리뷰 텍스트 임베딩 생성 및 평균
    embeddings = _encoder.encode(reviews)
    return np.mean(embeddings, axis=0)

def generate_random_password(length: int = 12) -> str:
    """랜덤 패스워드 생성"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

async def create_user_document(
    reviewer: str,
    book_ids: List[str],
    embedding: np.ndarray
) -> Dict[str, Any]:
    """
    User 스키마에 맞는 문서 생성
    
    Args:
        reviewer (str): 리뷰어 이름
        book_ids (List[str]): 리뷰한 책 ID 리스트 (문자열)
        embedding (np.ndarray): 유저 임베딩
        
    Returns:
        Dict[str, Any]: 저장할 유저 문서
    """
    # book_ids를 ObjectId로 변환
    book_object_ids = [ObjectId(id_) for id_ in book_ids]
    
    user = User(
        name=reviewer,
        password=generate_random_password(),
        book=book_object_ids,
        survey_completed=True
    )
    
    # 임베딩 추가 (MongoDB에 저장하기 위해 리스트로 변환)
    user_dict = user.model_dump()  # Pydantic v2 방식 사용
    user_dict["embedding"] = embedding.tolist()
    
    return user_dict

async def main():
    """메인 실행 함수"""
    # 1. 활성 리뷰어 추출
    reviewers = await get_active_reviewers(min_books=10)
    print(f"Found {len(reviewers)} active reviewers")
    
    # 2. 유저 DB 연결
    user_db = await get_user_db()
    
    # 3. 각 리뷰어에 대해 처리
    for reviewer in reviewers:
        try:
            # 3.1 리뷰어의 모든 리뷰 텍스트 수집
            reviews = await get_reviewer_reviews(reviewer["reviewer"])
            
            if not reviews:
                print(f"Skipping {reviewer['reviewer']}: no reviews found")
                continue
                
            # 3.2 임베딩 생성
            embedding = generate_user_embedding(reviews)
            
            # 3.3 유저 문서 생성
            user_doc = await create_user_document(
                reviewer["reviewer"],
                reviewer["book_ids"],
                embedding
            )
            
            # 3.4 MongoDB에 저장
            await user_db.users.insert_one(user_doc)
            print(f"Created example user: {reviewer['reviewer']}")
            
        except Exception as e:
            print(f"Error processing reviewer {reviewer['reviewer']}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
