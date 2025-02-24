"""
Similarity Service
----------------
유저 간 유사도 관련 서비스 로직
"""

from typing import List, Dict, Any
from bson import ObjectId
from fastapi import HTTPException, status

from ..database.mongodb import get_user_db, get_crawling_db
from ..models.user_similarity import SimilarUser, Book

async def get_similar_users(user_id: str, limit: int = 5) -> List[SimilarUser]:
    """
    특정 유저와 가장 유사한 유저들을 조회
    
    Args:
        user_id (str): 기준 유저 ID
        limit (int): 반환할 유사 유저 수
        
    Returns:
        List[SimilarUser]: 유사한 유저 정보 리스트
    """
    try:
        db = await get_user_db()
        
        # 유사도 정보 조회
        similarity_doc = await db.user_similarities.find_one({"user_id": user_id})
        if not similarity_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="유사도 정보를 찾을 수 없습니다."
            )
            
        # 유사도 높은 순으로 정렬
        similarities = similarity_doc["similarities"]
        sorted_users = sorted(
            similarities.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        # 유사 유저들의 상세 정보 조회
        similar_users = []
        book_db = await get_crawling_db()
        
        for other_id, similarity_score in sorted_users:
            # 유저 정보 조회
            user = await db.users.find_one({"_id": ObjectId(other_id)})
            if not user:
                continue
                
            # 책 정보 조회
            books = []
            for book_id in user.get("book", []):
                book_doc = await book_db.books.find_one({"_id": book_id})
                if book_doc:
                    try:
                        book = Book(
                            _id=str(book_doc["_id"]),
                            title=book_doc.get("book_name", "Unknown"),  # book_name 필드 사용
                            author=book_doc.get("author", "Unknown"),
                            cover_image=book_doc.get("cover_image"),
                            description=book_doc.get("description")
                        )
                        books.append(book)
                    except Exception as e:
                        print(f"Error creating Book model: {str(e)}")
                        continue
            
            # SimilarUser 객체 생성
            try:
                similar_user = SimilarUser(
                    user_id=str(user["_id"]),
                    similarity_score=similarity_score,
                    books=books
                )
                similar_users.append(similar_user)
            except Exception as e:
                print(f"Error creating SimilarUser model: {e}")
                continue
            
        return similar_users
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"유사 유저 조회 중 오류가 발생했습니다: {str(e)}"
        )
