from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import numpy as np

from ..database.mongodb import get_crawling_db, get_user_db
from ..schemas.survey import Rating

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

class UserEmbedding:
    """사용자의 책 평가를 기반으로 임베딩을 생성하고 저장하는 클래스"""
    
    @staticmethod
    def _normalize_ratings(ratings: List[int]) -> np.ndarray:
        """
        1~5 범위의 rating을 -1~1 범위의 가중치로 변환
        
        Args:
            ratings (List[int]): 1~5 범위의 rating 리스트
            
        Returns:
            np.ndarray: -1~1 범위의 가중치 배열
        """
        return (np.array(ratings) - 3) / 2

    async def _get_book_embeddings(self, book_ids: List[str]) -> Dict[str, np.ndarray]:
        """
        주어진 book_id들에 대한 임베딩을 조회
        
        Args:
            book_ids (List[str]): 책 ID 리스트
            
        Returns:
            Dict[str, np.ndarray]: book_id를 key로, 임베딩을 value로 하는 딕셔너리
        """
        db = await get_crawling_db()
        book_embeddings = {}
        
        for book_id in book_ids:
            try:
                book = await db.books.find_one(
                    {"_id": ObjectId(book_id)},
                    {"embedding": 1}
                )
                if book and "embedding" in book:
                    book_embeddings[book_id] = np.array(book["embedding"])
            except Exception:
                continue
                
        return book_embeddings

    async def calculate_embedding(self, ratings: List[Rating]) -> Optional[np.ndarray]:
        """
        사용자의 책 평가를 기반으로 사용자 임베딩을 계산
        
        Args:
            ratings (List[Rating]): 책 평가 리스트
            
        Returns:
            Optional[np.ndarray]: 계산된 사용자 임베딩 벡터. 
                                유효한 임베딩이 하나도 없으면 None 반환
        """
        # 책 임베딩 조회
        book_ids = [r.book_id for r in ratings]
        book_embeddings = await self._get_book_embeddings(book_ids)
        
        if not book_embeddings:
            return None
            
        # 임베딩이 있는 책들의 rating만 추출
        valid_ratings = []
        valid_embeddings = []
        for rating in ratings:
            if rating.book_id in book_embeddings:
                valid_ratings.append(rating.rating)
                valid_embeddings.append(book_embeddings[rating.book_id])
        
        if not valid_embeddings:
            return None
            
        # rating을 가중치로 변환
        weights = self._normalize_ratings(valid_ratings)
        embeddings = np.stack(valid_embeddings)
        
        # 모든 가중치가 0이면 단순 평균 사용
        if np.all(weights == 0):
            return np.mean(embeddings, axis=0)
            
        # 가중 평균 계산
        return np.sum(weights[:, np.newaxis] * embeddings, axis=0) / np.sum(np.abs(weights))

    async def save_embedding(self, user_id: str, embedding: np.ndarray) -> bool:
        """
        계산된 임베딩을 사용자 문서에 저장
        
        Args:
            user_id (str): 사용자 ID
            embedding (np.ndarray): 저장할 임베딩 벡터
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            db = await get_user_db()
            result = await db.user.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"embedding": embedding.tolist()}}
            )
            return result.modified_count > 0
        except Exception:
            return False